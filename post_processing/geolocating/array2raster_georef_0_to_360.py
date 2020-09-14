#!/usr/bin/python2.7
# coding: utf-8
'''
this f() builds tif files from roughness arrays. 
input: roughness array 
output: georeferenced tif file 
'''

import numpy as np
import os, glob
import gdal, osr # python2.7
import MisrToolkit as Mtk # python2.7
from MisrToolkit import * # 
from subprocess import call
import datetime as dt

########################################################################################################################
# dir path setup by user
########################################################################################################################
#~ setup dir w/ roughness files
roughness_dir_path = '/Volumes/Ehsanm_DRI/research/MISR/roughness_files/'  # main dir where all subdirs with roughness imgs are
roughness_dir_name = "multithreaded_atmmodel_newASCM"  # subdir that includes roughness imgs

# tiff dir; where arr2tiff goes to, for now se build it inside rouhness dir
georefTif_dir_name = 'test_outputDataType_reprojectionToPolar_0_180'
########################################################################################################################
#~ global IDfiers
########################################################################################################################
path_num = 40
misr_img_res = (512, 2048)
# img_nrows = misr_img_dims[0]
# img_ncols = misr_img_dims[1]
misr_res_meter = 275
gcp_mode = "corners_n_inside"                       # 'inside' OR "corners_n_inside"
########################################################################################################################

########################################################################################################################
''' this function'''
def main():

    rough_files_fullpath_list, tot_found_rough_files, rough_dir_fullpath = make_roughness_list_from_dir(roughness_dir_path, roughness_dir_name, path_num)
    # ## build a dir where images from arr2img will go to

    image_dir = img_dir_setup(rough_dir_fullpath, georefTif_dir_name)

    #~ reading roughness files in loop & process each at a time
    for file_count, rough_fname in enumerate(rough_files_fullpath_list):
        
        print("########################################################################################################")
        print('-> processing new roughness array: (%d/ %d)' % (file_count+1, tot_found_rough_files))
        print(rough_fname)
        
        block_num, rough_arr_2d = read_rough_file(rough_fname)
        
        ## write img to disc w/using arr2img_plot_n_save() function
        img_name = 'block_'+str(block_num)

        ret = arr2img_plot_n_save(rough_arr_2d, img_name, image_dir)
        
        if ((ret=='skipIt') or (ret=='onlyShowImg')):
            print('-> continue to next img.')
            continue
        else:
            out_img_fullpath = ret
        
        ## open saved image from previous step
        in_ds = gdal.Open(out_img_fullpath)
        # print(type(in_ds)) # returns a Dataset obj
        
        gcp_list, total_gcps = create_gcp_list(path_num, block_num, misr_res_meter)
        
        translated_img_fullpath = apply_gcp(img_name, image_dir, in_ds, gcp_list)

        warp_img(img_name, total_gcps, image_dir, translated_img_fullpath)

    return 0

########################################################################################################################
'''this func'''
def arr2img_plot_n_save(in_arr_2d, img_label, img_dir):

    from matplotlib import image as pltimg, pyplot as plt  #  pyplot uses the actual RGB values as they are, more accurate than PIL
    
    save_mode = True
    print('-> save mode: %s' % save_mode)
        
    if (in_arr_2d.max() < 1):
        print('-> PlotImgFunc: img is dark! skip it.')
        return 'skipIt'
    
    else:
        img_format = ".jpg"
        # get_ipython().run_line_magic('matplotlib', 'inline')
        plt.gray() # This will show the images in grayscale as default
        plt.figure(figsize=(20,20))  # set the figure size
        plt.imshow(in_arr_2d, cmap='gray', vmin=0 , vmax=in_arr_2d.max())
        # plt.show() # to show the img inline here

        if (save_mode==True):

            out_img = img_label+img_format
            out_img_fullpath = os.path.join(img_dir, out_img)
            print("-> saving output img as: %s" %out_img_fullpath)
            pltimg.imsave(out_img_fullpath, in_arr_2d)
            # plt.savefig(out_img)
            del plt
            return out_img_fullpath

        else:
            print('-> save mode is False, so we only show img here.')
            return 'onlyShowImg'
########################################################################################################################
'''this f() builds image dir inside roughness dir'''
def img_dir_setup(arr2tiff_dir_path, georefTif_dir_name):
    img_dir = os.path.join(arr2tiff_dir_path, georefTif_dir_name) 
    if (os.path.isdir(img_dir)):
        print('-> img dir exists!')
        print(img_dir)
    else:
        print('-> img dir NOT exist. we make it.')
        os.mkdir(img_dir)
        print(img_dir)
    return img_dir
########################################################################################################################

