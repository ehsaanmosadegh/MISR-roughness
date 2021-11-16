#!/usr/bin/python3.6
# coding: utf-8

import MisrToolkit as mtk
import pandas as pd
import numpy as np
import sys, glob, os

# !pip uninstall jedi --yes

# check python version be 3.6 cuz MTK works with 3.6
py_version = sys.version
py_ver = py_version[0:3]
if (py_ver != str(3.6)):
	print('python version is NOT 3.6- MTK does not work')
	raise SystemExit()
else:
	print('python version: %s' %py_ver)

'''
note: -999.0 represents no MISR toa file
'''
# set up paths
masked_toa_home = "/home/ehsan/misr_lab/orders/14528_apr2016/toa_refl_april_2016_9cam4bands_day1_16_p1_233_b1_46/masked_toa_refl_april_2016_9cam4bands_day1_16_p1_233_b1_46"
atm_dir = '/home/ehsan/misr_lab/ATM_apr2016_5days/test_20'

atmmodel_dir = '/home/ehsan/misr_lab/atmmodels/april_2016'
output_ds_label = 'april_2016_9cam4bands_testWithApril20_subset.csv'

# setup pattern- do not change
atm_file_pattern = 'ILATM2*'+'.csv'

# atm_file_sample = 'ILATM2_20160420_175457_smooth_nadir3seg_50pt.csv'
# atm_file_fp = os.path.join(atm_dir, atm_file_sample)
# check ATM file exists
# print(os.path.isfile(atm_file_fp))
# print(atm_file_fp)


#### create datadet table
# cam_labels = ['Da_r','Ca_r','Ba_r','Aa_r','An_r','An_g','An_b','An_nir','Af_r','Bf_r','Cf_r','Df_r','mean_ATM_roughness']

# add all found fields to pandas.DataFrame and make a dataset with column labels and filter for similar pixels
# column_names = ['path','orbit','block','line','sample','lat','lon', 'points_in_pixel', cam_labels[0],cam_labels[1],cam_labels[2],cam_labels[3],cam_labels[4],cam_labels[5],cam_labels[6],cam_labels[7],cam_labels[8],cam_labels[9],cam_labels[10],cam_labels[11],'mean_ATM_roughness']

ds_row_index = 0

column_names = ['path','orbit','block','line','sample','lat','lon','points_in_pixel','Da_r','Ca_r','Ba_r','Aa_r','An_r','An_g','An_b','An_nir','Af_r','Bf_r','Cf_r','Df_r','mean_ATM_roughness']
# final_ds = pd.DataFrame(columns=column_names, index=range(100000))

#-- get a list of ATM csv files
atm_list = glob.glob(os.path.join(atm_dir, atm_file_pattern))

total_atm_files_found = len(atm_list)
print('total ATM.csv files: %d' %total_atm_files_found)

#-- create pandas DF and set index to DF based on pre-estimate: 100000 per each ATM file
final_ds = pd.DataFrame(columns=column_names, index=range(total_atm_files_found*50000))

#-- this does not work
# final_ds.set_index(total_atm_files_found*10000)


