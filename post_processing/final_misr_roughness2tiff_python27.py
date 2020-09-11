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
	misr_dir = "/Users/ehsanmos/Documents/RnD/Ehsan_lab_MISR/sample4raster"
	misr_file = "MISR_AM1_GRP_ELLIPSOID_GM_P180_O088147_AN_F03_0024.hdf" # projParam from Mtk
	#~ 
	raster_dir, proj_param_obj = hdf_metadata_info(misr_dir, misr_file)

	#~ we process block-1 first
	ulc_lat_b1, ulc_lon_b1, lrc_lat_b1, lrc_lon_b1, offset_list, ulc_somx_b1, ulc_somy_b1, lrc_somx_b1, lrc_somy_b1 = process_block1(proj_param_obj, path)
	cell_width_res, cell_height_res = setup_raster_resolution(ulc_lat_b1, ulc_lon_b1, lrc_lat_b1, lrc_lon_b1, ncols_img, nrows_img)
	roughness_list = setup_roughness_filelist(misr_dir, path, extract_sorting_key_from_list_element)
	# for k in roughness_list:
	#   print(k)

	# print('\n')
	for roughness_img in roughness_list:

		#~ parse and get block number
		block_num_str, roughness_filename = extract_sorting_key_from_list_element(roughness_img)
		block_num = int(block_num_str)	# change str to int for counting
		print('\n-> processing block: %s' % block_num)

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
		roughness_array = roughness_array*10	# to increase intensity to be able to look at images on Google Earth
		# print("-> img min: %d" % roughness_array.min())
		# print("-> img mean: %d" % roughness_array.mean())		
		# print("-> img max: %d" % roughness_array.max())

		raster_fullPath = setup_rastername(roughness_filename, raster_dir)

		#~ process each roughness file absed on block number; similar to the following

		if block_num==1:
			#~ write out block 1 as tif file and offset the other blocks
			# this is correct ulc, by swapping y-coords in latlon format
			# ulc_lat_b1 = 66.223581
			# ulc_lon_b1 = -178.841471 #-166.103258

			# ulc= 66.223581, -178.841471		y-swapped based on Mtk and 
			# lrc= 65.752107, -166.103258  		y-swapped
# 			
			array2raster(ulc_lat_b1, ulc_lon_b1, cell_width_res, cell_height_res, ncols_img, nrows_img, raster_fullPath, roughness_array)
		
		else:
			#~ for blocks 2 and rest we use y-offset from ulcorner of block-1
			ul_new_somx_rel2b1, ul_new_somy_rel2b1 = block_offset_to_SOM(block_num, offset_list, ulc_somx_b1, ulc_somy_b1, lrc_somx_b1, lrc_somy_b1)
			print('-> problem is here...')
			newblock_ul_lat, newblock_ul_lon = Mtk.somxy_to_latlon(path, ul_new_somx_rel2b1, ul_new_somy_rel2b1)	# ulc, order matters here
			# newblock_lr_lat, newblock_lr_lon = Mtk.somxy_to_latlon(path, lr_new_somx_rel2b1, lr_new_somy_rel2b1)	# lrc, order matters here


			#~ test for block-2
			# newblock_ulc = (67.44907847403444, -166.86173134299995)
			# newblock_lrc = (66.88915827806183, 179.7994128373612)
			
			print('-> ulc block(%s) in lat,lon= %f, %f' % (block_num, newblock_ul_lat, newblock_ul_lon))
			# print('-> lrc lat,lon= %f, %f' % (newblock_lr_lat, newblock_lr_lon))

			array2raster(newblock_ul_lat, newblock_ul_lon, cell_width_res, cell_height_res, ncols_img, nrows_img, raster_fullPath, roughness_array)
			# array2raster(newblock_ulc[0], newblock_lrc[1], cell_width_res, cell_height_res, ncols_img, nrows_img, raster_fullPath, roughness_array)

			print('diff of lat-b1-b2= %s' % (ulc_lat_b1-newblock_ul_lat))
			print('diff of lon-b1-b2= %s' % (ulc_lon_b1-newblock_ul_lon))

	return 0

#-----------------------------------------------------------------------------------------------------------------------

