import numpy as np
import MisrToolkit as Mtk
import os, gdal


roughness_file = "/Volumes/MISR_REPO/misr_roughness_data/test_p180/roughness_P180_O088147_B001.dat"
# # print(g1.field_name)

input_rough_file = np.fromfile(roughness_file, dtype='float64') 	# is this roughness in cm?

print("-> roughness array size: %d" % input_rough_file.size)


#roughness_list = input_rough_file[0:1048576] 
#roughness_list = input_rough_file[1048576:2097152] # 512*2048 = 1048576
roughness_list = input_rough_file[2097152:3145728] # 512*2048 = 1048576


for i in range(len(roughness_list)):
	print i, roughness_list[i] #, type(input_rough_file[i])



# print(type(input_rough_file))
# print("ndim of input_rough_file:" , input_rough_file.ndim)

roughness_array = roughness_list.reshape((512,2048))
print("-> shape of roughness array:" , np.shape(roughness_array))