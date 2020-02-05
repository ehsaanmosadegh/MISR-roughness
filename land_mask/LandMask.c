// MaskS.c
// Read surface data files, mask and save
// Gene Mar 25 Apr 18
// Ehsan Nov 12 2019
// notes:
// selects toa_refl OR surf_refl files based on the available files inside the input directory
// to-do:
/* should read from 3 cam directories */

#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <math.h>
#include <png.h>
#include <dirent.h>

#define NO_DATA -999999.0
#define BACKGROUND -999998.0
#define FOREGROUND -999997.0
#define TDROPOUT -999996.0
#define CMASKED -999995.0
#define LMASKED -999994.0
#define VERBOSE 0

char fname[4][256];
unsigned char *mask = 0;
char **ReflFileList = 0;
int ReflFileNum;
int max_nfiles = 0;
int nlines = 512;
int nsamples = 2048;
double *data = 0;

png_structp png_ptr = 0;
png_infop info_ptr = 0;

char *data2image(double *data, int ny, int nx);
int write_png(char *fname, char *image, int ny, int nx);
int write_data(char *fname, double *data, int nlines, int nsamples);
int read_data(char *fname, double **data, int nlines, int nsamples);
int read_byte_data(char *fname, unsigned char **data, int nlines, int nsamples);
int maskData(void);
int getFileList(char *dir);
char *strsub(char *s, char *a, char *b);

//#####################################################################################################

int maskData(void)
{
int i, j, i2, j2;
double z;

for (j = 0; j < nlines; j ++)
	for (i = 0; i < nsamples; i ++)
		{
		//z = data[i + j * nsamples];
		//if (z == NO_DATA) continue;
		//if (z == TDROPOUT) continue;
		
		if (mask[i + j * nsamples] == 0) continue;
		data[i + j * nsamples] = LMASKED;
		}

return 1;
}

//#####################################################################################################

char *data2image(double *data, int nlines, int nsamples)
{
char *image;
double min, max, z, dz;
int i;

min = 1.0e23;
max = -1.0e23;
for (i = 0; i < nlines * nsamples; i ++)
	{
	z = data[i];
	if (z == NO_DATA) continue;
	if (z == TDROPOUT) continue;
	if (z == CMASKED) continue;
	if (z == LMASKED) continue;
	if (z < min) min = z;
	else if (z > max) max = z;
	}
if (VERBOSE) fprintf(stderr, "data2image: Gmin=%.3f, max=%.3f\n", min, max);
if (max != min) dz =  255.0 / (max - min);
else dz = 0.0;

image = (char *) malloc(nlines * nsamples);
if (!image)
	{
	fprintf(stderr, "data2image: couldn't malloc image\n");
	return 0;
	}

for (i = 0; i < nlines * nsamples; i ++)
	{
	z = data[i];
	if (z == NO_DATA) image[i] = 0;
	else if (z == TDROPOUT) image[i] = 0;
	else if (z == CMASKED) image[i] = 0;
	else if (z == LMASKED) image[i] = 0;
	else 
		{
		z = (z - min) * dz;
		if (z > 255.0) image[i] = 255;
		else if (z < 0.0) image[i] = 0;
		else image[i] = z;
		}
	}

return image;
}

//#####################################################################################################

int write_png(char *fname, char *image, int ny, int nx)
{
FILE *fp;
png_bytepp row_ptrs;
int j;

row_ptrs = (png_bytepp) malloc(ny * sizeof(png_bytep));
if (!row_ptrs)
	{
	fprintf(stderr, "write_png: couldn't malloc row_ptrs\n");
	return 0;
	}
for (j = 0; j < ny; j ++) row_ptrs[j] = (png_bytep)(image + j * nx);

fp = fopen(fname, "wb");
if (!fp)
	{
	fprintf(stderr, "write_png: couldn't open %s\n", fname);
	return 0;
	}

png_ptr = png_create_write_struct(PNG_LIBPNG_VER_STRING, 
	png_voidp_NULL, png_error_ptr_NULL, png_error_ptr_NULL);
if (!png_ptr)
	{
	fclose(fp);
	fprintf(stderr, "write_png: png_create_write_struct failed\n");
	return 0;
	}

info_ptr = png_create_info_struct(png_ptr);
if (!info_ptr)
	{
	png_destroy_write_struct(&png_ptr, (png_infopp)NULL);
	fclose(fp);
	fprintf(stderr, "write_png: png_create_info_struct failed\n");
	return 0;
	}

if (setjmp(png_jmpbuf(png_ptr)))
	{
	png_destroy_write_struct(&png_ptr, &info_ptr);
	fclose(fp);
	fprintf(stderr, "write_png: longjmp from png error\n");
	return 0;
	}

png_init_io(png_ptr, fp);

png_set_IHDR(png_ptr, info_ptr, nx, ny, 8, PNG_COLOR_TYPE_GRAY, 
	PNG_INTERLACE_NONE, PNG_COMPRESSION_TYPE_DEFAULT, PNG_FILTER_TYPE_DEFAULT);
	
png_set_rows(png_ptr, info_ptr, row_ptrs);

png_write_png(png_ptr, info_ptr, PNG_TRANSFORM_IDENTITY, NULL);
       
png_destroy_write_struct(&png_ptr, &info_ptr);

fclose(fp);
if (row_ptrs) free(row_ptrs);
return 1;
}

