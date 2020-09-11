#!/usr/bin/env python
########################################################################################################################
'''
author: Ehsna Mosadegh (emosadegh@nevada.unr.edu)

version history: 2 Nov 2019

about:
	reads each hdf (img) file, transforms TOA-rad to TOA-refl, extract data for each block from each hdf file, and write out data to each block.
	each hdf file includes nominally 180 blocks in a file.

how to use:
	update path to storage to point to where ellipsoid.hdf files are


data required:
	inputs: dhf Ellipsoid files
	outputs: toa_file_fullpath???

to do: 
	- padd block num with 3 digs?
	- writes data to 3 differenct dorrectories for each camera??

notes: 
	user should create a directory called "input_dir_name" and put all hdf files there.
	user provides labling tags for "output_dir_name" and this code makes it here.
	this code and the next code needs img data from 3 cameras/hdf_files, so input shoud include at least those 3 files.

debugging:
	-
'''
########################################################################################################################

import glob, os, subprocess
import datetime as dt

########################################################################################################################
#~ directory path setting (>>> set by USER <<<)

#===== input directory #=====

#~ input_storage_path: is where we stored hdf data for each project in sub-directories under this directories. subdirectories can be data for each month. hdf radiance files reflectance (GRP_ELLIPSOID) files, where we downloaded files
input_storage_path = '/Volumes/Ehsanm_DRI/research/MISR/hdf_files'	# path to home dir that hdf files are stored in sub-directories

#~ input dir == dir label with hdf files and w/ specific label for each directory
input_dir_name = 'ellipsoid_apr2013_day1to16_p1to233_b1to40' # will use later to label output dir


#===== output directory #=====
#~ based on the application can be "toa_refl" OR "toa_rad". 

output_storage_path = '/Volumes/Ehsanm_DRI/research/MISR/toa_block_files' 	# path to processing home
output_filelabel = "toa_refl" 	# toa_rad OR toa_refl; change setting inside C-code; 0==false/off &  1==true/on
# save_not_to_cloud = '.nosync'		

output_dir_name = output_filelabel+'_'+input_dir_name #+save_not_to_cloud 		# label of output subdirectory to name output dir; output processed files go here. code with create this directory oif it does not exist

#~ directory path setting (>>> set by USER <<<)
########################################################################################################################








		###############################################################################
		###																			###
		###																			###
		###		 		do not change anything below this line						###
		###																			###
		###																			###
		###############################################################################








#~ other settings - do not change

exe_name = 'TOARad2blocks'
block_range = [1,40] # [start, stop]; should match with block range in downloading step
band_list = ['Red']
band_num = 2
minnaert = 0	# correction, turns off minnert parameter, f=0 it will not run inside C-code

#~ other settings - do not change
########################################################################################################################

def main():
	'''
	passes a pair of argumenst to cmd to run TOA.c program
	'''
	hdf_files_fullpath_list, total_hdf_files, output_dir_fullpath, band_num = in_n_out_dir_setup(input_storage_path, input_dir_name, output_storage_path, output_dir_name, band_list, minnaert)	# order of arg params: root_dir, input_dir, output_dir_name, band_list
	
	for hdf_counter, hdf_file_fullpath in enumerate(hdf_files_fullpath_list):
		path, orbit, camera = parse_file_names(hdf_file_fullpath, total_hdf_files, hdf_counter)
		if (camera != 'an') and (camera != 'cf') and (camera != 'ca'):
			print("-> but camera is not one of 3, we continue to the next hdf file...")
			continue

		for block_num in range(block_range[0], block_range[1]+1, 1): # why loop over 42 blocks in one hdf file
			toa_file_fullpath = define_toa_file(path, orbit, block_num, camera, output_dir_fullpath, output_filelabel)
			#~ use a function to check if toa-file available on disc? if not, pass it to run_from_cmd()
			if (check_file_availability(toa_file_fullpath)):
				continue; # to next iteration == inside for loop

			# ~ now run TOA from UNIX to process hdf ellipsoid data 
			# print("-> returned False from past step. Go to cmd...")
			run_from_cmd(exe_name, hdf_file_fullpath, block_num, band_num, minnaert, toa_file_fullpath)  # note: to just check runtime setting comment out this line

	return 0

