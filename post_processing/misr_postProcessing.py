"""
comments/notes:
-------------------------------------------------------------------------------------
author: Ehsan Mosadegh (emosadegh@nevada.unr.edu & ehsanm@dri.edu)
date: Jan 5, 2020

purpose: 
to geo-reference MISR roughness data

how to use: 
You have to have Mtk and GDAL libraries installed with the same version (e.g 2.7) and set in PATH on your machine. 
run this script with Python2.7 if you have compiled Mtk Python wrapper and GDAL with version 2.7. 

to-do:



"""
##############################################################################################

import numpy as np
import os, glob

import gdal, ogr, os, osr 		# for gdal library

import MisrToolkit as Mtk
from MisrToolkit import *
##############################################################################################

misr_dir = "/Volumes/MISR_REPO/misr_roughness_data/test_p180/"
misr_file = "MISR_AM1_GRP_ELLIPSOID_GM_P180_O088147_AN_F03_0024.hdf"
misr_file_fulPath = misr_dir+misr_file
# roughness_dir="/Users/ehsanmos/Downloads/misr_files/"
roughness_dir = "/Volumes/MISR_REPO/misr_roughness_data/mostRecent_with_roughness_labels/"
# roughness_file = "roughness_P180_O088147_B001.dat"
# roughness_file="roughness_P180_O088147_B002.dat"
# roughness_file_fullPath = roughness_dir + roughness_file





#rough_file_open = open(roughness_file)


# for i in range(900):
# 	print i, input_rough_file[i] #, type(input_rough_file[i])


# roughness_list = input_rough_file[1048576:2097152] # 1048576*2 = 2097152

# ave_3_cam_list = []
# count = 0
# x = 0
# for i in range(len(input_rough_file)):
# 	print(i)
# 	while count < 3:
# 		x += input_rough_file[i]
# 		count+1

# 	mean_3_cam = x/3
# 	print(mean_3_cam)
# 	ave_3_cam_list.append(mean_3_cam)
# 	count = 0



# print("misr hdf file:" , misr_file_fulPath)


# get lat lon from ELLIPSOID data raster_fullPath/swath, 
# use MisrToolkit library
# block_corner_obj = Mtk.MtkBlockCorners(misr_file_fulPath)
# print(block_corner_obj)


# m = Mtk.MtkFile(misr_file_fulPath)
# proj_param_obj = Mtk.MtkProjParam(misr_file_fulPath)
# proj_parameters = proj_param_obj.projparam
# proj_param_res = proj_param_obj.resolution
# print("-> projection params are: %d" % len(proj_parameters))
# print("-> resolution from projParam: %d" % proj_param_res)

# grid_obj = Mtk.MtkGrid(misr_file_fulPath) 
# grid_res = grid_obj.resolution
# print("-> grid resolution: %d" % grid_res)


# for i in proj_parameters:
# 	print("\t %s" % i)


# print("proj code:" , proj_param_obj.projcode)
# upper_left_corner = proj_param_obj.ulc  							# order should be: (lon,lat) == (X,Y) ==> CHECK the order
# print("===> from hdf file: upper-left corners (lon,lat):" , upper_left_corner)





paths = [180, 196, 212, 228]
grid_res = 275

