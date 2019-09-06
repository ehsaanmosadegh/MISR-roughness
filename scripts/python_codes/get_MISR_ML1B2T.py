#!/usr/bin/python

#from __future__ import print_function
import sys, os, os.path, signal
from ftplib import FTP

host = "l5ftl01.larc.nasa.gov"

username = "ehsanm"
#password = "bahramisepid@gmail.com"
password = 'E@dri2019'

root_dir_local = '/Volumes/MISR_REPO/'
local_donwload_dir = '/Nolin/2001/Ml1b2e/August/'

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
remote_orders_list = ['0627517786',
	  '0627517787',
    '0627517794',
	  '0627517791',
	  '0627517789',
	  '0627517788',
	  '0627517792',
	  '0627517793']

for remote_order_dir in remote_orders_list:

   local_dir = root_dir_local+local_download_dir # local dir- ldir directory? DL dir???

   remote_dir_path = '/PullDir/' + remote_order_dir + '/' # is it local or on the server? what is rdir directory?

   ftp = FTP(host, username, password)

   ftp.cwd(remote_dir_path) # cwd = change work directory to this dir on the server

   files_list = []

   ftp.dir(files_list.append)  # Produces a directory listing

   for file_to_download in files_list:

      if (file_to_download.endswith('.hdf')):

         index_of_path = file_to_download.index('_P')

         path = int( file_to_download[ index_of_path + 2 : index_of_path + 5 ] )

         index_of_orbit = file_to_download.index('_O')

         orbit = int( file_to_download[ index_of_orbit + 2 : index_of_orbit + 8 ] )

	 if (True):
         #if (path > 45) and (path < 100): #Arctic SeaIce
         #if (path > 222) or (path < 51):
         #if (path < 80) and (path > 72):
         #if (path < 66) and (path > 59):

             if (file_to_download.find('CLOUD') < 0): continue  # if files have CLOUD (?) then do not download?
             #if (file_to_download.find('ELLIPSOID') < 0): continue
             #if (file_to_download.find('TERRAIN') < 0): continue
             #if (file_to_download.find('.f') > 0): continue
             #if (file_to_download.find('GMP') < 0): continue

	     index_of_MISR = file_to_download.index('MISR_')
	     
             remote_file = file_to_download[ index_of_MISR : ]  # ???

             if (not os.path.exists(local_dir + remote_file)):

                print ( f'-> this remote file does not exist on FTP server: {remote_file}')

                downloading_file = open(local_dir + remote_file, 'wb')  # w= write to file, b= in binary mode
                # ???????
                try:
                        ftp.retrbinary('RETR %s' % remote_file, downloading_file.write)  # Retrieve a file in binary transfer mode
                        downloading_file.close()

                except ftplib.error_temp:
                        print ('FTP ERROR: checksum failure on file "%s/%s"' % (remote_dir_path, remote_file))

ftp.close()