########################################################################################################################

def check_file_availability(infile):

	if (os.path.isfile(infile)):
		print("-> EXIST: DOES exist on disc.: %s" % infile)
		return True
	else:
		print("-> EXIST: NOT exist on disc.")
		return False

########################################################################################################################

def define_toa_file(path, orbit, block_num, camera, output_dir_name, file_label):

	block_num = str(block_num).rjust(3, '0') # added 3 to right-adjust for 3-zero digits for all range of blocks
	print('\n-> processing block: (%s) (w/ rjust performed) \n' %block_num)


	# toa output file names to CMD command --> to do: make function for this section
	toa_file_pattern = (file_label+'_%s_%s_B%s_%s.dat' %(path, orbit, block_num, camera)) # will be written by TOA
		
	if (camera == 'an'):
		toa_file_fullpath = os.path.join(output_dir_name, 'An', toa_file_pattern)
		print('-> toa file will be= %s' % (toa_file_fullpath))

	if (camera == 'ca'):
		toa_file_fullpath = os.path.join(output_dir_name, 'Ca', toa_file_pattern)
		print('-> toa file will be= %s' % (toa_file_fullpath))

	if (camera == 'cf'):
		toa_file_fullpath = os.path.join(output_dir_name, 'Cf', toa_file_pattern)
		print('-> toa file will be= %s' % (toa_file_fullpath))

	return toa_file_fullpath

########################################################################################################################

def run_from_cmd(exe_name, hdf_file_fullpath, block_num, band_num, minnaert, toa_file_fullpath):
	
	# toa_image_file = '%stoa_%s_%s_b%s_%s.png' % (output_dir_name, path, orbit, block_num, camera)  #~ note: this is removed from the original C code, so we do not need image anymore
	# print(toa_image_file)

	#~ run the C-cmd program
	#cmd = 'TOA3 "%s" %s %s %s \"%s\" \"%s\"' %(hdf_file_fullpath, block_num, band_num, minnaert, toa_file_fullpath, toa_image_file) # old version
	print(" ")
	print('-> python= program-name	Ellipsoid-file	block 	band 	minnaert	toa-file')
	cmd = (' "%s" "%s" %s %s %s \"%s\"' %(exe_name, hdf_file_fullpath, block_num, band_num, minnaert, toa_file_fullpath))  # TOA writes data into toa_file_fullpath
	print('-> to cmd= %s \n' % (cmd))	# run the cmd command.

	# return_value_of_cmd = 0 # for debug 

	# run the cmd command
	return_value_of_cmd = subprocess.call(cmd, shell=True)
	# print('-> return value= %s' %return_value_of_cmd)

	print("\n******************************************\n") # this line represents a signal from python that shows we go to next iteration inside python without any cmd ERROR

	if (return_value_of_cmd != 0):
		print('-> ERROR: EITHER %s program path NOT set in path, or issue from C-code. *** Exiting' %exe_name)
		raise SystemExit() 

########################################################################################################################