for path in paths:

	# get a list of available roughness files
	roughness_file_patern = 'roughness_P'+str(path)+'*.dat' 					# for ELLIPSOID data - check file names 
	print("============================================")
	print("-> looking for pattern: %s" , roughness_file_patern)

	# get a list of available/downloaded Ellipsoid files, the list will be list of file_fullpath-s 
	list_of_misr_files_fullpath = glob.glob(os.path.join(roughness_dir, roughness_file_patern))

	for block_num in range(len(list_of_misr_files_fullpath)):

		roughness_file = list_of_misr_files_fullpath[block_num]
		print("\n-> roughness file num: (%d) @ %s" % (block_num, roughness_file))

		# lon_lat_list = path_block_range_to_block_corners(path, block_num+1, block_num+1)

		# print(lon_lat_list.ulc)
		# som_block_coord_corners = bls_to_somxy(path, grid_res, block_num+1, 1, 1)
		# print("-> corners:")
		# print(som_block_coord_corners)


		# block_crnr = block_corner_obj.block
		# print("block conners:" , block_crnr[1])


		input_rough_file = np.fromfile(roughness_file, dtype='float64') 	# is this roughness in cm?
		print("-> roughness file elements:" , input_rough_file.size)
		print("-> roughness file dim:" , input_rough_file.ndim)



		# for i in range(900):
		# 	print i, input_rough_file[i] #, type(input_rough_file[i])


		roughness_list = 	input_rough_file[0:1048576]
		lat_list = 			input_rough_file[1048576:2097152]
		lon_list = 			input_rough_file[2097152:3145728]


		 					# 512*2048 = 1048576
		roughness_array = roughness_list.reshape((512,2048))
		lat_array = lat_list.reshape((512,2048))
		lon_array = lon_list.reshape((512,2048))

		print("-> shape of roughness array:" , np.shape(roughness_array))
		print("-> shape of lat array:" , np.shape(lat_array))
		print("-> shape of lon array:" , np.shape(lon_array))
		print(lat_array[0,0])
		print(lon_array[0,0])


		num_of_bands = 1
		datatype = gdal.GDT_Float32
		epsg_code =     4326 #	#3031			# output map projection == coord-ref-sys; code for SOM?


		# define output raster
		raster_name = roughness_file.split("/")[-1]+".tif"
		raster_dir = "/Volumes/MISR_REPO/tif_files/with_lat_lon_"+str(epsg_code)+"/"
		raster_fullPath = raster_dir + raster_name
		print("-> raster name: %s" % (raster_name))
		print("-> raster fullPath: %s" % (raster_fullPath))


		#raster_origin = ( top_left_lon , top_left_lat ) # unit? metere or degree? it can be either meter, or degrees --> ImportFromProj4(+units=m)
		block_topLeft_lon = lon_array[0,0] #som_block_coord_corners[0] 	# top-left X ? from ELLIPSOID data, start of each raster_fullPath?
		block_topLeft_lat = lat_array[0,0] #som_block_coord_corners[1]		# top-left Y ?	where is the origin?

		rough_pixel_width = 275 	# meters; roughness dataset resolution of each pixel; 
		rough_pixel_height = 275 	# meters;

		nrows_rough_arr, ncols_rough_arr = np.shape(roughness_array) 	# get dim of 2D roughness array
		geotransform = (block_topLeft_lon , rough_pixel_width , 0 , block_topLeft_lat , 0 , rough_pixel_height) # units meter or degrees --> (top-left-X,...,top-left-Y)

		coord_ref_sys = osr.SpatialReference() 					# initialize class of coordinate reference system
		coord_ref_sys.ImportFromEPSG(epsg_code) 				# we define/set projection parameters for our array that we want to transfor to a raster; ellipsoid is this: WGS84; 

		coord_ref_sys.ImportFromProj4("6378137.0, -0.006694348, 0.0, 98018013.752, 127045037.92824034, 0.0, 0.0, 0.0, 98.88, 0.0, 0.0, 180.0, 0.0, 0.0, 0.0")
		# coord_ref_sys.ImportFromProj4( '+proj=som +lat_0=40.000  +lon_0=-120.806  +lat_1=40.450  +lat_2=36.450  +units=m , +datum=WGS84 +no_defs' )
		# coord_ref_sys.ImportFromProj4('+proj=som , +units=m , +datum=WGS84 +no_defs')


		driver = gdal.GetDriverByName('GTiff') 										# Initialize driver
		out_raster = driver.Create(raster_fullPath, ncols_rough_arr, nrows_rough_arr, num_of_bands , datatype )	 	# create output raster/matrix dataseet to put data into it (raster_fullPath, ncols_rough_arr, nrows_rough_arr, bands, dtype-> GDAL data type arg)
		out_raster.SetGeoTransform(geotransform)  				# Specify raster coordinates
		out_raster.SetProjection(coord_ref_sys.ExportToWkt()) 	# Exports the coordinate system to the file; #

		print("-> writing the raster ...")
		out_raster.GetRasterBand(num_of_bands).WriteArray(roughness_array)  # write my array to the raster
		
		out_raster.FlushCache()

		out_raster = None 		# Once we're done, close the dataset properly
		print("-> DONE!")

		del out_raster













# # # if (case == "warp"):

# # # 	raster_name = roughness_file+".tif"
# # # 	raster_dir = "/Users/ehsanmos/Documents/MISR/MISR-roughness/post_processing/"
# # # 	raster_fullPath = raster_dir + raster_name
# # # 	# to re-project into new projection
# # # 	gdal.Warp(raster_fullPath, roughness_array, dstSRS='EPSG:3031')




# # # if (case=='cookbook'):

# # # 		rasterOrigin = (-123.25745,45.43013) == (lon,lat) == (X,Y)
# # # 		originX = rasterOrigin[0]
# # #     	originY = rasterOrigin[1]
# # #     newRasterfn = 'test_misr.tif'
# # #     ncols_rough_arr = array.shape[1]
# # #     nrows_rough_arr = array.shape[0]
# # #     rough_pixel_width = 10 	# ?
# # #     rough_pixel_height = 10	# ?

# # #     driver = gdal.GetDriverByName('GTiff')													# define driver=
# # #     outRaster = driver.Create(newRasterfn, ncols_rough_arr, nrows_rough_arr, 1, gdal.GDT_Byte)
# # #     outRaster.SetGeoTransform((originX, rough_pixel_width, 0, originY, 0, rough_pixel_height))
# # #     outband = outRaster.GetRasterBand(1)
# # #     outband.WriteArray(array)
# # #     outRasterSRS = osr.SpatialReference() 	#
# # #     outRasterSRS.ImportFromEPSG(4326) 		#
# # #     outRaster.SetProjection(outRasterSRS.ExportToWkt())
# # #     outband.FlushCache()

# # # if (case='gis'):
# # # 	pass









