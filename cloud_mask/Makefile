#!/usr/bin/env python

src_name=ReadASCMFile.c
exe_path=/data/gpfs/home/emosadegh/MISR-roughness/exe_dir
exe_name=ReadASCMCloudMask

all:
	gcc -I/Users/ehsanmos/Documents/MISR/mtk_root/Mtk-1.5.0/include 	\
		-I/Users/ehsanmos/Documents/MISR/mtk_root/hdfeoslibs/include 	\
		-L/Users/ehsanmos/Documents/MISR/mtk_root/Mtk-1.5.0/lib 		\
		-L/Users/ehsanmos/Documents/MISR/mtk_root/fftw-3.3.8_install/lib \
		-I/Users/ehsanmos/Documents/MISR/mtk_root/fftw-3.3.8_install/include \
		-o ${exe_path}/${exe_name} ${src_name} -lMisrToolkit  -lm -lfftw3 -lpng
	
clean:

	rm ${exe_path}/${exe_name}