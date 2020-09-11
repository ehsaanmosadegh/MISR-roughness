#!/bin/bash

exe_name="gdal_translate"
input_img=block2.jpg
output_img=block2_jpg2tiff.tif


##########################~ block-1

#~ this part in LatLon only= GCPs in latlon 
#~ only setup GCPs in img

gdal_translate \
-gcp 0 0 -166.1032584351828 66.22358078624517 \
-gcp 2047 0 -177.602425 64.605643 \
-gcp 2047 511 -178.841471 65.752107 \
-gcp 0 511 -166.860177 67.446689 \
-gcp 0 300 -166.538817 66.942084 \
-gcp 2047 300 -178.316493 65.280033 \
-gcp 500 511 -169.932982 67.118607 \
-gcp 1000 511 -172.918040 66.732948 \
-gcp 1500 511 -175.804917 66.292631 \
-gcp 500 0  -169.03858429114882 65.91032806969683 \
-gcp 1000 0 -171.8983540699897 65.54228012573581 \
-gcp 1500 0 -174.673063 65.121978 \
-gcp 500 300 -169.553297 66.620316 \
-gcp 1000 300 -172.485354 66.242142 \
-gcp 1500 300 -175.324941 65.810315 \
-of GTiff \
block1.jpg \
tif_files.nosync/block1_15gcps.tif



gdalwarp \
-r bilinear \
-s_srs "EPSG:4326" \
-t_srs "EPSG:4326" \
-overwrite \
-tps \
-co TILED=YES \   # compression option
-tr 0.001 0.001 \ 
-srcnodata 0 \
-dstnodata 0 \
tif_files.nosync/block1_15gcps.tif \
tif_files.nosync/block1_15gcps_reproj.tif


-wo SKIP_NOSOURCE=YES \


gdal_translate -of VRT block1_15gcps_t2.tif block1_15gcps_t2.vrt


##########################~ block-2 ##########################~

# -gcp imgColCnt imgRowCnt easting noirthing  --> for each coordPoint

gdal_translate \

-gcp 0 0 -166.861731 67.449078 \
-gcp 500 0 -169.934818 67.120966 \
-gcp 1000 0 -172.920132 66.735271 \
-gcp 1500 0 -175.807236 66.294913 \
-gcp 2047 0 -178.844006 65.754340 \
-gcp 0 300 -167.341944 68.165380 \
-gcp 500 300 -170.501988 67.827789 \
-gcp 1000 300 -173.565895 67.430896 \
-gcp 1500 300 -176.522669 66.977879 \
-gcp 2047 300 -179.625207 66.422088 \
-gcp 0 511 -167.697312 68.668316 \
-gcp 500 511 -170.921504 68.323681 \
-gcp 1000 511 -174.043051 67.918496 \
-gcp 1500 511 -177.050565 67.456136 \
-gcp 2047 511 -180.200587 66.889158 \
-of GTiff \
block2.jpg \
tif_files.nosync/block2_15gcps_allWestern.tif



-gcp 2047 511 179.799413 66.889158 \  # this is lrc from MTK == raster origin?
#~ change it, wrap it around that long start from western side and all long have negative long
#~ and center and output is centered on -180 west

-gcp 2047 511 -180.200587 66.889158 \


gdalwarp \ 
-r bilinear \  # resampling algorithm
-s_srs "EPSG:4326" \
-t_srs "EPSG:4326" \
-overwrite \
-tps \
-co TILED=YES \
-tr 0.001 0.001 \
--config CENTER_LONG -180 \
-srcnodata 0 \
-dstnodata 0 \
tif_files.nosync/block2_15gcps_allWestern.tif \
tif_files.nosync/block2_15gcps_allWestern_reproj.tif


#~ othger options
-srcnodata 0
-crop_to_cutline \ ?
--config CENTER_LONG -180 \ # for Western hemisohere
--config CENTER_LONG -180 \ # for Eastern hemisohere



# block-1
# Origin = 		(-178.849368888279486,67.449071779086864)
# gcp 2047 511 = -178.841471 65.752107 #
# diff= 0.008 long

# block-2
# 68.670690985640803, 179.8347 => lon from my calculations
# 68.670690985640803, 179.799413 => lon from gcp lrc
# diff= 0.04 long