def make_roughness_list_from_dir(roughness_dir_path, roughness_dir_name, path_num):
    rough_dir_fullpath = os.path.join(roughness_dir_path, roughness_dir_name) # full path to roughness files
    print(rough_dir_fullpath)

    #~ make a list of existing roughness files
    roughness_file_patern = 'roughness_toa_refl_P0'+str(path_num)+'*.dat'   # for ELLIPSOID data - check file names 
    print("-> looking for pattern: %s" %roughness_file_patern)

    #~ get a list of available/downloaded Ellipsoid files, the list will be list of file_fullpath-s 
    rough_files_fullpath_list = glob.glob(os.path.join(rough_dir_fullpath, roughness_file_patern))

    tot_found_rough_files = len(rough_files_fullpath_list)
    print("-> files found: %d" %tot_found_rough_files)
    #~ maybe split and sort?
    return rough_files_fullpath_list, tot_found_rough_files, rough_dir_fullpath
########################################################################################################################

def read_rough_file(rough_fname):
    rough_1d_arr = np.fromfile(rough_fname, dtype='float64')     # is this roughness in cm?
    #~ get some info about each array
#     print("-> input file elements: %d" % rough_latlon_arr.size)
#     print("-> input file dim: %d" % rough_latlon_arr.ndim)
#     print("-> input file shape: %s" % rough_latlon_arr.shape)

    #~ get only the roughness values from file, roughness file has roughness-lat-lon in it as a list
    rough_arr_1d = rough_1d_arr[0:1048576]

    #~ create 2D roughness array from list
    rough_arr_2d = rough_arr_1d.reshape((512,2048))
    print("-> roughness array new shape: (%d, %d)" % rough_arr_2d.shape)

    block_num = rough_fname.split("/")[-1].split("_")[-1].split(".")[0]
    block_num = int(block_num[-2:])
    print("-> roughnessArrayBlock: %s" % (block_num))

    return block_num, rough_arr_2d
########################################################################################################################

def create_gcp_list(path_num, block_num, misr_res_meter):
    #~ create list of GCPs 
    
    '''index is useful here, so first we create a list from img coordinates from all img pixels
    then we use the index of each element in the pixel coord list as the index/count of each GCP'''

    print("-> transfer img frame -> latlon frame for path_num: %d, block_num: %s" %(path_num, block_num))
    #~ make 2 lists for img and geographic frames, then analyze long. to see if all are neg. or all are pos.; if all are the same then pass, else: change <-> to <+>
    pixel_rowcol_list = []  # (row, column)
    geographic_latlon_list = []


    for jrow in [0, 200, 400, 511]:
        for icol in [0, 300, 600, 1000, 1300, 1700, 2047]:

            #~ process each col of each row
#             print("\n-> processing img coords: (%d, %d)" %(jrow, icol))
    
            #~ use MTK function to map from img frame to geographic frame
            pixel_latlon_tuple = bls_to_latlon(path_num, misr_res_meter, block_num, jrow, icol) # struct=(lat, lon)?
            print(pixel_latlon_tuple)  # print every tuple of transfered latlon

            pixel_rowcol_list.append([jrow, icol])
            geographic_latlon_list.append(pixel_latlon_tuple)

    print("-> total GCPs from img frame: %d" %len(pixel_rowcol_list))    
    # print(pixel_rowcol_list)
    # print(geographic_latlon_list)  # print to check all latlon list


    #~ check all elements of long. to have same sign, either +/-
    # all(iterable); iterable==list or anything that we can iterate on; Return True if all elements of the iterable are true
    if (any( [LatLon_tuple[1] < 0  for  LatLon_tuple in geographic_latlon_list] )):   # if any Lon in geographic_latlon_list is neg. we change that to pos.
        ''' we do this part if any or all block pixels are on West hemisphere (have neg. long.) in img block, and we change them to pos. and the range will be [0, +360] '''

        print("-> West Hem.: found neg. lon. in geographic_latlon_list! will update neg. to pos. long.")

        gcp_list = []  # a list of ground control points

        for index, element in enumerate(pixel_rowcol_list):    # index == each GCP ; element order == [row, col]

            #~ for each point we add GCPs to a list
            gcp_list.append(gdal.GCP())  # initialize GCP dataStruct for each coordinate point

            #~ X,Y in img frame
            gcp_list[index].GCPLine  = pixel_rowcol_list[index][0]       # y == row
            gcp_list[index].GCPPixel = pixel_rowcol_list[index][1]       # x == column == pixel


            #~ chnage "-" Lon to "+" w.r.t CENTER_LONG = +180
            #~ print("-> updating neg. lon. to positive")
            
            #~ do this section for blocks that pass AntiMeridian, and we change all neg. long. to pos. long. that will span [0, 360] range 
            
            #~ 1st we add lat to list
            gcp_list[index].GCPY = geographic_latlon_list[index][0]  # lat=northing 

            #~ 2nd check for long. note; this section is as a result of any() meaning that we have 2 scenarios: some long. are neg./pos. or all are neg.
            pixel_long = geographic_latlon_list[index][1]

            if ( pixel_long < 0 ):  # if we find neg. long., we change it to pos. long. and will be in range [0, +360], especially case is all in neg. side of A.M.
                print("-> found neg. pixel long. in the crossing block: %f" % pixel_long)

                updated_lon_passed_AntiMerid = (360.0 + pixel_long )  # this long. is changed to pos. and will be in range [0, +360]
                print("=================> update: neg.long. updated to: %f" %updated_lon_passed_AntiMerid)

                #~ update neg. long. to pos. long.
                gcp_list[index].GCPX = updated_lon_passed_AntiMerid

            else:  # here we collect some pos. long. among neg. long. in the case block is crossing A.M. line
                
                # print("-> found pos. long. among neg. longs. in the crossing block: %f" %geographic_latlon_list[index][1])

                #~ no need to update Lon. since it is pos. Lon.
                gcp_list[index].GCPX = geographic_latlon_list[index][1]

    else:
        print("-> East Hem.: all image is on East hemisphere (positive long.)!")

        gcp_list = []  # a list of ground control points

        for index, element in enumerate(pixel_rowcol_list):    # index == each GCP ; element order == [row, col]

            #~ for each point we add GCPs to a list
            gcp_list.append(gdal.GCP())  # initialize GCP dataStruct for each coordinate point

            #~ X,Y in img frame
            gcp_list[index].GCPLine  = pixel_rowcol_list[index][0]       # y == row
            gcp_list[index].GCPPixel = pixel_rowcol_list[index][1]       # x == column == pixel

            #~ add lat&lon
            gcp_list[index].GCPY = geographic_latlon_list[index][0]  # lat=northing 
            gcp_list[index].GCPX = geographic_latlon_list[index][1]  # lon=easting

    return gcp_list, len(pixel_rowcol_list)
