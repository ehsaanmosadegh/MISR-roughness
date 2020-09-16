#!/usr/bin/env python

# Generate ASCM cloudmask from MISR MIL2TCCL.
# The MISR ASCM was upsampled from 128 x 512 to 512 x 2048.
# created 18 Aug 2020 by Ehsan Mosadegh
# original name: readASCMFile.py


import sys, os, os.path 

# idir = "/home/mare/Nolin/2012/MIL2TCCL/MarJun"
# nodir = "/home/mare/Nolin/2012/MIL2TCCL/JunJul/ASCM"
# odir = "/home/mare/Nolin/2012/MIL2TCCL/MarJun/ASCM_w17.6km_10%"
# idir = "/Volumes/easystore/from_home/Nolin_except_dataFolder/remainder_forExternalHD_3.1TB/2013/MIL2TCSP/Apr"
# idir = "/Volumes/Ehsanm_DRI/research/MISR/cloud_mask/cloudmask_apr2013_day1to16_p1to233/"

# set the input path
idir = '/Volumes/Ehsanm_DRI/research/MISR/cloud_mask/cloudmask_apr2013_day1to16_p1to233/TC_CLASSIFIERS_F07' # test for only 1 path
# set a label for output dir
out_dir_label = 'cloudmask_F07_HC4_only' # we build this dir inside our input dir



################################## DO NOT CHANGE ##################################

exe_name = "ReadASCMCloudMask"
end_block_not_included = 41  # reads up to this number

out_dir_fullpath = os.path.join(idir, out_dir_label)
print("-> out dir full path: %s" % out_dir_fullpath)

if (not os.path.isdir(out_dir_fullpath)):
	print('-> output directory NOT exist. We make it.')
	# raise SystemExit()
	cmd = "mkdir " + out_dir_fullpath
	sys.stderr.write('%s\n' % cmd)
	if os.system(cmd) != 0:
		sys.exit(1)

# if not os.path.exists(odir):
# 	cmd = "mkdir \"" + odir + "\""
# 	sys.stderr.write('%s\n' % cmd)
# 	if os.system(cmd) != 0:
# 		sys.exit(1)


n = 0
files_list = [file for file in os.listdir(idir) if (os.path.splitext(file)[1] == '.hdf')]

for file_count, file in enumerate(files_list):

	print("\n-> file (%d/%d): %s \n" % (file_count+1, len(files_list), file))
	path = file.split('_')[4]
	orbit = file.split('_')[5]
	# cmdir = odir + '/cloudmask_' + orbit + '_' + path
	# cmd = 'mkdir \"' + cmdir + '\"'
	# if not os.path.exists(cmdir):
	# 		sys.stderr.write('%s\n' % cmd)
	# 		if os.system(cmd) != 0:
	# 			sys.exit(1)

	f = open(idir + '/' + file, 'rb') # open each hdf file
	# items = file.split('_') # ? # based on old file name pattern
	# print("items: %s" % items[0])

	ifile = idir + '/' + file # define hdf file
	# for block in range(int(items[1][1:4]), int(items[1][5:8]) + 1):  # 
	for block in range(1, end_block_not_included, 1):  # define range for blocks

		ofile = out_dir_fullpath + '/' + 'cloudmask_' + path + '_' + orbit + '_B%03d.msk' % block		
		cmd = "./%s \"%s\" %d \"%s\"" % (exe_name, ifile, block, ofile)
		sys.stderr.write('%5d: %s\n' % (n + 1, cmd)) # why n+1 ?
		if (os.system(cmd) != 0):
			sys.exit(1)
		n += 1
	f.close() # close each hdf file
	#break;
