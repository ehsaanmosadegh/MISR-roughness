#!/usr/bin/python3
###############################################################################
# run_SurfSeaIce.py
# author: Ehsna Mosadegh (emosadegh@nevada.unr.edu)
# version history: 2 Dec 2019
# usage:
#
# data required:
#	inputs: 
#	outputs: 
# to do: 
# - 
# - 
# notes: 
#   - 
# debugging:
#	-
###############################################################################

import os

###############################################################################
# directory path setting

toa_dir_name = 'toa_dir_July_2016'
toa_dir_path = '/home/mare/Ehsan_lab/misr_proceesing_dir' 	# path to toa dir 
surf_dir_name =
surf_dir_path = 

study_domain_pob_file = 'some_list.txt'
study_domain_pob_path = 

nband
exe_name

############################################################################### toa_file

def main():
	# create a list of POB from the POB list
	study_domain_pob_list = domain_POB_list_maker(study_domain_pob_path, study_domain_pob_file):
	# make a list of all available toa files
	toa_file_list = toa_list_maker(toa_dir_path, toa_dir_name)
	# pick each toa file and parse P,O,B
	for toa_file in toa_file_list:
		#
		toa_path, toa_orbit, toa_block, camera = toa_file_parser(toa_file)
		#
		toa_file_fullpath = POB_domain_checker(study_domain_pob_list, toa_path, toa_orbit, toa_block, toa_file)
		# 
		surf_file_fullpath, surf_img_fullpath = surf_files(surf_dir_path, surf_dir_name, toa_path, toa_orbit, toa_block, camera)
		# find a GP file for each P,O that comes from from toa file
		GP_GMP_file_fullpath = GP_finder(toa_path, toa_orbit, geometric_param_fullpath_list)
		# run the C code
		cmd_runner(exe_name, toa_file, GP_GMP_file_fullpath, nband, surf_file_fullpath, surf_img_fullpath)

	return 0

###############################################################################

def toa_list_maker(toa_dir_path, toa_dir_name):
	'''
	looks at the toa dir and make a list of the available files from there
	'''
	toa_dir = os.path.join(toa_dir_path, toa_dir_name)
	toa_file_list = sorted(os.listdir(toa_dir))

	return toa_file_list

###############################################################################

def toa_file_parser(toa_file):

	# extract p,o,b
	if toa_file.endswith('.dat'):  
		i = toa_file.index('_p')
		toa_path = int(toa_file[i + 2: i + 5])

		i = toa_file.index('_o')
		toa_orbit = int(toa_file[i + 2: i + 8]) 

		i = toa_file.index('_b')
		toa_block = int(toa_file[i + 2: i + 5])

		camera = '??'
		if toa_file.find('_cf') > -1:
			camera = 'cf'
		elif toa_file.find('_ca') > -1:
			camera = 'ca'

	return toa_path, toa_orbit, toa_block, camera

###############################################################################

def POB_domain_checker(study_domain_pob_list, toa_path, toa_orbit, toa_block, toa_file):
'''
we compare each toa_file with all domain_pob and if toa file is in the domain, we output toa_file_fullpath as the processing file for C code
'''
	for domain_pob in study_domain_pob_list:  # l=?????; study_domain_pob_list, Q- for specific region??? does study_domain_pob_list define our study domain? how to obtain POB for the a study region?
		# now cross-check p/o/b with the list/ if toa_pob matches with the domain:
		if (domain_pob[0] == toa_path and domain_pob[1] == toa_orbit and domain_pob[2] == toa_block):

			toa_file_fullpath = os.path.join(each_toa_dir, toa_file) # if toa file in the list is availabe in the dir, then pich the toa.dat -> fname1 = toa.dat

			return toa_file_fullpath
		else:
			print('-> domain POB file did NOT match with toa file')


###############################################################################

def domain_POB_list_maker(study_domain_pob_path, study_domain_pob_file):
	'''
	creates a list of POB from the POB list
	'''
	study_domain_pob_list = [] # a list of desired toa_p-o-b --> ???????????????????????????? what is this list? where is it coming from? how can I make it for each project?  
	#f = open('../Lists/toa_path_orbit_block.txt', 'r')
	#	f= domain_pob_file
	domain_pob_file = with open(os.path.join(study_domain_pob_path, study_domain_pob_file), 'r') # this list has a list of desired (path-orbit-block)
	
		for line in domain_pob_file:

			fields = line.strip().split()
			domain_path = int(fields[0])
			domain_orbit = int(fields[1])
			domain_block = int(fields[2])
			study_domain_pob_list.append((domain_path, domain_orbit, domain_block))

	return study_domain_pob_list

###############################################################################

def surf_files(surf_dir_path, surf_dir_name, toa_path, toa_orbit, toa_block, camera):

	output_dir = os.path.join(surf_dir_path, surf_dir_name)
	surf_file_fullpath = ('%ssurf_p%03d_o%06d_b%03d_%s.dat' % (output_dir, toa_path, toa_orbit, toa_block, camera)) # dir1 and dir2 = output dir for surface reflectance
	surf_img_fullpath = ('%ssurf_p%03d_o%06d_b%03d_%s.png' % (output_dir, toa_path, toa_orbit, toa_block, camera))	# if camera is cf, it goes to dir1

	return surf_file_fullpath, surf_img_fullpath

###############################################################################

def GP_finder(toa_path, toa_orbit, geometric_param_fullpath_list):
	'''
	looks for a geometric parameter file that matches the path-orbit 
	'''
	GP_file_pattern = ('MISR_AM1_GP_GMP_P%03d_O%06d_F03_0013' %(toa_path, toa_orbit))
	# found = False
	for each_GP_file in geometric_param_fullpath_list:

		# if thats the file we are looking for:
		if each_GP_file.startswith(GP_file_pattern) and each_GP_file.endswith('.hdf'):
			# found = True
			GP_GMP_file_fullpath = os.path.join(geo_param_dir, each_GP_file)
		else:
			print('-> geometric parametr file NOT found!')

###############################################################################

def cmd_runner(exe_name, toa_file, GP_GMP_file_fullpath, nband, surf_file_fullpath, surf_img_fullpath):

	cmd = ('%s \"%s\" \"%s\" %s %s' %(exe_name, toa_file, GP_GMP_file_fullpath, nband, surf_file_fullpath, surf_img_fullpath)) # band=? before surf_file_fullpath; bandshould be 2 similar to run_TOA.py
	# run the cmd command
	return_value_of_cmd = subprocess.call(cmd, shell=True)
	print('-> return value= %s' %return_value_of_cmd)

	if (return_value_of_cmd != 0):
		print('-> ERROR: TOA exe NOT found in path. Exiting...')
		raise SystemExit()


###############################################################################

if __name__ == '__main__':

	main()