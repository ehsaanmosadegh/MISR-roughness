/* Ehsan Jan 15, 2020
originally from dir: /home/mare/Nolin/SeaIce/Code/C
name: atm_to_misr_pixels.c
usage: associates ATM roughness values to surf refl MISR pixels
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

int read_data(char *fname, int line, int sample, double *data);
//int write_data(char *fname, double *data, int nlines, int nsamples);
char *strsub(char *s, char *a, char *b);

int read_data(char *fname, int line, int sample, double *data)
{
    FILE *f;
    int nlines = 512;
    int nsamples = 2048;
    double *array_data;

    f = fopen(fname, "r");
    if (!f) {
	fprintf(stderr,  "read_data: FileNotFound: %s\n", fname);
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

// ///////////////////////////////////////////////////////// main //////////////////////////////////////////////////////

int main(char argc, char *argv[]) {
    DIR *dirp;
    FILE *fp, *filePtr;
    struct dirent *entryObjPtr; // ptr to fileObj == struct
    //char atm_dir[256] = "/home/mare/Nolin/SeaIce/ILATM2.002";
    //char masked_surf_dir[256] = "/home/mare/Nolin/2013/MaskedSurf/April_sdcmClearHC";
    //char atmfile[256] = "/home/mare/Nolin/SeaIce/ILATM2.002/combined_atm.csv";
    //char atmmodel[256] = "/home/mare/Nolin/SeaIce/ILATM2.002/SeaIce_Apr2013_atmmodel.csv";

    // inputes
    char atm_dir[256] = "/home/mare/Projects/MISR/Julienne/IceBridge2016/july_atm_Ehsan/ehsan_test_for_atm20160714"; // start from ATM files == ILATM2 csv files
    // char masked_surf_dir[256] = "/home/mare/Nolin/data_2000_2016/2016/Surface3_LandMasked/Jul"; // surf dat files
    char masked_surf_dir[256] = "/home/mare/Ehsan_lab/misr_proceesing_dir/masked_surf_refl"; // from LandMask.c; produce surf_masked files for specific day
    char cloud_masked_dir[256] = "/home3/mare/Nolin/2016/MaskedSurf/Jul_sdcmClearHC_LandMasked"; // cloud mask data == lsdcm dat files
    //char atmfile[256] = "/home/mare/Projects/MISR/Julienne/IceBridge2016/combined_atm.csv";

    // output
    char atmmodel[256] = "/home/mare/Ehsan_lab/MISR-roughness/atm_to_misr_pixels/Ehsan_14_July2016_atmmodel_cloud_var.csv"; // writes output=atmmodel to current dir
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
    int atm_nfiles_found = 0;
    int misr_nfiles = 0;
    int ATM_fileObj_element = 0;
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
    int ATMnewLine = 0;

    /*////////////////////////////////////////////////////////////////////////////////////////////////////////////////*/
    /* Get list of all available ATM.csv files available in directory */
    printf("making list of ATM.csv files...\n");
    dirp = opendir(atm_dir);
    if (dirp) {
    	while ((entryObjPtr = readdir(dirp)) != NULL) { // num of iterations == num of ATM files available == atm_nfiles_found == entryObjPtr is ptr to fileObj, we create it for every iteration = ATM csv file available
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
                atm_fileList = (char **) realloc(atm_fileList, (atm_nfiles_found + 1) * sizeof(char *));
                if (!atm_fileList) {
                    printf("getFileList: couldn't realloc atm_fileList\n");
                    return 0;
                }
            }
            atm_fileList[atm_nfiles_found] = (char *) malloc(strlen(entryObjPtr->d_name) + 1);
            if (!atm_fileList[atm_nfiles_found]) {
                printf("main: couldn't malloc atm_fileList[%d]\n", atm_nfiles_found);
                return 0;
            }
            strcpy(atm_fileList[atm_nfiles_found], entryObjPtr->d_name); // fill the list with available ATM files
            atm_nfiles_found ++;
        }
    	closedir (dirp); // close the stream
    }
    else {
        strcat(message, "Can't open ATM.csv file\n");
        strcat(message, atm_dir);
        perror (message);
        return EXIT_FAILURE;
    }
    printf("----------------------------------------------------------------------------------------------\n");
    printf("num of ATM.csv files found %d \nin the direcotry: %s \n" , atm_nfiles_found, atm_dir);
    printf("\n");
    // Get list of available ATM csv files /////////////////////////////////////////////////////////////////////////////


    //for (i = 0; i < atm_nfiles_found; i++) {
	//printf("%d %s\n", i, atm_fileList[i]);
    //}

    /*////////////////////////////////////////////////////////////////////////////////////////////////////////////////*/
    /* read all available ATM file in the list we made in the past section */
    for (i = 0; i < atm_nfiles_found; i++) { // i = num of available ATM files in the list
        printf("----------- start a new ATM nfile -------------------\n");
        printf("\nprocessing ATM file: %s \n", atm_fileList[i]);
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
        printf("yr: %s; mon: %d; day: %s \n", yearCopy, month, sday);

        for (k  = -1; k < 2; k++) { // k=days; yesterday (-1) or tmrw (+1) == 0.5 of the ATM overpass; today=o
            printf("\nprocess for k-day: %d \n", k);
            day = atoi(sday) + k;
            printf("day: %d \n" , day);
            sprintf(ATMStartTime, "%s-%02d-%02dT00:00:00Z", yearCopy, month, day); // start time
            sprintf(ATMEndTime, "%s-%02d-%02dT23:59:59Z", yearCopy, month, day); // end time
            printf("ATM time: %s, %s, %s\n", atm_fileList[i], ATMStartTime, ATMEndTime);

            if (k == 0) weight = 1.0; // for today k=0; w=1 of the ATM overpass;
            else weight = 0.5; // yesterday or tmrw; weight=0.5 of the ATM overpass
            //if (monthday[month][day] == 0) {
            status = MtkTimeRangeToOrbitList(ATMStartTime, ATMEndTime, &orbitcnt, &orbitlist); // outputs are orbitCount and list
            //printf("status: %d \n" , status);
            if (status != MTK_SUCCESS) return 1;

            /*check orbit list*/
            int e;
            printf("found these MISR orbits for k_day: %d (%d) \n", day, k);
            for (e=0; e<orbitcnt; e++) {
                printf("orbit: %d\n" , orbitlist[e]);
            }

            for (j = 0; j < orbitcnt; j++) { // what is orbitcnt? orbitCount; Q- orbit during each day?
                status = MtkOrbitToPath(orbitlist[j], &path); // what is path, given the orbit? or which path the orbit belong to?
                printf("process each orbit: MtkOrbitToPath says: orbit %d is for path %d, day= %d\n" , orbitlist[j], path, day);

                if (status != MTK_SUCCESS) return 1;
                //printf("MISR orbit & path in this k: \n");
                //printf("orbit %d goes to path: %d \n", orbitlist[j], path); // MISR: checking orbit and path of MISR
                sprintf(fname, "%s/%s", atm_dir, atm_fileList[i]); // ATM: create full path of each ATM file(i)
                fp = fopen(fname, "r"); // create stream = fp for ATM file == open ATM file
                if (!fp) {
                    fprintf(stderr, "main: couldn't open %s \n", fname);
                    return 1;
                }

                //printf("\n______open ATM fileNum(%d), orbit/path(%d), in day_k(%d), WhileLoop each sample/row info from: %s \n\n", i, path, k, fname); // the ATM file
                // now associate each ATM row/sample to 3 MISR surf files
                while ((read = getline(&sline, &slen, fp)) != -1) { // read each line of each ATM csv
                    // printf("--- processing ATM line (%d) in file (%d) \n", ATMnewLine, i);  // E- counts how many rows are read
//                     printf("------------------------------------------\n");
                    //printf("Retrieved line of length \n"); //%zu :\n", read);
                    //printf("ATM line: %s\n", sline);
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
                    if (xcam != 0) { // if not ATM nadir; because we only use nadier camera from ATM
                        //printf("xcam not nadier (%f)... skipping the ATM sample/row \n" , xcam);
                        continue;
                    }
                    status = MtkLatLonToBls(path, 275, xlat, xlon, &block, &fline, &fsample); // find each MISR pixel based on each ATM xlat/xlon/row;
                    if (status != MTK_SUCCESS) {
                        if (block == -1) { //Q- why/when it gets -1?
                            //printf("lat/lon to block = %d, continue! \n", block);
                            continue;
                        } // Q- why -1 ???
//                        printf("ERROR for: %f %f %d %f %f", xlat, xlon, block, fline, fsample); // Q- why float for line-sample?
//                        return 1;
                    }
                    line = rint(fline); // rounds int
                    sample = rint(fsample); // Q- why round this?
                    //printf("ATM lat/lon to MISR pixel: line: %d; sample: %d \n" , line, sample);
                    /* now find/define MISR surf files based on the extracted info from each ATM row; we should look into these files */
                    sprintf(cf_fname, "%s/Cf/masked_surf_refl_P%03d_O%06d_B%03d_cf.dat", masked_surf_dir, path, orbitlist[j], block);
                    //if (access(cf_fname, F_OK) == -1) continue; // check if file is accessible
                    sprintf(ca_fname, "%s/Ca/masked_surf_refl_P%03d_O%06d_B%03d_ca.dat", masked_surf_dir, path, orbitlist[j], block);
                    //if (access(ca_fname, F_OK) == -1) continue;
                    sprintf(an_fname, "%s/An/masked_surf_refl_P%03d_O%06d_B%03d_an.dat", masked_surf_dir, path, orbitlist[j], block);
                    //if (access(an_fname, F_OK) == -1) continue;
                    sprintf(cm_fname, "%s/An/lsdcm_p%03d_o%06d_b%03d_an.dat", cloud_masked_dir, path, orbitlist[j], block); // lsdcm =?

                    cm_exist = 1; // to associate with line=358
//                    if (access(cm_fname, F_OK) == -1) {
//                        cm_exist = 0;
//                    }
                    //printf("SUCCESS: MISR-ATM info: %d, %d, %d, %d, %d, %f, %f, %f\n", path, orbitlist[j], block, line, sample, xlat, xlon, xrms); // for each csv row == label info

                    /*////////////////////////////////////////////////////////////////////////////////////////////////*/
                    /* now try to find pixels that each ATM roughness falls into it and then sum all roughness values */

                    atm_found = 0; // a switch to check every new point, reset to zero for every new entry=ATM line
                    //printf("atm_found1: %d \n" , atm_found);

                    if (ATM_fileObj_element == 0) atm_fileObj = (atm_type *) malloc(sizeof(atm_type)); // 1st allocate mem-- for each row of csv file
                    else { /* for 2nd ATM_fileObj_element and the rest */
                        n = 0;
                        while ((n < ATM_fileObj_element) && !atm_found) { // checks all points inside fileObj until pixel is found
                            /* we compare new path/block/... (associated with ATM point/row) with every n path available in fileObj;
                             * if similar pixel was found, ATM point is in MISR pixel and we sum rms/npts to previous pixel values in fileObj,
                             * esle: */
                            if ((atm_fileObj[n].path == path) && (atm_fileObj[n].block == block) && (atm_fileObj[n].line == line) &&
                                (atm_fileObj[n].sample == sample) && (atm_fileObj[n].weight == weight)) {   // Q- what is this condition? why check to be the same? in same day in same pixel????
                                    //printf(">>> FOUND: ATM point in MISR pixel: summing with past ones...\n");
                                    //printf(">>> FOUND: ATM in MISR pixel >>> day: (%d), path: (%d), block: (%d), line: (%d), sample: (%d)\n\n", k, path, block, line, sample);
                                    atm_fileObj[n].rms += weight * xrms; // sum of weighted ATM roughness in the same pixel?
                                    atm_fileObj[n].npts += weight; // sum of num of points in the same pixel?
                                    atm_fileObj[n].var += weight * xrms * xrms; // sum of what???? variance?
                                    atm_found = 1; // ATM point is found in pixel; turns on here==1
                            }
                            n++; // iterate to next point in file Obj
                        }
                        /* if ATM point not found in previous MISR pixels so far, we allocate mem- for new the new point in atm_fileObj */
                        if (!atm_found) atm_fileObj = (atm_type * ) realloc(atm_fileObj, (ATM_fileObj_element + 1) * sizeof(atm_type));
                    }
                    /* check if mem- is allocated */
                    if (!atm_fileObj) {
                        fprintf(stderr,  "main: couldn't malloc/realloc atm_fileObj\n");
                        return 0;
                    }
                    /* since the new ATM point was not found in previous MISR pixels, we add it as new dataPoint in a new pixel */
                    if (!atm_found) { /* if we could not find any MISR pixel associated to ATM data location,
 *                                      we add that point as new pixel along ATM flight path */
                        atm_fileObj[ATM_fileObj_element].path = path;
                        atm_fileObj[ATM_fileObj_element].orbit = orbitlist[j];
                        atm_fileObj[ATM_fileObj_element].block = block;
                        atm_fileObj[ATM_fileObj_element].line = line;
                        atm_fileObj[ATM_fileObj_element].sample = sample;
                        atm_fileObj[ATM_fileObj_element].lat = xlat;
                        atm_fileObj[ATM_fileObj_element].lon = xlon;
                        atm_fileObj[ATM_fileObj_element].weight = weight;
                        atm_fileObj[ATM_fileObj_element].cloud = -1; // Q- why -1?

                        //printf("\ncf1: %f \n" , cf);
                        read_data(cf_fname, line, sample, &cf); // returns 1 pixel value
                        read_data(ca_fname, line, sample, &ca);
                        read_data(an_fname, line, sample, &an);
                       // printf("cf2 should be single value: %f \n" , cf);
//                        printf("ca: %f \n" , ca);
//                        printf("an: %f \n" , an);
                        //printf("\n");


                        if (cm_exist == 1) {
                            read_data(cm_fname, line, sample, &cm); // cloud mask
                            if (cm > 0) atm_fileObj[ATM_fileObj_element].cloud = 0;
                            else {
                                if (cm == CMASKED) atm_fileObj[ATM_fileObj_element].cloud = 1; // Q-???
                            }
                        }
                        atm_fileObj[ATM_fileObj_element].an = an;
                        atm_fileObj[ATM_fileObj_element].ca = ca;
                        atm_fileObj[ATM_fileObj_element].cf = cf;
                        atm_fileObj[ATM_fileObj_element].npts = weight;
                        atm_fileObj[ATM_fileObj_element].rms = weight * xrms;
                        atm_fileObj[ATM_fileObj_element].var = weight * xrms * xrms;

                        ATM_fileObj_element++; // increment for every fileObj element
                        //printf("ATM_fileObj_element updates.........................\n");
                        //printf("%d %d %d %d %d %f %f %f\n", ATM_fileObj_element, path, block, line, sample, an, cf, ca);
                    }
                    ATMnewLine++;
                } // get/read each line of ATM csv
                //printf("*** close csv and go to next orbit\n");
                fclose(fp); // fp=ATM file closed
            }   // for each orbit num
                //monthday[month][day] = 1;
        }
    }
    // /////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    double max_npts = -1e23;
    double max_rms = -1e23;
    double min_rms = 1e23;
    //fp = fopen(atmfile, "w");
    filePtr = fopen(atmmodel, "w"); // create and open a csv file to write into it; return the ptr
    printf("writing data into output...");
    printf("\nnum of elements in ATM_fileObj_element= %d after checking all ATM files, k days, orbits\n", ATM_fileObj_element);
    cloud_pts = 0;
    nocloud_pts = 0;
    misscloud_pts = 0;
    cloud_x = 0;
    nocloud_x = 0;
    misscloud_x = 0;
    orbit_x = 0;

    fprintf(filePtr, "path, orbit, block, line, sample, lat, lon, an, ca, cf, rms, weight, npts, cloud, var\n");

    for (n = 0; n < ATM_fileObj_element; n++) {  // num of points= the MISR pixels that ATM found for them == size of elements in atm_fileObj
        atm_fileObj[n].rms /= atm_fileObj[n].npts; // average weighted roughness // Q- atm_fileObj is for each what? pixel? or
        atm_fileObj[n].var = sqrt(atm_fileObj[n].var / atm_fileObj[n].npts - atm_fileObj[n].rms * atm_fileObj[n].rms);

        if (atm_fileObj[n].an > 0) {    // Q- why an camera is checked? can camera be negative? surf refl > 0
            natm_valid++; // increment
            avg_valid_rms += atm_fileObj[n].rms; // sum roughness of every valid pixel/element; Q- wby we vheck valid refl value?
            if (atm_fileObj[n].rms > max_rms) max_rms = atm_fileObj[n].rms; // Q- can roughness be negative? and minus? // set the max roughness value
            if (atm_fileObj[n].rms < min_rms) min_rms = atm_fileObj[n].rms; // set min roughness value
            if (atm_fileObj[n].weight == 0.5) natm_half_weight++;
        }

        avg_rms += atm_fileObj[n].rms; // sum with initial value

        if (atm_fileObj[n].npts > max_npts) max_npts = atm_fileObj[n].npts; // collect num of points

        //fprintf(fp, "%d, %d, %d, %d, %d, %lf, %lf, %lf, %lf, %lf, %lf, %lf, %lf\n", atm_fileObj[n].path, atm_fileObj[n].orbit, atm_fileObj[n].block, atm_fileObj[n].line, atm_fileObj[n].sample, atm_fileObj[n].lat, atm_fileObj[n].lon, atm_fileObj[n].an, atm_fileObj[n].ca, atm_fileObj[n].cf, atm_fileObj[n].rms, atm_fileObj[n].weight, atm_fileObj[n].npts);
        /* why check this condition? */
        if ((atm_fileObj[n].cloud == 0) || (atm_fileObj[n].cloud == 1) || // E- check this condition
            ((atm_fileObj[n].cloud == -1) && (atm_fileObj[n].an > 0) && (atm_fileObj[n].ca > 0) && (atm_fileObj[n].cf > 0))) {
            if (orbit_x==0) { // Q-why zero?
                printf("path, orbit, block, weight, cloud, nocloud, misscloud, orbit_x= %d\n", orbit_x);
            }
            int atm_orbit = atm_fileObj[n].orbit;
            //printf("atm_orbit: %d \n" , atm_orbit);
            if (atm_orbit != orbit_x) { // if atm_orbit not zero
                //printf("path_x: %d \n" , path_x);
                printf("\n%d, %d, %d, %lf, %d, %d, %d\n", path_x, orbit_x, block_x, weight_x, cloud_x, nocloud_x, misscloud_x); // Q- whats x?
                //printf("path_x: %d \n" , path_x);
                path_x = atm_fileObj[n].path;
                orbit_x = atm_fileObj[n].orbit;
                block_x = atm_fileObj[n].block;
                weight_x = atm_fileObj[n].weight;
                cloud_x = 0;
                nocloud_x = 0;
                misscloud_x = 0;
            }
            if (atm_fileObj[n].cloud == 0) { // no-cloud
                nocloud_pts += 1;
                nocloud_x += 1;
            }
            if (atm_fileObj[n].cloud == 1) { // cloudy
                cloud_pts += 1;
                cloud_x += 1;
            }
            if (atm_fileObj[n].cloud == -1) { // miss-cloud
                misscloud_pts += 1;
                misscloud_x += 1;
            }

            fprintf(filePtr, "%d, %d, %d, %d, %d, %lf, %lf, %lf, %lf, %lf, %lf, %lf, %lf, %d, %lf\n", atm_fileObj[n].path, atm_fileObj[n].orbit, atm_fileObj[n].block, atm_fileObj[n].line, atm_fileObj[n].sample, atm_fileObj[n].lat, atm_fileObj[n].lon, atm_fileObj[n].an, atm_fileObj[n].ca, atm_fileObj[n].cf, atm_fileObj[n].rms, atm_fileObj[n].weight, atm_fileObj[n].npts, atm_fileObj[n].cloud, atm_fileObj[n].var); // 14

            path_x = atm_fileObj[n].path;
            orbit_x = atm_fileObj[n].orbit;
            block_x = atm_fileObj[n].block;
            weight_x = atm_fileObj[n].weight;
        }
    }

    //fclose(fp);
    fclose(filePtr);
    avg_rms /= ATM_fileObj_element; // Q- why?
    avg_valid_rms /= natm_valid;
    printf("**************************************\n");
    printf("Number of Total ATM rms points = %d\n", ATM_fileObj_element);
    printf("Number of Valid ATM rms points = %d\n", natm_valid);
    printf("Number of Valid ATM rms with weight of 1.0  = %d\n", natm_valid - natm_half_weight);
    printf("Number of Valid ATM rms with weight of 0.5  = %d\n", natm_half_weight);
    printf("Total Average rms = %lf %lf\n", avg_rms, max_npts);
    printf("Average valid rms = %lf\n", avg_valid_rms);
    printf("Max valid rms = %lf\n", max_rms);
    printf("Min valid rms = %lf\n", min_rms);
    printf("Number of cloud points = %d\n", cloud_pts);
    printf("Number of nocloud points = %d\n", nocloud_pts);
    printf("Number of missing cloud mask pts = %d\n", misscloud_pts);
    printf("\n***** FINISHED SUCCESSFULLY!***** \n\n");
    return 0;
}
