#!/bin/bash
##---------------------------------------------------------
#SBATCH --job-name=MISRtest
##---------------------------------------------------------
## --- run on test account for QA

#SBATCH --account=cpu-s6-test-0 
#SBATCH --partition=cpu-s6-test-0

##---------------------------------------------------------
## --- run on MISR_roughness account/partition

##SBATCH --account=cpu-s5-misr_roughness-0
##SBATCH --partition=cpu-core-0			 			# Submit job to the cpu partition

##---------------------------------------------------------
## --- multi-core/threaded

#SBATCH -n 40 



##SBATCH --cores-per-socket=40 --> error

##SBATCH --ntasks=20
##SBATCH --cpus-per-task=30
##SBATCH --threads-per-core=2


#SBATCH --mail-type=ALL             		 # Send mail on all state changes
#SBATCH --mail-user=ehsanmos@icloud.com

#SBATCH --output=logs/log_misr2roughness_testPartition_2.txt   		 # The output file name
#SBATCH --error=logs/log_error_misr2roughness_testPartition_2.txt		 	# The error file nam


##SBATCH --hint=compute_bound
##SBATCH --nodes=1
##SBATCH --mem=1gb                                # Job memory request
##SBATCH --mem-per-cpu=4000M        		 	# Allocate 3.5GB of memory per CPU
##SBATCH --time=14-00:00				 		# sets the max. run time; format: D-HH:MM

##---------------------------------------------------------

##hostname
date

## module load intel/compiler/64/2018/18.0.1
module list 


echo “===> MISR job starts here...”

## ./data/gpfs/home/emosadegh/MISR-roughness/exe_dir/MISR2Roughness_parallel

MISR2Roughness_parallel

echo “===> MISR job ends here...”

date
