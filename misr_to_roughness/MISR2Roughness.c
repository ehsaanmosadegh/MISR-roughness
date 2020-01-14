// Ehsan Mosadegh 10 Nov 2019
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

    f = fopen(fname, "r");
    if (!f) {
	fprintf(stderr,  "read_data: couldn't open %s\n", fname);
	return 0;
    }
	
    *data = (double *) malloc(nlines * nsamples * sizeof(double));
    if (!*data) {
	fprintf(stderr,  "read_data: couldn't malloc data\n");
	return 0;
    }
	
    if (fread(*data, sizeof(double), nlines * nsamples, f) != nlines * nsamples) {
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

int pixel2grid(int path, int block, int line, int sample, double *xlat, double *xlon, int *r, int *c)
{
int status;
char *errs[] = MTK_ERR_DESC;
double lat, lon;
/* parameters for grid stereographic : 				*/
/* MOD44W.A2000055.h14v01.005.2009212173527_MOD44W_250m_GRID.dat	*/ 

status = MtkBlsToLatLon(path, 275, block, line * 1.0, sample * 1.0, &lat, &lon);
if (status != MTK_SUCCESS) 
	{
	printf("pixel2grid: MtkBlsToLatLon failed!!!, status = %d (%s)\n", status, errs[status]);
	return 0;
	}
	
if (VERBOSE) printf("pixel2grid: lat = %.6f, lon = %.6f\n", lat, lon);

double psize = 10./12000.;
double lon0 = -130.0;
double lat0 = 90.0;

*xlat = lat;
*xlon = lon;
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

int main(char argc, char *argv[])
{
    DIR* dirp;
    FILE* fp;
    struct dirent* ent; // directory entries
    
    // inputs
    char surf_masked_file_dir[256] = "/home/mare/Nolin/data_2000_2016/2016/Surface3_LandMasked/Jul/An/"; // output of LandMask.c - use masked_surf files instead
    char atmfile[256] = 	"/home/mare/Projects/MISR/Julienne/IceBridge2016/SeaIce_Jul2016_atmmodel2_r025.csv"; // ATM csv file; source from where/
    char razimuth[256] =  	"/home/mare/Projects/MISR/Julienne/IceBridge2016/RelativeAzimuth_Jul2016_sorted.txt"; // we don't need this anymore; source from where?
    
    // outputs 
    char rms_dir[256] = 	"/home/mare/Ehsan_lab/misr_proceesing_dir/misr_roughness"; // MISR roughness; rms file;
    
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
    char **misr_list = 0;
    int misr_nfiles = 0;
    int atm_np = 0;
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
    int raz_nlines;
    int *raz_table;
    int block1, block2;
    int block12;
    int ascend;
    //unsigned char *mask;
    //int gridlines = 24000;
    //int gridsamples = 84000;

    //printf("Reading /home/mare/Nolin/SeaIce/ArcticTiles.dat ...\n");
    //if (!read_bytedata("/home/mare/Nolin/SeaIce/ArcticTiles.dat", &mask, gridlines, gridsamples)) return 1;

    // E- reads azimuth file //////////////////////////////////////////////////////////////////////
    sprintf(command, "wc -l %s", razimuth); // stoes command 
    fp = popen(command, "r"); // pipe-open; fp pointer to a stream
    if (fp == NULL) {
	printf("Failed to run command\n" );
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
	if (w == 0) raz_nlines = atoi(words); // no of lines in relAzimuth file
	printf("nlines= %d \n", raz_nlines);
    }
    /* close */
    pclose(fp);

    // E- reads azimuth file //////////////////////////////////////////////////////////////////////
    fp = fopen(razimuth, "r"); // opens file, stores it somewhere and returns the mem-add
    if (!fp) {
	fprintf(stderr, "main: couldn't open %s\n", razimuth);
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
	while ((l == raz_nlines - 1) && (words != NULL)) {
	    if (w == 1) end_orbit = atoi(words);
    	words = strtok (NULL, " ");
	    w++;
	}
	l++;
    }
    //printf("start_orbit= %d  end_orbit= %d\n", start_orbit, end_orbit);
    fseek(fp, 0, SEEK_SET);

    raz_table = (int *) malloc((end_orbit - start_orbit + 1) * sizeof(int));
    while ((read = getline(&sline, &slen, fp)) != -1) {
	words = strtok(sline, " ");
	w = 0; // what is w? is it counter?
	//printf(" w2 is: %d \n" , w);
	//printf("word2 is: %s \n" ,  words); // gets words in a rel azimuth in a loop
	while (words != NULL) { // the end of file EOF
	    if (w == 1) orbit = atoi(words);
	    if (w == 3) block12 = 100*atoi(words);
	    if (w == 4) block12 += atoi(words);
    	    words = strtok (NULL, " ");
	    w++;
	}
	raz_table[orbit - start_orbit] = block12;
    }

    fclose(fp);


    // E- reads ATM scsv file //////////////////////////////////////////////////////////////////////////////
    fp = fopen(atmfile, "r");
    if (!fp) {
	fprintf(stderr, "main: couldn't open %s\n", atmfile);
	return 1;
    }
    //printf("%s", atmfile);
    
    // 
    while ( (read = getline(&sline, &slen, fp)) != -1) { // reads/extracts each row
        //printf("num of char read: %zu \n", read);
        //printf("row extracted: %s", sline);
    w = 0;
    //printf("w is: %d \n" , w);
	words = strtok (sline," ,"); // moves ptr to first token == path in this case
	//printf("word is: %s \n\n" , words);
	
  	while (words != NULL) { // NULL = end of line or EOF; Q- how about w=0==path?
    	//printf ("inside loop, w = %d and words = %s \n",w,words);
	    if (w == 1) orbit = atof(words);
	    if (w == 2) block = atof(words);
	    if (w == 7) xan = atof(words);
	    if (w == 8) xca = atof(words);
	    if (w == 9) xcf = atof(words);
	    if (w == 10) xrms = atof(words);
	    if (w == 13) xweight = atof(words);
	    if (w == 14) tweight = atof(words);
	    if (w == 15) ascend = atoi(words);
    	words = strtok (NULL, " ,"); // whats this?
    	//printf("word updates: %s \n" , words);
    	//printf("\n");
	    w++;
  	}
  	printf("atm_np: %d \n", atm_np);

	if (atm_np == 0) atm_model = (atm_type * ) malloc(sizeof(atm_type));
	else atm_model = (atm_type * ) realloc(atm_model, (atm_np + 1) * sizeof(atm_type));
	// update elements/variables of a new member
	atm_model[atm_np].orbit = orbit;
	atm_model[atm_np].block = block;
	atm_model[atm_np].an = xan;
	atm_model[atm_np].ca = xca;
	atm_model[atm_np].cf = xcf;
	atm_model[atm_np].rms = xrms;
	atm_model[atm_np].weight = xweight;
	atm_model[atm_np].tweight = tweight;
	atm_model[atm_np].ascend = ascend;
	atm_np++;// counter
    }
    //printf("atm_model now is: %d \n", atm_model->d_name);

    fclose(fp);

    // Get list of Masked Surface An files //////////////////////////////////////////////////////////////////////////////
    printf("Getting list of Masked Surface An files ...\n"); // called misr_list
    dirp = opendir(surf_masked_file_dir); // define dir stream
    if (dirp) { // if ptr TRUE
    	while ((ent = readdir(dirp)) != NULL) {// read the first item in dir and moves the ptr to next item
	    if (!strstr(ent->d_name, ".dat")) continue; // if cound not find the this string
	    if (misr_list == 0) {
			misr_list = (char **) malloc(sizeof(char *));
		if (!misr_list) {
		    printf("main: couldn't malloc atm_flist\n");
		    return 0;
		}
	    }
	    else {
		misr_list = (char **) realloc(misr_list, (misr_nfiles + 1) * sizeof(char *));
		if (!misr_list) {
		    printf("getFileList: couldn't realloc atm_flist\n");
		    return 0;
		}
	    }
	    misr_list[misr_nfiles] = (char *) malloc(strlen(ent->d_name) + 1);
	    if (!misr_list[misr_nfiles]) {
		printf("main: couldn't malloc atm_flist[%d]\n", misr_nfiles);
		return 0;
	    }
	    strcpy(misr_list[misr_nfiles], ent->d_name);
	    printf("d_name: %s \n", ent->d_name); // d_name is char array inside <dirent.h>
	    //printf("%d %s\n", misr_nfiles, misr_list[misr_nfiles]);
	    misr_nfiles ++;
    	}
    	closedir (dirp);
    } 
    else {
	strcat(message, "Can't open ");
	strcat(message, surf_masked_file_dir);
  	perror (message);
  	return EXIT_FAILURE;
    }

	// Processing MISR files ////////////////////////////////////////////////////////////////////////////
    printf("Processing MISR files ...\n");
    for (i = 0; i < misr_nfiles; i++) {
	if (strstr(misr_list[i], "_p")) { // if _P is in the file name, find _P in each surf file
	    strncpy(spath, strstr(misr_list[i], "_p") + 2, 3); // find path
	    spath[3] = 0; // ?
	    path = atoi(spath);
	    //printf("path from MISR: %d \n", path);

        }
    else {
	    printf("No path info in file name\n");
	    return 1;
        }
	//if (path != 78) continue;
	//if (path != 83) continue;
	if ((path < 167) || (path > 240)) continue; // E- what is this path region????
	//printf("now ... \n");
	printf("processing: %s%s \n", surf_masked_file_dir, misr_list[i]);
	
	if (strstr(misr_list[i], "_o")) {
	    strncpy(sorbit, strstr(misr_list[i], "_o") + 2, 6); // get the orbit and copy to sorbit
	    sorbit[6] = 0; //?
	    orbit = atoi(sorbit);
        }
    else {
	    printf("No orbit info in file name\n");
	    return 1;
        }
	sprintf(an_fname, "%s/%s", surf_masked_file_dir, misr_list[i]);
	sprintf(cf_fname, "%s/%s", surf_masked_file_dir, misr_list[i]);
	// printf("an_fname: %s \n", an_fname);
	// printf("cf_fname: %s \n",cf_fname);
	strsub(cf_fname, "An", "Cf"); // why this?
	strsub(cf_fname, "_an", "_cf"); // substitute an with cfront!
	//printf("cf_fname: %s \n",cf_fname);

	if (access(cf_fname, F_OK) == -1) continue;	// check if file is acessible, returns 0

	sprintf(ca_fname, "%s/%s", surf_masked_file_dir, misr_list[i]);
	strsub(ca_fname, "An", "Ca");
	strsub(ca_fname, "_an", "_ca"); // rename file to ca
	// printf("ca_fname: %s \n", ca_fname);
	// printf("\n");
	if (access(ca_fname, F_OK) == -1) continue; // check if file is acessible, returns 0





	
	// from here //////////////////////////////////////////////////////////////////////

	if (!read_data(an_fname, nlines, nsamples, &an_data)) return 0;
	//printf("%d %s\n", i, an_fname);
	if (!read_data(ca_fname, nlines, nsamples, &ca_data)) return 0;
	//printf("%d %s\n", i, ca_fname);
	if (!read_data(cf_fname, nlines, nsamples, &cf_data)) return 0;
	//printf("%d %s\n", i, cf_fname);
	rms_data = (double *) malloc(5*nlines * nsamples * sizeof(double));

        if (strstr(misr_list[i], "_b")) {
	    strncpy(sblock, strstr(misr_list[i], "_b") + 2, 3);
	    sblock[3] = 0;
	    block = atoi(sblock);
        }
        else {
	    printf("No block info in file name\n");
	    return 1;
        }

	block1 = raz_table[orbit - start_orbit] /= 100;
	block2 = raz_table[orbit - start_orbit] %= 100;
	radius = 0.025;

	//radius = radius_descend;
	//if ((block < 20) || ((block >= block1) && (block <= block2))) {
	if ((block >= block1) && (block <= block2)) {
	    ascend = 1;
	    //radius = radius_ascend;
	}

	//////////////////////////////////////////////////////////////////////////////
	for (r=0; r<nlines; r++) {
	    for (c=0; c<nsamples; c++) {
		if (!pixel2grid(path, block, r, c, &lat, &lon, &r2, &c2)) return 0;
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
		for (n=0; n<atm_np; n++) {
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

	sprintf(rms_fname, "%s/%s", rms_dir, misr_list[i]);
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

    return 0;
}
