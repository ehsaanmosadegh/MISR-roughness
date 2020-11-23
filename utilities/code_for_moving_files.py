#!/usr/bin/python3

#~ written by: Ehsan 19 Nov 2020
#~ goal: move MISR ELLIPOSID files from subdirectories to target directory

import os, glob, shutil

src_dir_fullpath='/Volumes/Ehsan7757420250/april_2016/sample_ellipsoid_files'
target_dir_fullpath='/Volumes/Ehsan7757420250/april_2016/sample_ellipsoid_files'

print('source dir: %s' % src_dir_fullpath)
print('target dir: %s' % target_dir_fullpath)

dir_content_list = os.listdir(src_dir_fullpath)  # make list of all contents in a dir
for idir in dir_content_list:
	found_dir = os.path.join(src_dir_fullpath, idir)
	if (os.path.isdir(found_dir)):
		print('found dir: %s' % found_dir)
		file_pattern = 'MISR_AM1_GRP_ELLIPSOID_GM_P*'+'.hdf'
		dir_files = glob.glob(os.path.join(found_dir, file_pattern))
		for ifile in dir_files:
			print('file found: %s' % ifile)
			print(os.path.isfile(ifile))
			shutil.move(ifile, target_dir_fullpath)
			if (os.path.isfile(os.path.join(target_dir_fullpath, ifile.split('/')[-1]))):
				print('file moved successfully!')
			else:
				print('warning on moving file')


