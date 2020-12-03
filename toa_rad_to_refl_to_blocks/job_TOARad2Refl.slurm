#!/bin/bash
#SBATCH --job-name=TOA
#SBATCH --account=cpu-s6-test-0 
#SBATCH --partition=cpu-s6-test-0
##SBATCH --account=cpu-s5-misr_roughness-0
##SBATCH --partition=cpu-core-0			 			# Submit job to the cpu partition
#SBATCH --ntasks=1
#SBATCH --ntasks-per-core=1
#SBATCH --mail-type=ALL             		 # Send mail on all state changes
#SBATCH --mail-user=emosadegh@nevada.unr.edu
#SBATCH --output=log1_toa2rad.txt   		 # The output file name
#SBATCH --error=log1_toa2rad.txt		 	# The error file nam
date
module list 
echo “MISR job started ...”
python /data/gpfs/home/emosadegh/MISR-roughness/toa_rad_to_refl_to_blocks/run_TOARad2Refl4AllBlocks.py
echo “MISR job ended ...”
date