########################################################################################################################

def apply_gcp(img_name, image_dir, in_ds, gcp_list):
    #~ gdal.translate to convert data set formats (how input data from memory???)
    #~ write/save image array into raster ??????

    translated_img = img_name+"_translated.tif"
    translated_img_fullpath = os.path.join(image_dir, translated_img)


    #~ define Translate Options --> we don't need to create a TranslateOptions object, we only need do define anything as an keyword_argument for the .Translate()
    #~ writes translated output to a .tif file and returns a gdal.Dataset object; after writing it, translate_ds will be empty --> how do it VRT???
    translate_ds = gdal.Translate(
                                translated_img_fullpath,
                                in_ds,  
                                format = 'GTiff',
                                outputType = gdal.GDT_Float32, # maybe here chnage dtype to make it smaller img????
                                GCPs = gcp_list
                                ) 

    # print(type(ds_obj))


    #~ Properly close the datasets to flush to disk
    translate_ds = None
    in_ds = None

    return translated_img_fullpath
########################################################################################################################

def warp_img(img_name, total_gcps, image_dir, translated_img_fullpath):
    '''
    #~ note: commandLine implementation of gdalwarp, since <--config CENTER_LONG> is not an option for the gdal.Warp() lib. function
    #~ note: CENTER_LONG +180 assumes all neg. lon. ...???
    '''

    warped_img = img_name+"_reprojected_"+str(total_gcps)+"GCPs_noRes"+".tif"
    out_warped = os.path.join(image_dir, warped_img)

    # print(os.path.isfile(translated_img_fullpath))
    # print(os.path.isfile(out_warped))
    print('-> to cmdLine... \n')

    cmd = 'gdalwarp\
        -r bilinear\
        -s_srs "EPSG:4326"\
        -t_srs "EPSG:4326"\
        -overwrite\
        -tps\
        -co TILED=YES\
        --config CENTER_LONG +180\
        -srcnodata 0\
        -dstnodata 0 ' + translated_img_fullpath + ' ' + out_warped  #  -tr 0.001 0.001\ this makes output tif file large, so we use default resolution

    #~ note: shell=true to execute the line as full command including arguments
    return_code = call(cmd, shell=True)  # subprocess.call() is better/safer that os.system() ==> finally used os.system() cos call returned error! correct return code?      
    # stat = os.system(input_str_args)  

    print("\n-> return stat from gdalWarp subprocess call: %d" %return_code)
    print(out_warped)
    print("\n-> OK: GdalWarp FINISHED SUCCESSFULLY! \n")

    return 0
########################################################################################################################

if __name__ == '__main__':
    
    start_time = dt.datetime.now()
    print('-> start time: %s' %start_time)
    print(" ")
    main()
    end_time = dt.datetime.now()
    print('-> end time= %s' %end_time)
    print('-> runtime duration= %s' %(end_time-start_time))
    print(" ")
    print('######################## TOA COMPLETED SUCCESSFULLY ########################')

########################################################################################################################