for atm_cntr, ATMfile in enumerate(atm_list):

	print('\nprocessing ATM file: (%d/%d)' %(atm_cntr+1, len(atm_list)))
	# get date-time from ATM file label
	atm_label = ATMfile.split('/')[-1]
	yrmonday = atm_label.split('_')[1]
	atm_yr = yrmonday[0:4]
	atm_mon = yrmonday[4:6]
	atm_day = yrmonday[6:8]
	# print(atm_yr)
	# print(atm_mon)
	# print(atm_day)


	ATM_start_time = atm_yr+'-'+atm_mon+'-'+atm_day+"T00:00:00Z" # YYYY-MM-DDThh:mm:ssZ
	ATM_end_time = atm_yr+'-'+atm_mon+'-'+atm_day+"T23:59:59Z"
	print(ATM_start_time)
	print(ATM_end_time)


	# get a list of orbits for date-time
	orbit_list = mtk.time_range_to_orbit_list(ATM_start_time, ATM_end_time)
	# print('num of orbits found: %s' %len(orbit_list))
	# print(orbit_list)


	for misr_orbit in orbit_list:
		# print('\nprocessing orbit: %d' %misr_orbit)

		# orbit to path
		misr_path_num = mtk.orbit_to_path(misr_orbit)
		# print('path: %s' %misr_path_num)


		# open and read ATM file
		# atm_file_columnt = []

		in_atm = pd.read_csv(ATMfile, skiprows=9, header=0) # header line# is 9

		# in_atm.head(5)

		# find total atm_rows to make DF with Nan
		csv_total_rows = in_atm.shape[0]


		# read each row
		for atm_row_num in range(csv_total_rows): 
			atm_lat = in_atm.iloc[atm_row_num, 1]#.round(7)
			atm_lon = in_atm.iloc[atm_row_num, 2]#.round(7)
			atm_roughness = in_atm.iloc[atm_row_num, 6]#.round(7)

			# print('atm lat %s' %atm_lat)
			# print('atm lon %s' %atm_lon)
			# print('roughness %s' %atm_roughness)


			# print('finidng list of paths for ATM location...')
			try:  # to ignore Exception for some path numbers
				paths_cover_ATM_location = mtk.latlon_to_path_list(atm_lat, atm_lon)
				# print('MISR list of paths that cover ATM latlon:')
				# print(paths_cover_ATM_location)
			except Exception:
				# print('Exception was raised- continue to next ATM row')
				continue


			if misr_path_num not in paths_cover_ATM_location:
				# print('MISR path %d in day %s not match with path that ATM lat-lon falls in, continue to next ATM latLon row!' %(misr_path_num, atm_day))
				continue    # to next location == latLon
			# else:
			#     print('MISR path %d covers ATM location- we will find Block-Line-Sample!' %misr_path_num)

	
			# find MISR pixel from that
			resolution_meters = 275
			
			misr_block, misr_pixel_x, misr_pixel_y = mtk.latlon_to_bls(misr_path_num, resolution_meters, atm_lat, atm_lon) # q- why crash? these paths cover that that ATM location
			
			# print('block: %s' %misr_block)
			# print('pixel x: %s' %misr_pixel_x)
			# print('pixel y: %s' %misr_pixel_y)


			path_num_str = str(misr_path_num).zfill(3)
			misr_orbit_str = str(misr_orbit).zfill(6) 
			misr_block_str = str(misr_block).zfill(3)


			# print('path-str: %s' %path_num_str)
			# print('orbit-str: %s' %misr_orbit_str)
			# print('block-str: %s' %misr_block_str)


			#### create fulll path to 9 cameras and 4 spectral bands

			# find MISR files associated with P-O-B: masked_toa_P_O_B
			# aft/back cameras
			aa_red_fp = os.path.join(masked_toa_home,'Aa', ('masked_toa_refl_P'+path_num_str+'_'+'O'+misr_orbit_str+'_'+'B'+misr_block_str+'_aa_red.dat'))
			ba_red_fp = os.path.join(masked_toa_home,'Ba', ('masked_toa_refl_P'+path_num_str+'_'+'O'+misr_orbit_str+'_'+'B'+misr_block_str+'_ba_red.dat'))
			ca_red_fp = os.path.join(masked_toa_home,'Ca', ('masked_toa_refl_P'+path_num_str+'_'+'O'+misr_orbit_str+'_'+'B'+misr_block_str+'_ca_red.dat'))
			da_red_fp = os.path.join(masked_toa_home,'Da', ('masked_toa_refl_P'+path_num_str+'_'+'O'+misr_orbit_str+'_'+'B'+misr_block_str+'_da_red.dat'))
		   
			# front cameras
			af_red_fp = os.path.join(masked_toa_home,'Af', ('masked_toa_refl_P'+path_num_str+'_'+'O'+misr_orbit_str+'_'+'B'+misr_block_str+'_af_red.dat'))
			bf_red_fp = os.path.join(masked_toa_home,'Bf', ('masked_toa_refl_P'+path_num_str+'_'+'O'+misr_orbit_str+'_'+'B'+misr_block_str+'_bf_red.dat'))
			cf_red_fp = os.path.join(masked_toa_home,'Cf', ('masked_toa_refl_P'+path_num_str+'_'+'O'+misr_orbit_str+'_'+'B'+misr_block_str+'_cf_red.dat'))
			df_red_fp = os.path.join(masked_toa_home,'Df', ('masked_toa_refl_P'+path_num_str+'_'+'O'+misr_orbit_str+'_'+'B'+misr_block_str+'_df_red.dat'))
			
			# nadir
			an_red_fp = os.path.join(masked_toa_home,'An', ('masked_toa_refl_P'+path_num_str+'_'+'O'+misr_orbit_str+'_'+'B'+misr_block_str+'_an_red.dat'))
			an_green_fp = os.path.join(masked_toa_home,'An', ('masked_toa_refl_P'+path_num_str+'_'+'O'+misr_orbit_str+'_'+'B'+misr_block_str+'_an_green.dat'))
			an_blue_fp = os.path.join(masked_toa_home,'An', ('masked_toa_refl_P'+path_num_str+'_'+'O'+misr_orbit_str+'_'+'B'+misr_block_str+'_an_blue.dat'))
			an_nir_fp = os.path.join(masked_toa_home,'An', ('masked_toa_refl_P'+path_num_str+'_'+'O'+misr_orbit_str+'_'+'B'+misr_block_str+'_an_nir.dat'))

			#### check if camera files availabel


			# create a list of camreas based on order from Da->Df- order if important 
			masked_toaFile_orderedList = [da_red_fp, ca_red_fp, ba_red_fp, aa_red_fp,
										  an_red_fp, an_green_fp, an_blue_fp, an_nir_fp, 
										  af_red_fp, bf_red_fp, cf_red_fp, df_red_fp]

			available_file_status = []
			# check file exists
			for masked_toa_file in masked_toaFile_orderedList:
				# print(masked_toa_file)
				available_status = os.path.isfile(masked_toa_file)
				# print(available_status)
				available_file_status.append(available_status)


			##-- check if all 12 cameras are available
			# if (all(available_file_status)==False): # check if any element is false==file not found
			#     # print('***some masked-files missing- continue*** \n')
			#     continue # to the next ATM row

			if (not any(available_file_status)):
				# print('did not find even a single camera value for ATM location/row- continue')
				continue

			# print(available_file_status)



			# open masked-toa-refl and extract pixel value
			pixel_values = []
			for maskedTOA_rawfile in masked_toaFile_orderedList:
				print(maskedTOA_rawfile)
				is_file = os.path.isfile(maskedTOA_rawfile)
				print(is_file)
				
				#-- if a camera is missing, assign fill value for cameras that are not found
				if (is_file==False):
					pixel_values.append(-99.0) 
				else:
					rough_2d_arr = np.fromfile(maskedTOA_rawfile, dtype=np.double)[0:1048576].reshape((512,2048))   # 'double==float64'     # is this roughness in cm?
					# print(rough_2d_arr.shape)
					# print(type(rough_2d_arr))
					#-- maybe make a image from it?
					pixel_value = rough_2d_arr[int(misr_pixel_x), int(misr_pixel_y)]
					pixel_values.append(pixel_value)
				


			# print('path-str: %s' %path_num_str)
			# print('orbit-str: %s' %misr_orbit_str)
			# print('block-str: %s' %misr_block_str)

			print(pixel_values)


			# update dataframe 
			# final_ds.iloc[atm_row_num] = [misr_path_num, misr_orbit, misr_block, misr_pixel_x, misr_pixel_y, atm_lat, atm_lon, pixel_values[0],pixel_values[1],pixel_values[2],pixel_values[3],pixel_values[4],pixel_values[5],pixel_values[6],pixel_values[7],pixel_values[8],pixel_values[9],pixel_values[10],pixel_values[11],atm_roughness]
			# print(final_ds)

			# new_row = pixel_values2
			
			#### check if similar data exists
			# ref: https://www.askpython.com/python-modules/pandas/update-the-value-of-a-row-dataframe

			returned_row = final_ds.loc[(final_ds['path']==misr_path_num) & (final_ds['block']==misr_block) & (final_ds['line']==misr_pixel_x) & (final_ds['sample']==misr_pixel_y)]

			npoints_in_pixel = 1

			# print('adding new datapoint (%d) to dataset...' %(ds_row_index+1))

			if (not returned_row.empty):
				print('found row in dataset, will +update it')
				final_ds.loc[returned_row.index, ['Da_r']] = returned_row.Da_r.values + pixel_values[0]
				final_ds.loc[returned_row.index, ['Ca_r']] = returned_row.Ca_r.values + pixel_values[1]
				final_ds.loc[returned_row.index, ['Ba_r']] = returned_row.Ba_r.values + pixel_values[2]
				final_ds.loc[returned_row.index, ['Aa_r']] = returned_row.Aa_r.values + pixel_values[3]
				final_ds.loc[returned_row.index, ['An_r']] = returned_row.An_r.values + pixel_values[4]
				final_ds.loc[returned_row.index, ['An_g']] = returned_row.An_g.values + pixel_values[5]
				final_ds.loc[returned_row.index, ['An_b']] = returned_row.An_b.values + pixel_values[6]
				final_ds.loc[returned_row.index, ['An_nir']] = returned_row.An_nir.values+pixel_values[7]
				final_ds.loc[returned_row.index, ['Af_r']] = returned_row.Af_r.values + pixel_values[8]
				final_ds.loc[returned_row.index, ['Bf_r']] = returned_row.Bf_r.values + pixel_values[9]
				final_ds.loc[returned_row.index, ['Cf_r']] = returned_row.Cf_r.values + pixel_values[10]
				final_ds.loc[returned_row.index, ['Df_r']] = returned_row.Df_r.values + pixel_values[11]    
				
				npoints_in_pixel += 1
				
				#-- update mean roughness and points per pixel
				final_ds.loc[returned_row.index, ['mean_ATM_roughness']] = ((returned_row.mean_ATM_roughness.values+atm_roughness)/npoints_in_pixel)
				final_ds.loc[returned_row.index, ['points_in_pixel']] += 1 
				
			else:
				#add new-row as seperate row
				# print('adding to DS row index: %d' %ds_row_index)
				final_ds.iloc[ds_row_index] = [misr_path_num, misr_orbit, misr_block, misr_pixel_x, misr_pixel_y, atm_lat, atm_lon, npoints_in_pixel, pixel_values[0],pixel_values[1],pixel_values[2],pixel_values[3],pixel_values[4],pixel_values[5],pixel_values[6],pixel_values[7],pixel_values[8],pixel_values[9],pixel_values[10],pixel_values[11],atm_roughness]

			ds_row_index +=1


print('all ATM csv files were processed, writing out final DS...')
out_DS  = os.path.join(atmmodel_dir, output_ds_label)
final_ds.to_csv(out_DS)
print(out_DS)
print('successfully finished!')




