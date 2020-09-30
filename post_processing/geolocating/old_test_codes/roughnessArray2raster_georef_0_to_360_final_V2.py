#!/usr/bin/python2.7
# coding: utf-8
'''
this f() builds tif files from roughness arrays. 
input: roughness array 
output: georeferenced tif file 

note:
	this code does not have reprojection f()
	code reads all roughness files inside roughness_dir and returns a list of roughness files, not a spicific single path!
'''

import numpy as np
import os, glob
import gdal, osr # python2.7
import MisrToolkit as Mtk # python2.7
from MisrToolkit import * # 
from subprocess import call
import datetime as dt
from matplotlib import pyplot as plt  #  pyplot uses the actual RGB values as they are, more accurate than PIL

########################################################################################################################
# dir path setup by user
########################################################################################################################
#~ setup dir w/ roughness files
roughness_dir_path = '/Volumes/Ehsanm_DRI/research/MISR/roughness_files/'	 # main dir where all subdirs with roughness imgs are
roughness_dir_name = 'roughnessArray_p173_smallset'  # subdir that includes roughness imgs

# tiff dir; where arr2tiff goes to, for now se build it inside rouhness dir
georefRaster_dir_name = 'test_1_AMcrossing_noLonUpdate_2rasterParts'
########################################################################################################################
#~ global IDfiers
########################################################################################################################
# path_num = 40
misr_img_res = (512, 2048)
# img_nrows = misr_img_dims[0]
# img_ncols = misr_img_dims[1]
misr_res_meter = 275
gcp_mode = "corners_n_inside"                       # 'inside' OR "corners_n_inside"
reprojection = 'on'
skip_meridian = 'off'
########################################################################################################################

########################################################################################################################
''' this function'''
def main():

	#~ new iter
	rough_files_fullpath_list, tot_found_rough_files, rough_dir_fullpath = make_roughness_list_from_dir(roughness_dir_path, roughness_dir_name)
	# ## build a dir where images from arr2img will go to

	image_dir = img_dir_setup(rough_dir_fullpath, georefRaster_dir_name)

	#~ reading roughness files in loop & process each at a time
	for file_count, rough_fname in enumerate(rough_files_fullpath_list):
		
		print("--------------------------------------------------------------------------------------------------------")
		print('-> processing new roughness array: (%d/ %d)' % (file_count+1, tot_found_rough_files))
		print(rough_fname)
		
		block_num, path_num, rough_arr_2d = read_rough_file(rough_fname)
		
		## write img to disc w/using arr2img_plot_n_save() function
		path_label = 'path_'+str(path_num)
		block_label = 'block_'+str(block_num)

		ret = arr2img_plot_n_save(rough_arr_2d, path_label, block_label, image_dir)
		
		if (ret=='skipThisImg'):
			print('-> continue to next img.')
			continue
		else:
			out_img_fullpath = ret
		
		#~ open saved image from previous step
		in_ds = gdal.Open(out_img_fullpath)
		# print(type(in_ds)) # returns a Dataset obj
		
		# gcp_list, total_gcps, antimaridina_crossing, gcp_step, gcp_numbers = create_gcp_list_for_imgBlockPixels_mostGCPs(path_num, block_num, misr_res_meter)
		gcp_list, total_gcps, antimaridina_crossing, gcp_step, gcp_numbers = create_gcp_list_for_imgBlockPixels_fewGCPs(path_num, block_num, misr_res_meter)

		if (skip_meridian=='on'):
			if (antimaridina_crossing==True):
				print('-> note: we skip Maridina crossing image block!')
				continue

			# for blocks that cross AM line, make 2 copies of blocks that cross A.M., then mask each for + and - long. and write that block 2 times with masked + and - sides 
			# note: all raster files will be in range: [0, +180] and [0, -180], so change the rest of the code where lon. are get changed

		if (antimaridina_crossing==True):
			translated_img_1_fullpath, translated_img_2_fullpath = apply_gcp_and_copy_AMCrossingBlock(path_label, block_label, image_dir, in_ds, gcp_list)  # inside this f() we make a copy of AM crossing raster, then mask raster for each side of AM line, one for + lon. and one for - lon., then this f() will return 2 translated images
			warpedFile_1_fullPath_noExt = warp_img(path_label, block_label, total_gcps, image_dir, translated_img_1_fullpath, gcp_step, gcp_numbers)
			warpedFile_2_fullPath_noExt = warp_img(path_label, block_label, total_gcps, image_dir, translated_img_2_fullpath, gcp_step, gcp_numbers)
			if (reprojection == 'on'):
				reproject_to_polar(warpedFile_1_fullPath_noExt)
				reproject_to_polar(warpedFile_2_fullPath_noExt)

		else:
			translated_img_fullpath = apply_gcp_normalBlock(path_label, block_label, image_dir, in_ds, gcp_list)
			warpedFile_fullPath_noExt = warp_img(path_label, block_label, total_gcps, image_dir, translated_img_fullpath, gcp_step, gcp_numbers)
			if (reprojection == 'on'):
				reproject_to_polar(warpedFile_fullPath_noExt)

	return 0

