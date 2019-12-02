#!/usr/bin/python3
#-------------------------------------------------------------------------------------
# author: Ehsan Mosadegh (emosadegh@nevada.unr.edu & ehsanm@dri.edu)
# date: Oct 2, 2019
#
# purpose: 
# to download MISR Ellipsoid and Geometric data from NASA Langley server and QA check on downloaded data
#
# how to use: 
# We use Python3, and ftplib library to communicate with the server.
# change the setting on top of the script that says (USER) based on your local machine

# TO-DO tasks:
# how get the file if starts with capital letter?
# a new constraint for finding the dir pattern on remote server, not DIR, e.g. sparse and get "PullDir" as keyword and get the next numbers which are the dir names
##################################################################################################

import os, os.path , glob
import ftplib
from ftplib import FTP

##################################################################################################

def main() :

	#-----------------------------------------------------------------------------------------------
	# (USER-start) change these setting based on your local machine for downloading files from NASA server

	#--- set user pass info

	ftp_host = 'l5ftl01.larc.nasa.gov'
	username = 'anonymous'
	password = 'emosadegh@nevada.unr.edu'

	#--- set local directory path

	MISR_email_dir = '/Users/ehsanmos/Documents/MISR/emails/'
	MISR_download_dir = 'misr_download_test/'

	file_name_index = 0 		# 0 = elliposid; 1 = geometric

	# (USER-end) change these setting based on your local machine for downloading files from NASA server
	#-----------------------------------------------------------------------------------------------
	# NOTE: user does NOT need to update or change other sections of this script.

	file_name_list = ['ell', 'geo']
	file_name = file_name_list[file_name_index]

	# check the environment setting
	list_of_txt_files , download_dir_fullpath = check_local_environment(MISR_email_dir, MISR_download_dir, file_name)

	print('-> connecting to FTP')
	ftp_connection = FTP(ftp_host, username, password)
	#print(f'-> ftp is: {ftp_connection}')

	#--- loop through local email text files
	for email_file in range(len(list_of_txt_files)):

		email_txt = list_of_txt_files[email_file]

		email_file = os.path.join(MISR_email_dir, email_txt)
		print('-> processing email file= %s' %email_file)

		#--- use function to get the lists of filenames and sizes
		MISR_file_list, MISR_size_list, FTP_dir_list = email_order_processor(email_file)
		downloadable_files, downloadable_sizes, missing_files, missing_sizes = quality_assurance(FTP_dir_list, ftp_connection, MISR_file_list, MISR_size_list)
		#print( f'-> DL files= { downloadable_files } ')
		#print( f'-> files sizes= { downloadable_sizes }')
		incomplete_files_list , incomplete_size_list , diff_size_list = download_from_ftp(downloadable_files, downloadable_sizes, download_dir_fullpath, ftp_connection)

		if ( len(incomplete_files_list) == 0 ) :
			print('-> DOWNLOAD FINISHED SUCCESSFULLY!')

		else:

			print('-> NOTE: %s file(s) NOT downloaded completely.' %len(incomplete_files_list))
			print('-> list of incomplete files:')
			print(incomplete_files_list)
			print('-> list of incomplete sizes:')
			print(incomplete_size_list)
			print('-> list of diff sizes (bytes):')
			print(diff_size_list)
			print('-> list of missing files on the server:')
			print(missing_files)
			print('-> list of missing sizes on the server:')
			print(missing_sizes)

	ftp_connection.close()

	return 0

##################################################################################################

# def get_xml( download_file_fullpath , remote_file_name , ftp_connection ) :

# 	# Open the local file for writing in ASCII mode
# 	with open ( download_file_fullpath , 'wb' ) as fileObject :
# 		print( f'-> file created/opened: {download_file_fullpath}')
# 		#ftp_connection.retrlines( f'RETR {remote_file_name}' , callback=fileObject.write )
# 		ftp_connection.retrbinary( f'RETR {remote_file_name}' , callback=fileObject.write )
# 		#ftp_connection.retrlines( f'RETR {remote_file_name}' , write_xml_line( remote_file_name , fileObject ) ) 
# 		fileObject.flush()

# 	return download_file_fullpath

##################################################################################################

