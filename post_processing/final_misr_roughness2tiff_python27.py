'''
author: Ehsan Mosadegh (emosadegh@nevada.unr.edu & ehsanm@dri.edu)

date: 
	June 1, 2020

purpose: 
	to georeference roughness files

how to use: 
we should have Mtk and Gdal installed on the system. then, run this script with python2.7 on your system

to-do tasks:
	check different ways to 

'''
########################################################################################################################
#~ import necessary libraries

import gdal, osr 			# python2.7
# import rasterio 			# python2.7
import MisrToolkit as Mtk 	# python2.7
from MisrToolkit import * 	# 
import numpy as np
import os, glob
import datetime as dt

########################################################################################################################
#~ define functions

def main():

	#~ set constants
	path = 180
	misr_img_dims = (512,2048)
	nrows_img = misr_img_dims[0]
	ncols_img = misr_img_dims[1]
	#~ set paths
	misr_dir = "/Users/ehsanmos/Documents/MISR/postProcess_files_temp.nosync/sample4raster/"
	misr_file = "MISR_AM1_GRP_ELLIPSOID_GM_P180_O088147_AN_F03_0024.hdf" # projParam from Mtk
	#~ use functions on the mainstream of program
	misr_file_fullPath = hdf_file_check(misr_dir, misr_file)
	raster_dir = setup_dir_raster(misr_dir)
	#~ we use Mtk-ProjParam class to extract 
	print("-> processing hdf file: %s" % misr_file)
	proj_param_obj = Mtk.MtkProjParam(misr_file_fullPath)
	# print("-> projection parameter code: %s" % proj_param_obj.projcode)
	b1_ul_lat, b1_ul_lon, b1_lr_lat, b1_lr_lon, offset_list, b1_ulx, b1_uly = process_block1(proj_param_obj, path)
	x_res, y_res = setup_resolution(b1_ul_lat, b1_ul_lon, b1_lr_lat, b1_lr_lon, ncols_img, nrows_img)
	roughness_list = setup_roughness(misr_dir, path, extract_sorting_key_from_list_element)
	# for k in roughness_list:
	#   print(k)

	print('\n')
	for roughness_img in roughness_list:

		#~ parse and get block number
		block_num_str, roughness_filename = extract_sorting_key_from_list_element(roughness_img)
		block_num = int(block_num_str)	# change str to int for counting
		print('-> block num is: %s' % block_num)

		#~ change roughness img from string to array 
		rough_arr = np.fromfile(roughness_img, dtype='float64') # is this roughness in cm?
		# print("-> roughness file elements: %d" % rough_arr.size)
		# print("-> roughness file dim: %d" % rough_arr.ndim)
		# print("-> roughness file shape: %s" % rough_arr.shape)
		# print(type(rough_arr))

		#~ get only the roughness values from file, roughness file has roughness-lat-lon in it as a list
		rough_array = rough_arr[0:1048576]
		# print("-> shape of rough_arr: %d" % rough_array.shape)
		# create 2D roughness array
		roughness_array = rough_array.reshape(misr_img_dims)
		# print("-> rough arr reshaped: %s" % type(roughness_array))
		# print("-> roughness file elements: %d" % roughness_array.size)
		# print("-> roughness file new dim: %d" % roughness_array.ndim)
		# print("-> roughness file new shape: (%d,%d)" % roughness_array.shape)

		#~ get the shape of array
		nrows_img, ncols_img = np.shape(roughness_array) # get dimensions of the 2D roughness array
		# print(nrows_img, ncols_img)

		#~ zero-ing negative values in roughness arrays
		roughness_array = np.where(roughness_array<0, 0, roughness_array)  # change values to 0.0
		# print("-> img min: %d" % roughness_array.min())
		# print("-> img max: %d" % roughness_array.max())

		raster_fullPath = setup_rasterfile(roughness_filename, raster_dir)

		#~ process each roughness file absed on block number; similar to the following

		if block_num==1:
			# ~ write out block 1 as tif file and offset the other blocks
			array2raster(b1_ul_lon, b1_ul_lat, x_res, y_res, ncols_img, nrows_img, raster_fullPath, roughness_array)
		else:
			#~ for blocks 2 and later we use offset from ulcorner of block-1
			ulx_new_block, uly_new_block = blockoffset2som(block_num, offset_list, b1_ulx, b1_uly)
			block_ul_lat, block_ul_lon = Mtk.somxy_to_latlon(path, ulx_new_block, uly_new_block)	# order matters here
			print('-> block_ul_lon: %s' % block_ul_lon)
			print('-> block_ul_lat: %s' % block_ul_lat)
			array2raster(block_ul_lon, block_ul_lat, x_res, y_res, ncols_img, nrows_img, raster_fullPath, roughness_array)
	return 0


