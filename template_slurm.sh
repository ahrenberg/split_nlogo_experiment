#!/bin/bash
#SBATCH --job-name={experiment}
#SBATCH --output=%x-%A_%a.out
#SBATCH --error=%x-%A_%a.err
#SBATCH --array=1-{numexps}

echo "Model: {modelname}"
echo "Experiment: {experiment}_${SLURM_ARRAY_TASK_ID}"

netlogo-headless.sh \
    --model {model} \
    --setup-file {experiment}_${SLURM_ARRAY_TASK_ID}.xml \
    --table {csvfpath}/{experiment}_${SLURM_ARRAY_TASK_ID}.csv

### DEBUG
# {experiment} - [experiment] - The value of the parameter experiment.
# {model} - [model] - The value of the parameter nlogofile.
# {modelname} - [modelname] - Model name.
# {csvfpath} - [csvfpath] - The value of the parameter csv_output_dir.