def check_local_environment( MISR_email_dir , download_directory_name , file_name ) :

	# check if download file exists... mkdir the file first
	print('-> downloading data= %s' %file_name)
	print('-> current working directory= %s' %os.getcwd())

	if not (os.path.isdir(MISR_email_dir)):
		print('-> looks like you forgot to set the "MISR root directory". Please set the path and run the script again.')
		raise SystemExit()

	print('-> change to local MISR root directory')
	os.chdir(MISR_email_dir)
	print('-> now we are at= %s' %os.getcwd())

	# get the download file pattern
	local_dir_file_pattern = file_name+'*.txt'
	# check current dir for email text files
	list_of_txt_files = glob.glob( local_dir_file_pattern ) # how get the file if starts with capital letter?

	if ( len( list_of_txt_files ) == 0 ) :
		print('-> looks like you forgot to save the order emails. Please save the emails in <.txt> format in the following directory and run the script again.')
		print(MISR_email_dir)
		raise SystemExit()

	print('-> list of available txt files to process= %s' %list_of_txt_files)

	# define download dir
	download_dir_fullpath = MISR_email_dir+download_directory_name
	# check if download dir exists
	if not (os.path.isdir(download_dir_fullpath)):
		print('-> the download dir was not created, so we create the dir now!')
		os.mkdir(download_dir_fullpath)

	return list_of_txt_files , download_dir_fullpath

##################################################################################################

def get_files( download_file_fullpath , remote_file_name , ftp_connection , list_index ) :

	# use BINARY function as transfter mode
	print('-> getting the file %s' %(list_index+1))
	print(remote_file_name)

	# Open the local file for writing in BINARY mode
	with open ( download_file_fullpath , 'wb' ) as fileObject :
		print('-> file created/opened: %s' %download_file_fullpath)
		ftp_connection.retrbinary( f'RETR {remote_file_name}' , callback=fileObject.write )
		fileObject.flush()

	return download_file_fullpath

##################################################################################################

# def write_xml_line( remote_file , fileObject ) :
	
# 	print(f'-> remote xml file= {remote_file}')
# 	for line in remote_file :
# 		fileObject.write( line )

# 	return fileObject

##################################################################################################

# def compare_dl_sizes( file_extension , remote_file_name , remote_file_size , download_file_fullpath ) :

# 	# incomplete_files_list = []
# 	# incomplete_size_list = []

# 	# get the local file size after download
# 	downloaded_file_size = os.path.getsize( download_file_fullpath )

# 	print('-> compare DL sizes...')
# 	print(f'-> {file_extension} local size= {downloaded_file_size} bytes.')
# 	print(f'-> {file_extension} remote size= {remote_file_size} bytes.')

# 	if ( downloaded_file_size == int(remote_file_size) ) :
# 		print(f'-> file size MATCH!')

# 	else:
# 		print(f'-> WARNING: file size NOT match for= {download_file_fullpath}')
# 		# get the file name from download_file_fullpath
# 		dl_file_with_issue = download_file_fullpath.split('/')[-1]
# 		print(f'-> WARNING: we added the file to incomplete file list: {dl_file_with_issue}')

# 	print(" ")

# 	return download_file_fullpath , downloaded_file_size

##################################################################################################

def email_order_processor(email_file) :

	FTP_dir_list = []
	MISR_file_list = []
	MISR_size_list = []

	print('-> opening order: %s' %email_file)

	with open(email_file, 'r') as file_obj:
		for row in file_obj :
			split_row = row.split() # splitting each row and get the parsed words
			#print('-> split_row= %s' %split_row)
			#print(len(split_row))

			if (len(split_row) == 0) :
				#print('-> WARNING: split_row of list is empty!')
				continue

			else :
				first_word = split_row[0]
				#print('-> first word of list= %s' %first_word)

				if (first_word == 'FILENAME:'): # looks for this keyword in txt file
					MISR_file = split_row[1]
					#print('-> misr file= %s' %MISR_file)
					MISR_file_list.append( MISR_file )

				if (first_word == 'FILESIZE:'): # looks for this keyword in txt file
					MISR_size = split_row[1]
					MISR_size_list.append(MISR_size)

				# if (first_word == 'FTPDIR:'): # looks for this keyword in txt file
				if (first_word == 'DIR:'): # looks for this keyword in txt file
					print('-> dir path is= %s' %split_row)
					FTP_dir = split_row[1]
					ftp_split = FTP_dir.split('/')
					print('-> appending the path= %s' %FTP_dir)
					FTP_dir_list.append(FTP_dir)

					# for split_index in range(len(ftp_split)) :
					# 	if ( ftp_split[split_index] == 'PullDir' ) :
					# 		pulldir_number = ftp_split[split_index+1]
					# 		FTP_dir_list.append( pulldir_number )

	print('-> len of MISR file list is= %s' %len(MISR_file_list))
	print('-> len of MISR file size is= %s' %len(MISR_size_list))
	print('-> FTP dir is= %s' %FTP_dir_list)

	return MISR_file_list , MISR_size_list , FTP_dir_list

##################################################################################################