########################################################################################################################
'''this func'''
def arr2img_plot_n_save(in_arr_2d, path_label, block_label, img_dir):
		
	if (in_arr_2d.max() < 1):
		print('-> PlotImgFunc(.): img is dark! We skip it.')
		return 'skipThisImg'
	
	else:

		img_format = ".jpg"
		
		out_img_label = path_label+'_'+block_label+img_format
		print(img_dir)
		print(out_img_label)

		out_img_fullpath = os.path.join(img_dir, out_img_label)
		print("-> saving output img as:")
		print(out_img_fullpath)
		plt.imsave(out_img_fullpath, in_arr_2d, cmap='gray', vmin=0, vmax=in_arr_2d.max())  # note: vmin=in_arr_2d.min() is wrong in this case, cuz roughness array
																							# 		has many fill values with ranges in -99999, so vmin=0 to plot images in range [0,max)

		return out_img_fullpath

########################################################################################################################
'''this f() builds image dir inside roughness dir'''
def img_dir_setup(arr2tiff_dir_path, georefRaster_dir_name):
	img_dir = os.path.join(arr2tiff_dir_path, georefRaster_dir_name) 
	if (os.path.isdir(img_dir)):
		print('-> img dir exists!')
		print(img_dir)
	else:
		print('-> img dir NOT exist. We will make it.')
		os.mkdir(img_dir)
		print(img_dir)
	return img_dir
########################################################################################################################
def reproject_to_polar(warpedFile_fullPath_noExt):
	target_epsg = 3995
	print('-> re-projecting to EPSG: %s' % target_epsg)
	file_extension = '.tif'
	input_raster = warpedFile_fullPath_noExt+file_extension
	output_raster_fullpath = warpedFile_fullPath_noExt+'_reprojToEPSG_'+str(target_epsg)+file_extension
	print(output_raster_fullpath)
	gdal.Warp(output_raster_fullpath, input_raster, dstSRS='EPSG:3995')
	print('-> final re-projected file: %s \n' % output_raster_fullpath)
	return 0
########################################################################################################################

def make_roughness_list_from_dir(roughness_dir_path, roughness_dir_name):
	rough_dir_fullpath = os.path.join(roughness_dir_path, roughness_dir_name) # full path to roughness files
	print(rough_dir_fullpath)

	#~ make a list of existing roughness files
	roughness_file_patern = 'roughness_toa_refl_P*'+'_O*'+'_B*'+'.dat'   # for ELLIPSOID data - check file names 
	print("-> looking for pattern: %s" %roughness_file_patern)

	#~ get a list of available/downloaded Ellipsoid files, the list will be list of file_fullpath-s 
	rough_files_fullpath_list = glob.glob(os.path.join(rough_dir_fullpath, roughness_file_patern))

	tot_found_files = len(rough_files_fullpath_list)
	print("-> files found: %d" %tot_found_files)
	#~ maybe split and sort?
	return rough_files_fullpath_list, tot_found_files, rough_dir_fullpath
