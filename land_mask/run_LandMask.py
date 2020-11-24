#!/usr/bin/env python
'''
by: Ehsan Mosadegh 20 August 2020
this script runs LandMask.c 
old:Should make directory for input and output based on the labels of files from orevious step
setup input and output dir path, and output dir will be created inside it
'''
from subprocess import call
import os
import datetime as dt
from platform import python_version

########################################################################################################################
#~ input dir- <toa_refl> data should be in 3 different directories in here
input_dir_fullpath = '/Volumes/Ehsan7757420250/april_2016/sample_ellipsoid_files_april2016/toa_refl_april2016_day1to16_p1to233_b1to46' ;  # //  "/home3/mare/Nolin/2016/Surface3/Jul/";
#~ landmask dir
lsmask_dir_fullpath = '/Volumes/Ehsan7757420250/landseamask_blocks_1to46' ;  	# Ehsan: mask file, output from <ArcticTileToGrid.c> // at: /Volumes/easystore/from_home/Nolin_except_dataFolder/SeaIce/LWData/MISR_LandSeaMask on easystore drive

#~ output dir for masked_toa_refl file
output_path = input_dir_fullpath  # we will create output dir inside input dir

########################################################################################################################
exe_name = "LandMask" # should be set in $PATH

def main():
	#~ check if input dir exists
	print("-> input dir: %s" % input_dir_fullpath)
	if (not os.path.isdir(input_dir_fullpath)):
		print("-> ERROR: input dir NOT exist: %s" % input_dir_fullpath)
		raise SystemExit()


	#~ 1st we make output dir 
	output_dir = "masked_" + input_dir_fullpath.split('/')[-1]
	output_dir_fullpath = os.path.join(output_path, output_dir)	# output dir; dat and png files; go to 3 different directories	//"/home3/mare/Nolin/2016/Surface3_LandMasked/Jul/"; 
	if (not os.path.isdir(output_dir_fullpath)):
		print("-> Warning: output dir NOT exist, we will make it.")
		os.mkdir(output_dir_fullpath) 		# doesnt return anything
		if (not os.path.isdir(output_dir_fullpath)):
			print("-> ERROR: we could NOT make output dir.")
			raise SystemExit()
		else:
			print("-> output dir: %s" % output_dir_fullpath)

	lsmask_files_fullpath = os.path.join(lsmask_dir_fullpath, 'lsmask_pP_bB.dat');
	print('-> landMask dir: %s' % lsmask_files_fullpath)

	#~ now, we make 3 dirs for 3 cameras
	camera_list = ['Ca', 'An', 'Cf']
	for cam in camera_list:
		cam_dir = os.path.join(output_dir_fullpath, cam)
		if (os.path.isdir(cam_dir)==False):
			os.mkdir(cam_dir)	 # note mkdir() doen't return anything!
			if (not os.path.isdir(cam_dir)):
				print("-> we could not create cam_dir")
				raise SystemExit()
			else:
				print('-> Successfully created cam dir for: %s' % cam)
		else:
			print('-> %s dir exist!' % cam)


	cmd = ('"%s" "%s" "%s" "%s"' % (exe_name, input_dir_fullpath, lsmask_files_fullpath, output_dir_fullpath) )  # cmd = should be a string
	# print(cmd)
	call(cmd, shell=True)

	return 0;

########################################################################################################################

if __name__ == '__main__':
	
	start_time = dt.datetime.now()
	print('-> start time: %s' %start_time)
	print('-> python version: %s' % python_version())
	print(" ")
	main()
	end_time = dt.datetime.now()
	print('-> end time= %s' %end_time)
	print('-> runtime duration= %s' %(end_time-start_time))
	print(" ")
	print('######################## TOA COMPLETED SUCCESSFULLY ########################')

########################################################################################################################









