/* Ehsan Jan 15, 2020
from dir: /home/mare/Nolin/SeaIce/Code/C
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <ctype.h>
#include <MisrToolkit.h>
#include <MisrError.h>
#include <dirent.h>

#define NO_DATA -999999.0
#define BACKGROUND -999998.0
#define FOREGROUND -999997.0
#define TDROPOUT -999996.0
#define CMASKED -999995.0
#define LMASKED -999994.0
#define VERBOSE 0

typedef struct {
    int path;
    int orbit;
    int block;
    int line;
    int sample;
    double npts;
    double lat;
    double lon;
    double an;
    double ca;
    double cf;
    double rms;
    float weight;
    int cloud;
    double var;
} atm_type;

MTKt_status status;
atm_type *atm_fileObj;
int block_min, block_max;
int orbit;
int nfiles;
double *data = 0;
double *cfdata = 0;
double *londata = 0;
double *latdata = 0;

int nlines = 512;
int nsamples = 2048;

int read_misr_data(char *fname, int line, int sample, double *data);
//int write_data(char *fname, double *data, int nlines, int nsamples);
char *strsub(char *s, char *a, char *b);

int read_misr_data(char *fname, int line, int sample, double *data)
{
    FILE *f;
    int nlines = 512;
    int nsamples = 2048;
    double *array_data;

    f = fopen(fname, "r");
    if (!f) {
	fprintf(stderr,  "read_data: couldn't open %s\n", fname);
	return 0;
    }
	
    array_data = (double *) malloc(nlines * nsamples * sizeof(double));
    if (!array_data) {
	fprintf(stderr,  "read_data: couldn't malloc data\n");
	return 0;
    }
	
    if (fread(array_data, sizeof(double), (nlines * nsamples), f) != nlines * nsamples) { // On success, it reads n items from the file and returns n. On error or end of the file, it returns a number less than n.
	fprintf(stderr,  "read_data: couldn't read data in %s\n", fname);
	return 0;
    }

    *data = array_data[line * nsamples + sample];

    free(array_data);

    fclose(f);
    return 1;
}

char *strsub(char *s, char *a, char *b)
{
    char *p, t[256];
    p = strstr(s, a);
    if(p==NULL) return NULL;  /*a not found */
    t[0] = 0; /*now t contains empty string */
    strncat(t, s, p-s); /*copy part of s preceding a */
    strcat(t, b); /*add the substitute word */
    strcat(t, p+strlen(a)); /*add on the rest of s */
    strcpy(s, t);
    return p+strlen(b); /*p+s points after substitution */
}

//////////////////////////////////////////////////////////// main ///////////////////////////////////////////////////