//#####################################################################################################

int write_data(char *fname, double *data, int nlines, int nsamples)
{
FILE *f;

f = fopen(fname, "wb");
if (!f)
	{
	fprintf(stderr, "write_data: couldn't open %s\n", fname);
	return 0;
	}
	
if (fwrite(data, sizeof(double), nlines * nsamples, f) != nlines * nsamples)
	{
	fprintf(stderr, "write_data: couldn't write data\n");
	return 0;
	}
	
fclose(f);
return 1;
}

//#####################################################################################################

int read_data(char *fname, double **data, int nlines, int nsamples) {
FILE *filePtr;

filePtr = fopen(fname, "rb");

if (!filePtr) {
	fprintf(stderr, "read_data: couldn't open %s\n", fname);
	return 0;
	}
	
*data = (double *) malloc(nlines * nsamples * sizeof(double));

if (!*data) {
	fprintf(stderr, "read_data: couldn't malloc data\n");
	return 0;
	}
	
if (fread(*data, sizeof(double), nlines * nsamples, filePtr) != nlines * nsamples) { // reads all pixels inside surf_file into <data>
	fprintf(stderr, "read_data: couldn't read data\n");
	return 0;
	}
	
fclose(filePtr);
return 1;
}

//#####################################################################################################

int read_byte_data(char *fname, unsigned char **data, int nlines, int nsamples)
{
FILE *f;

f = fopen(fname, "rb");
if (!f)
	{
	fprintf(stderr, "read_byte_data: couldn't open %s \n", fname);
	return 0;
	}
	
*data = (unsigned char *) malloc(nlines * nsamples * sizeof(unsigned char));
if (!*data)
	{
	fprintf(stderr, "read_byte_data: couldn't malloc data \n");
	return 0;
	}
	
if (fread(*data, sizeof(unsigned char), nlines * nsamples, f) != nlines * nsamples)
	{
	fprintf(stderr, "read_byte_data: couldn't read data2 \n");
	return 0;
	}
	
fclose(f);

return 1;
}

//#####################################################################################################

