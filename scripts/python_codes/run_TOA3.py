#!/usr/bin/env python

# Run TOA3 program on all files in list
# Sky Coyote 18 March 2009
# Must be run from /Volumes/MISR_Nolin_Mac/2007/Code/

from __future__ import print_function
import sys, os, os.path, signal

class Entry:
	def __init__(self, path, orbit, block):
		self.path = path
		self.orbit = orbit
		self.block = block
		self.cfFile = None
		self.caFile = None
		self.anFile = None

def sigintHandler(a, b):
	sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, sigintHandler)
	
    #l = []
    #f = open('../PSU/POB_2011_SantiamPass.txt', 'r')
    #f = open('../PSU/POB_2013_April_SeaIce.txt', 'r')
    """
    f = open('../PSU/POB_2016_Apr_SeaIce.txt', 'r')
    for line in f:
	fields = line.strip().split()
	path = int(fields[0])
	mask = int(fields[1])
	orbit = int(fields[2])
	block_l = int(fields[3])
	block_u = int(fields[4])
	if mask:
	    for block in range(block_l, block_u + 1):
		l.append(Entry(path, orbit, block))
    f.close()
    """
    # for Apr2016
    #orders = ['0624733845', 
	  #'0624733846', 
	  #'0624733854', 
	  #'0624733866', 
	  #'0624733868', 
	  #'0624733869', 
	  #'0624733870', 
	  #'0624733871', 
	  #'0624733872', 
	  #'0624733873', 
	  #'0624733874', 
	  #'0624733875', 
	  #'0624733902', 
	  #'0624733912', 
	  #'0624733913', 
	  #'0624733915', 
    	  #['0624733916', 
	  #'0624733917', 
	  #'0624733918', 
	  #'0624733940', 
    	  #'0624733944', 
	  #'0624733951', 
	  #'0624733952', 
	  #'0624733953']

    # for MI1B2E Jul2016
    # for MI1B2E Aug2001
    """
    ,,''''orders = ['0624779399', 
	  '0624779400', 
	  '0624779401', 
	  '0624779402', 
	  '0624779415', 
	  '0624779416', 
	  '0624779417', 
	  '0624779418', 
	  '0624779419', 
	  '0624779420', 
	  '0624779421', 
	  '0624779422', 
	  '0624779424', 
	  '0624779427', 
	  '0624779429', 
	  '0624779432', 
	  '0624779433', 
	  '0624779434', 
	  '0624779435', 
	  '0624779436', 
	  '0624779437', 
	  '0624779438', 
	  '0624779439', 
	  '0624779440', 
	  '0624779441']
    """
    # for MI1B2E May2016 days 1-5
    #orders = ['0624864632',
