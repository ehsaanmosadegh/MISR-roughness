#!/bin/bash
##---------------------------------------------------------
#SBATCH --job-name=cloud
##---------------------------------------------------------
##           select partition
##---------------------------------------------------------
## (test partition for QualityAssurance)

##SBATCH --account=cpu-s6-test-0 
##SBATCH --partition=cpu-s6-test-0

##---------------------------------------------------------
## (MISR_roughness partition)

#SBATCH --account=cpu-s5-misr_roughness-0
#SBATCH --partition=cpu-core-0			 			# Submit job to the cpu partition

##---------------------------------------------------------
##           set configuration
##---------------------------------------------------------
## --- multi-core/threaded

#SBATCH --ntasks=1
#SBATCH --ntasks-per-core=1


#SBATCH --mail-type=ALL             		 # Send mail on all state changes
#SBATCH --mail-user=ehsanmos@icloud.com

#SBATCH --output=log2_cm.txt   				 # The output file name
#SBATCH --error=log2_cm.txt				 	# The error file nam





## old settings:
##SBATCH --cores-per-socket=30  --> error
##SBATCH --hint=compute_bound
##SBATCH --nodes=1
##SBATCH --mem=1gb                                # Job memory request
##SBATCH --mem-per-cpu=4000M        		 	# Allocate 3.5GB of memory per CPU
##SBATCH --time=14-00:00				 		# sets the max. run time; format: D-HH:MM

##---------------------------------------------------------
##			set run script
##---------------------------------------------------------
##hostname
date

## module load intel/compiler/64/2018/18.0.1
module list 


echo “MISR job started ...”

# MISR2Roughness_parallel
python /data/gpfs/home/emosadegh/MISR-roughness/cloud_mask/run_ReadASCMFile.py 


echo “MISR job ended ...”

date
