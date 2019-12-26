#!/usr/bin/python3
###############################################################################
# run_TOA.py
# author: Ehsna Mosadegh (emosadegh@nevada.unr.edu)
# version history: 2 Nov 2019
# usage:
# receives each hdf (imagery?) file and allocates the data to each(?) block. each hdf file includes 180 blocks in a file.
# data required:
#	inputs: dhf Ellipsoid files
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
# directory path setting - by USER

# path of root dir that inclides all prcessing directories
root_dir = '/home/mare/Ehsan_lab/misr_proceesing_dir'
# update following 3 directories
MISR_download_dir_name = 'misr_dl_July_2016/test1'
#root_dir = '/home/mare/Ehsan_lab/misr_proceesing_dir'  # path to hdf radiance files reflectance (GRP_ELLIPSOID) files, where we downloaded files
output_dir_name = 'toa_radiance_July_2016/test1'	# path to toa dir 
#root_dir = '/home/mare/Ehsan_lab/misr_proceesing_dir' # output of TOA run

# directory path setting - by USER
###############################################################################
# other settings - do not change

exe_name = 'TOARad2blocks'
block_range = [1,43] # [start, stop]; should match with block range in downloading step
band_list = ['Red']
band_num = 3
# minnert = is set inside the program

# other settings - do not change
###############################################################################

def main():
	'''
	passes a pair of argumenst to cmd to run TOA.c program
	'''
	list_of_misr_files_fullpath, output_dir, band_no, minnaert = dir_n_file_setting(root_dir, MISR_download_dir_name, root_dir, output_dir_name, band_list)
	
	for each_ellipsoid_file in list_of_misr_files_fullpath:

		path, orbit, camera = parse_file_names(each_ellipsoid_file)

		for each_block in range(block_range[0], block_range[1], 1): # why loop over 42 blocks in one hdf file

			toa_file_fullpath = define_toa_rad_files(path, orbit, each_block, camera, output_dir)

			# now run TOA from linux to process Ellipsoid data
			#run_from_cmd(exe_name, each_ellipsoid_file, each_block, band_no, minnaert, toa_file_fullpath)

	return 0

###############################################################################

def define_toa_rad_files(path, orbit, each_block, camera, output_dir):

	if (each_block <= 9):
		#print('-> block was: %s' %each_block)
		each_block = str(each_block).rjust(2, '0')
		print('-> rjust performed, block is: %s' %each_block)
	# else:
	# 	pass

	# toa output file names to CMD command --> to do: make function for this section
	toa_file_pattern = ('toa_rad_%s_%s_B%s_%s.dat' %(path, orbit, each_block, camera)) # will be written by TOA
	toa_file_fullpath = os.path.join(output_dir, toa_file_pattern)
	print('-> %s writes toa radiance data to file= %s' % (exe_name, toa_file_fullpath))

	return toa_file_fullpath

###############################################################################

def run_from_cmd(exe_name, each_ellipsoid_file, each_block, band_no, minnaert, toa_file_fullpath):

	# this is removed from the original C code, so we do not need image anymore
	# toa_image_file = '%stoa_%s_%s_b%s_%s.png' % (output_dir, path, orbit, each_block, camera)
	# print(toa_image_file)

	# run the C-cmd program
	#cmd = 'TOA3 "%s" %s %s %s \"%s\" \"%s\"' %(each_ellipsoid_file, each_block, band_no, minnaert, toa_file_fullpath, toa_image_file) # old version
	print('-> program-name	radiance-file-name	block 	band 	minnaert	path-to-toa-dataFile')
	cmd = (' "%s" "%s" %s %s %s \"%s\"' %(exe_name, each_ellipsoid_file, each_block, band_no, minnaert, toa_file_fullpath))  # TOA writes data into toa_file_fullpath
	print('-> runScript to %s= %s' %(exe_name, cmd))	# run the cmd command.

	# if os.system(cmd) != 0 :
	# run the cmd command
	return_value_of_cmd = subprocess.call(cmd, shell=True)
	#print('-> return value= %s' %return_value_of_cmd)

	if (return_value_of_cmd != 0):
		print('-> ERROR: %s.exe NOT found in path. Exiting...' %exe_name)
		raise SystemExit() 

###############################################################################

def dir_n_file_setting(input_dir_path, input_dir_name, root_dir, output_dir_name, band_list):
	'''
	reads dir paths and check if they exist, lists all ellipsoid files and returns a list of files w/ fullpath
	'''

	download_dir = os.path.join(root_dir, MISR_download_dir_name)
	output_dir = os.path.join(root_dir, output_dir_name)
	print('-> input dir : %s' % (download_dir))
	print('-> output dir: %s' % (output_dir))
	# check if directories exist
	if not (os.path.isdir(download_dir)):
		print('-> download directory NOT exist! check the path')
		raise SystemExit()

	if not (os.path.isdir(output_dir)):
		print('-> output directory NOT exist!')
		print('-> we try to create the output dir')
		os.mkdir(output_dir)
		if not (os.path.isdir(output_dir)):
			print('-> we could not create outpur dir. You should create it manually.')
			raise SystemExit()
		else:
			print('-> output dir created successfully!')

	# checking some constants
	for band in band_list:
		if (band == 'Red'):
			band_no = band_num  # red band=3
		else:
			print('-> WARNING: band is NOT set correctly, we only work woth RED band.')
	print('-> band= %s' %band_no)

	# correction
	minnaert = 0

	# we need Ellipsoid radiance files
	misr_file_patern = 'MISR_AM1_GRP_ELLIPSOID_GM*.hdf' # for ELLIPSOID data - check file names 

	# get a list of available/downloaded Ellipsoid files, the list will be list of file_fullpath-s 
	list_of_misr_files_fullpath = glob.glob(os.path.join(download_dir, misr_file_patern))
	print('-> no. of "GRP_ELLIPSOID" files found= %s' %len(list_of_misr_files_fullpath))

	return list_of_misr_files_fullpath, output_dir, band_no, minnaert

###############################################################################

def parse_file_names(each_ellipsoid_file):

	print('-> Ellipsoid rad file= %s' %each_ellipsoid_file)

	# get the index of path and the path number
	path_index = each_ellipsoid_file.index('_P')
	path = each_ellipsoid_file[ path_index+1 : path_index+5 ]


	# get the index of orbit and the orbit number
	orbit_index = each_ellipsoid_file.index('_O')
	orbit = each_ellipsoid_file[ orbit_index+1 : orbit_index+8]

	# find the camera in the file name
	if each_ellipsoid_file.find('_CF') != -1 :
		camera = 'cf'
	elif each_ellipsoid_file.find('_CA') != -1 :
		camera = 'ca'
	elif each_ellipsoid_file.find('_AN') != -1 :
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
