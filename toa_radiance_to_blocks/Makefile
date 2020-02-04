Exe_path=/home/mare/Ehsan_lab/MISR-roughness/exe_dir
program=TOARad2blocks
src=TOARad2BlocksAllBlocks.c #TOARad2Blocks_noblokcs1to6.c #TOARad2BlocksAllBlocks.c

all:
	gcc -I/home/mare/Ehsan_lab/Ehsan_Mtk_root/Mtk-1.4.5/include -I/home/mare/Ehsan_lab/Ehsan_Mtk_root/hdfeoslibs/include -L/home/mare/Ehsan_lab/Ehsan_Mtk_root/Mtk-1.4.5/lib -o ${Exe_path}/${program} ${src} -lMisrToolkit  -lm -lfftw3	
	
clean:

	rm ${Exe}/${program}
