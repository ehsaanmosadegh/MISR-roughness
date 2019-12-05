#!/usr/bin/python3

# by: Ehsna Mosadegh (emosadegh@nevada.unr.edu)
# 24 Dec 2019
# usage: 
# to-do: 

import sys, os, os.path, signal

def sigintHandler(a, b):
	sys.exit(0)

if __name__ == '__main__':
	signal.signal(signal.SIGINT, sigintHandler)
	

	# Q- do we need to seperate output for each camera?
	dir1 = '../Surface/Cf/'
	dir2 = '../Surface/Ca/'
	
##########################################################

	study_domain_pob_list = [] # a list of desired toa_p-o-b --> ???????????????????????????? what is this list? where is it coming from? how can I make it for each project?  
	#f = open('../Lists/toa_path_orbit_block.txt', 'r')
	#	f= domain_pob_file
	domain_pob_file = open('/media/WD1TB (ntfs)/Nolin/2007/Lists/toa_path_orbit_block.txt', 'r') # this list has a list of desired (path-orbit-block)
	
	for line in domain_pob_file:

		fields = line.strip().split()
		path = int(fields[0])
		orbit = int(fields[1])
		block = int(fields[2])
		study_domain_pob_list.append((path, orbit, block))

	domain_pob_file.close()

##########################################################

	#geo_param_dir = '../GeometricParameters/'
	geo_param_dir = '/media/WD1TB (ntfs)/Nolin/2007/GeometricParameters/'
	geometric_param_files_list = sorted(os.listdir(geo_param_dir))
	
	#dirs = ['../TOA/Cf/', '../TOA/Ca/']
	dirs = ['/media/WD1TB (ntfs)/Nolin/2007/TOA/Cf/', '/media/WD1TB (ntfs)/Nolin/2007/TOA/Ca/'] # toa files here
	

	some_cte = 0

	for each_toa_dir in dirs: # dir of toa files
		files = sorted(os.listdir(d))


############################################	main algorithm		############################################

########### parse function toa.dat files

		# pick each toa file and parse p,o,b
		for toa_file in files: # f= loop for each toa file
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
				if camera == 'cf' or camera == 'ca':

########################################################################################################################

					for domain_pob in study_domain_pob_list:  # l=?????; study_domain_pob_list, Q- for specific region??? does study_domain_pob_list define our study domain? how to obtain POB for the a study region?

						# now cross-check p/o/b with the list/ if toa_pob matches with the domain:
						if (domain_pob[0] == toa_path and domain_pob[1] == toa_orbit and domain_pob[2] == toa_block):

							toa_file_fullpath = os.path.join(each_toa_dir, toa_file) # if toa file in the list is availabe in the dir, then pich the toa.dat -> fname1 = toa.dat

							# do we have to seperte surf_file_fullpath and surf_img_fullpath for each camera? do they get similar? -> camera diferenciates them
							if camera == 'cf':
								surf_file_fullpath = '%ssurf_p%03d_o%06d_b%03d_%s.dat' % (dir1, toa_path, toa_orbit, toa_block, camera) # dir1 and dir2 = output dir for surface reflectance
								surf_img_fullpath = '%ssurf_p%03d_o%06d_b%03d_%s.png' % (dir1, toa_path, toa_orbit, toa_block, camera)	# if camera is cf, it goes to dir1

							if camera == 'ca':
								surf_file_fullpath = '%ssurf_p%03d_o%06d_b%03d_%s.dat' % (dir2, toa_path, toa_orbit, toa_block, camera)
								surf_img_fullpath = '%ssurf_p%03d_o%06d_b%03d_%s.png' % (dir2, toa_path, toa_orbit, toa_block, camera)


							fname4 = 'MISR_AM1_GP_GMP_P%03d_O%06d_F03_0013' % (toa_path, toa_orbit)
							found = False

########################################################################################################################

							for each_GP_file in geometric_param_files_list:

								if each_GP_file.startswith(fname4) and each_GP_file.endswith('.hdf'):
									found = True
									#cmd = 'Surf %s %s %s %s' % (toa_file_fullpath, os.path.join(geo_param_dir, g), surf_file_fullpath, surf_img_fullpath)

									# from C code: SurfSeaIce_exe, toa_data_file, GP_GMP_file_fullpath, band, output_data_file, output_image_file
									GP_GMP_file_fullpath = os.path.join(geo_param_dir, each_GP_file)

									cmd = 'SurfSeaIce \"%s\" \"%s\" %s %s' % (toa_file_fullpath, GP_GMP_file_fullpath, nband=missing , surf_file_fullpath, surf_img_fullpath) # band=? before surf_file_fullpath; bandshould be 2 similar to run_TOA.py


####################################################################################   ???????????????
									if some_cte >= 0:
										sys.stderr.write('%5d: %s\n' % (some_cte + 1, cmd))
										if os.system(cmd) != 0:
											sys.exit(1)
									some_cte += 1
									#if n >= 10:
									#	sys.exit(1)
									break
							if found:
								break

	sys.exit(0)

	# 	fprintf(stderr, "Usage: SurfSeaIce_exe, toa_data_file, GP_GMP_file_fullpath, band, output_data_file, output_image_file\n");
	#	l= study_domain_pob_list
	#	d= each_toa_dir
	#	f= toa_file
	#	path= toa_path
	# 	orbit = toa_orbit
	#	block= toa_block
	# 	g= each_GP_file
	#	n= some_cte
	
