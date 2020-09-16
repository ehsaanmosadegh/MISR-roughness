#!/bin/bash

#SBATCH --job-name=MISR2Roughness


			       

## --- hybrid 
##SBATCH --nodes=2
##SBATCH --ntasks=2
##SBATCH --cpus-per-task=8
##SBATCH --hint=compute_bound

## --- multi-processor/threaded
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --threads-per-core=2
##SBATCH --hint=compute_bound

# --- MPI
##SBATCH --ntasks=128
##SBATCH --cpus-per-task=1
##SBATCH --nodes=16
##SBATCH --ntasks-per-node=8
##SBATCH --ntasks-per-socket=4

##SBATCH --mem=1gb                                # Job memory request
#SBATCH --mem-per-cpu=4000M        		 # Allocate 3.5GB of memory per CPU

#SBATCH --time=14-00:00				 # sets the max. run time; format: D-HH:MM
#SBATCH --partition=cpu             		 # Submit job to the cpu partition
#SBATCH --mail-type=ALL             		 # Send mail on all state changes

#SBATCH --output=logs/log.cmaq.test   		 # The output file name
#SBATCH --error=logs/log.error.test		 # The error file nam
#SBATCH --mail-user=ehsanm@dri.edu

##---------------------------------------------------------

hostname
date

module load intel/compiler/64/2018/18.0.1
module list 

@ cores_per_task = $SLURM_CPUS_PER_TASK / 2

echo "===================================================="
echo "***** Some runtime informartiuon *****"
echo "===> Total number of nodes in the job's resource allocation is = $SLURM_JOB_NUM_NODES"
echo "===> Name of the partition in which the job is running is = $SLURM_JOB_PARTITION"
echo "===> List of nodes allocated to the job is = $SLURM_JOB_NODELIST"
echo "===> Number of cpus requested per task is = $SLURM_CPUS_PER_TASK (=threads)"
echo "===> Number of COREs per task is = $cores_per_task"
echo "===> Number of hyperthreaded CPUS on each allocated node is = $SLURM_CPUS_ON_NODE"
echo "===> Count of processors available to the job on this node is = $SLURM_JOB_CPUS_PER_NODE"
echo "===> Name of the job is = $SLURM_JOB_NAME"
echo "===> Memory per cpu is = $SLURM_MEM_PER_CPU MB"
echo "===> The MPI rank (or relative process ID) of the current process is = $SLURM_PROCID"
echo "===> The directory from which sbatch was invoked is = $SLURM_SUBMIT_DIR"
echo "===> The hostname of the computer from which sbatch was invoked is = $SLURM_SUBMIT_HOST"
echo "===> Name of the node running the job script is = $SLURMD_NODENAME"
echo "===================================================="

echo “===> job script starts here...”

##setenv I_MPI_PMI_LIBRARY "/cm/shared/apps/slurm/17.02.2/lib64/libpmi.so"

source run_cctm_CA.csh 

echo “===> job script ends here...”

date