########################################################################################################################

def read_rough_file(rough_fname):
	rough_1d_arr = np.fromfile(rough_fname, dtype=np.double) # 'double==float64'     # is this roughness in cm?

	#~ get some info about each array
#     print("-> input file elements: %d" % rough_latlon_arr.size)
#     print("-> input file dim: %d" % rough_latlon_arr.ndim)
#     print("-> input file shape: %s" % rough_latlon_arr.shape)

	#~ get only the roughness values from file, roughness file has roughness-lat-lon in it as a list
	rough_arr_1d = rough_1d_arr[0:1048576]

	#~ create 2D roughness array from list
	rough_arr_2d = rough_arr_1d.reshape((512,2048))
	print("-> roughnessArray new shape: (%d, %d)" % rough_arr_2d.shape)
	
	#~ find and extract path number
	path_num = rough_fname.split("/")[-1].split("_")[3][1:] # extract path chuncka and then etract just the number
	path_num = int(path_num)
	print("-> roughness-Path: %s" % (path_num))

	#~ find and extract block number
	block_num = rough_fname.split("/")[-1].split("_")[-1].split(".")[0]
	block_num = int(block_num[-2:])
	print("-> roughness-Block: %s" % (block_num))

	return block_num, path_num, rough_arr_2d
########################################################################################################################

def create_gcp_list_for_imgBlockPixels_fewGCPs(path_num, block_num, misr_res_meter):
	#~ create list of GCPs 
	gcp_step = 100
	print('\n-> GCP steps: %d \n' % gcp_step)
	
	'''index is useful here, so first we create a list from img coordinates from all img pixels
	then we use the index of each element in the pixel coord list as the index/count of each GCP'''

	print("-> transfer img frame -> latlon frame for path_num: %d, block_num: %s" %(path_num, block_num))
	#~ make 2 lists for img and geographic frames, then analyze long. to see if all are neg. or all are pos.; if all are the same then pass, else: change <-> to <+>
	img_pixelFrame_rowcol_list = []  # (row, column)
	img_worldFrame_latlon_list = []


	for jrow in [0, 200, 400, 511]:
		for icol in [0, 300, 600, 1000, 1300, 1700, 2047]:

			#~ process each col of each row
