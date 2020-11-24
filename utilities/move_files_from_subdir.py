#!/usr/bin/python
'''
	written by: Ehsan 19 Nov 2020
	usage: make a list from available directories and moves files inside dir out to target dir == current dir (to the save level)

'''

import os, glob, shutil

src_dir_fullpath = '/data/gpfs/assoc/misr_roughness/2016/july_2016'
target_dir_fullpath = '/data/gpfs/assoc/misr_roughness/2016/all_ellipsoid_july'


#~ define file pattern
file_pattern = 'MISR_AM1_GRP_ELLIPSOID_GM_P*'+'.hdf'
# file_pattern = 'ILATM2*.csv'


print('source dir: %s' % src_dir_fullpath)
print('target dir: %s' % target_dir_fullpath)
print('file pattern: %s' % file_pattern)

dir_content_list = os.listdir(src_dir_fullpath)  # make list of all contents in a dir
print('subdirs found in src dir: %s' % len(dir_content_list))
for idir in dir_content_list:
	src_dir = os.path.join(src_dir_fullpath, idir)
	if (os.path.isdir(src_dir)):  
		print('src dir: %s' % src_dir)
		src_files_fullpath_list = glob.glob(os.path.join(src_dir, file_pattern))
		if (len(src_files_fullpath_list)==0):
			print('src dir empty!')
			continue
		else:
			for src_file_fp in src_files_fullpath_list:
				print('src found: %s' % src_file_fp)
				# print(os.path.isfile(src_file_fp))
				#~ check if src file has moved before and exists in distination dir
				if (os.path.isfile(os.path.join(target_dir_fullpath, src_file_fp.split('/')[-1]))==True):
					continue
				#~ move files from src dir to target dir
				shutil.move(src_file_fp, target_dir_fullpath)
				#~ check if file was moved successfully
				if (os.path.isfile(os.path.join(target_dir_fullpath, src_file_fp.split('/')[-1]))):
					print('file moved successfully!')
				else:
					print('warning on moving file')