def quality_assurance( FTP_dir_list , ftp_connection , MISR_file_list , MISR_size_list ) :

	print('-> FTP directory is= %s' %FTP_dir_list)
	# get the FTP dir path 
	FTP_remote_dir = FTP_dir_list[0] # how many elements inside the list?
	print('-> order dir= %s' %FTP_remote_dir)

	# change work directory to this dir on the server
	ftp_connection.cwd(FTP_remote_dir)

	# check where we are now
	present_wd = ftp_connection.pwd()
	print('-> we are at dir: %s' %present_wd)
	print( " " )
	download_list = []

	# get the directory listing
	remote_dir_list = ftp_connection.nlst() 
	#print( f'-> remote dir list= ')
	#print(remote_dir_list)

	downloadable_files = []
	downloadable_sizes = []
	missing_files =[]
	missing_sizes = []

	# check each MISR file if they are available
	for ordered_file in range( len(MISR_file_list) ) :

		MISR_file = MISR_file_list[ ordered_file ]
		MISR_size = MISR_size_list[ ordered_file ]

		# check if file available in present list
		if MISR_file in remote_dir_list :
			#print( f'-> file available in remote list= { MISR_file }')
			downloadable_files.append( MISR_file )
			downloadable_sizes.append( MISR_size )

		else:
			#print( f'-> ordered file NOT available in remote list')
			missing_files.append( MISR_file )
			missing_sizes.append( MISR_size )


	print('-> no. of remote hdf and xml files= %s' %len( downloadable_files ))
	print('-> no. of elements in file size list= %s' %len( downloadable_sizes ))
	# print('-> list of remote files:')
	# print(downloadable_files)
	# print('-> list of files sizes=')
	# print(downloadable_sizes)

	return downloadable_files , downloadable_sizes , missing_files , missing_sizes

##################################################################################################

def download_from_ftp( downloadable_files , downloadable_sizes , download_dir_fullpath , ftp_connection ) :

	incomplete_files_list = []
	incomplete_size_list = []
	diff_size_list = []

	for list_index in range(len( downloadable_files )) :

		remote_file_name = downloadable_files[ list_index ]
		remote_file_size = downloadable_sizes[ list_index ]

		print(" ")
		download_file_fullpath = download_dir_fullpath+remote_file_name
		filename, file_extension = os.path.splitext( remote_file_name )
		# print( f'-> file is= { file_name }')
		# print( f'-> file extension is= { file_extension }')


		if ( file_extension == '.xml' ) :
			# use ASCII function as transfter mode
			download_file_fullpath = get_files( download_file_fullpath , remote_file_name , ftp_connection , list_index )

			# get the local file size after download
			downloaded_file_size = os.path.getsize( download_file_fullpath )

			print('-> "%s" local size= %s bytes.' %(file_extension, downloaded_file_size))
			print('-> "%s" remote size= %s bytes.' %(file_extension, remote_file_size))
			# compare  file sizes
			if ( downloaded_file_size == int(remote_file_size) ) :
				print('-> file size MATCH!')

			else:
				print('-> WARNING: file size NOT match for= %s' %download_file_fullpath)
				diff_size = abs(downloaded_file_size - int(remote_file_size))
				print('-> diff size= %s bytes.' %diff_size)
				# get the file name from download_file_fullpath
				dl_file_with_issue = download_file_fullpath.split('/')[-1]
				print('-> WARNING: we added the file to incomplete file list: %s' %dl_file_with_issue)

				incomplete_files_list.append( dl_file_with_issue )
				incomplete_size_list.append( downloaded_file_size )
				diff_size_list.append( diff_size )


		elif ( file_extension == '.hdf') :

			# use BINARY function as transfter mode
			download_file_fullpath = get_files( download_file_fullpath , remote_file_name , ftp_connection , list_index )

			# get the local file size after download
			downloaded_file_size = os.path.getsize( download_file_fullpath )

			print('-> "%s" local size= %s bytes.' %(file_extension, downloaded_file_size))
			print('-> "%s" remote size= %s bytes.' %(file_extension, remote_file_size))
			# compare  file sizes
			if ( downloaded_file_size == int(remote_file_size) ) :
				print('-> file size MATCH!')

			else:
				print('-> WARNING: file downloaded, but size NOT match for= %s' %download_file_fullpath)
				diff_size = abs(downloaded_file_size - int(remote_file_size))
				print('-> diff size= %s bytes.' %diff_size)
				# get the file name from download_file_fullpath
				dl_file_with_issue = download_file_fullpath.split('/')[-1]
				#print(f'-> WARNING: we added the file to incomplete file list: {dl_file_with_issue}')

				incomplete_files_list.append( dl_file_with_issue )
				incomplete_size_list.append( downloaded_file_size )
				diff_size_list.append( diff_size )

		else:
			print('-> WARNING: problem with file extension or downloading for file= %s' %remote_file_name)


	return incomplete_files_list , incomplete_size_list , diff_size_list

##################################################################################################

if __name__ == '__main__' :
	main()

##################################################################################################