#             print("\n-> processing img coords: (%d, %d)" %(jrow, icol))
	
			#~ use MTK function to map from img frame to geographic frame
			pixel_latlon_tuple = bls_to_latlon(path_num, misr_res_meter, block_num, jrow, icol) # struct=(lat, lon)?
			print(pixel_latlon_tuple)  # print every tuple of transfered latlon

			img_pixelFrame_rowcol_list.append([jrow, icol])
			img_worldFrame_latlon_list.append(pixel_latlon_tuple)

	print("-> total GCPs from img frame: %d" %len(img_pixelFrame_rowcol_list))
	gcp_numbers = len(img_pixelFrame_rowcol_list)

	# print(img_pixelFrame_rowcol_list)
	# print(img_worldFrame_latlon_list)  # print this to check all latlon list

	#~ find min long in array to
	min_long_in_img = min([i[1] for i in img_worldFrame_latlon_list])
	print('-> min long.: %s' % min_long_in_img)

	#~ check all elements of lon. to have same sign, either +/-
	# all(iterable); iterable==list or anything that we can iterate on; Return True if all elements of the iterable are true
	if (any( [pixel_LatLon_tuple[1] < 0  for  pixel_LatLon_tuple in img_worldFrame_latlon_list] )):   # if any Lon in img_worldFrame_latlon_list is neg. we change that to pos.
		''' we do this part if any OR all block pixels are on West hemisphere (have neg. long.) in img block, and we change them to pos. and the range will be [0, +360] '''

		print("-> found some neg. lon. in img_worldFrame_latlon_list!")

		if (all([pixel_LatLon_tuple[1] < 0  for  pixel_LatLon_tuple in img_worldFrame_latlon_list])):

			print('-> West Hem. all negative lon! we don NOT update lon. values') # update: not change anymore
			#~ convert W-> E: all lon. on W.H. side, change to range [0, 360] 
			gcp_list = []  # a list of ground control points

			for index, element in enumerate(img_pixelFrame_rowcol_list):    # index == each GCP ; element order == [row, col]

				#~ for each point we add GCPs to a list
				gcp_list.append(gdal.GCP())  # initialize GCP dataStruct for each coordinate point

				#~ X,Y in img frame
				gcp_list[index].GCPLine  = img_pixelFrame_rowcol_list[index][0]       # y == row
				gcp_list[index].GCPPixel = img_pixelFrame_rowcol_list[index][1]       # x == column == pixel
				
				#~ lat/lon in world frame
				gcp_list[index].GCPY = img_worldFrame_latlon_list[index][0]  # lat=northing 
				gcp_list[index].GCPX = img_worldFrame_latlon_list[index][1]
				antimaridina_crossing = False


		elif ((180-abs(min_long_in_img)) < 50):
			#~ for any block that crosses AM line, we write all neg. and pos. lon. in to a single raster
			print('\n-> image crosses A.M. line!\n')
			gcp_list = []  # a list of ground control points

			for index, element in enumerate(img_pixelFrame_rowcol_list):    # index == each GCP ; element order == [row, col]

				#~ for each point we add GCPs to a list
				gcp_list.append(gdal.GCP())  # initialize GCP dataStruct for each coordinate point

				#~ X,Y in img frame
				gcp_list[index].GCPLine  = img_pixelFrame_rowcol_list[index][0]       # y == row
				gcp_list[index].GCPPixel = img_pixelFrame_rowcol_list[index][1]       # x == column == pixel
								
				#~ 
				gcp_list[index].GCPY = img_worldFrame_latlon_list[index][0]  # lat=northing 
				gcp_list[index].GCPX = img_worldFrame_latlon_list[index][1]
				antimaridina_crossing = True


		else:
			print('\n-> image crosses P.M. line!\n')
			#~ for PM crossing we do NOT convert any lon. in the image, meaning we combine negative and positive lon. on both sides of PM line
			gcp_list = []  # a list of ground control points

			for index, element in enumerate(img_pixelFrame_rowcol_list):    # index == each GCP ; element order == [row, col]

				#~ for each point we add GCPs to a list
				gcp_list.append(gdal.GCP())  # initialize GCP dataStruct for each coordinate point

				#~ X,Y in img frame
				gcp_list[index].GCPLine  = img_pixelFrame_rowcol_list[index][0]       # y == row
				gcp_list[index].GCPPixel = img_pixelFrame_rowcol_list[index][1]       # x == column == pixel
				
				#~ we add lat and lon to list
				gcp_list[index].GCPY = img_worldFrame_latlon_list[index][0]  # lat=northing 
				gcp_list[index].GCPX = img_worldFrame_latlon_list[index][1]
				antimaridina_crossing = False


	else:
		print("\n-> East Hem.: all positive lon.!\n")

		gcp_list = []  # a list of ground control points

		for index, element in enumerate(img_pixelFrame_rowcol_list):    # index == each GCP ; element order == [row, col]

			#~ for each point we add GCPs to a list
			gcp_list.append(gdal.GCP())  # initialize GCP dataStruct for each coordinate point

			#~ X,Y in img frame
			gcp_list[index].GCPLine  = img_pixelFrame_rowcol_list[index][0]       # y == row
			gcp_list[index].GCPPixel = img_pixelFrame_rowcol_list[index][1]       # x == column == pixel

			#~ add lat&lon
			gcp_list[index].GCPY = img_worldFrame_latlon_list[index][0]  # lat=northing 
			gcp_list[index].GCPX = img_worldFrame_latlon_list[index][1]  # lon=easting
			antimaridina_crossing = False

	return gcp_list, len(img_pixelFrame_rowcol_list), antimaridina_crossing, gcp_step, gcp_numbers
########################################################################################################################