#~ for latlon?
-t_srs "+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0 \
        +over +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null \
        +wktext +lon_wrap=-180 +no_defs" \





gdal_translate \
-gcp 0 0 193.1382 67.449078 \
-gcp 2047 0 181.156 65.754340 \
-gcp 2047 511 179.799413 66.889158 \
-gcp 0 511 192.30 68.668316 \
-of GTiff \
block2.jpg \
tif_files.nosync/block2_4corner_360.tif



--config CENTER_LONG 180 \

-wo SOURCE_EXTRA=1000 \
--config CENTER_LONG 180 \
-te 179.799413 66.889158 -166.861731 67.449078 \
--config CENTER_LONG 180 \
-wo SOURCE_EXTRA=1000 \

##########################~ block-21 ##########################

gdal_translate \
-gcp 0 0 96.805486 83.949995 \
-gcp 500 0 99.832924 82.769875 \
-gcp 1000 0 102.011307 81.574764 \
-gcp 1500 0 103.650197 80.370554 \
-gcp 2047 0 105.032099 79.046902 \
-gcp 0 300 90.414530 83.682788 \
-gcp 500 300 94.327593 82.544496 \
-gcp 1000 300 97.200877 81.380334 \
-gcp 1500 300 99.390964 80.199823 \
-gcp 2047 300 101.254587 78.896402 \
-gcp 0 511 86.264203 83.451804 \
-gcp 500 511 90.670803 82.347488 \
-gcp 1000 511 93.959224 81.209162 \
-gcp 1500 511 96.492802 80.048793 \
-gcp 2047 511 98.665338 78.762784 \
-of GTiff \
block21.jpg \
tif_files/block21_15gcps.tif




#~ my script

360.0 -166.103258  
66.223581, 193.896742 

##########################~ some tests
gdal_translate -of VRT block2_15gcps_reproj.tif block2_15gcps_2.vrt


##########################~ gdal merge ##########################

#~ usage: gdal_merge -o output-name file1 file2 file3 ...

gdal_merge.py -o merged2blocks_WesternMode.tif block1_15gcps_reproj.tif block2_15gcps_allWestern_reproj.tif 



gdal_merge.py \
 block_1_reprojected_28GCPs_noRes.tif \
 block_2_reprojected_28GCPs_noRes.tif \
 block_3_reprojected_28GCPs_noRes.tif \
 block_4_reprojected_28GCPs_noRes.tif \
 block_5_reprojected_28GCPs_noRes.tif \
 block_6_reprojected_28GCPs_noRes.tif \
 block_7_reprojected_28GCPs_noRes.tif \
 -o merged_7blocks_tap_noRes.tif \
  -of GTiff \
  -n 0 \


# new try
gdal_merge.py \
 block_10_reprojected_28GCPs_noRes.tif \
 block_11_reprojected_28GCPs_noRes.tif \
 block_12_reprojected_28GCPs_noRes.tif \
 block_13_reprojected_28GCPs_noRes.tif \
 -o merged_b10_13_PMcrossing_outFromat.tif \


-of GTiff \
-n 0 

  
#~ we don't use gdal_merge.py anymore to build a mosaic.

gdalwarp \
reprojected_warped_p174_b9_28GCPs.tif \
reprojected_warped_p174_b10_28GCPs.tif \
reprojected_warped_p174_b11_28GCPs.tif \
reprojected_warped_p174_b12_28GCPs.tif \
reprojected_warped_p174_b13_28GCPs.tif \
reprojected_warped_p174_b14_28GCPs.tif \
reprojected_warped_p174_b15_28GCPs.tif \
reprojected_warped_p174_b16_28GCPs.tif \
reprojected_warped_p174_b17_28GCPs.tif \
reprojected_warped_p174_b18_28GCPs.tif \
mergedOutput_p174_b9_18.tif



