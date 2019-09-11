#!/usr/bin/python3

#from __future__ import print_function
import sys, os, os.path, signal
from ftplib import FTP

#------ setting for DL data from NASA server

ftp_host = 'l5ftl01.larc.nasa.gov'
username = 'anonymous'
password = 'emosadegh@nevada.unr.edu'

#------ setting for directory path 

root_dir_local = '/Volumes/MISR_REPO/'
local_download_dir = '/Nolin/2001/Ml1b2e/August/'
ftp_dir = '/PullDir/'
local_dir = root_dir_local+local_download_dir # local dir- check if it exists locally.

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
order_ID_list = [
	
		'062816110196687' ]  # '062816109811111'

for order_ID in order_ID_list:

	print(f'-> processing order: {order_ID}')
   #local_dir = root_dir_local+local_download_dir # local dir- ldir directory? DL dir???

   #remote_order_dir = '/PullDir/' + order_ID + '/' # is it local or on the server? what is rdir directory?
	order_dir = ftp_dir + order_ID
	print(f'-> connecting to FTP')
	my_ftp = FTP(ftp_host, username, password)
	#print(f'-> ftp is: {my_ftp}')

	print(f'-> change dir to: {order_dir}')  # does not woek???
	my_ftp.cwd(order_dir) # cwd = change work directory to this dir on the server
	#os.chdir(remote_order_dir)
	print(f'-> we are at dir: { my_ftp.pwd() } ')

	files_list = []  # for each loop inside a loop

	my_ftp.dir(files_list.append)  # Produces a directory listing; does it work anymore???

	print(f'-> size of list: { len(files_list) }')

	for file_to_download in files_list :
		print(f'-> doing QA check...')
		if (file_to_download.endswith('.hdf')):

			index_of_path = file_to_download.index('_P')

			path = int( file_to_download[ index_of_path + 2 : index_of_path + 5 ] )
			print(f'-> path no. is= {path}')
			index_of_orbit = file_to_download.index('_O')

			orbit = int( file_to_download[ index_of_orbit + 2 : index_of_orbit + 8 ] )
			print(f'-> orbit no. is= {orbit}')
  		### what QA should we use here? based on file name?

	 #if (True):
         #if (path > 45) and (path < 100): #Arctic SeaIce
         #if (path > 222) or (path < 51):
         #if (path < 80) and (path > 72):
         #if (path < 66) and (path > 59):

			# if (file_to_download.find('CLOUD') < 0) :  # if files have CLOUD (?) then do not download?
			# 	print(f'-> the file includes "CLOUD" keyword, so we skip it')
			# 	continue 
             #if (file_to_download.find('ELLIPSOID') < 0): continue
             #if (file_to_download.find('TERRAIN') < 0): continue
             #if (file_to_download.find('.f') > 0): continue
             #if (file_to_download.find('GMP') < 0): continue

			index_of_MISR = file_to_download.index('MISR_')
	     
			remote_file = file_to_download[ index_of_MISR : ]  # ???

			if ( not os.path.exists( local_dir + remote_file ) ) :

				print ( f'-> we do not have this file yet: {remote_file}')

	      # downloading_file = open(local_dir + remote_file, 'wb')  # w= write to file, b= in binary mode

	      # try :
	      	
	      # 	my_ftp.retrbinary('RETR %s' % remote_file, downloading_file.write)  # Retrieve a file in binary transfer mode
	      #   downloading_file.close()

	      # except ftplib.error_temp :

	      # 	print ('FTP ERROR: checksum failure on file "%s/%s"' % (remote_order_dir, remote_file))

my_ftp.close()