def create_gcp_list_for_imgBlockPixels_mostGCPs(path_num, block_num, misr_res_meter):
	#~ create list of GCPs 
	gcp_step = 1
	print('\n-> GCP steps: %d \n' % gcp_step)
	'''index is useful here, so first we create a list from img coordinates from all img pixels
	then we use the index of each element in the pixel coord list as the index/count of each GCP'''

	print("-> transfer img frame -to- latlon frame for path_num: %d, block_num: %s" %(path_num, block_num))
	#~ make 2 lists for img and geographic frames, then analyze long. to see if all are neg. or all are pos.; if all are the same then pass, else: change <-> to <+>
	img_pixelFrame_rowcol_list = []  # (row, column)
	img_worldFrame_latlon_list = []

	for jrow in range(0, 512, gcp_step):
		for icol in range(0, 2048, gcp_step):

			#~ process each col of each row
			# print("\n-> processing img coords: (%d, %d)" %(jrow, icol))
	
			#~ use MTK function to map from img frame to geographic frame
			pixel_latlon_tuple = bls_to_latlon(path_num, misr_res_meter, block_num, jrow, icol) # struct=(lat, lon)?
			# print(pixel_latlon_tuple)  # print every tuple of transfered latlon

			img_pixelFrame_rowcol_list.append([jrow, icol])
			img_worldFrame_latlon_list.append(pixel_latlon_tuple)

	print("-> total GCPs from img frame: %d" %len(img_pixelFrame_rowcol_list))
	gcp_numbers = len(img_pixelFrame_rowcol_list)

	# print(img_pixelFrame_rowcol_list)
	# print(img_worldFrame_latlon_list)  # print this to check all latlon list

	#~ find min long in array to
	min_long_in_img = min([i[1] for i in img_worldFrame_latlon_list])
	print('-> min long.: %s' % min_long_in_img)

	#~ check all elements of lon. to have same sign, either +/-
	# all(iterable); iterable==list or anything that we can iterate on; Return True if all elements of the iterable are true
	if (any( [pixel_LatLon_tuple[1] < 0  for  pixel_LatLon_tuple in img_worldFrame_latlon_list] )):   # if any Lon in img_worldFrame_latlon_list is neg. we change that to pos.
		''' we do this part if any OR all block pixels are on West hemisphere (have neg. long.) in img block, and we change them to pos. and the range will be [0, +360] '''

		print("-> found some neg. lon. in img_worldFrame_latlon_list!")

		if (all([pixel_LatLon_tuple[1] < 0  for  pixel_LatLon_tuple in img_worldFrame_latlon_list])):

			print('\n-> West Hem. all negative lon! we don NOT update lon. values\n') # update: not change anymore
			antimaridina_crossing = False

			#~ convert W-> E: all lon. on W.H. side, change to range [0, 360] 
			gcp_list = []  # a list of ground control points

			for index, element in enumerate(img_pixelFrame_rowcol_list):    # index == each GCP ; element order == [row, col]

				#~ for each point we add GCPs to a list
				gcp_list.append(gdal.GCP())  # initialize GCP dataStruct for each coordinate point

				#~ X,Y in img frame
				gcp_list[index].GCPLine  = img_pixelFrame_rowcol_list[index][0]       # y == row
				gcp_list[index].GCPPixel = img_pixelFrame_rowcol_list[index][1]       # x == column == pixel
				
				#~ lat/lon in world frame
				gcp_list[index].GCPY = img_worldFrame_latlon_list[index][0]  # lat=northing 
				gcp_list[index].GCPX = img_worldFrame_latlon_list[index][1]


		elif ((180-abs(min_long_in_img)) < 50):
			#~ for any block that crosses AM line, we write all neg. and pos. lon. in to a single raster
			print('\n-> image crosses A.M. line!\n')
			antimaridina_crossing = True

			gcp_list = []  # a list of ground control points

			for index, element in enumerate(img_pixelFrame_rowcol_list):    # index == each GCP ; element order == [row, col]

				#~ for each point we add GCPs to a list
				gcp_list.append(gdal.GCP())  # initialize GCP dataStruct for each coordinate point
				print('processing index: %d' % index)
				#~ X,Y in img frame
				gcp_list[index].GCPLine  = img_pixelFrame_rowcol_list[index][0]       # y == row
				gcp_list[index].GCPPixel = img_pixelFrame_rowcol_list[index][1]       # x == column == pixel
								
				#~ 
				gcp_list[index].GCPY = img_worldFrame_latlon_list[index][0]  # lat=northing 
				gcp_list[index].GCPX = img_worldFrame_latlon_list[index][1]


		else:
			print('\n-> image crosses P.M. line!\n')
			antimaridina_crossing = False

			#~ for PM crossing we do NOT convert any lon. in the image, meaning we combine negative and positive lon. on both sides of PM line
			gcp_list = []  # a list of ground control points

			for index, element in enumerate(img_pixelFrame_rowcol_list):    # index == each GCP ; element order == [row, col]

				#~ for each point we add GCPs to a list
				gcp_list.append(gdal.GCP())  # initialize GCP dataStruct for each coordinate point

				#~ X,Y in img frame
				gcp_list[index].GCPLine  = img_pixelFrame_rowcol_list[index][0]       # y == row
				gcp_list[index].GCPPixel = img_pixelFrame_rowcol_list[index][1]       # x == column == pixel
				
				#~ we add lat and lon to list
				gcp_list[index].GCPY = img_worldFrame_latlon_list[index][0]  # lat=northing 
				gcp_list[index].GCPX = img_worldFrame_latlon_list[index][1]


	else:
		print("\n-> East Hem.: all positive lon.!\n")
		antimaridina_crossing = False

		gcp_list = []  # a list of ground control points

		for index, element in enumerate(img_pixelFrame_rowcol_list):    # index == each GCP ; element order == [row, col]

			#~ for each point we add GCPs to a list
			gcp_list.append(gdal.GCP())  # initialize GCP dataStruct for each coordinate point

			#~ X,Y in img frame
			gcp_list[index].GCPLine  = img_pixelFrame_rowcol_list[index][0]       # y == row
			gcp_list[index].GCPPixel = img_pixelFrame_rowcol_list[index][1]       # x == column == pixel

			#~ add lat&lon
			gcp_list[index].GCPY = img_worldFrame_latlon_list[index][0]  # lat=northing 
			gcp_list[index].GCPX = img_worldFrame_latlon_list[index][1]  # lon=easting

	return gcp_list, len(img_pixelFrame_rowcol_list), antimaridina_crossing, gcp_step, gcp_numbers