def hdf_metadata_info(misr_dir, misr_file):
	"chedks metadata inside hdf file"
	print('-> hdf metadata info:')
	#~ use functions on the mainstream of program
	misr_file_fullPath = hdf_file_check(misr_dir, misr_file)
	raster_dir = setup_dir_raster(misr_dir)
	#~ we use Mtk-ProjParam class to extract 
	print("-> hdf file: %s" % misr_file)
	proj_param_obj = Mtk.MtkProjParam(misr_file_fullPath)
	print("-> projection resolution: %s m" % proj_param_obj.resolution)
	projParams_list = proj_param_obj.projparam
	print('-> projection parameters:')
	for pp in projParams_list:
		print(pp)
	print('-> inclination angle: %f' % projParams_list[3])
	print('-> lon of ascending node: %f' % projParams_list[4])	# format: packed ddd-mmm-sss.ss
	# print("-> projection parameter code: %s" % proj_param_obj.projcode)
	print('\n')
	return raster_dir, proj_param_obj

#-----------------------------------------------------------------------------------------------------------------------

def array2raster(block_ulc_lat, block_ulc_lon, cell_width_res, cell_height_res, ncols_img, nrows_img, raster_fullPath, roughness_array):
	"this function writes out the roughness image as a georeferenced tif file"

	# reversed_arr = roughness_array[::-1] # reverse array so the tif looks like the array
	#~ define band and numeric type
	bands_num = 1
	datatype = gdal.GDT_Float32
	raster_epsg_code = 4326		# EPSG code for lat-lon
	x_rotation = 0
	y_rotation = 0
	print('-> input2raster: ulc lat,lon= %f, %f' % (block_ulc_lat, block_ulc_lon))
	#geotrans_matrix_affine = (img_topLeft_x, img_pixel_width, 0, img_topLeft_y, 0, img_pixel_height) # units meter or degrees? in img coord or map coord? --> (top-left-X,...,top-left-Y)
	#geotransform_matrix = (block1_ulc_lon_b1, img_pixel_width, 0, block1_ulc_lat_b1, 0, img_pixel_height) # units in degrees cosOf lat-lon
	geotransform_matrix = (block_ulc_lon, cell_width_res, x_rotation, block_ulc_lat, y_rotation, -cell_height_res) # units in degrees because our output raster is in lat-lon

	#~ create output raster and setup driver=GTiff
	driver = gdal.GetDriverByName('GTiff')  # Initialize driver
	out_raster = driver.Create(raster_fullPath, ncols_img, nrows_img, bands_num, datatype)  # create output raster (img+georefrenced info) dataseet to write data into it (raster_fullPath, ncols_rough_arr, nrows_rough_arr, bands, dtype-> GDAL data type arg)
	out_raster.SetGeoTransform(geotransform_matrix)  # Set the affine transformation coefficients == Specify raster coordinates

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
	print("-> FINISHED SUCCESS!")
	# print(raster_fullPath)
	return 0

#-----------------------------------------------------------------------------------------------------------------------

def block_offset_to_SOM(block_num, offset_list, ulc_somx_b1, ulc_somy_b1, lrc_somx_b1, lrc_somy_b1):
	"calculates block offset of each new block relative to block1 tlcorner, retuens in SOMxy frame"
	"NOTE: in SOM frame, x-dir is along MISR ground track and y-dir is prependicular to that"
	"x-ofsset is 512 blocks * 275 m * for each block along MISR ground track"
	"y-offset is int number of blocks in left/right direction perpendicular to x-dir"

	print('-> block-1 ulc SOM x,y= %d, %d m' % (ulc_somx_b1, ulc_somy_b1))
	delta_x_along_MISR_groundtrack = 512*275 		# offset in x dir in mteres, constant= 140.8 km
	x_offset = delta_x_along_MISR_groundtrack*(block_num-1) 	# meters

	delta_y_rel2_b1_ulc = offset_list[block_num]	# offset in y dir in mteres
	y_offset = delta_y_rel2_b1_ulc*275
	
	print('-> offset of new ulc rel2 its above block x,y= %d, %d m' % (x_offset, y_offset))

	ul_new_somx_rel2b1 = ulc_somx_b1 + x_offset 	# constant meters in each step
	ul_new_somy_rel2b1 = ulc_somy_b1 + y_offset	# changes in each step relative to block1

	lr_new_somx_rel2b1 = lrc_somx_b1 + x_offset 	# constant meters in each step
	lr_new_somy_rel2b1 = lrc_somy_b1 + y_offset	# changes in each step relative to block1

	
	print('-> block(%s) ulc rel2b1 SOMx,y= %d, %d m' % (block_num, ul_new_somx_rel2b1, ul_new_somy_rel2b1))
	# print('-> lrc of block (%s) in relative-to-b1 SOM x,y= %d, %d m' % (block_num, lr_new_somx_rel2b1, lr_new_somy_rel2b1))

	return ul_new_somx_rel2b1, ul_new_somy_rel2b1#, lr_new_somx_rel2b1, lr_new_somy_rel2b1

