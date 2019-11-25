#!/usr/bin/env python

# Run TOA program on all files in list
# Sky Coyote 16 March 2009
# Must be run from /Volumes/MISR_Nolin_Mac/2007/Code/

import sys, os, os.path, signal

def sigintHandler(a, b):
	sys.exit(0)

if __name__ == '__main__':
	signal.signal(signal.SIGINT, sigintHandler)
	
	dir1 = '../Surface/Cf/'
	dir2 = '../Surface/Ca/'
	
	l = []
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
	dirs = ['/media/WD1TB (ntfs)/Nolin/2007/TOA/Cf/', '/media/WD1TB (ntfs)/Nolin/2007/TOA/Ca/']
	n = 0
	for d in dirs:
		files = sorted(os.listdir(d))
		for f in files:
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
						if e[0] == path and e[1] == orbit and e[2] == block:
							fname1 = os.path.join(d, f)
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
									cmd = 'Surf \"%s\" \"%s\" %s %s' % (fname1, os.path.join(gdir, g), fname2, fname3)
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
	