########################################################################################################################

def apply_gcp_and_copy_AMCrossingBlock(path_label, block_label, image_dir, in_ds, gcp_list):
	#~ gdal.translate to convert data set formats (how input data from memory???)
	#~ write/save image array into raster ??????
	print('-> inside apply_gcp()')

	translated_img = 'translated_'+path_label+'_'+block_label+'.tif'
	out_translated_img_fullpath = os.path.join(image_dir, translated_img)

	#~ define Translate Options --> we don't need to create a TranslateOptions object, we only need do define anything as an keyword_argument for the .Translate()
	#~ writes translated output to a .tif file and returns a gdal.Dataset object; after writing it, translate_ds will be empty --> how do it VRT???
	translate_ds = gdal.Translate(
								out_translated_img_fullpath,
								in_ds,  
								format = 'GTiff',
								outputType = gdal.GDT_Float64, # note: inout dtype is float_64==double, maybe here change dtype to make it smaller img????
								GCPs = gcp_list
								) 

	# print(type(ds_obj))

	#~ Properly close the datasets to flush to disk
	translate_ds = None
	in_ds = None



	# make 2 copies of out_translated_img_fullpath
	# copied_fullpath = out_translated_img_fullpath
	# copied_filename_fullpath = copied_fullpath[-4]+'_copied_'+copied_fullpath[-4]


	#~ Q- how mask it?
	# now mask each for + and - lon. in each one! 
	# where all lon<0 ==> zero all pixels, 
	# and in other one where lon>0 zero all pixels
	# in_1_DS_ptr = gdal.Open(out_translated_img_fullpath)
	# in_2_DS_ptr = gdal.CreateCopy(in_1_DS_ptr)
	# print(in_1_DS_ptr)
	# print(in_2_DS_ptr)







	return out_translated_img_fullpath, copied_translated_img_fullpath # ????