#-----------------------------------------------------------------------------------------------------------------------

def extract_sorting_key_from_list_element(list_lmnt):
	"sorting key is 3-digit block number based on labling of roughness files"
	#~ split each file label and extract block number
	filename = list_lmnt.split("/")[-1]
	sorting_key = filename.replace('.','_').split('_')[-2][-3:]
	return sorting_key, filename 	# block number==block_num

#-----------------------------------------------------------------------------------------------------------------------

def setup_roughness_filelist(misr_dir, path, extract_sorting_key_from_list_element):		# function as arg parameter?
	"set up path directories for roughness images"
	#~ roughness files
	roughness_dir_label = 'roughness_dir'
	roughness_dir = os.path.join(misr_dir, roughness_dir_label)    #"/Volumes/MISR_REPO/misr_roughness_data/mostRecent_with_roughness_labels/"
	if os.path.isdir(roughness_dir) == False:
		print('-> roughness dir NOT exist. Exiting...')
		print(roughness_dir)
		raise SystemExit()

	#~ make a list of available roughness files
	roughness_file_pattern = 'roughness_P'+str(path)+'*.dat'   # for ELLIPSOID data - check file names 
	# print("-> looking for pattern: %s" % roughness_file_pattern)
	#~ make a list of available Ellipsoid files, the list will be list of file_fullpath-s
	#~ check roughness dir

	roughness_list = glob.glob(os.path.join(roughness_dir, roughness_file_pattern))		# include filePattern to glob
	#~ sort based on block numbers
	roughness_list.sort(key=extract_sorting_key_from_list_element)  # sorts list elements in place
	return roughness_list

#-----------------------------------------------------------------------------------------------------------------------

def setup_rastername(roughness_filename, raster_dir):
	"setup directory and file name for output raster"
	#~ set raster label 
	raster_label = "LatLon_degreeRes"
	#~ define output raster
	raster_name = roughness_filename+'-'+raster_label+'.tif'
	# print(raster_name)
	#~ define raster output dir
	raster_fullPath = os.path.join(raster_dir, raster_name)
	print("-> output raster: %s" % (raster_name))
	# print("-> output raster fullPath:")
	# print(raster_fullPath)
	return raster_fullPath

#-----------------------------------------------------------------------------------------------------------------------

def setup_dir_raster(raster_out_dirpath):
	"setup output raster directory"
	#~ define raster directory
	raster_dir_label = "raster_dir"
	raster_outDir = os.path.join(raster_out_dirpath, raster_dir_label)
	return raster_outDir

#-----------------------------------------------------------------------------------------------------------------------

def hdf_file_check(misr_dir, misr_file):
	"check if hdf file available"
	misr_file_fullPath = os.path.join(misr_dir, misr_file)
	# print(misr_file_fullPath)
	if not os.path.isfile(misr_file_fullPath):
		print("-> MISR dhf file not available!")
		raise SystemExit()
	else:
		print("-> MISR hdf file available!")
		return misr_file_fullPath

#-----------------------------------------------------------------------------------------------------------------------

