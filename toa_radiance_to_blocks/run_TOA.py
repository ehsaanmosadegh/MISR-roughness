#!/usr/bin/python3
###############################################################################
# run_TOA.py
# author: Ehsna Mosadegh (emosadegh@nevada.unr.edu)
# version history: 2 Nov 2019
# usage:
# receives each hdf (imagery?) file and allocates the data to each(?) block. each hdf file includes 180 blocks in a file.
# data required:
#	inputs: dhf files
#	outputs: toa_file_fullpath
# to do: 
# - add period labels to dir name tags
# - 
# notes: 
#   - 
# debugging:
#	-
###############################################################################

import glob, os, subprocess
import datetime as dt

###############################################################################
# directory path setting
# update following 3 directories
MISR_download_dir_name = 'misr_dl_July_2016'
MISR_download_dir_path = '/home/mare/Ehsan_lab/misr_proceesing_dir'  # path to hdf radiance files reflectance (GRP_ELLIPSOID) files, where we downloaded files
output_dir_path = 'toa_dir_July_2016'	# path to toa dir 
output_dir_name = '/home/mare/Ehsan_lab/misr_proceesing_dir' # output of TOA run

###############################################################################

def main():
	'''
	passes a pair of argumenst to cmd to run TOA.c program
	'''
	list_of_misr_files_fullpath, output_dir, band_no, minnaert = local_file_setting(input_dir_path, input_dir_name, output_dir_path, output_dir_name)
	for each_hdf_file in list_of_misr_files_fullpath:
		path, orbit, camera = file_name_parser(each_hdf_file)

		for each_block in range(1,43) : # why loop over 42 blocks in one hdf file

			# toa output file names to CMD command
			toa_file_fullpath = ('%stoa_%s_%s_b%s_%s.dat' %(output_dir, path, orbit, each_block, camera)) # will be written by TOA
			print('-> TOA writes hdf data to file= %s' %toa_file_fullpath)

			# this is removed from the original C code, so we do not need image anymore
			# toa_image_file = '%stoa_%s_%s_b%s_%s.png' % (output_dir, path, orbit, each_block, camera)
			# print(toa_image_file)

			# run the C-cmd program
			#cmd = 'TOA3 "%s" %s %s %s \"%s\" \"%s\"' %(each_hdf_file, each_block, band_no, minnaert, toa_file_fullpath, toa_image_file) # old version
			print('-> program-name	radiance-file-name	block 	band 	minnaert	path-to-toa-dataFile')
			cmd = (' "TOA" "%s" %s %s %s \"%s\"' %(each_hdf_file, each_block, band_no, minnaert, toa_file_fullpath))  # TOA writes data into toa_file_fullpath
			print('-> runScript to TOA= %s' %cmd)

			# if os.system(cmd) != 0 :
			# run the cmd command
			return_value_of_cmd = subprocess.call(cmd, shell=True)
			print('-> return value= %s' %return_value_of_cmd)

			if (return_value_of_cmd != 0):
				print('-> ERROR: TOA exe NOT found in path. Exiting...')
				raise SystemExit()
	return 0

###############################################################################

def local_file_setting(input_dir_path, input_dir_name, output_dir_path, output_dir_name):
	'''
	reads dir paths and check if they exist, lists all ellipsoid files and returns a list of files w/ fullpath
	'''

	download_dir = os.path.join(MISR_download_dir_path, MISR_download_dir_name)
	output_dir = os.path.join(output_dir_path, output_dir_name)

	# check if directories exist
	if not (os.path.isdir(download_dir)):
		print('-> download directory NOT exist!')
		raise SystemExit()

	if not (os.path.isdir(output_dir)):
		print('-> output directory NOT exist!')
		raise SystemExit()

	# some constants
	bands = ['Red'] # why only red?
	for band in bands :
		if (band == 'Red') :
			band_no = 2  # what is band_no?
		else:
			print('-> WARNING: band is NOT set correctly.')
	print('-> band= %s' %band_no)

	# correction
	minnaert = 0

	# we need Ellipsoid radiance files
	misr_file_patern = 'MISR_AM1_GRP_ELLIPSOID_GM*.hdf' # for ELLIPSOID data - check file names 

	# get a list of available/downloaded Ellipsoid files, the list will be list of file_fullpath-s 
	list_of_misr_files_fullpath = glob.glob(os.path.join(download_dir, misr_file_patern))
	print('-> no. of hdf files found= %s' %len(list_of_misr_files_fullpath))

	return list_of_misr_files_fullpath, output_dir, band_no, minnaert

###############################################################################

def file_name_parser(each_hdf_file):

	print('-> hdf file is= %s' %each_hdf_file)

	# get the index of path and the path number
	path_index = each_hdf_file.index('_P')
	path = each_hdf_file[ path_index+1 : path_index+5 ]


	# get the index of orbit and the orbit number
	orbit_index = each_hdf_file.index('_O')
	orbit = each_hdf_file[ orbit_index+1 : orbit_index+8]

	# find the camera in the file name
	if each_hdf_file.find('_CF') != -1 :
		camera = 'cf'
	elif each_hdf_file.find('_CA') != -1 :
		camera = 'ca'
	elif each_hdf_file.find('_AN') != -1 :
		camera = 'an'
	else:
		print('-> ERROR: camera NOT found!')
		raise SystemExit()

	print('-> camera is= %s' %camera)

	return path, orbit, camera

###############################################################################

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

###############################################################################
# we don't use it anymore, we need to ahve the full path to the files
# cwd = os.getcwd()
# print('-> we are at run-script dir= %s' %cwd)
# os.chdir( download_dir )
# cwd = os.getcwd()
# print('-> chaged directory to download dir= %s' %cwd)
#######################################################################
