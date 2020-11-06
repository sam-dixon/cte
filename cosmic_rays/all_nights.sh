#!/bin/bash
#SBATCH --qos=debug
#SBATCH --nodes=4
#SBATCH --time=30:00
#SBATCH --licenses=cscratch1
#SBATCH --constraint=haswell

module load python/3.6-anaconda-4.4
source activate py3

srun -N 1 -n 1 -c 64 --cpu_bind=cores python nightly_tails.py 4 &
srun -N 1 -n 1 -c 64 --cpu_bind=cores python nightly_tails.py 5 &
srun -N 1 -n 1 -c 64 --cpu_bind=cores python nightly_tails.py 6 &
srun -N 1 -n 1 -c 64 --cpu_bind=cores python nightly_tails.py 7 &
srun -N 1 -n 1 -c 64 --cpu_bind=cores python nightly_tails.py 8 &
srun -N 1 -n 1 -c 64 --cpu_bind=cores python nightly_tails.py 9 &
srun -N 1 -n 1 -c 64 --cpu_bind=cores python nightly_tails.py 10 &
srun -N 1 -n 1 -c 64 --cpu_bind=cores python nightly_tails.py 11 &
wait