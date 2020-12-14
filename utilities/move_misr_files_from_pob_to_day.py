#!/usr/bin/python2.7

# import numpy as np
import os, glob
# import gdal, osr # python2.7
import MisrToolkit as Mtk # python2.7
from MisrToolkit import * # 
# from subprocess import call
# import datetime as dt
# from matplotlib import pyplot as plt 
import shutil

'''
this code makes directoriesd for a single day of MISR files and moves files belonging to each dat to its folder
1st, set the number of days that you have data available for.
we use python2.7 + MTK library to do this task. MTK lib will find associated day/time from orbit data on file labels

'''

##~ setup roughness dir, files in this dir can be files that are dowbloaded from PH parallel dir, or are on PH now
main_roughness_dir_fullpath = '/data/gpfs/assoc/misr_roughness/2016/july_2016/roughness_2016_july1to16_p1to233_b1to46'

##~ setup year and month of roughness files
year = 2016
month = 7	# april=4, july=7
num_of_days = 16  # this is the upper limit of processing 

##~ setup ...
process_mode_num = 0 
process_mode_list = ['roughness_files', 'GRP_ELLIPSOID_GM']
process_mode = process_mode_list[process_mode_num]

########################################################################################################################
##~ proicessing section - do not change

if (process_mode == 'roughness_files'):
	#~ loop through all 16 days and move files for each day to its roughness subdir
	for iday in range(num_of_days):

		day = iday+1
		print('\n-> processing day= %d \n' %day)
		start_time = str(year)+'-'+str(month)+'-'+str(day)+'T00:00:00Z'
		end_time = str(year)+'-'+str(month)+'-'+str(day)+'T23:59:59Z'
		print(start_time)
		print(end_time)

		orbit_list = Mtk.time_range_to_orbit_list(start_time, end_time)
		print(orbit_list)
		print('\n-> found %d orbits!' %len(orbit_list))

		rough_subdir_name = 'roughness_subdir_'+str(year)+'_'+str(month)+'_'+str(day)
		print(rough_subdir_name)

		rough_subdir_fullpath = os.path.join(main_roughness_dir_fullpath, rough_subdir_name)
		print(rough_subdir_fullpath)

		#~ check if directory for specific day exists, else we create the directory
		if (not (os.path.isdir(rough_subdir_fullpath))):
			print('-> roughness subdir does NOT exist! We make that directory.')
			os.mkdir(rough_subdir_fullpath)
			print(rough_subdir_fullpath)
			print(os.path.isdir(rough_subdir_fullpath))
		else:
			print('-> roughness subdir exists!')
			print(rough_subdir_fullpath)
			print(os.path.isdir(rough_subdir_fullpath))



		## make list of all available roughness file patterns for specific day
		for orbit in orbit_list:
			print('-> processing orbit= %d' %orbit)
			#~ file pattern that we will use 
			file_pattern = 'roughness_toa_refl_P*'+'*_O0'+str(orbit)+'*'+'.dat'
			print('-> looking for pattern= %s' %file_pattern)
			#~ search for file pattern and make a list
			roughness_files_found_list = glob.glob(os.path.join(main_roughness_dir_fullpath, file_pattern))
			print('-> roughness files found: %s' % len(roughness_files_found_list))
		#     print(roughness_files_found_list)

			for rough_file_day in roughness_files_found_list:
				print('-> moving data to subdir for: %s ' %rough_file_day)
				new_path = shutil.move(rough_file_day, rough_subdir_fullpath)

##----------------------------------------------------------------------------------------------------------------------

if (process_mode == 'GRP_ELLIPSOID_GM'):
	#~ loop through all 16 days and move files for each day to its roughness subdir
	for iday in range(num_of_days):

		day = iday+1
		print('\n-> processing day= %d \n' %day)
		start_time = str(year)+'-'+str(month)+'-'+str(day)+'T00:00:00Z'
		end_time = str(year)+'-'+str(month)+'-'+str(day)+'T23:59:59Z'
		print(start_time)
		print(end_time)

		orbit_list = Mtk.time_range_to_orbit_list(start_time, end_time)
		print(orbit_list)
		print('\n-> found %d orbits!' %len(orbit_list))

		rough_subdir_name = 'roughness_subdir_'+str(year)+'_'+str(month)+'_'+str(day)
		print(rough_subdir_name)

		rough_subdir_fullpath = os.path.join(main_roughness_dir_fullpath, rough_subdir_name)
		print(rough_subdir_fullpath)

		#~ check if directory for specific day exists, else we create the directory
		if (not (os.path.isdir(rough_subdir_fullpath))):
			print('-> roughness subdir does NOT exist! We make that directory.')
			os.mkdir(rough_subdir_fullpath)
			print(rough_subdir_fullpath)
			print(os.path.isdir(rough_subdir_fullpath))
		else:
			print('-> roughness subdir exists!')
			print(rough_subdir_fullpath)
			print(os.path.isdir(rough_subdir_fullpath))



		## make list of all available roughness file patterns for specific day
		for orbit in orbit_list:
			print('-> processing orbit= %d' %orbit)
			#~ file pattern that we will use to move files 
			# file_pattern = 'roughness_toa_refl_P*'+'*_O0'+str(orbit)+'*'+'.dat'
			print('-> looking for pattern= %s' %file_pattern)
			#~ search for file pattern and make a list
			roughness_files_found_list = glob.glob(os.path.join(main_roughness_dir_fullpath, file_pattern))
			print('-> roughness files found: %s' % len(roughness_files_found_list))
		#     print(roughness_files_found_list)

			for rough_file_day in roughness_files_found_list:
				print('-> moving data to subdir for: %s ' %rough_file_day)
				new_path = shutil.move(rough_file_day, rough_subdir_fullpath)