# path 40: [18, 36 included]
gdalwarp \
block_18_reprojected_28GCPs_noRes.tif \
block_19_reprojected_28GCPs_noRes.tif \
block_20_reprojected_28GCPs_noRes.tif \
block_21_reprojected_28GCPs_noRes.tif \
block_22_reprojected_28GCPs_noRes.tif \
block_23_reprojected_28GCPs_noRes.tif \
block_24_reprojected_28GCPs_noRes.tif \
block_25_reprojected_28GCPs_noRes.tif \
block_26_reprojected_28GCPs_noRes.tif \
block_27_reprojected_28GCPs_noRes.tif \
block_28_reprojected_28GCPs_noRes.tif \
block_29_reprojected_28GCPs_noRes.tif \
block_30_reprojected_28GCPs_noRes.tif \
block_31_reprojected_28GCPs_noRes.tif \
block_32_reprojected_28GCPs_noRes.tif \
block_33_reprojected_28GCPs_noRes.tif \
block_34_reprojected_28GCPs_noRes.tif \
block_35_reprojected_28GCPs_noRes.tif \
block_36_reprojected_28GCPs_noRes.tif \
merged_b18_36.tif





# path 174
gdalwarp \
reprojected_warped_p174_b14_28GCPs.tif \
reprojected_warped_p174_b15_28GCPs.tif \
reprojected_warped_p174_b16_28GCPs.tif \
reprojected_warped_p174_b17_28GCPs.tif \
reprojected_warped_p174_b18_28GCPs.tif \
reprojected_warped_p174_b19_28GCPs.tif \
reprojected_warped_p174_b20_28GCPs.tif \
reprojected_warped_p174_b21_28GCPs.tif \
reprojected_warped_p174_b22_28GCPs.tif \
reprojected_warped_p174_b23_28GCPs.tif \
reprojected_warped_p174_b24_28GCPs.tif \
reprojected_warped_p174_b25_28GCPs.tif \
reprojected_warped_p174_b26_28GCPs.tif \
reprojected_warped_p174_b27_28GCPs.tif \
reprojected_warped_p174_b28_28GCPs.tif \
reprojected_warped_p174_b29_28GCPs.tif \
reprojected_warped_p174_b30_28GCPs.tif \
reprojected_warped_p174_b31_28GCPs.tif \
reprojected_warped_p174_b32_28GCPs.tif \
reprojected_warped_p174_b33_28GCPs.tif \
reprojected_warped_p174_b34_28GCPs.tif \
reprojected_warped_p174_b35_28GCPs.tif \
reprojected_warped_p174_b36_28GCPs.tif \
reprojected_warped_p174_b37_28GCPs.tif \
reprojected_warped_p174_b38_28GCPs.tif \
reprojected_warped_p174_b39_28GCPs.tif \
reprojected_warped_p174_b40_28GCPs.tif \
reprojected_warped_p174_b41_28GCPs.tif \
reprojected_warped_p174_b42_28GCPs.tif \
reprojected_warped_p174_b43_28GCPs.tif \
reprojected_warped_p174_b44_28GCPs.tif \
reprojected_warped_p174_b45_28GCPs.tif \
reprojected_warped_p174_b46_28GCPs.tif \
reprojected_warped_p174_b47_28GCPs.tif \
reprojected_warped_p174_b48_28GCPs.tif \
reprojected_warped_p174_b49_28GCPs.tif \
reprojected_warped_p174_b50_28GCPs.tif \
reprojected_warped_p174_b51_28GCPs.tif \
reprojected_warped_p174_b52_28GCPs.tif \
reprojected_warped_p174_b53_28GCPs.tif \
reprojected_warped_p174_b54_28GCPs.tif \
reprojected_warped_p174_b55_28GCPs.tif \
reprojected_warped_p174_b56_28GCPs.tif \
reprojected_warped_p174_b57_28GCPs.tif \
reprojected_warped_p174_b58_28GCPs.tif \
reprojected_warped_p174_b59_28GCPs.tif \
reprojected_warped_p174_b60_28GCPs.tif \
reprojected_warped_p174_b61_28GCPs.tif \
reprojected_warped_p174_b62_28GCPs.tif \
reprojected_warped_p174_b63_28GCPs.tif \
reprojected_warped_p174_b64_28GCPs.tif \
reprojected_warped_p174_b65_28GCPs.tif \
reprojected_warped_p174_b66_28GCPs.tif \
reprojected_warped_p174_b67_28GCPs.tif \
reprojected_warped_p174_b68_28GCPs.tif \
reprojected_warped_p174_b69_28GCPs.tif \
reprojected_warped_p174_b70_28GCPs.tif \
reprojected_warped_p174_b71_28GCPs.tif \
reprojected_warped_p174_b72_28GCPs.tif \
reprojected_warped_p174_b73_28GCPs.tif \
reprojected_warped_p174_b74_28GCPs.tif \
reprojected_warped_p174_b75_28GCPs.tif \
reprojected_warped_p174_b76_28GCPs.tif \
reprojected_warped_p174_b77_28GCPs.tif \
reprojected_warped_p174_b78_28GCPs.tif \
reprojected_warped_p174_b79_28GCPs.tif \
reprojected_warped_p174_b80_28GCPs.tif \
reprojected_warped_p174_b81_28GCPs.tif \
reprojected_warped_p174_b82_28GCPs.tif \
reprojected_warped_p174_b83_28GCPs.tif \
reprojected_warped_p174_b84_28GCPs.tif \
reprojected_warped_p174_b85_28GCPs.tif \
reprojected_warped_p174_b86_28GCPs.tif \
reprojected_warped_p174_b87_28GCPs.tif \
reprojected_warped_p174_b88_28GCPs.tif \
reprojected_warped_p174_b89_28GCPs.tif \
reprojected_warped_p174_b90_28GCPs.tif \
reprojected_warped_p174_b91_28GCPs.tif \
reprojected_warped_p174_b92_28GCPs.tif \
reprojected_warped_p174_b93_28GCPs.tif \
reprojected_warped_p174_b94_28GCPs.tif \
reprojected_warped_p174_b95_28GCPs.tif \
reprojected_warped_p174_b96_28GCPs.tif \
reprojected_warped_p174_b97_28GCPs.tif \
reprojected_warped_p174_b98_28GCPs.tif \
reprojected_warped_p174_b99_28GCPs.tif \
reprojected_warped_p174_b100_28GCPs.tif \
reprojected_warped_p174_b101_28GCPs.tif \
reprojected_warped_p174_b102_28GCPs.tif \
reprojected_warped_p174_b103_28GCPs.tif \
reprojected_warped_p174_b104_28GCPs.tif \
reprojected_warped_p174_b105_28GCPs.tif \
reprojected_warped_p174_b106_28GCPs.tif \
reprojected_warped_p174_b107_28GCPs.tif \
reprojected_warped_p174_b108_28GCPs.tif \
reprojected_warped_p174_b109_28GCPs.tif \
reprojected_warped_p174_b110_28GCPs.tif \
reprojected_warped_p174_b111_28GCPs.tif \
reprojected_warped_p174_b112_28GCPs.tif \
reprojected_warped_p174_b113_28GCPs.tif \
reprojected_warped_p174_b114_28GCPs.tif \
reprojected_warped_p174_b115_28GCPs.tif \
reprojected_warped_p174_b116_28GCPs.tif \
reprojected_warped_p174_b117_28GCPs.tif \
reprojected_warped_p174_b118_28GCPs.tif \
reprojected_warped_p174_b119_28GCPs.tif \
reprojected_warped_p174_b120_28GCPs.tif \
reprojected_warped_p174_b121_28GCPs.tif \
reprojected_warped_p174_b122_28GCPs.tif \
reprojected_warped_p174_b123_28GCPs.tif \
reprojected_warped_p174_b124_28GCPs.tif \
reprojected_warped_p174_b125_28GCPs.tif \
reprojected_warped_p174_b126_28GCPs.tif \
reprojected_warped_p174_b127_28GCPs.tif \
reprojected_warped_p174_b128_28GCPs.tif \
reprojected_warped_p174_b129_28GCPs.tif \
reprojected_warped_p174_b130_28GCPs.tif \
reprojected_warped_p174_b131_28GCPs.tif \
reprojected_warped_p174_b132_28GCPs.tif \
reprojected_warped_p174_b133_28GCPs.tif \
reprojected_warped_p174_b134_28GCPs.tif \
reprojected_warped_p174_b135_28GCPs.tif \
reprojected_warped_p174_b136_28GCPs.tif \
reprojected_warped_p174_b137_28GCPs.tif \
reprojected_warped_p174_b138_28GCPs.tif \
reprojected_warped_p174_b139_28GCPs.tif \
reprojected_warped_p174_b140_28GCPs.tif \
reprojected_warped_p174_b141_28GCPs.tif \
reprojected_warped_p174_b142_28GCPs.tif \
merged_output_p174_b14_142.tif


