#!/usr/bin/python

#from __future__ import print_function
import sys, os, os.path, signal
from ftplib import FTP

host = "l5ftl01.larc.nasa.gov"

username = "anonymous"
password = "bahramisepid@gmail.com"

root_dir = '/Volumes/MISR_REPO/'

# for MI1B2E Jul2016
"""
orders = ['0624779399', 
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
# for MIB2GEOP Apr2016
#orders = ['0624777838']

# for MIB2GEOP May2016
#orders = ['0624871775']

# for MIB2GEOP Jul2016
#orders = ['0624786633']
"""
# for MI1B2E May2016
orders = ['0624864632',
	  '0624864633',
	  '0624864634',
	  '0624864635']
"""
# for MIL2TCSP Apr2016
#orders = ['0624906331',
	  #'0624906332',
	  #'0624906333]

# for MIL2TCSP May2016
#orders = ['0624911745']

# for MIL2TCSP Jul2016
#orders = ['0624907089',
	  #'0624907091',
	  #'0624907093']

# for ML1BTE Aug2001
orders = ['0627517786',
	  			'0627517787',
          '0627517794',
	  '0627517791',
	  '0627517789',
	  '0627517788',
	  '0627517792',
	  '0627517793']

for order in orders:

   ldir_path = root_dir+'/Nolin/2001/Ml1b2e/August/' # local dir- ldir directory? DL dir???

   rdir_path = '/PullDir/' + order + '/' # is it local or on the server? what is rdir directory?

   ftp = FTP(host, username, password)

   ftp.cwd(rdir_path) # change wd to this on the server

   entries = []

   ftp.dir(entries.append)

   for entry in entries:

      if (entry.endswith('.hdf')):

         i = entry.index('_P')

         path = int(entry[i + 2 : i + 5])

         i = entry.index('_O')

         orbit = int(entry[i + 2 : i + 8])

	 if (True):
         #if (path > 45) and (path < 100): #Arctic SeaIce
         #if (path > 222) or (path < 51):
         #if (path < 80) and (path > 72):
         #if (path < 66) and (path > 59):

             if (entry.find('CLOUD') < 0): continue
             #if (entry.find('ELLIPSOID') < 0): continue
             #if (entry.find('TERRAIN') < 0): continue
             #if (entry.find('.f') > 0): continue
             #if (entry.find('GMP') < 0): continue

	     i = entry.index('MISR_')
	     
             rfile = entry[i:]

             if (not os.path.exists(ldir_path + rfile)):

                print (rfile)
                lfile = open(ldir_path + rfile, 'wb')

                try:
                        ftp.retrbinary('RETR %s' % rfile, lfile.write)
                        lfile.close()

                except ftplib.error_temp:
                        print ('FTP ERROR: checksum failure on file "%s/%s"' % (rdir_path, rfile))

ftp.close()