int getFileList(char* dir) { // returns ReflFileList
DIR* dirPtr;
struct dirent* entryPtr; //char* d_name

dirPtr = opendir(dir); // pointer to dir; creates stream;
if (!dirPtr) {
	printf("getFileList: issue with dirPtr; couldn't open %s\n", dir);
	return 0;
	}
	
while (entryPtr = readdir(dirPtr)) {

	//printf("entryPtr->d_name %s \n" , entryPtr->d_name);
	if (strstr(entryPtr->d_name, ".hdr")) continue; //if returns a pointer, continue
	if (!strstr(entryPtr->d_name, ".dat")) continue; //if not return pointer, continue
	//if (!strstr(entryPtr->d_name, "sdcm_")) continue;
	//if (!strstr(entryPtr->d_name, "rms_")) continue;
	if (ReflFileList == 0) {
		//printf("ReflFileNum is zero, we pass \n");
	    ReflFileList = (char **) malloc(sizeof(char *));
	    if (!ReflFileList) {
            printf("getFileList: couldn't malloc ReflFileList \n");
            return 0;
	    }
	}
	else {
		//printf("nfilesII= %d \n" , ReflFileNum); E

	    if (ReflFileNum > max_nfiles) {
            ReflFileList = (char **) realloc(ReflFileList, (ReflFileNum + 1) * sizeof(char *));
            if (!ReflFileList) {
                printf("getFileList: couldn't realloc ReflFileList\n");
                return 0;
            }
	    }
	}

    ReflFileList[ReflFileNum] = (char *) malloc(strlen(entryPtr->d_name) + 1); // alloc mem-

	if (!ReflFileList[ReflFileNum]) {
	    printf("getFileList: couldn't malloc ReflFileList[ReflFileNum]\n");
	    return 0;
	}

	strcpy(ReflFileList[ReflFileNum], entryPtr->d_name); // fill file list=ReflFileList with files in dir == An/Cf/Ca at a time

	//printf("ReflFileList= %s\n", ReflFileList[ReflFileNum]); E
	ReflFileNum ++;
	}
	
closedir(dirPtr);
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


// ################################  main  #############################

int main(int argc, char* argv[]) {

    // input dir
    char reflectance_dir[256] = "/home/mare/Ehsan_lab/misr_proceesing_dir/toa_radiance/toa_refl_july_14_2016/"; // toa_refl data; should be in 3 different directories	//"/home3/mare/Nolin/2016/Surface3/Jul/";
    char lsmask_files[256] = "/home3/mare/Nolin/SeaIce/LWData/MISR_LandSeaMask/lsmask_pP_bB.dat";  	// Ehsan: mask file, output of <ArcticTileToGrid.c>
    
    // output dir 
    char masked_refl_dir[256] = "/home/mare/Ehsan_lab/misr_proceesing_dir/masked_refl/";	// output dir; dat and png files; 	//"/home3/mare/Nolin/2016/Surface3_LandMasked/Jul/"; 
    
    // other variables
    char inputDir[256], lsMaskedFile[256];
    char outputDir[256];
    char fname[256];
    char outFile[256], ofile1[256];
    char spath[10], sblock[10];
    int i, j, k;
    int i_init = 0; //E- added to constrain to 2=Cf
    char masked_outfile[256];
    char s[256];

    strcpy(masked_outfile, "masked_");

    for (i=i_init; i < 3; i++ ) {   //starts from camera= 0 to 2

        strcpy(inputDir, reflectance_dir); // copies the pointer
        if (i == 0) strcat(inputDir, "An/"); // adds this dir to the end of surf file dir
        if (i == 1) strcat(inputDir, "Ca/");
        if (i == 2) strcat(inputDir, "Cf/");

        strcpy(outputDir, masked_refl_dir);
        if (i == 0) strcat(outputDir, "An/");
        if (i == 1) strcat(outputDir, "Ca/");
        if (i == 2) strcat(outputDir, "Cf/");

        printf("inputDir: %s \n" , inputDir);
//        printf("ReflFileNum 1= %d \n" , ReflFileNum);
//        printf("max ReflFileNum 1= %d \n" , max_nfiles);

        if (ReflFileNum > max_nfiles) max_nfiles = ReflFileNum; //E- why? to remember how many iterations/files we did in past step?
        
        ReflFileNum = 0; // defined as initial value
        if (!getFileList(inputDir)) return 1; // returns ReflFileList

        printf("total number of refl_files found: %d \n" , ReflFileNum); // E
//        ReflFileNum = 40; //E-i added to test it
        for (j=0; j < ReflFileNum; j++) { // loop over all ReflFileNum == num of surf refl in AN dir

            sprintf(fname, "%s%s", inputDir, ReflFileList[j]); // copies surf_file name into fname
            printf("pro SurfFile: %s \n",fname); // E
            if (!read_data(fname, &data, nlines, nsamples)) return 1; // reads surf_refl and returns mem-add od data

            if (strstr(fname, "_P")) { // finds path#
                strncpy(spath, strstr(fname, "_P") + 2, 3);
                spath[3] = 0;
                printf("spath: %s\n" , spath);
            }
            else {
                fprintf(stderr, "No path info in file name\n");
                return 1;
            }

            if (strstr(fname, "_B")) { // finds block#
                strncpy(sblock, strstr(fname, "_B") + 2, 3); // note: change 2 to 3 if blocks go larger than 99 (100)
                sblock[3] = 0; // should get blocks with 3 digits
                printf("sblock= %s \n" , sblock);
            }
            else {
                fprintf(stderr, "No block info in file name\n");
                return 1;
            }
            strcpy(lsMaskedFile, lsmask_files);
            strsub(lsMaskedFile, "P", spath);
            strsub(lsMaskedFile, "B", sblock);
            printf(">>> lsMaskedFile for read_byte func: %s\n", lsMaskedFile); // E

            if (!read_byte_data(lsMaskedFile, &mask, nlines, nsamples)) return 1;
            if (!maskData()) return 1;

            strcat(masked_outfile, ReflFileList[j]);
            //strcpy(ofile1, ReflFileList[j]); //E

            //ofile1 = ("masked_%s", ofile1);
            //strsub(ofile1, "surf", "surf_lsm");
            //strcat("masked_", ofile1);
            strcpy(outFile, outputDir);
            //printf("ofile1: %s \n", outFile);

            //strcat(outFile, ofile1); //E
            strcat(outFile, masked_outfile); //E

            //printf("writing output: %s \n", outFile);

            if (!write_data(outFile, data, nlines, nsamples)) return 1;

            strsub(outFile, ".dat", ".png");
            if (!write_png(outFile, data2image(data, nlines, nsamples), nlines, nsamples)) return 1;

            for (k=0; k < nlines*nsamples; k++) {
            data[k] = 0;
            mask[k] = "\0";
            }

            free(data);
            free((unsigned char *) mask);

            //memset(outFile, '\0', sizeof outFile);
            strcpy(masked_outfile, "masked_"); //E

        }	//end of j for loop
    }   //end of i for loop

    printf("***** SUCCESSFULLY FINISHED! *****");
    return 0;
} // end of main