#~ test 0-180
gdalwarp \
block_10_reprojected_28GCPs_noRes.tif \
block_11_reprojected_28GCPs_noRes.tif \
block_12_reprojected_28GCPs_noRes.tif \
block_13_reprojected_28GCPs_noRes.tif \
block_14_reprojected_28GCPs_noRes.tif \
block_15_reprojected_28GCPs_noRes.tif \
block_16_reprojected_28GCPs_noRes.tif \
block_17_reprojected_28GCPs_noRes.tif \
block_18_reprojected_28GCPs_noRes.tif \
block_19_reprojected_28GCPs_noRes.tif \
block_20_reprojected_28GCPs_noRes.tif \
block_21_reprojected_28GCPs_noRes.tif \
block_22_reprojected_28GCPs_noRes.tif \
block_23_reprojected_28GCPs_noRes.tif \
block_24_reprojected_28GCPs_noRes.tif \
block_25_reprojected_28GCPs_noRes.tif \
block_26_reprojected_28GCPs_noRes.tif \
block_27_reprojected_28GCPs_noRes.tif \
block_28_reprojected_28GCPs_noRes.tif \
block_29_reprojected_28GCPs_noRes.tif \
block_30_reprojected_28GCPs_noRes.tif \
block_31_reprojected_28GCPs_noRes.tif \
block_32_reprojected_28GCPs_noRes.tif \
block_33_reprojected_28GCPs_noRes.tif \
block_34_reprojected_28GCPs_noRes.tif \
block_35_reprojected_28GCPs_noRes.tif \
block_36_reprojected_28GCPs_noRes.tif \
merged_blocks_10_36_0to180.tif



