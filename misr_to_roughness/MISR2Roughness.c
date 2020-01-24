// Ehsan Mosadegh 10 Nov 2019-Jan 2020
// notes:
// to-do: 

// E- header files
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <ctype.h>
#include <MisrToolkit.h>
#include <MisrError.h>
#include <dirent.h>

// E- declarations
#define NO_DATA -999999.0
#define BACKGROUND -999998.0
#define FOREGROUND -999997.0
#define TDROPOUT -999996.0
#define MASKED -999995.0
#define LMASKED -999994.0
#define VERBOSE 0

// E- global variables
typedef struct // E- why not path??? --> 9 var/elements
{
    int block;
    int orbit;
    double an;
    double ca;
    double cf;
    double rms;
    float weight;
    float tweight; // E-???
    int ascend;
} atm_type;

MTKt_status status;
atm_type* atm_model; // declare an instance/member
int nfiles;

int nlines = 512;
int nsamples = 2048;

int read_misr_data(char *fname, int nline, int nsample, double **data);
int read_bytedata(char *fname, unsigned char **data, int nlines, int nsamples);
int write_data(char *fname, double *data, int nlines, int nsamples);
int pixel2grid(int path, int block, int line, int sample, double *lat, double*lon, int *r, int *c);
char *strsub(char *s, char *a, char *b);

//#####################################################################################################

int read_data(char *fname, int nline, int nsample, double **data)
{
    FILE *f;

    f = fopen(fname, "r"); // f = stream; ptr that is opened and shows where data is stored in memory;
    if (!f) {
        fprintf(stderr,  "read_data: couldn't open %s\n", fname);
        return 0;
    }
	
    *data = (double *) malloc(nlines * nsamples * sizeof(double));
    if (!*data) {
        fprintf(stderr,  "read_data: couldn't malloc data\n");
        return 0;
    }
	// read data from stream = f --> *data;  f is the pointer to a FILE object that specifies an input stream.
    if (fread(*data, sizeof(double), nlines * nsamples, f) != nlines * nsamples) { // check see if number of elements read= initial number of elements
        fprintf(stderr,  "read_data: couldn't read data in %s\n", fname);
        return 0;
    }

    fclose(f);
    return 1;
}

//#####################################################################################################

int read_bytedata(char *fname, unsigned char **data, int nlines, int nsamples)
{
    FILE *f;

    f = fopen(fname, "rb");
    if (!f)
	{
	    printf("read_bytedata: couldn't open %s\n", fname);
	    return 0;
	}
	
    *data = (unsigned char *) malloc(nlines * nsamples * sizeof(unsigned char));
    if (!*data)
	{
	    printf("read_bytedata: couldn't malloc data\n");
	    return 0;
	}
	
    if (fread(*data, sizeof(unsigned char), nlines * nsamples, f) != nlines * nsamples)
	{
	    printf("read_bytedata: couldn't read data %s\n", fname);
	    return 0;
	}

    //fprintf(stderr, "read_bytedata: %s\n", fname);
	
    fclose(f);
    return 1;
}

//#####################################################################################################

int write_data(char *fname, double *data, int nlines, int nsamples)
{
    FILE *f;

    f = fopen(fname, "wb");
    if (!f) {
	fprintf(stderr, "write_data: couldn't open %s\n", fname);
	return 0;
    }
	
    if (fwrite(data, sizeof(double), 3*nlines * nsamples, f) != 3*nlines * nsamples) {
	fprintf(stderr, "write_data: couldn't write data\n");
	return 0;
    }
	
    fclose(f);
    return 1;
}

//#####################################################################################################

int pixel2grid(int path, int block, int line, int sample, double* xlat, double* xlon, int* r, int* c)
{ // receives path-block-line-sample and updates/outputs xlat,xlon,r,c
int status;
char *errs[] = MTK_ERR_DESC;
double lat, lon;
/* parameters for grid stereographic : 				*/
/* MOD44W.A2000055.h14v01.005.2009212173527_MOD44W_250m_GRID.dat	*/ 
//printf("lat before: %d \n", lat);
status = MtkBlsToLatLon(path, 275, block, line * 1.0, sample * 1.0, &lat, &lon);
//printf("lat after: %d \n", lat);

if (status != MTK_SUCCESS) 
	{
	printf("pixel2grid: MtkBlsToLatLon failed!!!, status = %d (%s)\n", status, errs[status]);
	return 0;
	}
	
if (VERBOSE) printf("pixel2grid: lat = %.6f, lon = %.6f\n", lat, lon);

double psize = 10./12000.;
double lon0 = -130.0;
double lat0 = 90.0;

// out
*xlat = lat; // updates value at xlat == lat
*xlon = lon; // updates value at xlon == lon
*c = rint((lon - lon0)/psize);
*r = rint(-(lat - lat0)/psize);

return 1;
}
//#####################################################################################################

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

