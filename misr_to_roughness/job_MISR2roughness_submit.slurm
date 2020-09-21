#!/bin/bash
##---------------------------------------------------------
#SBATCH --job-name=MISR2Roughness
##---------------------------------------------------------
## --- run on test account for QA

#SBATCH --account=cpu-s6-test-0 
#SBATCH --partition=cpu-s6-test-0
##---------------------------------------------------------
## --- multi-processor/threaded

##SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --threads-per-core=2
##SBATCH --hint=compute_bound


##SBATCH --mem=1gb                                # Job memory request
##SBATCH --mem-per-cpu=4000M        		 	# Allocate 3.5GB of memory per CPU

##SBATCH --time=14-00:00				 		# sets the max. run time; format: D-HH:MM
##SBATCH --partition=cpu             		 # Submit job to the cpu partition
#SBATCH --mail-type=ALL             		 # Send mail on all state changes

#SBATCH --output=logs/log_misr2roughness_test1   		 # The output file name
#SBATCH --error=logs/log_error_misr2roughness_test1		 	# The error file nam
#SBATCH --mail-user=ehsanmos@icloud.com
##---------------------------------------------------------

##hostname
date

## module load intel/compiler/64/2018/18.0.1
module list 


echo “===> MISR job starts here...”

./data/gpfs/home/emosadegh/MISR-roughness/exe_dir/MISR2Roughness_parallel

## MISR2Roughness_parallel

echo “===> MISR job ends here...”

date