def array2raster(block_tl_lon, block_tl_lat, x_res, y_res, ncols_img, nrows_img, raster_fullPath, roughness_array):
	"this function writes out the roughness image as a georeferenced tif file"
	#~ define band and numeric type
	bands_num = 1
	datatype = gdal.GDT_Float32
	raster_epsg_code = 4326		# EPSG code for lat-lon

	#geotrans_matrix_affine = (img_topLeft_x, img_pixel_width, 0, img_topLeft_y, 0, img_pixel_height) # units meter or degrees? in img coord or map coord? --> (top-left-X,...,top-left-Y)
	#geotrans_matrix = (block1_ulc_lon, img_pixel_width, 0, block1_ulc_lat, 0, img_pixel_height) # units in degrees cosOf lat-lon
	geotrans_matrix = (block_tl_lon, x_res, 0, block_tl_lat, 0, y_res) # units in degrees cosOf lat-lon

	#~ create output raster and setup driver=GTiff
	driver = gdal.GetDriverByName('GTiff')  # Initialize driver
	out_raster = driver.Create(raster_fullPath, ncols_img, nrows_img, bands_num, datatype)  # create output raster (img+georefrenced info) dataseet to write data into it (raster_fullPath, ncols_rough_arr, nrows_rough_arr, bands, dtype-> GDAL data type arg)
	out_raster.SetGeoTransform(geotrans_matrix)  # Set the affine transformation coefficients == Specify raster coordinates

	outband = out_raster.GetRasterBand(bands_num)
	outband.WriteArray(roughness_array)

	crs = osr.SpatialReference()
	crs.ImportFromEPSG(raster_epsg_code)
	# print("-> outout frame: %s" % crs.ExportToWkt())
	out_raster.SetProjection(crs.ExportToWkt())
	outband.FlushCache()

	#~ Once we're done, close the dataset properly
	out_raster = None
	outband = None
	# print("-> FINISHED SUCCESS!")
	# print(raster_fullPath)
	return 0


def blockoffset2som(block_num, offset_list, b1_ulx, b1_uly):
	"changes block offset from tlcorner to SOMxy"
	offset_x_from_b1 = 512*275*block_num	# offset in x dir in mteres
	offset_y_from_b1 = offset_list[block_num]*275	# offset in y dir in mteres
	print('-> offset x: %s m' % offset_x_from_b1)
	print('-> offset y: %s m' % offset_y_from_b1)
	ulx_new_block = b1_ulx + offset_x_from_b1
	uly_new_block = b1_uly + offset_y_from_b1
	print('-> ulx new: %s' %ulx_new_block)
	print('-> uly new: %s' %uly_new_block)
	return ulx_new_block, uly_new_block


def extract_sorting_key_from_list_element(list_lmnt):
	"sorting key is 3-digit block number based on labling of roughness files"
	#~ split each file label and extract block number
	filename = list_lmnt.split("/")[-1]
	sorting_key = filename.replace('.','_').split('_')[-2][-3:]
	return sorting_key, filename 	# block number==block_num


def setup_roughness(misr_dir, path, extract_sorting_key_from_list_element):		# function as arg parameter?
	"set up path directories for roughness images"
	#~ roughness files
	roughness_dir = misr_dir+"rough_files"    #"/Volumes/MISR_REPO/misr_roughness_data/mostRecent_with_roughness_labels/"
	#~ make a list of available roughness files
	roughness_file_pattern = 'roughness_P'+str(path)+'*.dat'   # for ELLIPSOID data - check file names 
	# print("-> looking for pattern: %s" % roughness_file_pattern)
	#~ make a list of available Ellipsoid files, the list will be list of file_fullpath-s 
	roughness_list = glob.glob(os.path.join(roughness_dir, roughness_file_pattern))
	#~ sort based on block numbers
	roughness_list.sort(key=extract_sorting_key_from_list_element)  # sorts list elements in place
	return roughness_list


