#!/usr/bin/python2.7

#~ by: Ehsan Mosadegh, 25 Sep 2020

'''
input: directory to raster.tif files
output: intermediate VRT file, and then final mosaic.tif file at the same directory

note: before running thsi script, we have to build raster.tif files forst
'''
import glob, os, gdal
from subprocess import call
import datetime as dt


def main():

	print('-> start main(): ')

	raster_dir_fullpath = '/Volumes/Ehsanm_DRI/research/MISR/roughness_files/from_PH/roughness_2013_apr1to16_p1to233_b1to40/roughness_subdir_2013_4_1/test_roughness_p75_180/rasters'
	#~ naming labels
	day_label = 'allDays' # use a day label to assign to output VRT and mosaic files
	output_VRT_dataset_name = 'virtualDataset_byte_'+day_label+'.vrt'
	output_mosaic_name = 'mosaic_fromVRT_byte_'+day_label+'.tif'

	########################################################################################################################
	VRT_fullpath = os.path.join(raster_dir_fullpath, output_VRT_dataset_name)

	print('-> raster dir: %s' %raster_dir_fullpath)
	print('-> VRT: %s' %VRT_fullpath)


	#~ we find this file pattern
	raster_file_pattern = 'raster_path_*'+'*_reprojToEPSG_3995.tif'
	print('-> looking for pattern: %s' % raster_file_pattern)

	#~ build a list from input raster files
	files_to_mosaic = glob.glob(os.path.join(raster_dir_fullpath, raster_file_pattern))
	print('-> files found: %d' % len(files_to_mosaic))
	
	########################################################################################################################
	#~ method 1- gdal_merge.py cmdLine
	#~ problems: slow cuz of beiing cmdLine + a long string of inoput files into memory

	# files_string = " ".join(files_to_mosaic)
	# command = "gdal_merge.py -o " + VRT_fullpath + " -v -of GTiff -ot Float64 " + files_string
	# ret = call(command, shell=True)
	# print(ret)

	########################################################################################################################
	#~ mwthod 2- VRT and gdal_translate
	print('-> building VRT dataset!')
	# vrt_options = gdal.BuildVRTOptions(resampleAlg='linear') #, addAlpha=True)
	my_vrt_ptr = gdal.BuildVRT(
								VRT_fullpath, 
								files_to_mosaic
							) 					#, options=vrt_options)
	
	print('-> closing VRT dataset!')
	my_vrt_ptr = None 


	########################################################################################################################
	# gdal_translate -of GTiff -co "COMPRESS=JPEG" -co "PHOTOMETRIC=YCBCR" -co "TILED=YES" virtualDS_paths_41_139_233_Float64.vrt mosaic.tif

	#~ name of mosaic
	out_mosaic_fullpath = os.path.join(raster_dir_fullpath, output_mosaic_name)


	#~ define Translate Options --> we don't need to create a TranslateOptions object, we only need do define anything as an keyword_argument for the .Translate()
	#~ writes translated output to a .tif file and returns a gdal.Dataset object; after writing it, mosaic_ds will be empty --> how do it VRT???
	print('-> building mosaic from VRT dataset!')
	mosaic_ds = gdal.Translate( 								# verbose?
									out_mosaic_fullpath,
									VRT_fullpath,
									format = 'GTiff',
									outputType = gdal.GDT_Byte 	# note: inout dtype is float_64==double, maybe here change dtype to make it smaller img????
								) 

	print('-> output mosaic: ')
	print(out_mosaic_fullpath)

	#~ Properly close the datasets to flush to disk
	print('-> closing mosaic dataset!')
	mosaic_ds = None
	VRT_fullpath = None  # close opened input file

	return 0


########################################################################################################################
if __name__ == '__main__':
	
	start_time = dt.datetime.now()
	print('-> start time: %s' %start_time)
	print(" ")

	main()
	
	end_time = dt.datetime.now()
	print('\n-> end time= %s' %end_time)
	print('-> runtime duration= %s' %(end_time-start_time))
	print(" ")
	print('######################## MOSAIC COMPLETED SUCCESSFULLY ########################')
########################################################################################################################

