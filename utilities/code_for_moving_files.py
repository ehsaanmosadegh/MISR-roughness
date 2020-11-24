#!/usr/bin/python
'''
	written by: Ehsan 19 Nov 2020
	usage: make a list from available directories and moves files inside dir out to target dir == current dir (to the save level)

'''

import os, glob, shutil

src_dir_fullpath = '/Volumes/Ehsan7757420250/2016/april_2016/ATM_IceBridge_ILATM2_V002'
target_dir_fullpath = src_dir_fullpath


#~ define file pattern
# file_pattern = 'MISR_AM1_GRP_ELLIPSOID_GM_P*'+'.hdf'
file_pattern = 'ILATM2*.csv'

print('source dir: %s' % src_dir_fullpath)
print('target dir: %s' % target_dir_fullpath)
print('file pattern: %s' % file_pattern)

dir_content_list = os.listdir(src_dir_fullpath)  # make list of all contents in a dir
for idir in dir_content_list:
	found_dir = os.path.join(src_dir_fullpath, idir)
	if (os.path.isdir(found_dir)):
		print('found dir: %s' % found_dir)
		dir_files = glob.glob(os.path.join(found_dir, file_pattern))
		for ifile in dir_files:
			print('file found: %s' % ifile)
			print(os.path.isfile(ifile))
			shutil.move(ifile, target_dir_fullpath)
			if (os.path.isfile(os.path.join(target_dir_fullpath, ifile.split('/')[-1]))):
				print('file moved successfully!')
			else:
				print('warning on moving file')


