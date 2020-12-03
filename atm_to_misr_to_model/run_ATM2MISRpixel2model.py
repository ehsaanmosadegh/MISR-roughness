#!/usr/bin/python
'''
by: Ehsan Mosadegh 26 November 2020

this script runs LandMask.c 

'''
from subprocess import call
import os
import datetime as dt
from platform import python_version

########################################################################################################################
#~~ setup paths

atm_dir = "/Volumes/Ehsan7757420250/2016/april_2016/ATM_IceBridge_ILATM2_V002" ;
masked_toa_refl_home = "/Volumes/Ehsan7757420250/2016/april_2016/sample_ellipsoid_april2016/toa_refl_april2016_day1to16_p1to233_b1to46/masked_toa_refl_april2016_day1to16_p1to233_b1to46" ; # path to home dir that includes 3 subdirectories
cloud_masked_dir = "/Volumes/Ehsan7757420250/2016/TC_CLASSIFIERS_F07/cloudmask_TC_CLASSIFIERS_F07_HC4_only" ;

out_atmmodel_dir = "/Volumes/Ehsan7757420250/2016/april_2016/atmmodel/" ;
atmmodel_csvfile_label = "atmmodel_april_2016.csv"

exe_dir = "/Users/ehsanmos/Documents/MISR/MISR-roughness/exe_dir"
exe_name = "ATM2MISRpixel2model"
########################################################################################################################
def main():
	'''
	passes a pair of argumenst to cmd to run TOA.c program
	'''
	input_dir_list = [atm_dir, masked_toa_refl_home, cloud_masked_dir, out_atmmodel_dir, exe_dir]
	for in_dir in input_dir_list:
		ret_check = os.path.isdir(in_dir)
		if (ret_check==True):
			print('dir exists: %s' % in_dir)
		else:
			print('dir NOT found: %s' % in_dir)
			raise SystemExit()

	exe_fullpath = os.path.join(exe_dir, exe_name)
	out_atmmodel_fullpath = os.path.join(out_atmmodel_dir, atmmodel_csvfile_label)

	#~~ now run exe from UNIX to process hdf ellipsoid data 
	run_from_cmd(exe_fullpath, atm_dir, masked_toa_refl_home, cloud_masked_dir, out_atmmodel_fullpath)

	return 0
########################################################################################################################
def run_from_cmd(exe_fp, atm, maskedTOA, cm, atmmodel):
	#~~ run the C-cmd program
	print(" ");
	print('-> python: "Usage: <exe-name> <ATM-dir> <maskedTOA-dir> <cloudMask-dir> <atmmodelCSV-file>')
	cmd = (' %s %s %s %s %s' %(exe_fp, atm, maskedTOA, cm, atmmodel));
	print('-> to cmd= %s \n' %cmd)	# run the cmd command.
	#~~ run the cmd command
	return_value_of_cmd = call(cmd, shell=True);
	#~~ print('-> return value= %s' %return_value_of_cmd)
	print("\n******************************************\n")	# this line represents a signal from python that shows we go to next iteration inside python without any cmd ERROR
	if (return_value_of_cmd != 0):
		print('-> ERROR: either %s program path NOT set in path, or issue from C-code. *** Exiting' %exe_fp)
		raise SystemExit();
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
	print('######################## ATM-to-MISR COMPLETED SUCCESSFULLY ########################')
########################################################################################################################


