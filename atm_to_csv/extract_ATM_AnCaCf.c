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
	
    if (fread(array_data, sizeof(double), nlines * nsamples, f) != nlines * nsamples) {
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
    struct dirent *entryObj; // ptr to fileObj == struct
    //char atm_dir[256] = "/home/mare/Nolin/SeaIce/ILATM2.002";
    //char misr_dir[256] = "/home/mare/Nolin/2013/MaskedSurf/April_sdcmClearHC";
    //char atmfile[256] = "/home/mare/Nolin/SeaIce/ILATM2.002/combined_atm.csv";
    //char atmmodel[256] = "/home/mare/Nolin/SeaIce/ILATM2.002/SeaIce_Apr2013_atmmodel.csv";
    // inputes
    char atm_dir[256] = "/home/mare/Projects/MISR/Julienne/IceBridge2016"; // ATM files == ILATM2 csv files
    char misr_dir[256] = "/home/mare/Nolin/data_2000_2016/2016/Surface3_LandMasked/Jul"; // surf dat files
    char cm_dir[256] = "/home3/mare/Nolin/2016/MaskedSurf/Jul_sdcmClearHC_LandMasked"; // cloud mask data == lsdcm dat files
    //char atmfile[256] = "/home/mare/Projects/MISR/Julienne/IceBridge2016/combined_atm.csv";
    // output
    char atmmodel[256] = "/home/mare/Ehsan_lab/MISR-roughness/atm/SeaIce_Jul2016_atmmodel_cloud_var.csv";
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
    char **atm_flist = 0;
    char syear[4];
    char sday[2];
    char smonth[2];
    char stime[32];
    char etime[32];
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
    int atm_np = 0;
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

    // Get list of ATM text files
    dirp = opendir(atm_dir);
    if (dirp) {
    	while ((entryObj = readdir(dirp)) != NULL) { // num of iterations == num of atm files available == atm_nfiles == entryObj is ptr to fileObj, we create it for every iteration
		    if (strstr(entryObj->d_name, "combine")) continue; // d_name is string of fileName in fileObj
		    if (strstr(entryObj->d_name, "SeaIce")) continue;
		    if (!strstr(entryObj->d_name, ".csv")) continue;
		    if (atm_flist == 0) {
                atm_flist = (char **) malloc(sizeof(char *));
                if (!atm_flist) {
                    printf("main: couldn't malloc atm_flist\n");
                    return 0;
                }
            }
            else {
                atm_flist = (char **) realloc(atm_flist, (atm_nfiles + 1) * sizeof(char *));
                if (!atm_flist) {
                    printf("getFileList: couldn't realloc atm_flist\n");
                    return 0;
                }
            }
            atm_flist[atm_nfiles] = (char *) malloc(strlen(entryObj->d_name) + 1);
            if (!atm_flist[atm_nfiles]) {
                printf("main: couldn't malloc atm_flist[%d]\n", atm_nfiles);
                return 0;
            }
            strcpy(atm_flist[atm_nfiles], entryObj->d_name);
            atm_nfiles ++;
    	}
    	closedir (dirp);
    } 
    else {
        strcat(message, "Can't open ");
        strcat(message, atm_dir);
        perror (message);
        return EXIT_FAILURE;
    }

    //for (i = 0; i < atm_nfiles; i++) {
	//printf("%d %s\n", i, atm_flist[i]);
    //}

    for (i = 0; i < atm_nfiles; i++) { // i is num of available atm files in the list
        printf("processing atm file: %s \n", atm_flist[i]);
        //memset(syear, '\0', sizeof(syear));
        strncpy(syear, (atm_flist[i] + 7), 4); // get year from file name; why not in ptr format?
        syear[4] = '\0'; // problem, why syear is printed as empty?
        char* yearCopy = strdup(syear); // replaced every syear with yearCopy
        
        //memset(smonth, '\0', sizeof(smonth));
        strncpy(smonth, (atm_flist[i] + 11), 2); // get month from file name; how?
        smonth[2] = '\0';
        month = atoi(smonth);

        //memset(sday, '\0', sizeof(sday));
        strncpy(sday, (atm_flist[i] + 13), 2); // get dat from file name
        sday[2] = '\0';
        printf("yr: %s mon: %d day: %s \n", yearCopy, month, sday);

        for (k  = -1; k < 2; k++) { // k=yesterday (-1) or tmrw (+1) == 0.5 of the ATM overpass; today=o
            //printf("k is: %d \n", k);
            day = atoi(sday) + k;
            printf("day is: %d \n" , day);
            sprintf(stime, "%s-%02d-%02dT00:00:00Z", yearCopy, month, day); // start time
            sprintf(etime, "%s-%02d-%02dT23:59:59Z", yearCopy, month, day); // end time
            printf("process for: %s %s %s\n", atm_flist[i], stime, etime);
            if (k == 0) weight = 1.0; // for today k=0; w=1 of the ATM overpass;
            else weight = 0.5; // yesterday or tmrw; weight=0.5 of the ATM overpass
            //if (monthday[month][day] == 0) {
            status = MtkTimeRangeToOrbitList(stime, etime, &orbitcnt, &orbitlist); // outputs are orbitCount and list
            //printf("status: %d \n" , status);
            if (status != MTK_SUCCESS) return 1;
            for (j = 0; j < orbitcnt; j++) { // what is orbitcnt? orbitCount
                printf("orbit cnt: %d \n" , j);
                printf("orbit file: %d \n" , orbitlist[j]); // ????????????????????????????????

                status = MtkOrbitToPath(orbitlist[j], &path);
                if (status != MTK_SUCCESS) return 1;
                printf("now %d %d \n", orbitlist[j], path);
                sprintf(fname, "atm file fullPath:%s/%s", atm_dir, atm_flist[i]);
                fp = fopen(fname, "r"); // create stream=fp for stm files
                if (!fp) {
                    fprintf(stderr, "main: couldn't open %s\n", fname);
                    return 1;
                }
                //printf("%s\n", fname);
                while ((read = getline(&sline, &slen, fp)) != -1) { // get each line of atm csv
                    //printf("Retrieved line of length %zu :\n", read);
                    //printf("%s\n", sline);
                    words = strtok (sline," ,"); // gets the 1st token
                    w = 0;
                    //printf ("%s\n",words);
                    if (!strcmp(words, "#")) continue;
                    while (words != NULL) { // untile we get to the last word in line
                        //printf ("%s\n",words);
                        if (w == 1) xlat = atof(words);
                        if (w == 2) xlon = atof(words);
                        if (w == 6) xrms = atof(words);
                        if (w == 10) xcam = atof(words); // Track_Identifier?
                        words = strtok (NULL, " ,");
                        w++;
                    }
                if (xcam != 0) continue; // Track_Identifier?
                status = MtkLatLonToBls(path, 275, xlat, xlon, &block, &fline, &fsample);
                if (status != MTK_SUCCESS) {
                    if (block == -1) continue;
                    printf("%f %f %d %f %f", xlat, xlon, block, fline, fsample);
                    return 1;
                }
                line = rint(fline); // rounds int
                sample = rint(fsample);

                sprintf(cf_fname, "%s/Cf/surf_p%03d_o%06d_b%03d_cf.dat", misr_dir, path, orbitlist[j], block);
                if (access(cf_fname, F_OK) == -1) continue;
                sprintf(ca_fname, "%s/Ca/surf_p%03d_o%06d_b%03d_ca.dat", misr_dir, path, orbitlist[j], block);
                if (access(ca_fname, F_OK) == -1) continue;
                sprintf(an_fname, "%s/An/surf_p%03d_o%06d_b%03d_an.dat", misr_dir, path, orbitlist[j], block);
                if (access(an_fname, F_OK) == -1) continue;
                sprintf(cm_fname, "%s/An/lsdcm_p%03d_o%06d_b%03d_an.dat", cm_dir, path, orbitlist[j], block);
                cm_exist = 1;
                if (access(cm_fname, F_OK) == -1) {
                    cm_exist = 0;
                }
                printf("Success: %d %d %f %f %f %d %d %d\n", path, orbitlist[j], xlat, xlon, xrms, block, line, sample);
                atm_found = 0;
                if (atm_np == 0) atm_fileObj = (atm_type * ) malloc(sizeof(atm_type));
                else {
                    n = 0;
                    while ((n < atm_np) && !atm_found) { // ???
                        if ((atm_fileObj[n].path == path) && (atm_fileObj[n].block == block) && (atm_fileObj[n].line == line) &&
                            (atm_fileObj[n].sample == sample) && (atm_fileObj[n].weight == weight)) { // ???
                                atm_fileObj[n].rms += weight * xrms;
                                atm_fileObj[n].npts += weight;
                                atm_fileObj[n].var += weight * xrms * xrms;
                                atm_found = 1;
                        }
                        n++;
                    }
                    if (!atm_found) atm_fileObj = (atm_type * ) realloc(atm_fileObj, (atm_np + 1) * sizeof(atm_type));
                }
                if (!atm_fileObj) {
                    fprintf(stderr,  "main: couldn't malloc/realloc atm_fileObj\n");
                    return 0;
                }
                if (!atm_found) {
                    atm_fileObj[atm_np].path = path;
                    atm_fileObj[atm_np].orbit = orbitlist[j];
                    atm_fileObj[atm_np].block = block;
                    atm_fileObj[atm_np].line = line;
                    atm_fileObj[atm_np].sample = sample;
                    atm_fileObj[atm_np].lat = xlat;
                    atm_fileObj[atm_np].lon = xlon;
                    atm_fileObj[atm_np].weight = weight;
                    read_misr_data(cf_fname, line, sample, &cf);
                    read_misr_data(ca_fname, line, sample, &ca);
                    read_misr_data(an_fname, line, sample, &an);
                    atm_fileObj[atm_np].cloud = -1;
                    if (cm_exist == 1) {
                        read_misr_data(cm_fname, line, sample, &cm);
                        if (cm > 0) atm_fileObj[atm_np].cloud = 0;
                        else {
                            if (cm == CMASKED) atm_fileObj[atm_np].cloud = 1;
                        }
                    }
                    atm_fileObj[atm_np].an = an;
                    atm_fileObj[atm_np].ca = ca;
                    atm_fileObj[atm_np].cf = cf;
                    atm_fileObj[atm_np].npts = weight;
                    atm_fileObj[atm_np].rms = weight * xrms;
                    atm_fileObj[atm_np].var = weight * xrms * xrms;
                    atm_np++;
                    printf("%d %d %d %d %d %f %f %f\n", atm_np, path, block, line, sample, an, cf, ca);
                }
                }
                fclose(fp);
                    }
                //monthday[month][day] = 1;
            //}
        }
    }

    double max_npts = -1e23;
    double max_rms = -1e23;
    double min_rms = 1e23;
    //fp = fopen(atmfile, "w");
    fm = fopen(atmmodel, "w"); // create and open a csv file and return the ptr
    printf("atm_np = %d\n", atm_np);
    cloud_pts = 0;
    nocloud_pts = 0;
    misscloud_pts = 0;
    cloud_x = 0;
    nocloud_x = 0;
    misscloud_x = 0;
    orbit_x = 0;
    for (n = 0; n < atm_np; n++) {
        atm_fileObj[n].rms /= atm_fileObj[n].npts;
        atm_fileObj[n].var = sqrt(atm_fileObj[n].var / atm_fileObj[n].npts - atm_fileObj[n].rms * atm_fileObj[n].rms);
        if (atm_fileObj[n].an > 0) {
            natm_valid++;
            avg_valid_rms += atm_fileObj[n].rms;
            if (atm_fileObj[n].rms > max_rms) max_rms = atm_fileObj[n].rms;
            if (atm_fileObj[n].rms < min_rms) min_rms = atm_fileObj[n].rms;
            if (atm_fileObj[n].weight == 0.5) natm_half_weight++;
        }
        avg_rms += atm_fileObj[n].rms;

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
    avg_rms /= atm_np;
    avg_valid_rms /= natm_valid;

    printf("Number of Total ATM rms points = %d\n", atm_np);
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
