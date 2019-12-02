// MaskS.c
// Read surface data files, mask and save
// Gene Mar 25 Apr 18
// Ehsan Nov 12 2019
// notes:
// to-do:

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
char **flist = 0;
int nfiles;
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


int read_data(char *fname, double **data, int nlines, int nsamples)
{
FILE *f;

f = fopen(fname, "rb");
if (!f)
	{
	fprintf(stderr, "read_data: couldn't open %s\n", fname);
	return 0;
	}
	
*data = (double *) malloc(nlines * nsamples * sizeof(double));
if (!*data)
	{
	fprintf(stderr, "read_data: couldn't malloc data\n");
	return 0;
	}
	
if (fread(*data, sizeof(double), nlines * nsamples, f) != nlines * nsamples)
	{
	fprintf(stderr, "read_data: couldn't read data\n");
	return 0;
	}
	
fclose(f);
return 1;
}


int read_byte_data(char *fname, unsigned char **data, int nlines, int nsamples)
{
FILE *f;

f = fopen(fname, "rb");
if (!f)
	{
	fprintf(stderr, "read_byte_data: couldn't open %s\n", fname);
	return 0;
	}
	
*data = (unsigned char *) malloc(nlines * nsamples * sizeof(unsigned char));
if (!*data)
	{
	fprintf(stderr, "read_byte_data: couldn't malloc data\n");
	return 0;
	}
	
if (fread(*data, sizeof(unsigned char), nlines * nsamples, f) != nlines * nsamples)
	{
	fprintf(stderr, "read_byte_data: couldn't read data2\n");
	return 0;
	}
	
fclose(f);

return 1;
}

int getFileList(char *dir)
{
DIR *dp;
struct dirent *ep;

dp = opendir(dir);
if (!dp)
	{
	printf("getFileList: couldn't open %s\n", dir);
	return 0;
	}
	
while (ep = readdir(dp))
	{
	if (strstr(ep->d_name, ".hdr")) continue;
	if (!strstr(ep->d_name, ".dat")) continue;
	//if (!strstr(ep->d_name, "sdcm_")) continue;
	//if (!strstr(ep->d_name, "rms_")) continue;
	if (flist == 0)
	{
	    flist = (char **) malloc(sizeof(char *));
	    if (!flist)
	    {
		printf("getFileList: couldn't malloc flist\n");
		return 0;
	    }
	}
	else
	{
	    if (nfiles > max_nfiles)
	    {
		flist = (char **) realloc(flist, (nfiles + 1) * sizeof(char *));
		if (!flist)
		{
		    printf("getFileList: couldn't realloc flist\n");
		    return 0;
		}
	    }
	}
	flist[nfiles] = (char *) malloc(strlen(ep->d_name) + 1);
	if (!flist[nfiles])
	{
	    printf("getFileList: couldn't malloc flist[nfiles]\n");
	    return 0;
	}
	strcpy(flist[nfiles], ep->d_name);
	//printf("%s\n", flist[nfiles]);
	nfiles ++;
	}
	
closedir(dp);
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


// ################################  main  #############################

int main(int argc, char *argv[])
{
    char s[256];
    char idir0[256] = "/home3/mare/Nolin/2016/Surface3/Jul/";  // Ehsan: surf_ files for each month; surf_p078_o087995_b019_an.dat; AN: replace surf with toa;atm data
    char mfile0[256] = "/home3/mare/Nolin/SeaIce/LWData/MISR_LandSeaMask/lsmask_pP_bB.dat";  // Ehsan: mask file, output of <ArcticTileToGrid.c>
    char odir0[256] = "/home3/mare/Nolin/2016/Surface3_LandMasked/Jul/"; // output dir; dat and png files
    char idir[256], mfile[256];
    char odir[256];
    char fname[256];
    char ofile[256], ofile1[256];
    char spath[10], sblock[10];
    int i, j, k;

    for (i=2; i < 3; i++ )
    {
	strcpy(idir, idir0);
	if (i == 0) strcat(idir, "An/"); 
	if (i == 1) strcat(idir, "Ca/"); 
	if (i == 2) strcat(idir, "Cf/"); 
	strcpy(odir, odir0);
	if (i == 0) strcat(odir, "An/"); 
	if (i == 1) strcat(odir, "Ca/"); 
	if (i == 2) strcat(odir, "Cf/"); 

	if (nfiles > max_nfiles) max_nfiles = nfiles;
	nfiles = 0;
	if (!getFileList(idir)) return 1;

	for (j=0; j < nfiles; j++)
	{
	    sprintf(fname, "%s%s", idir, flist[j]);
	    printf("%s\n",fname);
	    if (!read_data(fname, &data, nlines, nsamples)) return 1;	

	    if (strstr(fname, "_p"))
	    {
		strncpy(spath, strstr(fname, "_p") + 2, 3);
		spath[3] = 0;
	    }
	    else
	    {
		fprintf(stderr, "No path info in file name\n");
		return 1;
	    }

	    if (strstr(fname, "_b"))
	    {
		strncpy(sblock, strstr(fname, "_b") + 2, 3);
		sblock[3] = 0;
	    }
	    else
	    {
		fprintf(stderr, "No block info in file name\n");
		return 1;
	    }
	    strcpy(mfile, mfile0);
	    strsub(mfile, "P", spath);
	    strsub(mfile, "B", sblock);
	    //printf("mfile : %s\n", mfile);
	    if (!read_byte_data(mfile, &mask, nlines, nsamples)) return 1;
	    if (!maskData()) return 1;

	    strcpy(ofile1, flist[j]);
	    //strsub(ofile1, "surf", "surf_lsm");
	    strcpy(ofile, odir);	
	    strcat(ofile, ofile1);
	    //printf("ofile: %s\n", ofile);
	    if (!write_data(ofile, data, nlines, nsamples)) return 1;
	    strsub(ofile, ".dat", ".png");
	    if (!write_png(ofile, data2image(data, nlines, nsamples), nlines, nsamples)) return 1;

	    for (k=0; k < nlines*nsamples; k++)
	    {
		data[k] = 0;
		mask[k] = "\0";
	    }
	    free(data);
	    free((unsigned char *) mask);
	}	//end of j for loop
    }   //end of i for loop

    return 0;
}
