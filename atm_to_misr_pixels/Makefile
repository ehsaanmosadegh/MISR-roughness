Exe = /home/mare/Ehsan_lab/MISR-roughness/exe_dir
src = atm_to_misr_pixels.c
program = ATMtoMISRPixels

all:
	gcc -I/home/mare/Ehsan_lab/Ehsan_Mtk_root/Mtk-1.4.5/include -I/home/mare/Ehsan_lab/Ehsan_Mtk_root/hdfeoslibs/include -L/home/mare/Ehsan_lab/Ehsan_Mtk_root/Mtk-1.4.5/lib -o ${Exe}/${program} ${src} -lMisrToolkit  -lm
	
clean:

	rm ${Exe}/${program}
	