def setup_rasterfile(roughness_filename, raster_dir):
	"setup directory and file name for output raster"
	#~ set raster label 
	raster_label = "LatLon_degreeRes"
	#~ define output raster
	raster_name = roughness_filename+'-'+raster_label+'.tif'
	# print(raster_name)
	#~ define raster output dir
	raster_fullPath = os.path.join(raster_dir, raster_name)
	print("-> output raster name will be: %s" % (raster_name))
	# print("-> output raster fullPath:")
	# print(raster_fullPath)
	return raster_fullPath


def setup_dir_raster(raster_out_dirpath):
	"setup output raster directory"
	#~ define raster directory
	raster_dir_label = "raster_dir"
	raster_outDir = os.path.join(raster_out_dirpath, raster_dir_label)
	return raster_outDir


def hdf_file_check(misr_dir, misr_file):
	"check if hdf file available"
	misr_file_fullPath = os.path.join(misr_dir, misr_file)
	print(misr_file_fullPath)
	if not os.path.isfile(misr_file_fullPath):
		print("-> MISR dhf file not available!")
		raise SystemExit()
	else:
		print("-> MISR hdf file available!")
		return misr_file_fullPath


def process_block1(proj_param_obj, path):
	"processes block-1 for every hdf file"
	# extract tlc and brc from hdf file from block-1
	b1_ul_corner = proj_param_obj.ulc  # order: (X,Y) = (lon,lat)
	b1_lr_corner = proj_param_obj.lrc  # order: (X,Y) = (lon,lat)
	print("-> b1 ul corner: (%d,%d) m" % b1_ul_corner)
	print("-> b1 lr corner: (%d,%d) m" % b1_lr_corner)
	# Define corners of block1
	# use top left corner or each block
	# We swap them based on MISR docs, values are in SOM projection
	b1_ulx = b1_ul_corner[0] # as lon
	b1_uly = b1_lr_corner[1] # as lat
	b1_lrx = b1_lr_corner[0] # as lon
	b1_lry = b1_ul_corner[1] # as lat
	print("-> img ulx= %s, uly= %s" %(b1_ulx, b1_uly))
	print("-> img lrx= %s, lry= %s" %(b1_lrx, b1_lry))
	# proj_param_res = proj_param_obj.resolution
	# print("-> resolution from projParam: %d" % proj_param_res)
	#~ get offset values from tlcorner
	offset_list = proj_param_obj.reloffset
	print("-> number of pixels offset values: %s" % len(offset_list))
	# print("-> offset of pixels from ULC origin:")
	# print(offset_list)
	#~ transform somxy to lat-lon
	b1_ul_lat, b1_ul_lon = Mtk.somxy_to_latlon(path, b1_ulx, b1_uly)  # order matters => to lat-lon of only ulc; goes inside loop
	b1_lr_lat, b1_lr_lon = Mtk.somxy_to_latlon(path, b1_lrx, b1_lry)  # order matters
	print("-> block-1-ULC: lat: %s, lon: %s" % (b1_ul_lat, b1_ul_lon))
	print("-> block-1-LRC: lat: %s, lon: %s" % (b1_lr_lat, b1_lr_lon))
	return b1_ul_lat, b1_ul_lon, b1_lr_lat, b1_lr_lon, offset_list, b1_ulx, b1_uly


def setup_resolution(b1_ul_lat, b1_ul_lon, b1_lr_lat, b1_lr_lon, ncols_img, nrows_img):
	"calculate resolution ob block"
	#~ define resolution of each roughness img in degrees
	x_res = abs((b1_lr_lon-b1_ul_lon)/float(ncols_img))
	y_res = abs((b1_lr_lat-b1_ul_lat)/float(nrows_img))
	print("-> x_res: %s, y_res: %s" % (x_res, y_res))
	return x_res, y_res

########################################################################################################################

if __name__ == '__main__':
	
	start_time = dt.datetime.now()
	print('-> start time: %s' %start_time)
	print(" ")
	main()
	end_time = dt.datetime.now()
	print(" ")
	print('-> end time: %s' %end_time)
	print('-> duration: %s' %(end_time-start_time))
	print('######################## PROGRAM COMPLETED SUCCESSFULLY ########################')

########################################################################################################################








