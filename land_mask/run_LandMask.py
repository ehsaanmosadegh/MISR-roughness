#!/usr/bin/env python
'''
by: Ehsan Mosadegh 20 August 2020
this script runs LandMask.c 
Should make directory for input and output based on the labels of files from orevious step
'''
from subprocess import call
import os


exe_name = "LandMask" # is set in $PATH

#~ input dir
input_dir = "toa_refl_ellipsoid_apr2013_day1to16_p1to233_b1to40"
input_path = "/Volumes/Ehsanm_DRI/research/MISR/toa_block_files/"	# toa_refl data should be in 3 different directories in here	//  "/home3/mare/Nolin/2016/Surface3/Jul/";

lsmask_files_fullpath = "/Users/ehsanmos/Documents/RnD/MISR_lab/misr_processing_dir/LandSeaMask.nosync/lsmask_pP_bB.dat" ;  	# Ehsan: mask file, output from <ArcticTileToGrid.c> // at: /Volumes/easystore/from_home/Nolin_except_dataFolder/SeaIce/LWData/MISR_LandSeaMask on easystore drive

output_path = "/Volumes/Ehsanm_DRI/research/MISR/masked_toa_files/"




input_dir_fullpath = os.path.join(input_path, input_dir)
print("-> input dir: %s" % input_dir_fullpath)
if (not os.path.isdir(input_dir_fullpath)):
	print("-> ERROR: input dir NOT exist: %s" % input_dir_fullpath)
	raise SystemExit()



#~ 1st we make output dir 
output_dir = "masked_" + input_dir
output_dir_fullpath = os.path.join(output_path, output_dir)	# output dir; dat and png files; go to 3 different directories	//"/home3/mare/Nolin/2016/Surface3_LandMasked/Jul/"; 
if (not os.path.isdir(output_dir_fullpath)):
	print("-> Warning: output dir NOT exist, we will make it.")
	os.mkdir(output_dir_fullpath) 		# doesnt return anything
	if (not os.path.isdir(output_dir_fullpath)):
		print("-> ERROR: we could NOT make output dir.")
		raise SystemExit()
	else:
		print("-> output dir: %s" % output_dir_fullpath)


#~ then, we make 3 dir for 3 cameras
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




cmd = ('"%s" "%s" "%s" "%s"' % (exe_name, input_dir_fullpath, lsmask_files_fullpath, output_dir_fullpath) )  # cmd = should be a string
# print(cmd)

call(cmd, shell=True)