//############################################### main ######################################################

int main(char argc, char *argv[]) {
    DIR* dirp;
    FILE* fp;
    struct dirent* DirEntryObj; // directory entries
    
    // inputs
    char surf_masked_dir[256] = "/home/mare/Nolin/data_2000_2016/2016/Surface3_LandMasked/Jul/An/test_ehsan"; // output of LandMask.c - use masked_surf files instead
   // char atmmodel[256] = "/home/mare/Projects/MISR/Julienne/IceBridge2016/SeaIce_Jul2016_atmmodel2_r025.csv"; // ATM csv file; source from where/
    char atmmodel[256] = "/home/mare/Ehsan_lab/MISR-roughness/atm_to_csv/Ehsan_Jul2016_atmmodel_cloud_var.csv"; // ATM csv file; source from where/

    char relAzimuthFile[256] =  "/home/mare/Projects/MISR/Julienne/IceBridge2016/RelativeAzimuth_Jul2016_sorted.txt"; // we don't need this anymore; source from where?
    
    // outputs 
    char predicted_rough_dir[256] = "/home/mare/Ehsan_lab/misr_proceesing_dir/misr_roughness"; // MISR roughness; rms file;
    
    // other variables
    char command[256];
    char wc_out[256];
    char message[256];
    char an_file[128];
    char rms_fname[256];
    char ca_fname[256];
    char cf_fname[256];
    char an_fname[256];
    char sblock[10], spath[10], sorbit[10];
    char *words;
    char *sline = NULL;
    char **misr_fileList = 0;
    int misr_nfiles = 0;
    int atmmodel_np = 0;
    int i, j, k, n, w;
    int r, c, r2, c2;
    double ca, cf, an;
    double xcf, xca, xan, xrms, xweight, tweight;
    double xrad, xrad_min, xrms_nearest;
    double *an_data, *cf_data, *ca_data;
    double *rms_data;
    double radius;
    double radius_ascend = 0.050; //Jul2016 SeaIce Model
    double radius_descend = 0.010; //Jul2016 SeaIce Model
    //double radius_ascend = 0.010; //AprMay2016 SeaIce Model
    //double radius_descend = 0.020; //AprMay2016 SeaIce Model
    //double radius = 0.015; //2009 SeaIce Model
    //double radius = 0.025; //2010 SeaIce Model
    //double radius = 0.025; //2013 SeaIce Model
    double lat, lon;
    int path, block, orbit;
    int dsize = nlines * nsamples;
    size_t slen = 0;
    ssize_t read;

    int l = 0;
    int start_orbit, end_orbit;
    int relAz_nlines;
    int *raz_table;
    int block1, block2;
    int block12;
    int ascend;
    //unsigned char *mask;
    //int gridlines = 24000;
    //int gridsamples = 84000;

    //printf("Reading /home/mare/Nolin/SeaIce/ArcticTiles.dat ...\n");
    //if (!read_bytedata("/home/mare/Nolin/SeaIce/ArcticTiles.dat", &mask, gridlines, gridsamples)) return 1;

    /* //////////////////////////// process azimuth file //////////////////////////////////////////////////////////// */

    sprintf(command, "wc -l %s", relAzimuthFile); // stoes command
    fp = popen(command, "r"); // pipe-open; fp pointer to a stream
    if (fp == NULL) {
	   printf("ERROR: Failed to run command\n" );
	   exit(1);
    }

    //char return_fgets[200];     // Ehsan

    /* Read the output a line at a time - output it. */
    //return_fgets = fgets(wc_out, sizeof(wc_out)-1, fp);
    //printf("fgets got: %s" , return_fgets);
    while (fgets(wc_out, sizeof(wc_out)-1, fp) != NULL) { // reads line from fp, stores in wc_out
    	//printf("wc_out: %s \n", wc_out);
    	words = strtok(wc_out, " "); // searches wc_out for tockens delimited by ""; words=no of lines in file
    	//printf("wordsare: %s \n", words);
    	w = 0;
    	if (w == 0) relAz_nlines = atoi(words); // no of lines in relAzimuthFile file
    	//printf("AznLines= %d \n", relAz_nlines);
    }
    /* close */
    pclose(fp);

    /*  E- reads azimuth file  */
    fp = fopen(relAzimuthFile, "r"); // opens file, stores it somewhere and returns the mem-add
    if (!fp) {
    	fprintf(stderr, "main: couldn't open %s\n", relAzimuthFile);
    	return 1;
    }

    l = 0;
    //printf("file ptr is: %p \n" , fp);
    while ( (read = getline(&sline, &slen, fp)) != -1) { // read is the return characters+ "\n" at the end, if -1 == EOF
        //printf("no of characters read from each line: %d \n" , read); // read is the return characters+\n, if -1 == EOF
        //printf("sline is: %s \n" , sline);
    	words = strtok(sline, " "); // breaks/parse line to its words in each line in a loop
    	w = 0;
    	//printf("word1 is: %s \n" , words); //  the 1st word, cos not in loop
    	while ((l == 0) && (words != NULL)) { // NULL at the end of each sentence
    		if (w == 1) start_orbit = atoi(words);
        	words = strtok (NULL, " "); // gets tokens in a sentence in a loop
        	//printf("word: %s \n" , words); // gets words in a rel azimuth in a loop
    		w++;
    	}
    	while ((l == relAz_nlines - 1) && (words != NULL)) {
    	    if (w == 1) end_orbit = atoi(words);
        	words = strtok (NULL, " ");
    	    w++;
    	}
    	l++;
    }
    //printf("start_orbit= %d  end_orbit= %d\n", start_orbit, end_orbit);
    fseek(fp, 0, SEEK_SET);

    raz_table = (int *) malloc((end_orbit - start_orbit + 1) * sizeof(int));
    while ((read = getline(&sline, &slen, fp)) != -1) { // read= no of char read from each line; fp=stream
    	words = strtok(sline, " ");
    	w = 0; // what is w? is it counter?
    	//printf(" w2 is: %d \n" , w);
    	//printf("word2 is: %s \n" ,  words); // gets words in a rel. azimuth in a loop
    	while (words != NULL) { // the end of file EOF
    	    if (w == 1) orbit = atoi(words);
    	    if (w == 3) block12 = 100*atoi(words); // col4*100
    	    if (w == 4) block12 += atoi(words); // 100col5 + col4; gets updated here
        	words = strtok (NULL, " "); // updates words and w in next line
    	    w++;
    	}
    	raz_table[orbit - start_orbit] = block12;
        //printf("block12: %d \n", block12);
    }
    fclose(fp);
    /* //////////////////////////// process azimuth file //////////////////////////////////////////////////////////// */

    /* //////////////////////////// reads ATMmodel csv file ///////////////////////////////////////////////////////////// */ // ok
    /* reads all rows of atmmodel csv file and fills the fileObj= atm_model */
    fp = fopen(atmmodel, "r");
    if (!fp) {
    	fprintf(stderr, "main: couldn't open %s\n", atmmodel);
    	return 1;
    }
    //printf("%s", atmmodel);
    
    while ( (read = getline(&sline, &slen, fp)) != -1) { // reads each row of atmmodel.csv
        //printf("num of char read: %zu \n", read);
        //printf("row extracted: %s", sline);
        //printf("read row: %d \n" , atmmodel_np);
        w = 0;
        //printf("w is: %d \n" , w);
    	words = strtok (sline," ,"); // moves ptr to first token == path in this case
    	//printf("word is: %s \n\n" , words);
    	
      	while (words != NULL) { // NULL = end of line or EOF; Q- how about w=0==path?
        	//printf ("inside loop, w = %d and words = %s \n",w,words);
    	    if (w == 1) orbit = atof(words);
    	    if (w == 2) block = atof(words);
    	    if (w == 7) xan = atof(words); // misr cam
    	    if (w == 8) xca = atof(words); // misr cam
    	    if (w == 9) xcf = atof(words); // misr cam
    	    if (w == 10) xrms = atof(words);
    	    if (w == 13) xweight = atof(words); // w from k_day; is cloud in ATM code ???
    	    if (w == 14) tweight = atof(words); // Q- ??? - is var
    	    if (w == 15) ascend = atoi(words); // Q- ??? - there is no col=15 in the csv file
        	words = strtok (NULL, " ,"); // whats this?
        	//printf("word updates: %s \n" , words);
        	//printf("\n");
    	    w++;
      	}
      	//printf("atmmodel_np: %d \n", atmmodel_np);
        /* fill the fileObj with each row of ATM data extracted from past step */
    	if (atmmodel_np == 0) atm_model = (atm_type * ) malloc(sizeof(atm_type));
    	else atm_model = (atm_type * ) realloc(atm_model, (atmmodel_np + 1) * sizeof(atm_type));
    	// update elements/variables of a new member
    	atm_model[atmmodel_np].orbit = orbit;
    	atm_model[atmmodel_np].block = block;
    	atm_model[atmmodel_np].an = xan;
    	atm_model[atmmodel_np].ca = xca;
    	atm_model[atmmodel_np].cf = xcf;
    	atm_model[atmmodel_np].rms = xrms;
    	atm_model[atmmodel_np].weight = xweight;
    	atm_model[atmmodel_np].tweight = tweight;
    	atm_model[atmmodel_np].ascend = ascend;
    	atmmodel_np++;// counter - max will be the max num of rows in atmmodel.csv
    }
    //printf("atm_model now is: %d \n", atm_model->d_name);
    fclose(fp);
    /* //////////////////////////// reads ATM csv file ///////////////////////////////////////////////////////////// */

    /* //////////////////////////// Get list of Masked Surface files /////////////////////////////////////////////// */ //ok

    printf("make a list of Masked Surface An files ...\n"); // == misr_fileList
    dirp = opendir(surf_masked_dir); // define dir stream == dirp == ptr to that directory
    if (dirp) {     // if ptr available == TRUE
    	while ((DirEntryObj = readdir(dirp)) != NULL) {     // read the first item in dir and moves the ptr to next item/file in dir; DirEntryObj == struct==fileObj for each file in dir
            if (!strstr(DirEntryObj->d_name, ".dat")) continue; // d_name= fileName, if could not find the pattern ".dat" in this string
            if (misr_fileList == 0) {  // if it has not been created yet
                misr_fileList = (char **) malloc(sizeof(char *));   // allocate mem-
                if (!misr_fileList) {
                    printf("main: couldn't malloc misr_fileList\n");
                    return 0;
                }
            }
            else {
                misr_fileList = (char **) realloc(misr_fileList, (misr_nfiles + 1) * sizeof(char *));
                if (!misr_fileList) {
                    printf("getFileList: couldn't realloc atm_flist\n");
                    return 0;
                }
            }
            misr_fileList[misr_nfiles] = (char *) malloc(strlen(DirEntryObj->d_name) + 1); // allocate mem-
            if (!misr_fileList[misr_nfiles]) {
                printf("main: couldn't malloc atm_flist[%d]\n", misr_nfiles);
                return 0;
            }
            strcpy(misr_fileList[misr_nfiles], DirEntryObj->d_name);  // fill the misr_fileList with d_name: misr surf files; from DirEntryObj=fileObj gets the fileName
            printf("FOUND: d_name: %s \n", DirEntryObj->d_name);       // d_name is char array inside <dirent.h>
            //printf("file no. %d, %s \n", misr_nfiles, misr_fileList[misr_nfiles]);
            misr_nfiles ++; // counter of num of MISR files found == elements in misr_fileList
    	}
    	closedir (dirp);
    } 
    else {
        strcat(message, "Can't open ");
        strcat(message, surf_masked_dir);
        perror (message);
        return EXIT_FAILURE;
    }
    /* //////////////////////////// Get list of Masked Surface An files ///////////////////////////////////////////// */

	/* //////////////////////////// Process each MISR surf file ///////////////////////////////////////////////////// */

    printf("Processing MISR files ...\n");
    for (i = 0; i < misr_nfiles; i++) { // i= loop for each num of surf MISR files found
        if (strstr(misr_fileList[i], "_p")) {   // search for _P in the file name, find _P in each surf file
            strncpy(spath, strstr(misr_fileList[i], "_p") + 2, 3); // find path
            spath[3] = 0; // Q- why? fills the 3 or 4 element?
            path = atoi(spath); // find path num from surf file
            //printf("path from MISR: %d \n", path);
        }
        else {
            printf("No path info in file name\n");
            return 1;
        }
        //if (path != 78) continue;
        //if (path != 83) continue;
        if ((path < 167) || (path > 240)) continue; // E- what is this path region? our domain?
        //printf("now ... \n");
        //printf("processing MISR surf file: %s%s \n", surf_masked_dir, misr_fileList[i]); // check the full path of surf file

        if (strstr(misr_fileList[i], "_o")) {  // check if orbit is found in file name
            strncpy(sorbit, strstr(misr_fileList[i], "_o") + 2, 6); // get the orbit num from surf file and copy to sorbit
            sorbit[6] = 0; // Q- why?
            orbit = atoi(sorbit); // find orbit no from surf file
        }
        else {
            printf("No orbit info in file name\n");
            return 1;
        }
        // fix file labeling here ???????????????????????????????????????????????????????????????????????????????????????????????

        //printf("misr list file: %s \n", misr_fileList[i]);
        sprintf(an_fname, "%s/%s", surf_masked_dir, misr_fileList[i]);      // stores surf fileName into an_fname buffer
        printf("an_fname: %s \n", an_fname);

        //printf("misr list file: %s \n", misr_fileList[i]);
        sprintf(cf_fname, "%s/%s", surf_masked_dir, misr_fileList[i]); // copy the same surf file into cf
        printf("cf_fname: %s \n",cf_fname);

        strsub(cf_fname, "An", "Cf"); // why this? // substitute an with cf in any format
        strsub(cf_fname, "_an", "_cf"); // substitute an with cfront!
        //printf("cf_fname after: %s \n",cf_fname);
        printf("\n");

        // fix acceess here ???????????????????????????????????????????????????????????????????????????????????????????????
        // check if cf_fname is accessible
        //if (access(cf_fname, F_OK) == -1) continue;	// check if file is acessible, returns 0

        // do the same thing with ca, copy the same surf file into ca
        sprintf(ca_fname, "%s/%s", surf_masked_dir, misr_fileList[i]);
        printf("ca_fname: %s \n",ca_fname);

        // substitute an with cf in any format
        strsub(ca_fname, "An", "Ca");
        strsub(ca_fname, "_an", "_ca"); // rename file to ca
        // printf("ca_fname: %s \n", ca_fname);
        // printf("\n");
        // check if ca_fname is accessible

        // fix acceess here ???????????????????????????????????????????????????????????????????????????????????????????????

        // check if file is accessible, returns 0
        //if (access(ca_fname, F_OK) == -1) continue; // check if file exists, returns 0

        printf("reading MISR surf file data\n");
        /* read MISR surf files */
        if (!read_data(an_fname, nlines, nsamples, &an_data)) return 0; // we fill an_data array from: an_fname
        //printf("%d %s\n", i, an_fname);
        if (!read_data(ca_fname, nlines, nsamples, &ca_data)) return 0;
        //printf("%d %s\n", i, ca_fname);
        if (!read_data(cf_fname, nlines, nsamples, &cf_data)) return 0;
        //printf("%d %s\n", i, cf_fname);

        rms_data = (double *) malloc(5*nlines * nsamples * sizeof(double)); // allocate mem-

        if (strstr(misr_fileList[i], "_b")) {  // get the block number from surf file name
            strncpy(sblock, strstr(misr_fileList[i], "_b") + 2, 3);
            sblock[3] = 0;
            block = atoi(sblock);
            printf("block: %d \n", block);
        }
        else {
            printf("No block info in file name\n");
            return 1;
        }
        // from relative azimush file/table
        block1 = raz_table[orbit - start_orbit] /= 100; // result
        block2 = raz_table[orbit - start_orbit] %= 100; // remainder
        printf("b1: %d; b2: %d \n", block1, block2);
        radius = 0.025; //

        //radius = radius_descend;
        //if ((block < 20) || ((block >= block1) && (block <= block2))) {
        if ((block >= block1) && (block <= block2)) { // E- why this condition?
            ascend = 1;
            printf("ascend block");
            //radius = radius_ascend;
        }

        //////////////////////////////////////////////////////////////////////////////
        for (r=0; r<nlines; r++) {
            for (c=0; c<nsamples; c++) {
                //printf("lat is: %d \n", lat);
                if (!pixel2grid(path, block, r, c, &lat, &lon, &r2, &c2)) return 0; // input &lat-&lon-&r2-&c2 to play with
                // E- r2 and c2 not used

                // start from here ******************************************************************

                rms_data[dsize + r*nsamples + c] = lat;
                rms_data[2*dsize + r*nsamples + c] = lon;
                //rms_data[3*dsize + r*nsamples + c] = 90.0 - r2/1200.0 ;
                //rms_data[4*dsize + r*nsamples + c] = -130.0 + c2/1200.0;

                if (an_data[r*nsamples + c] < 0) {
                    rms_data[r*nsamples + c] = an_data[r*nsamples + c];
                        //rms_data[3*dsize + r*nsamples + c] = an_data[r*nsamples + c];;
                    continue;
                }
                if (ca_data[r*nsamples + c] < 0) {
                    rms_data[r*nsamples + c] = ca_data[r*nsamples + c];
                        //rms_data[3*dsize + r*nsamples + c] = ca_data[r*nsamples + c];;
                    continue;
                }
                if (cf_data[r*nsamples + c] < 0) {
                    rms_data[r*nsamples + c] = cf_data[r*nsamples + c];
                        //rms_data[3*dsize + r*nsamples + c] = cf_data[r*nsamples + c];;
                    continue;
                }
                /***
                if (r2 >= 0 && r2 < gridlines && c2 >= 0 && c2 < gridsamples) {
                        k = c2 + r2 * gridsamples;
                        if (mask[k] == 1){
                        rms_data[r*nsamples + c] = LMASKED;
                        //rms_data[3*dsize + r*nsamples + c] = LMASKED;
                    continue;
                        }
                }
                ***/

                //////////////////////////////////////////////////////////////////////////////
                xrms = 0;
                tweight = 0;
                xrad_min = 1e23;
                for (n=0; n < atmmodel_np; n++) {
                    //if (atm_model[n].ascend != ascend) continue;
                    //if (~ascend || ((block < 20) && (atm_model[n].block < 20)) || ((block >= 20) && (atm_model[n].block >= 20))) {
                    if ((~ascend  && ((atm_model[n].block < 20) || ~atm_model[n].ascend)) || (ascend && (atm_model[n].block >= 20) && (atm_model[n].ascend))) {
                        xan = (an_data[r*nsamples + c] - atm_model[n].an);
                        xca = (ca_data[r*nsamples + c] - atm_model[n].ca);
                        xcf = (cf_data[r*nsamples + c] - atm_model[n].cf);
                    }
                    else {
                        xan = (an_data[r*nsamples + c] - atm_model[n].an);
                        xca = (cf_data[r*nsamples + c] - atm_model[n].ca);
                        xcf = (ca_data[r*nsamples + c] - atm_model[n].cf);
                    }
                    /***
                    xan = (an_data[r*nsamples + c] - atm_model[n].an);
                    xca = (ca_data[r*nsamples + c] - atm_model[n].ca);
                    xcf = (cf_data[r*nsamples + c] - atm_model[n].cf);
                    ***/

                    // E- is it misr refl?
                    xrad = sqrt(xan*xan + xca*xca + xcf*xcf);
                    //
                    if (xrad < radius) {
                    xrms += atm_model[n].tweight * atm_model[n].rms;
                    tweight += atm_model[n].tweight;
                        if (xrad < xrad_min) {
                            xrad_min = xrad;
                            xrms_nearest = atm_model[n].rms;
                        }
                    }
                }

                if (xrms == 0) xrms = xrms_nearest;
                else xrms /= tweight;
                rms_data[r*nsamples + c] = xrms;
                //rms_data[3*dsize + r*nsamples + c] = tweight;
            }
        }
        

        sprintf(rms_fname, "%s/%s", predicted_rough_dir, misr_fileList[i]);
        strsub(rms_fname, "_an.dat", ".dat");
        strsub(rms_fname, "surf", "rms");
        //strsub(rms_fname, "surf", "rms");
        //fp = fopen(rms_fname, "wb");
        printf("%d %s\n", i, rms_fname);
        write_data(rms_fname, rms_data, nlines, nsamples);

        free(an_data);
        free(ca_data);
        free(cf_data);
        free(rms_data);

    }
/* //////////////////////////// Process each MISR surf file ///////////////////////////////////////////////////// */
    return 0;
}
