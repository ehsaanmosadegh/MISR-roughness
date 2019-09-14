#!/usr/bin/python3
#-------------------------------------------------------------------------------------
# author: Ehsan Mosadegh (ehsan.mosadegh@gmail.com)
# date: Sep 10, 2019
# usage: to download MISR data from NASA Langley server
# usage: We use Python3, and ftplib library to communicate with the server
#-------------------------------------------------------------------------------------
#from __future__ import print_function
import sys, os, os.path, signal
import ftplib
from ftplib import FTP
#-------------------------------------------------------------------------------------
#--- setting for DL data from NASA server

ftp_host = 'l5ftl01.larc.nasa.gov'
username = 'anonymous'
password = 'emosadegh@nevada.unr.edu'

#--- setting for directory path 

local_root_dir = '/Volumes/MISR_REPO/'
local_download_dir = 'dl_test/'

ftp_dir = '/PullDir/'
local_dir = local_root_dir+local_download_dir # local dir- check if it exists locally.

ff_index = 0  #  either 0 or 1
ff_list = [ 'xml' , 'hdf' ]
file_format = ff_list[ ff_index]

# check if the local download dir exists
if ( os.path.isdir( local_dir ) == False ) :
	print(f'-> ERROR: either the root or the local donwload directory does not exist on your system. Pease make/set the download directory and try again.')
	print(f'-> Exiting...')
	raise SystemExit()

else:
	print(f'-> download dir is: {local_dir}')
	print( f'-> file format is: {file_format}')

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
order_ID_list = ['062816110196687'] #, '062816109987111']

for order_ID in order_ID_list :

	print(f'-> processing order: {order_ID}')
   #local_dir = local_root_dir+local_download_dir # local dir- ldir directory? DL dir???

   #remote_order_dir = '/PullDir/' + order_ID + '/' # is it local or on the server? what is rdir directory?
	order_dir = ftp_dir + order_ID
	print(f'-> connecting to FTP')
	my_ftp = FTP(ftp_host, username, password)
	#print(f'-> ftp is: {my_ftp}')

	print(f'-> change dir to: {order_dir} on FTP')  # does not woek???
	my_ftp.cwd(order_dir) # cwd = change work directory to this dir on the server
	#os.chdir(remote_order_dir)
	print(f'-> we are at dir: { my_ftp.pwd() } ')

	files_list = []  # for each loop inside a loop

	my_ftp.dir(files_list.append)  # Produces a directory listing; does it work anymore???

	print(f'-> size of list: { len(files_list) }')

	for file_to_download in files_list :
		print(" ")
		############# add QA quality check here...
		print(f'-> QA check on file: ==> "{file_to_download}" <==')

		if (file_to_download.endswith(file_format)) :

			index_of_path = file_to_download.index('_P')

			path = int( file_to_download[ index_of_path + 2 : index_of_path + 5 ] )
			#print(f'-> path no. is= {path}')
			index_of_orbit = file_to_download.index('_O')

			orbit = int( file_to_download[ index_of_orbit + 2 : index_of_orbit + 8 ] )
			#print(f'-> orbit no. is= {orbit}')
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
	     
			remote_file_name = file_to_download[ index_of_MISR : ]  # ???

			if ( not os.path.exists( local_dir + remote_file_name ) ) :

				print( f'-> we do NOT have this file on our local machine:' )
				print( f'-> {remote_file_name}' )
				#print(f'-> downloading the file...' )

				#local_file = open(local_dir + remote_file_name, 'wb')  # opens/creates a file on local machine; w= write to file, b= in binary mode
				#print(f'-> local file created: {local_file}')

				try :

					if ( file_format == 'xml' ) :

						# use ascii function as transfter mode
						print( f'-> downloading the file: ')
						print( f'-> {remote_file_name} ' )
						#local_file = open(local_dir + remote_file_name, 'w')  # opens/creates a file on local machine; w= write to file, b= in binary mode
						with open ( local_dir + remote_file_name , 'w' ) as local_file_object :

							my_ftp.retrlines( 'RETR {remote_file_name}' , local_file_object.write )

					elif ( file_format == 'hdf' ) :

						# use binary function as transfer mode
						pass

					else :

						print( f'-> check the file fomat settings; exiting ...')
						raise SystemExit()

				except :

					print(f'-> issue with downloading file from the FTP')
					ftplib.all_errors






					# print(f'-> downloading the file {remote_file_name}')
					# my_ftp.retrbinary( 'RETR {remote_file_name}' , local_file.write)
					# local_file.close()
				
				# except:
				# 	print(f'-> ERROR in downloading file')


	      # try :
	      	
	      # 	my_ftp.retrbinary('RETR %s' % remote_file_name, local_file.write)  # Retrieve a file in binary transfer mode
	      #   local_file.close()

	      # except ftplib.error_temp :

	      # 	print ('FTP ERROR: checksum failure on file "%s/%s"' % (remote_order_dir, remote_file_name))
			else:
				print(f'-> the file exist on our local directory; no need to downloading the file.')

		else:
			print(f'-> the file does NOT end to "{file_format}", skipping the file...')

print( " " )
print(f'-> tried downloading all ordered files to: {local_dir}')
print(f'-> closing the FTP connection...')
my_ftp.close()

