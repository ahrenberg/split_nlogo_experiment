#!/bin/bash
### XXX adjust the field width %3a for the number of tasks in the job array
#SBATCH --job-name={experiment}
#SBATCH --output=%x-%A_%3a.out
#SBATCH --error=%x-%A_%3a.err
#SBATCH --array=1-{numexps}

ne={numexps}
formatstr="%0${#ne}d"
my_task_id=$( printf $formatstr $SLURM_ARRAY_TASK_ID )

echo "Model: {modelname}"
echo "Experiment: {experiment}_${my_task_id}"

netlogo-headless.sh \
    --model {model} \
    --setup-file {experiment}_${my_task_id}.xml \
    --table {csvfpath}/{experiment}_${my_task_id}.csv

### DEBUG
# {experiment} - [experiment] - The value of the parameter experiment.
# {model} - [model] - The value of the parameter nlogofile.
# {modelname} - [modelname] - Model name.
# {csvfpath} - [csvfpath] - The value of the parameter csv_output_dir.
# {numexps} - [numexps] - Total number of experiments.
