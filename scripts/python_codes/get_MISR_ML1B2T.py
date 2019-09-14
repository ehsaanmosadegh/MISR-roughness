#!/usr/bin/python3
#-------------------------------------------------------------------------------------
# author: Ehsan Mosadegh (ehsan.mosadegh@gmail.com)
# date: Sep 10, 2019
# usage: to download MISR data from NASA Langley server
#
# to use: 
# We use Python3, and ftplib library to communicate with the server.
# change the setting on top of the script that says (USER) base on your local machine

# future to-do tasks:
# a QA on file name patterns; it should capture the file name pattern and selectes the pattern of interest, pattern such as camerta, orbit, path...
#-------------------------------------------------------------------------------------

import sys, os, os.path, signal
import ftplib
from ftplib import FTP

#-------------------------------------------------------------------------------------
# (USER) change these setting based on your local machine for downloading files from NASA server

ftp_host = 'l5ftl01.larc.nasa.gov'
username = 'anonymous'
password = 'emosadegh@nevada.unr.edu'

#-- setting for directory path 

local_root_dir = '/Users/ehsan/Documents/MISR/'
local_download_dir = 'test_download/'
ftp_dir = '/PullDir/'

ff_index = 1  #  either 0 or 1
ff_list = ['xml' , 'hdf']
file_format = ff_list[ ff_index]

#-- setting for orders; list all order numbers in thsi list wraped in single quotation and seperated by comma (from email from NASA server)

order_ID_list = ['062816110196687' ]#, '062816109987111' , '062816109811111' , '062816110081117' , '062816110281817' , '062816110468891' , '062816110389171']

# (USER) change these setting based on your local machine for downloading files from NASA server
#-------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------
# check if the local download dir exists

local_dir = local_root_dir + local_download_dir # local dir- check if it exists locally.

if ( os.path.isdir( local_dir ) == False ) :
	print(f'-> ERROR: either the root or the local donwload directory does not exist on your system. Pease make/set the download directory and try again.')
	print(f'-> Exiting...')
	raise SystemExit()

else:
	print(f'-> download dir is: {local_dir}')
	print( f'-> file format is: {file_format}')

# check if the local download dir exists
#-------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------
# connect to NASA server through FTP and donwload files

print(f'-> connecting to FTP')
ftp_connection = FTP(ftp_host, username, password)
#print(f'-> ftp is: {ftp_connection}')

for order_ID in order_ID_list :
	print( " " )
	print( '##########################################################################' )
	print(f'-> processing order: {order_ID}')

	order_dir = ftp_dir + order_ID

	print(f'-> change dir to: {order_dir} on FTP')  # does not woek???
	ftp_connection.cwd(order_dir) # cwd = change work directory to this dir on the server
	#os.chdir(remote_order_dir)
	print(f'-> we are at dir: { ftp_connection.pwd() } ')

	files_list = []  # for each loop inside a loop

	ftp_connection.dir(files_list.append)  # Produces a directory listing; does it work anymore???

	print(f'-> size of list: { len(files_list) }')

	for file_to_download in files_list :

		print(" ")
		print( f'-> QA check on file:')
		print( f' "{file_to_download}" ')

		if (file_to_download.endswith(file_format)) :

		############# add QA quality check here...
			# index_of_path = file_to_download.index('_P')

			# path = int( file_to_download[ index_of_path + 2 : index_of_path + 5 ] )
			# #print(f'-> path no. is= {path}')
			# index_of_orbit = file_to_download.index('_O')

			# orbit = int( file_to_download[ index_of_orbit + 2 : index_of_orbit + 8 ] )
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

				local_file_full_path = local_dir + remote_file_name  # opens/creates a file on local machine; w= write to file, b= in binary mode
				#print(f'-> local file created: {local_file_full_path}')

				try :

					if ( file_format == 'xml' ) :

						# use ASCII function as transfter mode
						print( f'-> downloading file: ')
						print( f'-> {remote_file_name} ' )
						
						# Open the local file for writing in ASCII mode
						with open ( local_file_full_path , 'w' ) as file_object :

							print( f'-> file created/opened: {local_file_full_path}')

							ftp_connection.retrlines( f'RETR {remote_file_name}' , file_object.writelines )  # remote file or just the file name?

							print( f'-> GREAT, data was written to the file')


					elif ( file_format == 'hdf' ) :

						# use BINARY function as transfter mode
						print( f'-> downloading file: ')
						print( f'-> {remote_file_name} ' )

						# Open the local file for writing in BINARY mode
						with open ( local_file_full_path , 'wb' ) as file_object :

							print( f'-> file created/opened: {local_file_full_path}')
							
							ftp_connection.retrbinary( f'RETR {remote_file_name}' , file_object.write )

							print( f'-> GREAT, data was written to the file')

					else :

						print( f'-> check the file fomat settings; exiting ...')
						raise SystemExit()

				except :# 
					ftplib.all_errors

					print(f'-> ERROR: issue with downloading file from the FTP. Existing...')
					raise SystemExit()

			else:
				print(f'-> file EXISTS on your local directory; no need to downloading the file.')

		else:
			print(f'-> file does NOT end to "{file_format}", skipping the file...')

# connect to NASA server through FTP and donwload files
#-------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------
# closing FTP connection and exiting

print( " " )
print(f'-> tried downloading all ordered files to: {local_dir}')
print(f'-> closing the FTP connection...')
ftp_connection.close()
print( f'-> SUCCESSFULLY ENDED!')

# closing FTP connection and exiting
#-------------------------------------------------------------------------------------