########################################################################################################################

def apply_gcp_normalBlock(path_label, block_label, image_dir, in_ds, gcp_list):
	#~ gdal.translate to convert data set formats (how input data from memory???)
	#~ write/save image array into raster ??????

	print('-> inside apply_gcp_normalBlock()')

	translated_img = 'translated_'+path_label+'_'+block_label+'.tif'
	out_translated_img_fullpath = os.path.join(image_dir, translated_img)

	#~ define Translate Options --> we don't need to create a TranslateOptions object, we only need do define anything as an keyword_argument for the .Translate()
	#~ writes translated output to a .tif file and returns a gdal.Dataset object; after writing it, translate_ds will be empty --> how do it VRT???
	translate_ds = gdal.Translate(
								out_translated_img_fullpath,
								in_ds,  
								format = 'GTiff',
								outputType = gdal.GDT_Float64, # note: inout dtype is float_64==double, maybe here change dtype to make it smaller img????
								GCPs = gcp_list
								) 

	# print(type(ds_obj))
	# print(type(out_translated_img_fullpath))

	#~ Properly close the datasets to flush to disk
	translate_ds = None
	in_ds = None

	return out_translated_img_fullpath
########################################################################################################################

def warp_img(path_label, block_label, total_gcps, image_dir, translated_img_fullpath, gcp_step, gcp_numbers):
	'''
	#~ note: commandLine implementation of gdalwarp, since < --config CENTER_LONG > is not an option for the gdal.Warp() lib. function
	#~ note: CENTER_LONG +180 maps from [0,-/+180] to [0,360] all will be positive lon. --> we don't use it anymore!
	'''
	out_dtype = 'Float64'
	warped_img_tag = 'projected_'+path_label+'_'+block_label+'_'+str(total_gcps)+'GCPs_noGdalRes_'+'dType'+out_dtype+'_'+str(gcp_step)+'gcpSteps_'+str(gcp_numbers)+'gcps'
	warped_img_extension = '.tif'

	warped_img = warped_img_tag+warped_img_extension
	output_file_warped = os.path.join(image_dir, warped_img)

	warpedFile_fullPath_noExt = os.path.join(image_dir, warped_img_tag)
	print(output_file_warped)
	# print(os.path.isfile(translated_img_fullpath))
	# print(os.path.isfile(output_file_warped))

	print('-> to cmdLine... \n')

	cmd = 'gdalwarp\
		-ot Float64 \
		-of "GTiff" \
		-r bilinear \
		-s_srs "EPSG:4326" \
		-t_srs "EPSG:4326" \
		-overwrite \
		-tps \
		-co TILED=YES \
		-srcnodata 0 \
		-dstnodata 0 ' + translated_img_fullpath + ' ' + output_file_warped  
	
	#~ NOTES: 
	# -tr 0.001 0.001 --> target res: this makes output tif file large, so we use default resolution
	# output raster dtype= Float64, not "double" or "float64" w/small f!
	# removed --config CENTER_LONG +180 to check new idea

	print('-> buttleNeck here? with multiple GCP points?')
	#~ note: shell=true to execute the line as full command including arguments
	return_code = call(cmd, shell=True)  # subprocess.call() is better/safer that os.system() ==> finally used os.system() cos call returned error! correct return code?      
	# stat = os.system(input_str_args)  

	print("\n-> gdalWarp subprocess call return stat: %d" %return_code)
	print('-> output warped file: %s' % output_file_warped)
	print("\n-> OK: GdalWarp FINISHED SUCCESSFULLY! \n")

	return warpedFile_fullPath_noExt
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







