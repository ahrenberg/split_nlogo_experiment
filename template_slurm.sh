#!/bin/bash
### XXX adjust the field width %3a for the number of tasks in the job array:
###     2 if you have tens, 3 if you have hundreds, etc.
#SBATCH --job-name={experiment}
#SBATCH --output=%x-%A_%3a.out
#SBATCH --error=%x-%A_%3a.err
#SBATCH --array=1-{numexps}
#SBATCH --mem=40G

module load netlogo/5.3.1

ne={numexps}
formatstr="%0${#ne}d"
my_task_id=$( printf $formatstr $SLURM_ARRAY_TASK_ID )

echo "Model: {modelname}"
echo "Experiment: {experiment}_${my_task_id}"

java -cp ${NETLOGOHOME}/app/NetLogo.jar \
    org.nlogo.headless.Main \
    --model {model} \
    --setup-file {experiment}_${my_task_id}.xml \
    --table {csvfpath}/{experiment}_${my_task_id}.csv

### DEBUG
# {model} - [model] - The value of the parameter nlogofile.
# {experiment} - [experiment] - The value of the parameter experiment.
# {modelname} - [modelname] - Model name.
# {csvfpath} - [csvfpath] - The value of the parameter csv_output_dir.
# {numexps} - [numexps] - Total number of experiments.
