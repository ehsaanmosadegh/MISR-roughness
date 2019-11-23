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
#define MASKED -999995.0
#define LMASKED -999994.0
#define VERBOSE 0


int read_bytedata(char *fname, unsigned char **data, int nlines, int nsamples);
int write_bytedata(char *fname, unsigned char *data, int nlines, int nsamples);
char *strsub(char *s, char *a, char *b);

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

int write_bytedata(char *fname, unsigned char *data, int nlines, int nsamples)
{
FILE *f;

f = fopen(fname, "wb");
if (!f)
	{
	fprintf(stderr, "write_bytedata: couldn't open %s\n", fname);
	return 0;
	}
	
//if (fwrite(data, sizeof(double), nlines * nsamples, f) != nlines * nsamples)
if (fwrite(data, sizeof(unsigned char), nlines * nsamples, f) != nlines * nsamples)
	{
	fprintf(stderr, "write_bytedata: couldn't write data\n");
	return 0;
	}
	
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


//############################################### main ######################################################


int main(char argc, char *argv[])
{
    char *tile[108];
    char fname[256];

    tile[107] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n70e170-lzw.dat";
    tile[106] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n70e160-lzw.dat";
    tile[105] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n70e150-lzw.dat";
    tile[104] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n70e140-lzw.dat";
    tile[103] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n70e130-lzw.dat";
    tile[102] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n70e120-lzw.dat";
    tile[101] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n70e110-lzw.dat";
    tile[100] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n70e100-lzw.dat";
    tile[99] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n70e090-lzw.dat";
    tile[98] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n70e080-lzw.dat";
    tile[97] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n70e070-lzw.dat";
    tile[96] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n70e060-lzw.dat";
    tile[95] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n70e050-lzw.dat";
    tile[94] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n70e040-lzw.dat";
    tile[93] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n70e030-lzw.dat";
    tile[92] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n70e020-lzw.dat";
    tile[91] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n70e010-lzw.dat";
    tile[90] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n70e000-lzw.dat";
    tile[89] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n70w010-lzw.dat";
    tile[88] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n70w020-lzw.dat";
    tile[87] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n70w030-lzw.dat";
    tile[86] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n70w040-lzw.dat";
    tile[85] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n70w050-lzw.dat";
    tile[84] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n70w060-lzw.dat";
    tile[83] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n70w070-lzw.dat";
    tile[82] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n70w080-lzw.dat";
    tile[81] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n70w090-lzw.dat";
    tile[80] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n70w100-lzw.dat";
    tile[79] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n70w110-lzw.dat";
    tile[78] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n70w120-lzw.dat";
    tile[77] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n70w130-lzw.dat";
    tile[76] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n70w140-lzw.dat";
    tile[75] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n70w150-lzw.dat";
    tile[74] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n70w160-lzw.dat";
    tile[73] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n70w170-lzw.dat";
    tile[72] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n70w180-lzw.dat";
    tile[71] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n80e170-lzw.dat";
    tile[70] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n80e160-lzw.dat";
    tile[69] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n80e150-lzw.dat";
    tile[68] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n80e140-lzw.dat";
    tile[67] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n80e130-lzw.dat";
    tile[66] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n80e120-lzw.dat";
    tile[65] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n80e110-lzw.dat";
    tile[64] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n80e100-lzw.dat";
    tile[63] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n80e090-lzw.dat";
    tile[62] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n80e080-lzw.dat";
    tile[61] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n80e070-lzw.dat";
    tile[60] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n80e060-lzw.dat";
    tile[59] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n80e050-lzw.dat";
    tile[58] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n80e040-lzw.dat";
    tile[57] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n80e030-lzw.dat";
    tile[56] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n80e020-lzw.dat";
    tile[55] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n80e010-lzw.dat";
    tile[54] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n80e000-lzw.dat";
    tile[53] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n80w010-lzw.dat";
    tile[52] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n80w020-lzw.dat";
    tile[51] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n80w030-lzw.dat";
    tile[50] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n80w040-lzw.dat";
    tile[49] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n80w050-lzw.dat";
    tile[48] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n80w060-lzw.dat";
    tile[47] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n80w070-lzw.dat";
    tile[46] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n80w080-lzw.dat";
    tile[45] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n80w090-lzw.dat";
    tile[44] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n80w100-lzw.dat";
    tile[43] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n80w110-lzw.dat";
    tile[42] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n80w120-lzw.dat";
    tile[41] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n80w130-lzw.dat";
    tile[40] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n80w140-lzw.dat";
    tile[39] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n80w150-lzw.dat";
    tile[38] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n80w160-lzw.dat";
    tile[37] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n80w170-lzw.dat";
    tile[36] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n80w180-lzw.dat";
    tile[35] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n90e170-lzw.dat";
    tile[34] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n90e160-lzw.dat";
    tile[33] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n90e150-lzw.dat";
    tile[32] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n90e140-lzw.dat";
    tile[31] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n90e130-lzw.dat";
    tile[30] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n90e120-lzw.dat";
    tile[29] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n90e110-lzw.dat";
    tile[28] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n90e100-lzw.dat";
    tile[27] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n90e090-lzw.dat";
    tile[26] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n90e080-lzw.dat";
    tile[25] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n90e070-lzw.dat";
    tile[24] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n90e060-lzw.dat";
    tile[23] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n90e050-lzw.dat";
    tile[22] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n90e040-lzw.dat";
    tile[21] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n90e030-lzw.dat";    
    tile[20] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n90e020-lzw.dat";
    tile[19] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n90e010-lzw.dat";
    tile[18] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n90e000-lzw.dat";
    tile[17] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n90w010-lzw.dat";
    tile[16] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n90w020-lzw.dat";
    tile[15] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n90w030-lzw.dat";
    tile[14] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n90w040-lzw.dat";
    tile[13] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n90w050-lzw.dat";
    tile[12] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n90w060-lzw.dat";
    tile[11] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n90w070-lzw.dat";
    tile[10] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n90w080-lzw.dat";
    tile[9] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n90w090-lzw.dat";
    tile[8] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n90w100-lzw.dat";
    tile[7] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n90w110-lzw.dat";
    tile[6] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n90w120-lzw.dat";
    tile[5] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n90w130-lzw.dat";
    tile[4] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n90w140-lzw.dat";
    tile[3] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n90w150-lzw.dat";
    tile[2] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n90w160-lzw.dat";
    tile[1] = "/home/mare/Nolin/SeaIce/LWData/ArcticTiles/n90w170-lzw.dat";
    tile[0] = " /n90w180-lzw.dat";

    double dppx = 10./12000.;
    double lat;
    double lon;
    int tidx;
    int tsample;
    double tsample_r;
    int tbit_i, tbit;

    char ofile[256] = "/home/mare/Nolin/SeaIce/LWData/MISR_LandSeaMask/lsmask_pP_bB.dat";  //Ehsan: output dir; input dir for Landmask.c
    int status;
    char *errs[] = MTK_ERR_DESC;
    char spath[10], sblock[10];
    int path, block;
    int i;
    int r, c;
    unsigned char *mask;
    unsigned char *lsmask;
    int nlines = 512;
    int nsamples = 2048;
    int tidx_p = -1;

    //double tsample_x;

    lsmask = (unsigned char *) malloc(nlines * nsamples * sizeof(unsigned char));

    for (path=1; path < 234; path++)
    {
	for (block=1; block < 41; block++)
	{
	    //if ((path != 70) || (block != 20)) continue;
	    //if ((path != 5) || (block != 32)) continue;
	    if ((path != 99) || (block != 16)) continue;
	    //if ((path != 230) || (block != 38)) continue;

	    for (r=0; r < nlines; r++)
	    {
		for (c=0; c < nsamples; c++)
		{
		    //if ((r < 205) || (r > 207) || (c < 904) || (c > 914)) continue;
		    //if ((r != 450) || (c < 1400) || (c > 1420)) continue;
		    //if ((r != 450) || (c < 1495) || (c > 1505)) continue;
		    status = MtkBlsToLatLon(path, 275, block, r*1.0, c*1.0, &lat, &lon);
		    if (status != MTK_SUCCESS) 
		    {
			printf("pixel2grid: MtkBlsToLatLon failed!!!, status = %d (%s)\n", status, errs[status]);
			return 0;
		    }

		    if ((lon+ 0.5*dppx) >= 180) lon = -180;
		    tidx = 36 * (int) (round((90 - lat)/dppx)/12000.) + (int) ((lon + 180)/10);
		    if (tidx < 108)
		    {
			if (tidx != tidx_p)
			{
			    if (tidx_p != -1)
			    {
				for (i=0; i < 12000*1500; i++)
				{
				    mask[i] = '\0';
				}
				free((unsigned char *) mask);
			    }
			    if (!read_bytedata(tile[tidx], &mask, 12000, 1500)) return 1;
			    //printf("1: tidx= %d  tidx_p= %d\n", tidx, tidx_p);
			    tidx_p = tidx;
			}
			//tsample_x = 1500*(((int) round(10*(ceil(lat/10.) - lat/10.)/dppx)) % 12000);
			tsample_r = 1500*(((int) round(10*(ceil(lat/10.) - lat/10.)/dppx)) % 12000) + 10*((lon + 180)/10. - (int)((lon + 180)/10.)) / (8 * dppx);
			tsample = tsample_r;
			tbit_i = round(8*(tsample_r - tsample));
			if (tbit_i != 8)
			{
			    tbit = 0x80 >> tbit_i;
			    lsmask[nsamples*r + c] = (mask[tsample] & tbit) >> (7 - tbit_i);
			}
			else	// use adjacent arctic land/sea mask tile (wrap at lon 180deg) 
			{
			    if ((lon + 180. + 0.5*dppx) < (10 * ceil((lon + 180.)/10.)))
				lsmask[nsamples*r + c] = (mask[tsample + 1] & 0x80) >> 7;
			    else
			    {
				for (i=0; i < 12000*1500; i++)
				{
				    mask[i] = '\0';
				}
				free((unsigned char *) mask);

				if ((tidx + 1) < (36 * ceil((tidx + 1)/36.)))
				{
				    tidx += 1;
				    if (!read_bytedata(tile[tidx], &mask, 12000, 1500)) return 1;
				    //printf("2: tidx= %d  tidx_p= %d\n", tidx, tidx_p);
				    tidx_p = tidx;
				}
				else
				{
				    tidx -= 35;
				    if (!read_bytedata(tile[tidx], &mask, 12000, 1500)) return 1;
				    //printf("3: tidx= %d  tidx_p= %d\n", tidx, tidx_p);
				    tidx_p = tidx;
				}
				
				tsample = 1500*(((int) round(10*(ceil(lat/10.) - lat/10.)/dppx)) % 12000);
				lsmask[nsamples*r + c] = (mask[tsample] & 0x80) >> 7;
			    }
			}
		    }
		    else { lsmask[nsamples*r + c] = 0;}
		    //if ((r >= 205) && (r <= 207) && (c >=904) && (c <=914)) {
		    //if ((r == 450) && (c >= 1495) || (c <= 1505)) {
			//printf("r= %d  c= %d  lat= %f  lon= %f  mask= %d  lsmask= %d  tsample_r= %f  tsample= %d  tbit_i=%d  tbit= %d\n", r, c, lat, lon, mask[tsample], lsmask[nsamples*r + c], tsample_r, tsample, tbit_i, tbit);
		    //}
		}
	    }
 
	    sprintf(spath, "%03d", path);
	    sprintf(sblock, "%03d", block);
	    strcpy(fname, ofile);
	    strsub(fname, "P", spath);
	    strsub(fname, "B", sblock);
	    printf("Saving to %s\n", fname);
	    if (!write_bytedata(fname, lsmask, nlines, nsamples)) return 1;
	}
    }
}
