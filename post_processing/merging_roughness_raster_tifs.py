import glob
import os

file_list = glob.glob("/Volumes/MISR_REPO/tif_files/with_lat_lon_4326/*.tif")

files_string = " ".join(file_list)

command = "gdal_merge.py -o merged_tiff_4326.tif -of GTiff -ot uint16 " + files_string

os.system(command)






# import rasterio

# from rasterio.merge import merge

# from rasterio.plot import show

# import glob

# import os

# dem_fps = glob.glob("/Volumes/MISR_REPO/tif_files/with_lat_lon_3031/*.tif")

# print(dem_fps)

# src_files_to_mosaic = []

# for fp in dem_fps:
# 	src = rasterio.open(fp)
# 	src_files_to_mosaic.append(src)

# mosaic, out_trans = merge(src_files_to_mosaic)
# show(mosaic, cmap='terrain')