def process_block1(proj_param_obj, path):
	"process block-1 for every hdf file, we have options for 2 run modes"

	# swap_lon = False
	# print('-> swapping longitutes: %s' % swap_lon)
	# mode_list = ['no_corner_swap', 'ul_lr_y_coord_swap', 'tl_br_full_swap']
	# corner_swap_mode = mode_list[1]
	# print('-> block-1 corner swap mode: %s' % corner_swap_mode)
	# img_transfer_mode_list = ['som2latlon', 'bls2som2latlon']
	# img_transfer_mode = img_transfer_mode_list[0]


	#~ extract ulc and lrc from hdf file from block-1
	ulc_tuple_b1 = proj_param_obj.ulc  # order: (X,Y) = (lon,lat)
	lrc_tuple_b1 = proj_param_obj.lrc  # order: (X,Y) = (lon,lat)
	print("-> ulc b1: (%d,%d) m" % ulc_tuple_b1)
	print("-> lrc b1: (%d,%d) m" % lrc_tuple_b1)

	#~ get offset values from tlc
	offset_list = proj_param_obj.reloffset
	print("-> number of pixels in offset list: %s" % len(offset_list))
	# print("-> offset of pixels from ULC origin:")
	# print(offset_list)

	# #~ we do swapping after transfroming to lat-lon
	# ulc_somx_b1, ulc_somy_b1, lrc_somx_b1, lrc_somy_b1 = no_corner_swap(ulc_tuple_b1, lrc_tuple_b1)


	#~ we swap somy coords for tlc and brc based on MISR science docs
	ulc_somx_b1, ulc_somy_b1, lrc_somx_b1, lrc_somy_b1 = ul_lr_y_coord_swap(ulc_tuple_b1, lrc_tuple_b1)


	#~ transform SOM(xy) y-swapped --> lat-lon
	print('-> img coord-vonversion mode: "SOM-to-latlon"')
	ulc_lat_b1, ulc_lon_b1 = Mtk.somxy_to_latlon(path, ulc_somx_b1, ulc_somy_b1)  # order matters => to lat-lon of only ulc; goes inside loop
	lrc_lat_b1, lrc_lon_b1 = Mtk.somxy_to_latlon(path, lrc_somx_b1, lrc_somy_b1)  # order matters
	
	#~ create tuples from elements
	ulc_latlon_tuple_b1 = (ulc_lat_b1, ulc_lon_b1)	
	lrc_latlon_tuple_b1 = (lrc_lat_b1, lrc_lon_b1)
	print('-> problem could be here in lat-lon conversion...? no swap here')
	print('-> ulc latlon= %s, %s' % ulc_latlon_tuple_b1)
	print('-> lrc latlon= %s, %s' % lrc_latlon_tuple_b1)
	#~ now swap y elements 
	#~ this time it is for lat-lon so that the coords look correct
	print('-> note: we swap y elements of ulc and lrc lat-lon coords here')
	ulc_lat_b1, ulc_lon_b1, lrc_lat_b1, lrc_lon_b1 = ul_lr_y_coord_swap(ulc_latlon_tuple_b1, lrc_latlon_tuple_b1)


	# print("-> b1-tlc lat,lon= %s, %s" % (ulc_lat_b1, ulc_lon_b1))
	# print("-> b1-brc lat,lon= %s, %s" % (lrc_lat_b1, lrc_lon_b1))
	return ulc_lat_b1, ulc_lon_b1, lrc_lat_b1, lrc_lon_b1, offset_list, ulc_somx_b1, ulc_somy_b1, lrc_somx_b1, lrc_somy_b1	# final somy is swapped!

#-----------------------------------------------------------------------------------------------------------------------

def	ul_lr_y_coord_swap(ulc_tuple_b1, lrc_tuple_b1):

	print('-> corner-elements swap mode: "ul_lr_y_coord_swap"')
	#~ use top left corner or each block to define corners of block1
	#~ We swap them based on MISR docs, values are in SOM projection
	ulc_somx = ulc_tuple_b1[0] # somx
	ulc_somy = lrc_tuple_b1[1] # tl somy is swapped with brc somy
	
	lrc_somx = lrc_tuple_b1[0] # as lon
	lrc_somy = ulc_tuple_b1[1] # as lat

	print("-> ulc y-swapped= %s, %s " %(ulc_somx, ulc_somy))
	print("-> lrc y-swapped= %s, %s " %(lrc_somx, lrc_somy))
	# proj_param_res = proj_param_obj.resolution
	# print("-> resolution from projParam: %d" % proj_param_res)
	return ulc_somx, ulc_somy, lrc_somx, lrc_somy

