
all:
	
	gcc -I/home/mare/Ehsan_lab/Ehsan_Mtk_root/Mtk-1.4.5/include -I/home/mare/Ehsan_lab/Ehsan_Mtk_root/hdfeoslibs/include -L/home/mare/Ehsan_lab/Ehsan_Mtk_root/Mtk-1.4.5/lib -o TOA_exe_Pouya TOA.c -lMisrToolkit  -lm -lfftw3
	
	./TOA_exe_Pouya "MISR_AM1_GRP_ELLIPSOID_GM_P091_O008237_AN_F03_0024.hdf" 1 2 0 "/media/mare/MISR_REPO/MISR_root/toa_images/toa_P091_O008237_b1_an.dat"
	
	
clean:
	rm TOAexe
