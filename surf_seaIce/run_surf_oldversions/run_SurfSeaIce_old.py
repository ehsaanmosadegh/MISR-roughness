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
	
	dir1 = '../Surface/Cf/'
	dir2 = '../Surface/Ca/'
	
	l = [] # a list of desired toa_p-o-b 
	#f = open('../Lists/toa_path_orbit_block.txt', 'r')
	f = open('/media/WD1TB (ntfs)/Nolin/2007/Lists/toa_path_orbit_block.txt', 'r')
	for line in f:
		fields = line.strip().split()
		path = int(fields[0])
		orbit = int(fields[1])
		block = int(fields[2])
		l.append((path, orbit, block))
	f.close()
	
	#gdir = '../GeometricParameters/'
	gdir = '/media/WD1TB (ntfs)/Nolin/2007/GeometricParameters/'
	geops = sorted(os.listdir(gdir))
	
	#dirs = ['../TOA/Cf/', '../TOA/Ca/']
	dirs = ['/media/WD1TB (ntfs)/Nolin/2007/TOA/Cf/', '/media/WD1TB (ntfs)/Nolin/2007/TOA/Ca/'] # toa files here
	n = 0
	for d in dirs: # dir of toa files
		files = sorted(os.listdir(d))


		# pick each toa file and parse p,o,b
		for f in files: # f= toa file
			# extract p,o,b
			if f.endswith('.dat'):
				i = f.index('_p')
				path = int(f[i + 2: i + 5])
				i = f.index('_o')
				orbit = int(f[i + 2: i + 8])
				i = f.index('_b')
				block = int(f[i + 2: i + 5])
				camera = '??'
				if f.find('_cf') > -1:
					camera = 'cf'
				elif f.find('_ca') > -1:
					camera = 'ca'
				if camera == 'cf' or camera == 'ca':


					for e in l:
						# now cross check p,o.b with the list
						if e[0] == path and e[1] == orbit and e[2] == block:
							fname1 = os.path.join(d, f) # if toa file in the list is availabe in the dir, then fname1

							if camera == 'cf':
								fname2 = '%ssurf_p%03d_o%06d_b%03d_%s.dat' % (dir1, path, orbit, block, camera)
								fname3 = '%ssurf_p%03d_o%06d_b%03d_%s.png' % (dir1, path, orbit, block, camera)

							if camera == 'ca':
								fname2 = '%ssurf_p%03d_o%06d_b%03d_%s.dat' % (dir2, path, orbit, block, camera)
								fname3 = '%ssurf_p%03d_o%06d_b%03d_%s.png' % (dir2, path, orbit, block, camera)

							fname4 = 'MISR_AM1_GP_GMP_P%03d_O%06d_F03_0013' % (path, orbit)
							found = False

							for g in geops:
								if g.startswith(fname4) and g.endswith('.hdf'):
									found = True
									#cmd = 'Surf %s %s %s %s' % (fname1, os.path.join(gdir, g), fname2, fname3)

									# from C code: SurfSeaIce_exe, toa_data_file, GP_GMP_file, band, output_data_file, output_image_file

									cmd = 'SurfSeaIce \"%s\" \"%s\" %s %s' % (fname1, os.path.join(gdir, g), nband=missing , fname2, fname3) # band=? before fname2; bandshould be 2 similar to run_TOA.py
									if n >= 0:
										sys.stderr.write('%5d: %s\n' % (n + 1, cmd))
										if os.system(cmd) != 0:
											sys.exit(1)
									n += 1
									#if n >= 10:
									#	sys.exit(1)
									break
							if found:
								break

	sys.exit(0)
	