#-----------------------------------------------------------------------------------------------------------------------

# #~ some future function
# if swap_lon == True:
# 	"we swap lon of tlc with brc"
# 	temp_lon = ulc_lon_b1
# 	ulc_lon_b1 = lrc_lon_b1
# 	lrc_lon_b1 = temp_lon

#-----------------------------------------------------------------------------------------------------------------------

	# if corner_swap_mode == 'tl_br_full_swap':
	# 	#~ use top left corner or each block to define corners of block1
	# 	#~ We swap them based on MISR docs, values are in SOM projection
	# 	ulc_somx_b1 = b1_br_corner[0] # somx as lon?
	# 	ulc_somy_b1 = b1_br_corner[1] # somy as lat?

	# 	lrc_somx_b1 = b1_tl_corner[0] # 
	# 	lrc_somy_b1 = b1_tl_corner[1] # 

	# 	print("-> img-tlc x,y= %s, %s m" %(ulc_somx_b1, ulc_somy_b1))
	# 	print("-> img-brc x,y= %s, %s m" %(lrc_somx_b1, lrc_somy_b1))

#-----------------------------------------------------------------------------------------------------------------------	

# #~ some future function
# if img_transfer_mode == 'bls2som2latlon':
# 	#~ convert block/line/sample --> SOM(xy)
# 	#~ Note: this section is NOT needed because images are in SOM projection already!
# 	resolution_meters = 275 # in meters
# 	tl_line = 0
# 	tl_sample = 0
# 	br_line = 511
# 	br_sample = 2047
# 	block = 1
# 	tl_somx, tl_somy = Mtk.bls_to_somxy(path, resolution_meters, block, tl_line, tl_sample)
# 	br_somx, br_somy = Mtk.bls_to_somxy(path, resolution_meters, block, br_line, br_sample)
# 	print('-> tlc-SOM x,y: %d, %d' % (tl_somx, tl_somy)) # order?
# 	print('-> brc-SOM x,y: %d, %d' % (br_somx, br_somy)) # order?
# 	#~ new implementation based on somx, somy
# 	ulc_lat_b1, ulc_lon_b1 = Mtk.somxy_to_latlon(path, tl_somx, tl_somy)  # order matters => to lat-lon of only ulc; goes inside loop
# 	lrc_lat_b1, lrc_lon_b1 = Mtk.somxy_to_latlon(path, br_somx, br_somy)  # order matters

#-----------------------------------------------------------------------------------------------------------------------	

def no_corner_swap(ulc_tuple_b1, lrc_tuple_b1):

	print('-> block-1 corner swap mode: "no_corner_swap"')
	#~ use top left corner for each block to define corners of block1
	ulc_somx_b1 = ulc_tuple_b1[0] # as lon
	ulc_somy_b1 = ulc_tuple_b1[1] # as lat 
	lrc_somx_b1 = lrc_tuple_b1[0] # as lon
	lrc_somy_b1 = lrc_tuple_b1[1] # as lat

	print("-> img-tlx= %s m, tly= %s m" %(ulc_somx_b1, ulc_somy_b1))
	print("-> img-brx= %s m, bry= %s m" %(lrc_somx_b1, lrc_somy_b1))
	# proj_param_res = proj_param_obj.resolution
	# print("-> resolution from projParam: %d" % proj_param_res)
	return ulc_somx_b1, ulc_somy_b1, lrc_somx_b1, lrc_somy_b1

#-----------------------------------------------------------------------------------------------------------------------

def setup_raster_resolution(ulc_lat_b1, ulc_lon_b1, lrc_lat_b1, lrc_lon_b1, ncols_img, nrows_img):
	"calculate resolution for each block"
	#~ define resolution of each roughness img in degrees, based on science docs
	cell_width_res = abs((lrc_lon_b1 - ulc_lon_b1) / float(ncols_img))
	cell_height_res = abs((lrc_lat_b1 - ulc_lat_b1) / float(nrows_img))
	print("-> x-res, y-res: %s, %s, degrees" % (cell_width_res, cell_height_res))
	return cell_width_res, cell_height_res

########################################################################################################################

if __name__ == '__main__':
	
	print('######################## PROGRAM STARTS ########################################')
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