int main(char argc, char *argv[]) {
    DIR *dirp;
    FILE *fp, *fm;
    struct dirent *entryObjPtr; // ptr to fileObj == struct
    //char atm_dir[256] = "/home/mare/Nolin/SeaIce/ILATM2.002";
    //char misr_dir[256] = "/home/mare/Nolin/2013/MaskedSurf/April_sdcmClearHC";
    //char atmfile[256] = "/home/mare/Nolin/SeaIce/ILATM2.002/combined_atm.csv";
    //char atmmodel[256] = "/home/mare/Nolin/SeaIce/ILATM2.002/SeaIce_Apr2013_atmmodel.csv";

    // inputes
    char atm_dir[256] = "/home/mare/Projects/MISR/Julienne/IceBridge2016/EhsanTest"; // ATM files == ILATM2 csv files
    char misr_dir[256] = "/home/mare/Nolin/data_2000_2016/2016/Surface3_LandMasked/Jul"; // surf dat files
    char cm_dir[256] = "/home3/mare/Nolin/2016/MaskedSurf/Jul_sdcmClearHC_LandMasked"; // cloud mask data == lsdcm dat files
    //char atmfile[256] = "/home/mare/Projects/MISR/Julienne/IceBridge2016/combined_atm.csv";

    // output
    char atmmodel[256] = "/home/mare/Ehsan_lab/MISR-roughness/atm_to_csv/SeaIce_Jul2016_atmmodel_cloud_var.csv";
    // char atmmodel[256] = "/home/mare/Projects/MISR/Julienne/IceBridge2016/SeaIce_Jul2016_atmmodel_cloud_var.csv"; // old
    //char lsmask_dir[256] = "/home/mare/Nolin/SeaIce/LWData/MISR_LandSeaMask";
    char message[256];
    char idir[256];
    char an_file[128];
    char fname[256];
    char ca_fname[256];
    char cf_fname[256];
    char an_fname[256];
    char cm_fname[256];
    //char lsmask_fname[256];
    //unsigned char lsmask;
    char xfile[256];
    char **atm_fileList = 0;
    char syear[4];
    char sday[2];
    char smonth[2];
    char ATMStartTime[32];
    char ATMEndTime[32];
    char str[16];
    char *words;
    char *sline = NULL;
    int *orbitlist;
    int orbitcnt;
    int month;
    int day;
    int path;
    int atm_nfiles = 0;
    int misr_nfiles = 0;
    int ATM_npRow = 0;
    int i, j, k, n, w;
    int block;
    int atm_found;
    int natm_half_weight = 0;
    int natm_valid = 0;
    //int monthday[12][31] = {0};
    double avg_rms = 0;
    double avg_valid_rms = 0;
    double weight;
    double ca, cf, an, cm;
    double xlat, xlon, xrms, xcam;
    float fline, fsample;
    int line, sample;
    int nocloud_pts, cloud_pts, misscloud_pts;
    int cm_exist;
    int path_x, orbit_x, block_x;
    double weight_x;
    int nocloud_x, cloud_x, misscloud_x;
    size_t slen = 0;
    ssize_t read;
    int ATMnRow = 0;

    // Get list of available ATM csv files /////////////////////////////////////////////////////////////////////////////
    dirp = opendir(atm_dir);
    if (dirp) {
    	while ((entryObjPtr = readdir(dirp)) != NULL) { // num of iterations == num of ATM files available == atm_nfiles == entryObjPtr is ptr to fileObj, we create it for every iteration = ATM csv file available
		    if (strstr(entryObjPtr->d_name, "combine")) continue; // d_name is string of fileName in fileObj
		    if (strstr(entryObjPtr->d_name, "SeaIce")) continue;
		    if (!strstr(entryObjPtr->d_name, ".csv")) continue;
		    if (atm_fileList == 0) {
                atm_fileList = (char **) malloc(sizeof(char *));
                if (!atm_fileList) {
                    printf("main: couldn't malloc atm_fileList\n");
                    return 0;
                }
            }
            else {
                atm_fileList = (char **) realloc(atm_fileList, (atm_nfiles + 1) * sizeof(char *));
                if (!atm_fileList) {
                    printf("getFileList: couldn't realloc atm_fileList\n");
                    return 0;
                }
            }
            atm_fileList[atm_nfiles] = (char *) malloc(strlen(entryObjPtr->d_name) + 1);
            if (!atm_fileList[atm_nfiles]) {
                printf("main: couldn't malloc atm_fileList[%d]\n", atm_nfiles);
                return 0;
            }
            strcpy(atm_fileList[atm_nfiles], entryObjPtr->d_name); // fill the list with available ATM files
            atm_nfiles ++;
        }
    	closedir (dirp); // close the stream
    }
    else {
        strcat(message, "Can't open ");
        strcat(message, atm_dir);
        perror (message);
        return EXIT_FAILURE;
    }
    printf("num of ATM files read: %d \n" , atm_nfiles);
    printf("\n");
    // Get list of available ATM csv files /////////////////////////////////////////////////////////////////////////////


    //for (i = 0; i < atm_nfiles; i++) {
	//printf("%d %s\n", i, atm_fileList[i]);
    //}

    // /////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    for (i = 0; i < atm_nfiles; i++) { // i = num of available ATM files in the list
        printf("processing ATM file: %s \n", atm_fileList[i]);
        //memset(syear, '\0', sizeof(syear));
        strncpy(syear, (atm_fileList[i] + 7), 4); // get year from file name; why not in ptr format?
        syear[4] = '\0'; // problem, why syear is printed as empty?
        char* yearCopy = strdup(syear); // replaced every syear with yearCopy
        
        //memset(smonth, '\0', sizeof(smonth));
        strncpy(smonth, (atm_fileList[i] + 11), 2); // get month from file name; how?
        smonth[2] = '\0';
        month = atoi(smonth);

        //memset(sday, '\0', sizeof(sday));
        strncpy(sday, (atm_fileList[i] + 13), 2); // get dat from file name
        sday[2] = '\0';
        printf("yr: %s mon: %d day: %s \n", yearCopy, month, sday);

        for (k  = -1; k < 2; k++) { // k=days; yesterday (-1) or tmrw (+1) == 0.5 of the ATM overpass; today=o
            printf("k day is: %d \n", k);
            day = atoi(sday) + k;
            printf("day of ATM file: %d \n" , day);
            sprintf(ATMStartTime, "%s-%02d-%02dT00:00:00Z", yearCopy, month, day); // start time
            sprintf(ATMEndTime, "%s-%02d-%02dT23:59:59Z", yearCopy, month, day); // end time
            printf("ATM file & info: %s, %s, %s\n", atm_fileList[i], ATMStartTime, ATMEndTime);

            if (k == 0) weight = 1.0; // for today k=0; w=1 of the ATM overpass;
            else weight = 0.5; // yesterday or tmrw; weight=0.5 of the ATM overpass
            //if (monthday[month][day] == 0) {
            status = MtkTimeRangeToOrbitList(ATMStartTime, ATMEndTime, &orbitcnt, &orbitlist); // outputs are orbitCount and list
            //printf("status: %d \n" , status);
            if (status != MTK_SUCCESS) return 1;

            for (j = 0; j < orbitcnt; j++) { // what is orbitcnt? orbitCount; Q- orbit during each day?
                //printf("orbit-counter: %d in orbit: %d \n" , j, orbitlist[j]);
                status = MtkOrbitToPath(orbitlist[j], &path); // what is path, given the orbit? or which path the orbit belong to?
                if (status != MTK_SUCCESS) return 1;
                //printf("MISR orbit & path in this k: \n");
                //printf("orbit %d goes to path: %d \n", orbitlist[j], path); // MISR: checking orbit and path of MISR
                sprintf(fname, "%s/%s", atm_dir, atm_fileList[i]); // ATM: create full path of each ATM file(i)
                fp = fopen(fname, "r"); // create stream = fp for ATM file == open ATM file
                if (!fp) {
                    fprintf(stderr, "main: couldn't open %s \n", fname);
                    return 1;
                }
                printf("\nopening ATM file (%d) for path (%d) to read each sample/row info: %s \n", i, path, fname); // the ATM file
                // now associate each ATM row/sample to 3 MISR surf files
                while ((read = getline(&sline, &slen, fp)) != -1) { // get/read each line of ATM csv
                    //printf("Retrieved line of length \n"); //%zu :\n", read);
                    //printf("%s\n", sline);
                    //printf("ATMnRow: %d \n" , ATMnRow);
                    words = strtok (sline," ,"); // get the 1st token
                    w = 0;
                    //printf ("%s\n",words);
//                    if (!strcmp(words, "#")) { // if line starts with #, skip it
//                        printf("found # in csv file; skipping the line in csv \n");
//                        continue; //
//                    }
                    int ret = strcmp(words, "#");
                    //printf("\n returnNo is: %d \n" , ret);
                    if (strcmp(words, "#") == 0) { // Q- how about this one? --> skip lines with #
                        //printf("\n -ret is: %d \n" , ret);
                        //printf("found # in csv file; skipping the row in csv \n");
                        continue;
                    }
                    while (words != NULL) { // parse line w/o # until we get to the last word in a line
                        //printf ("words: %s\n",words);
                        if (w == 1) xlat = atof(words); // ATM lat
                        if (w == 2) xlon = atof(words); // ATM lon
                        if (w == 6) xrms = atof(words); // roughness = target/label (cm)
                        if (w == 10) xcam = atof(words); // Track_Identifier == 0 == nadir ATM camera view
                        words = strtok (NULL, " ,");
                        w++;
                    }
                    if (xcam != 0) { // if not ATM nadir; we only use nadier
                        //printf("xcam not nadier (%f)... skipping the ATM sample/row \n" , xcam);
                        continue;
                    }
                    status = MtkLatLonToBls(path, 275, xlat, xlon, &block, &fline, &fsample); // assign each ATM xlat/xlon/row to each MISR block; Q- why block and not pixel?
                    if (status != MTK_SUCCESS) {
                        if (block == -1) continue; // Q- why -1 ???
                        printf("ERROR for: %f %f %d %f %f", xlat, xlon, block, fline, fsample); // Q- why float for line-sample?
                        return 1;
                    }
                    line = rint(fline); // rounds int
                    sample = rint(fsample); // Q- why round this?
                    //printf("ATM lat/lon to MISR pixel: line: %d; sample: %d \n" , line, sample);
                    /* now find/define MISR surf files based on the extracted info from each ATM row; we should look into these files */
                    sprintf(cf_fname, "%s/Cf/surf_p%03d_o%06d_b%03d_cf.dat", misr_dir, path, orbitlist[j], block);
                    //if (access(cf_fname, F_OK) == -1) continue; // check if file is accessible
                    sprintf(ca_fname, "%s/Ca/surf_p%03d_o%06d_b%03d_ca.dat", misr_dir, path, orbitlist[j], block);
                    //if (access(ca_fname, F_OK) == -1) continue;
                    sprintf(an_fname, "%s/An/surf_p%03d_o%06d_b%03d_an.dat", misr_dir, path, orbitlist[j], block);
                    //if (access(an_fname, F_OK) == -1) continue;
                    sprintf(cm_fname, "%s/An/lsdcm_p%03d_o%06d_b%03d_an.dat", cm_dir, path, orbitlist[j], block); // lsdcm =?

                    cm_exist = 1; // to associate with line=358
//                    if (access(cm_fname, F_OK) == -1) {
//                        cm_exist = 0;
//                    }
                    //printf("SUCCESSFULLY FOUND: %d, %d, %f, %f, %f, %d, %d, %d \n", path, orbitlist[j], xlat, xlon, xrms, block, line, sample); // for each csv row == label info

                    // up to here................................
                    atm_found = 0; // off-false
                    printf("atm_found1: %d \n" , atm_found);
                    printf("atm_np1: %d \n" , ATM_npRow);

                    if (ATM_npRow == 0) atm_fileObj = (atm_type * ) malloc(sizeof(atm_type)); // 1st allocate mem-- for each row of csv file
                    else {
                        n = 0;
                        while ((n < ATM_npRow) && !atm_found) { // Q- what is this stopping?
                            printf("check pointInGrid n: %d, atm_rowNum2: %d \n" , n, ATM_npRow);
                            /* we start to fill the fileObj with n */
                            if ((atm_fileObj[n].path == path) && (atm_fileObj[n].block == block) && (atm_fileObj[n].line == line) &&
                                (atm_fileObj[n].sample == sample) && (atm_fileObj[n].weight == weight)) { // Q- what is this condition? why check to be the same? in same day in same pixel????
                                    printf("ATM point found in pixel at n=%d\n" , n);
                                    atm_fileObj[n].rms += weight * xrms; // sum of weighted ATM roughness
                                    atm_fileObj[n].npts += weight; // sum of num of points
                                    atm_fileObj[n].var += weight * xrms * xrms; // sum of what???? variance?
                                    atm_found = 1; // Q- found in what? pixel??? // turns on here==1
                                    printf("\n");
                            }
                            n++;
                        }
                        //printf("notFound1= %d \n" , cond);
                        if (!atm_found) atm_fileObj = (atm_type * ) realloc(atm_fileObj, (ATM_npRow + 1) * sizeof(atm_type));
                    }
                    /*check if mem- is allocated*/
                    if (!atm_fileObj) { // Q- how not is compared here?
                        fprintf(stderr,  "main: couldn't malloc/realloc atm_fileObj\n");
                        return 0;
                    }
                    printf("atm_found2= %d \n" , atm_found);
                    if (!atm_found) { // if not turned on = true = 1 == still 0
                        printf("pick new ATMpoint\n");
                        atm_fileObj[ATM_npRow].path = path;
                        atm_fileObj[ATM_npRow].orbit = orbitlist[j];
                        atm_fileObj[ATM_npRow].block = block;
                        atm_fileObj[ATM_npRow].line = line;
                        atm_fileObj[ATM_npRow].sample = sample;
                        atm_fileObj[ATM_npRow].lat = xlat;
                        atm_fileObj[ATM_npRow].lon = xlon;
                        atm_fileObj[ATM_npRow].weight = weight;
                        atm_fileObj[ATM_npRow].cloud = -1; // Q- why -1?

                        read_misr_data(cf_fname, line, sample, &cf); // returns 1 pixel value
                        read_misr_data(ca_fname, line, sample, &ca);
                        read_misr_data(an_fname, line, sample, &an);

                        if (cm_exist == 1) {
                            read_misr_data(cm_fname, line, sample, &cm); // cloud mask
                            if (cm > 0) atm_fileObj[ATM_npRow].cloud = 0;
                            else {
                                if (cm == CMASKED) atm_fileObj[ATM_npRow].cloud = 1; // Q-???
                            }
                        }
                        atm_fileObj[ATM_npRow].an = an;
                        atm_fileObj[ATM_npRow].ca = ca;
                        atm_fileObj[ATM_npRow].cf = cf;
                        atm_fileObj[ATM_npRow].npts = weight;
                        atm_fileObj[ATM_npRow].rms = weight * xrms;
                        atm_fileObj[ATM_npRow].var = weight * xrms * xrms;
                        ATM_npRow++;
                        printf("\n");
                        //printf("%d %d %d %d %d %f %f %f\n", ATM_npRow, path, block, line, sample, an, cf, ca);
                    }
                ATMnRow++; // E- counts how many rows are read
                } // get/read each line of ATM csv
                printf("numRows read from csv: %d \n" , ATMnRow);
                fclose(fp); // fp=ATM file closed
            } // for each orbit num
                //monthday[month][day] = 1;
            //}
        }
    }
    // /////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    double max_npts = -1e23;
    double max_rms = -1e23;
    double min_rms = 1e23;
    //fp = fopen(atmfile, "w");
    fm = fopen(atmmodel, "w"); // create and open a csv file to write into it; return the ptr
    printf("\nfinal ATM_npRow after checking all ATM files, k days, orbits= %d \n", ATM_npRow);
    cloud_pts = 0;
    nocloud_pts = 0;
    misscloud_pts = 0;
    cloud_x = 0;
    nocloud_x = 0;
    misscloud_x = 0;
    orbit_x = 0;

    for (n = 0; n < ATM_npRow; n++) { // Q- why here? why num of points here? what is this num?
        atm_fileObj[n].rms /= atm_fileObj[n].npts; // average roughness
        atm_fileObj[n].var = sqrt(atm_fileObj[n].var / atm_fileObj[n].npts - atm_fileObj[n].rms * atm_fileObj[n].rms);

        if (atm_fileObj[n].an > 0) { // surf refl > 0
            natm_valid++;
            avg_valid_rms += atm_fileObj[n].rms; // sum all
            if (atm_fileObj[n].rms > max_rms) max_rms = atm_fileObj[n].rms;
            if (atm_fileObj[n].rms < min_rms) min_rms = atm_fileObj[n].rms;
            if (atm_fileObj[n].weight == 0.5) natm_half_weight++;
        }
        avg_rms += atm_fileObj[n].rms; // sum with initial value

        if (atm_fileObj[n].npts > max_npts) max_npts = atm_fileObj[n].npts;

        //fprintf(fp, "%d, %d, %d, %d, %d, %lf, %lf, %lf, %lf, %lf, %lf, %lf, %lf\n", atm_fileObj[n].path, atm_fileObj[n].orbit, atm_fileObj[n].block, atm_fileObj[n].line, atm_fileObj[n].sample, atm_fileObj[n].lat, atm_fileObj[n].lon, atm_fileObj[n].an, atm_fileObj[n].ca, atm_fileObj[n].cf, atm_fileObj[n].rms, atm_fileObj[n].weight, atm_fileObj[n].npts);
        if ((atm_fileObj[n].cloud == 0) || (atm_fileObj[n].cloud == 1) ||
            (atm_fileObj[n].cloud == -1) && (atm_fileObj[n].an > 0) && (atm_fileObj[n].ca > 0) && (atm_fileObj[n].cf > 0)) {
            if (orbit_x==0) {
                printf("path, orbit, block, weight, cloud, nocloud, misscloud\n");
            }
            if (atm_fileObj[n].orbit != orbit_x) {
                printf("%d, %d, %d, %lf, %d, %d, %d\n", path_x, orbit_x, block_x, weight_x, cloud_x, nocloud_x, misscloud_x);
                path_x = atm_fileObj[n].path;
                orbit_x = atm_fileObj[n].orbit;
                block_x = atm_fileObj[n].block;
                weight_x = atm_fileObj[n].weight;
                nocloud_x = 0;
                cloud_x = 0;
                misscloud_x = 0;
            }
            if (atm_fileObj[n].cloud == 0) {
                nocloud_pts += 1;
                nocloud_x += 1;
            }
            if (atm_fileObj[n].cloud == 1) {
                cloud_pts += 1;
                cloud_x += 1;
            }
            if (atm_fileObj[n].cloud == -1) {
                misscloud_pts += 1;
                misscloud_x += 1;
            }

            fprintf(fm, "%d, %d, %d, %d, %d, %lf, %lf, %lf, %lf, %lf, %lf, %lf, %lf, %d, %lf\n", atm_fileObj[n].path, atm_fileObj[n].orbit, atm_fileObj[n].block, atm_fileObj[n].line, atm_fileObj[n].sample, atm_fileObj[n].lat,\
             atm_fileObj[n].lon, atm_fileObj[n].an, atm_fileObj[n].ca, atm_fileObj[n].cf, atm_fileObj[n].rms, atm_fileObj[n].weight, atm_fileObj[n].npts, atm_fileObj[n].cloud, atm_fileObj[n].var);
            path_x = atm_fileObj[n].path;
            orbit_x = atm_fileObj[n].orbit;
            block_x = atm_fileObj[n].block;
            weight_x = atm_fileObj[n].weight;
        }
    }
    //fclose(fp);
    fclose(fm);
    avg_rms /= ATM_npRow; // Q- why?
    avg_valid_rms /= natm_valid;

    printf("Number of Total ATM rms points = %d\n", ATM_npRow);
    printf("Number of Valid ATM rms points = %d\n", natm_valid);
    printf("Number of Valid ATM rms with weight of 1.0  = %d\n", natm_valid - natm_half_weight);
    printf("Number of Valid ATM rms with weight of 0.5  = %d\n", natm_half_weight);
    printf("Total Average rms = %lf %lf\n", avg_rms, max_npts);
    printf("Averge valid rms = %lf\n", avg_valid_rms);
    printf("Max valid rms = %lf\n", max_rms);
    printf("Min valid rms = %lf\n", min_rms);
    printf("Number of cloud points = %d\n", cloud_pts);
    printf("Number of nocloud points = %d\n", nocloud_pts);
    printf("Number of missing cloud mask pts = %d\n", misscloud_pts);

    return 0;
}