def in_n_out_dir_setup(storage_path, input_dir, output_storage_path, output_dir_name, band_list, minnaert):
	'''
	reads dir paths and check if they exist, lists all hdf ellipsoid files and returns a list of files in fullpath mode
	'''

	input_dir_fullpath = os.path.join(storage_path, input_dir)
	output_dir_fullpath = os.path.join(output_storage_path, output_dir_name)
	print('-> input dir : %s' % (input_dir_fullpath))
	print('-> output dir: %s' % (output_dir_fullpath))
	# check if directories exist
	if not (os.path.isdir(input_dir_fullpath)): # needs fullpath
		print('-> input/download directory NOT exist! check the input path')
		raise SystemExit()

	if not (os.path.isdir(output_dir_fullpath)):
		print('-> output directory NOT exist!')
		print('-> so we try to create the output dir now ...\n')

		os.mkdir(output_dir_fullpath)
		if not (os.path.isdir(output_dir_fullpath)):
			print('-> we could not create outpur dir. You should create it manually.')
			raise SystemExit()
		else:
			print('-> output dir created successfully!\n')

	#~ we create 3 dir for 3 cameras
	camera_list = ['Ca', 'An', 'Cf']
	for cam in camera_list:
		cam_dir = os.path.join(output_dir_fullpath, cam)
		if (not os.path.isdir(cam_dir)):
			os.mkdir(cam_dir)	 # note mkdir() doen't return anything!
			if (not os.path.isdir(cam_dir)):
				print("-> we could not create cam_dir")
				raise SystemExit()
			else:
				print('-> Successfully created cam dir for: %s' % cam)
		else:
			print('-> %s dir exist!' % cam)


	# checking some constants
	for band in band_list:
		if (band == 'Red'):
			nband = band_num  # red band=3
		else:
			print('-> WARNING: band is NOT set correctly, we only work woth RED band.\n')
	print('-> band= %s' %nband)
	print('-> minnaert= %d' % minnaert)

	# we need Ellipsoid radiance files
	misr_file_patern = 'MISR_AM1_GRP_ELLIPSOID_GM*.hdf' # for ELLIPSOID data - check file names t

	# get a list of available/downloaded Ellipsoid files, the list will be list of file_fullpath-s 
	hdf_files_fullpath_list = glob.glob(os.path.join(input_dir_fullpath, misr_file_patern))
	total_hdf_files = len(hdf_files_fullpath_list)

	print('-> number of "GRP_ELLIPSOID".HDF files that will be processed= %s \n' % total_hdf_files)

	return hdf_files_fullpath_list, total_hdf_files, output_dir_fullpath, nband

########################################################################################################################

def parse_file_names(hdf_file_fullpath, total_hdf_files, hdf_counter):
	print('===========================================================================================================')
	print('=========================> NOW PROCESSING ELLIPSOID RADIATION HDF FILE: (%d/%d) <==========================' % (hdf_counter+1, total_hdf_files)) 
	print('===========================================================================================================\n')
	print('-> hdf file: %s \n' %hdf_file_fullpath)

	# get the index of path and the path number
	path_index = hdf_file_fullpath.index('_P')
	path = hdf_file_fullpath[ path_index+1 : path_index+5 ]


	# get the index of orbit and the orbit number
	orbit_index = hdf_file_fullpath.index('_O')
	orbit = hdf_file_fullpath[ orbit_index+1 : orbit_index+8]

	# find the camera in the file name

	#~ three needed cameras
	if hdf_file_fullpath.find('_CF') != -1 :
		camera = 'cf'
	elif hdf_file_fullpath.find('_CA') != -1 :
		camera = 'ca'
	elif hdf_file_fullpath.find('_AN') != -1 :
		camera = 'an'

	#~ other cameras, but we don't need them
	elif hdf_file_fullpath.find('_AF') != -1 :
		camera = 'af'
	elif hdf_file_fullpath.find('_BF') != -1 :
		camera = 'bf'
	elif hdf_file_fullpath.find('_AA') != -1 :
		camera = 'aa'
	elif hdf_file_fullpath.find('_BA') != -1 :
		camera = 'ba'
	elif hdf_file_fullpath.find('_DF') != -1 :
		camera = 'df'
	elif hdf_file_fullpath.find('_DA') != -1 :
		camera = 'da'

	else:
		print('-> ERROR: needed camera NOT found! Check input hdf for camera label. Exiting...')
		raise SystemExit()

	print('-> camera is= %s' %camera)

	return path, orbit, camera

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
# we don't use it anymore, we need to ahve the full path to the files
# cwd = os.getcwd()
# print('-> we are at run-script dir= %s' %cwd)
# os.chdir( download_dir )
# cwd = os.getcwd()
# print('-> chaged directory to download dir= %s' %cwd)
########################################################################################################################