#	      '0624864633',
#	      '0624864634',
#	      '0624864635']
    # for MILB2E August 2001
    orders = ['0627517785']

    bands = ['Red']
    minnaert = 0

    odirs = ['/home/mare/Nolin/2001/TOA3/August/Cf/',
	     '/home/mare/Nolin/2001/TOA3/August/Ca/',
	     '/home/mare/Nolin/2001/TOA3/August/Aa/']
	     #'/home/mare/Nolin/2009/TOA3/Apr_ascend/NIR/']

    for order in orders:
	idirs = ['/home/mare/Nolin/2001/Ml1b2e/August/' + order + '/'] 

	for d in idirs:
	    files = sorted(os.listdir(d))
	    n = 0
	    for f in files:
		#if f.find('GRP_TERRAIN_GM') > -1 and f.endswith('.hdf'):
		if f.find('GRP_ELLIPSOID_GM') > -1 and f.endswith('.hdf'):
		    i = f.index('_P') # finds the pattern
		    path = int(f[i + 2: i + 5])
		    i = f.index('_O')
		    orbit = int(f[i + 2: i + 8])
		    if f.find('_CF') > -1:
			camera = 'cf'
		    elif f.find('_CA') > -1:
			camera = 'ca'
		    elif f.find('_AN') > -1:
			camera = 'an'
		    else:
			camera = '??'
		    """
		    if camera == 'cf' or camera == 'ca' or camera == 'an':
			for e in l:
			    if e.path == path and e.orbit == orbit:
				if camera == 'cf':
				    e.cfFile = os.path.join(d, f)
				elif camera == 'ca':
				    e.caFile = os.path.join(d, f)
				elif camera == 'an':
				    e.anFile = os.path.join(d, f)

		    if camera == 'cf':
			cfFile = os.path.join(d, f)
		    elif camera == 'ca':
			caFile = os.path.join(d, f)
		    elif camera == 'an':
			anFile = os.path.join(d, f)
		    """
		    File = os.path.join(d, f) 
		#for e in l:
		for block in xrange(1, 41):
		    for band in bands:
			if (band == 'NIR'): nband = 3
			elif (band == 'Red'): nband = 2
			elif (band == 'Green'): nband = 1
			elif (band == 'Blue'): nband = 0

			if (orbit == 87985) and (block == 25) and (order == '0624779399'): continue
			if (orbit == 88220) and (block == 16) and (order == '0624779399'): continue
			if (orbit == 88390) and (block == 20) and (order == '0624779400'): continue
			if (orbit == 88269) and (block == 15) and (order == '0624779402'): continue
			if (orbit == 88143) and (block == 34) and (order == '0624779415'): continue
			if (orbit == 88153) and (block == 35) and (order == '0624779417'): continue
			if (orbit == 88030) and (block == 29) and (order == '0624779417'): continue
			if (orbit == 88030) and (block == 30) and (order == '0624779417'): continue
			if (orbit == 88091) and (block == 29) and (order == '0624779417'): continue
			if (orbit == 88096) and (block == 29) and (order == '0624779421'): continue
			if (orbit == 88245) and (block == 32) and (order == '0624779422'): continue
			if (orbit == 88116) and (block == 15) and (order == '0624779429'): continue
			if (orbit == 87979) and (block == 35) and (order == '0624779433'): continue
			if (orbit == 87979) and (block == 36) and (order == '0624779433'): continue
			if (orbit == 88342) and (block == 9) and (order == '0624779435'): continue
			#if ((e.cfFile != None) and (nband != 3)):
			if (camera == 'cf') and (nband != 3):
			    fname2 = '%stoa_p%03d_o%06d_b%03d_%s.dat' % (odirs[0], path, orbit, block, 'cf')
			    fname3 = '%stoa_p%03d_o%06d_b%03d_%s.png' % (odirs[0], path, orbit, block, 'cf')
			    #fname2 = '%smisr_p%03d_o%06d_b%03d_%s.dat' % (odirs[0], e.path, e.orbit, e.block, 'cf')
			    #fname3 = '%smisr_p%03d_o%06d_b%03d_%s.png' % (odirs[0], e.path, e.orbit, e.block, 'cf')
				
			## here ....
			    cmd = 'TOA3 \"%s\" %d %d %d \"%s\" \"%s\"' % (File, block, nband, minnaert, fname2, fname3)
			    #if (n >= 0):
			    if not (os.path.exists(fname2) and os.path.exists(fname3)) :
				sys.stderr.write('%5d: %s\n' % (n, cmd))
				if os.system(cmd) != 0:
					sys.exit(1)
			#if ((e.caFile != None) and (nband != 3)):
			if (camera == 'ca') and (nband != 3):
			    fname2 = '%stoa_p%03d_o%06d_b%03d_%s.dat' % (odirs[1], path, orbit, block, 'ca')
			    fname3 = '%stoa_p%03d_o%06d_b%03d_%s.png' % (odirs[1], path, orbit, block, 'ca')
			    #fname2 = '%smisr_p%03d_o%06d_b%03d_%s.dat' % (odirs[1], e.path, e.orbit, e.block, 'ca')
			    #fname3 = '%smisr_p%03d_o%06d_b%03d_%s.png' % (odirs[1], e.path, e.orbit, e.block, 'ca')
			    cmd = 'TOA3 \"%s\" %d %d %d \"%s\" \"%s\"' % (File, block, nband, minnaert, fname2, fname3)
			    #if (n >= 0):
			    if not (os.path.exists(fname2) and os.path.exists(fname3)) :
				sys.stderr.write('%5d: %s\n' % (n, cmd))
				if os.system(cmd) != 0:
					sys.exit(1)
			#if (e.anFile != None):
			if (camera == 'an'):
			    if (nband == 3): idx = -1
			    elif (nband == 2): idx = 2
			    elif (nband == 1): idx = 1 
			    #else: idx = 2
			    fname2 = '%stoa_p%03d_o%06d_b%03d_%s.dat' % (odirs[idx], path, orbit, block, 'an')
			    fname3 = '%stoa_p%03d_o%06d_b%03d_%s.png' % (odirs[idx], path, orbit, block, 'an')
			    #fname2 = '%smisr_p%03d_o%06d_b%03d_%s.dat' % (odirs[band], e.path, e.orbit, e.block, 'an')
			    #fname3 = '%smisr_p%03d_o%06d_b%03d_%s.png' % (odirs[band], e.path, e.orbit, e.block, 'an')
			    cmd = 'TOA3 \"%s\" %d %d %d \"%s\" \"%s\"' % (File, block, nband, minnaert, fname2, fname3)
			    #if (n >= 0):
			    if not (os.path.exists(fname2) and os.path.exists(fname3)) :
				sys.stderr.write('%5d: %s\n' % (n, cmd))
				if os.system(cmd) != 0:
					sys.exit(1)
			n += 1

    sys.exit(0)
	
