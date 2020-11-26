#!/usr/bin/python2.7

import MisrToolkit as Mtk 	# python2.7
import os, glob, cv2, gdal
import numpy as np
from PIL import Image



def arr2img_func(in_arr_2d, img_label, img_dir):

	from matplotlib import image as pltimg, pyplot as plt  #  pyplot uses the actual RGB values as they are, more accurate than PIL
	
	save_mode = True
	print('-> save mode: %s' % save_mode)
	img_format = ".jpg"
	plt.gray() # This will show the images in grayscale as default
	plt.figure(figsize=(20,20))  # set the figure size
	plt.imshow(in_arr_2d, cmap='gray', vmin=0 , vmax=in_arr_2d.max())
	# plt.show() # to show the img inline here
	if (save_mode==True):
		out_img = img_label + img_format
		out_img_fullpath = os.path.join(img_dir, out_img)
		print("-> saving output img as: %s" %out_img_fullpath)
		pltimg.imsave(out_img_fullpath, in_arr_2d)
		# plt.savefig(out_img)
		del plt
		return out_img_fullpath
	else:
		print('-> save mode is False, wo we onlu show ig here.')
		return 'onlyShowImg'





hdf_dir = '/Volumes/Ehsanm_DRI/research/MISR/hdf_files/ellipsoid_apr2013_day1to16_p1to233_b1to40/an_rad_images_test2'
hdf_file = "MISR_AM1_GRP_ELLIPSOID_GM_P174_O070759_AN_F03_0024.hdf"

hdf_file_fullpath = os.path.join(hdf_dir, hdf_file) # platform independent
print(os.path.isfile(hdf_file_fullpath))



hdf_obj = Mtk.MtkFile(hdf_file_fullpath)
# print(type(hdf_obj))
total_block_range = hdf_obj.block
print(total_block_range)



path = 174
misr_res_meter = 275


for block in range(total_block_range[0], total_block_range[1], 1):
	print('\nprocess block: %d' % block)


	my_block = Mtk.MtkRegion(path, block, block)
	rad_arr = hdf_obj.grid('RedBand').field('Red Radiance/RDQI').read(my_block).data()
	print(type(rad_arr))

	img_label = 'path_'+str(path)+'_b'+str(block)
	img_dir = hdf_dir
	inDS = arr2img_func(rad_arr, img_label, img_dir)


	raster_img_dir = hdf_dir
	raster_fname = 'img2raster_'+'b'+str(block)+'_translated.tif'
	raster_translated_fullpath = os.path.join(raster_img_dir, raster_fname)
	print(raster_translated_fullpath)



	print("-> transfer img frame -> latlon frame for path_num: %d, block_num: %s" %(path, block))
	#~ make 2 lists for img and geographic frames, then analyze long. to see if all are neg. or all are pos.; if all are the same then pass, else: change <-> to <+>
	pixel_rowcol_list = []  # (row, column)
	geographic_latlon_list = []


	for jrow in [0, 200, 400, 511]:
		for icol in [0, 300, 600, 1000, 1300, 1700, 2047]:

			#~ process each col of each row
	#             print("\n-> processing img coords: (%d, %d)" %(jrow, icol))

			#~ use MTK function to map from img frame to geographic frame
			pixel_latlon_tuple = Mtk.bls_to_latlon(path, misr_res_meter, block, jrow, icol) # struct=(lat, lon)?
			# print(pixel_latlon_tuple)  			# print every tuple of transfered latlon

			pixel_rowcol_list.append([jrow, icol])
			geographic_latlon_list.append(pixel_latlon_tuple)



			# print("-> total GCPs from img frame: %d" %len(pixel_rowcol_list))    
			# print(pixel_rowcol_list)
			# print(geographic_latlon_list)  # print to check all latlon list


			#~ check all elements of long. to have same sign, either +/-
			# all(iterable); iterable==list or anything that we can iterate on; Return True if all elements of the iterable are true
			if (any( [LatLon_tuple[1] < 0  for  LatLon_tuple in geographic_latlon_list] )):   # if any Lon in geographic_latlon_list is neg. we change that to pos.
				''' we enter this part if all or any pixels are on West hemisphere (have neg. long.) in img block, and we change them to pos. and the range will be [0, +360] '''

				print("-> note-1: found neg. lon. in geographic_latlon_list! will update neg. to pos. long.")

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
						# print("-> found neg. pixel long. in the crossing block: %f" % pixel_long)

						updated_lon_passed_AntiMerid = (360.0 + pixel_long )  # this long. is changed to pos. and will be in range [0, +360]
						# print("=================> update: neg.long. updated to: %f" %updated_lon_passed_AntiMerid)

						#~ update neg. long. to pos. long.
						gcp_list[index].GCPX = updated_lon_passed_AntiMerid

					else:  # here we collect some pos. long. among neg. long. in the case block is crossing A.M. line

						# print("-> found pos. long. among neg. longs. in the crossing block: %f" %geographic_latlon_list[index][1])

						#~ no need to update Lon. since it is pos. Lon.
						gcp_list[index].GCPX = geographic_latlon_list[index][1]



			else:
				print("-> note-2: all long. are on Eastern hemisphere (positive) in the img block!")

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




	translate_ds = gdal.Translate(
								raster_translated_fullpath,
								inDS,  
								format = 'GTiff',
								outputType = gdal.GDT_Float32, # maybe here chnage dtype to make it smaller img????
								GCPs = gcp_list
								) 

	print(os.path.isfile(raster_translated_fullpath))
	print(raster_translated_fullpath)

	#~ Properly close the datasets to flush to disk
	translate_ds = None
	inDS = None


	total_gcps = len(pixel_rowcol_list)

	img_tag = 'p'+str(path)+'_b'+str(block)
	warped_img = 'reprojected_warped_'+img_tag+'_'+str(total_gcps)+"GCPs"+".tif"
	outDS_warped = os.path.join(hdf_dir, warped_img)
	print('output tif: %s' % outDS_warped)


	from subprocess import call

	# print(os.path.isfile(out_translated_fullpath))
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
		-dstnodata 0 ' + raster_translated_fullpath + ' ' + outDS_warped  #  -tr 0.001 0.001\  this makes the final tif much larger cuz of very fine/large resolution
		


	#     print(cmd)

	#~ note: shell=true to execute the line as full command including arguments
	return_code = call(cmd, shell=True)  # subprocess.call() is better/safer that os.system() ==> finally used os.system() cos call returned error! correct return code? 
	print('cmd return code: %d \n\n' % return_code)     