gdalwarp \
-ot Byte \
-of "GTiff" \
-srcnodata 0 \
-dstnodata 0 \
-s_srs "EPSG:4326" \
-t_srs "EPSG:9810" \
reprojected_block_10_28GCPs_noGdalResolution.tif \
reprojected_block_11_28GCPs_noGdalResolution.tif \
reprojected_block_12_28GCPs_noGdalResolution.tif \
reprojected_block_13_28GCPs_noGdalResolution.tif \
reprojected_block_14_28GCPs_noGdalResolution.tif \
reprojected_block_15_28GCPs_noGdalResolution.tif \
reprojected_block_16_28GCPs_noGdalResolution.tif \
reprojected_block_17_28GCPs_noGdalResolution.tif \
reprojected_block_18_28GCPs_noGdalResolution.tif \
reprojected_block_19_28GCPs_noGdalResolution.tif \
reprojected_block_20_28GCPs_noGdalResolution.tif \
reprojected_block_21_28GCPs_noGdalResolution.tif \
reprojected_block_22_28GCPs_noGdalResolution.tif \
reprojected_block_23_28GCPs_noGdalResolution.tif \
reprojected_block_24_28GCPs_noGdalResolution.tif \
reprojected_block_25_28GCPs_noGdalResolution.tif \
reprojected_block_26_28GCPs_noGdalResolution.tif \
reprojected_block_27_28GCPs_noGdalResolution.tif \
reprojected_block_28_28GCPs_noGdalResolution.tif \
reprojected_block_28_28GCPs_noGdalResolution.tif \
reprojected_block_29_28GCPs_noGdalResolution.tif \
reprojected_block_30_28GCPs_noGdalResolution.tif \
reprojected_block_31_28GCPs_noGdalResolution.tif \
reprojected_block_32_28GCPs_noGdalResolution.tif \
reprojected_block_33_28GCPs_noGdalResolution.tif \
reprojected_block_34_28GCPs_noGdalResolution.tif \
reprojected_block_35_28GCPs_noGdalResolution.tif \
reprojected_block_36_28GCPs_noGdalResolution.tif \
merged_blocks_10_to_36_0_to_180_smallSize_byte_nodata_reprojectTo9810.tif


-r bilinear\
-s_srs "EPSG:4326"\
-t_srs "EPSG:4326"\
-overwrite\
-tps\
-co TILED=YES\
--config CENTER_LONG +180\
-srcnodata 0\
-dstnodata 0 \


