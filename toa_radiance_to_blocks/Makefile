Exe = /home/mare/Ehsan_lab/MISR-roughness/scripts/exe_dir
program = TOA
src = TOA.c

all:
	gcc -I/home/mare/Ehsan_lab/Ehsan_Mtk_root/Mtk-1.4.5/include -I/home/mare/Ehsan_lab/Ehsan_Mtk_root/hdfeoslibs/include -L/home/mare/Ehsan_lab/Ehsan_Mtk_root/Mtk-1.4.5/lib -o ${Exe}/${program} ${src} -lMisrToolkit  -lm -lfftw3	
	
clean:

	rm ${Exe}/${program}
