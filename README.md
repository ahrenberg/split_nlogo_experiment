# split_nlogo_experiment

Splits NetLogo BehaviorSpace experiments, creating one XML setup file per 
possible variable value combination.


Author: Lukas Ahrenberg <lukas@ahrenberg.se>

License: GNU GPL-3.0. See LICENSE file for details.


## About

This script was written to ease the burden of running 
[NetLogo](https://ccl.northwestern.edu/netlogo/) simulations on computing grids.
It parses a `.nlogo` file, looking for the `<experiments>` XML setup, and then 
constructs unique setup files for each variable value combination in the 
experiment. Each of these files represents a single simulation and can be run 
simultaneously on a computing cluster using `netlogo-headless.sh` with the 
`--setup-file` switch.

In addition `split_nlogo_experiment` has basic templating functionality that 
can be used to automatically generate a job array script.


## Requirements and testing

`split_nlogo_experiment` requires [Python](https://www.python.org) and has been 
tested with Python 2.7 and 3.6, other Python3 versions should work as well, and 
perhaps also Python 2.6 (though this has not been tested).

The generated XML files was tested with BehaviorSpace in NetLogo 4.1.3 and 
5.0RC7.


## Installation
See `INSTALL.md`


## Brief manual

For a full list of options run: 

    split_nlogo_experiment -h


### Basic usage

To split an experiment called 'experiment' in the file model.nlogo use:

    split_nlogo_experiment model.nlogo experiment

This will produce a set of files called `experiment_<XYZ>.xml` where `<XYZ>` is 
a zero-padded number. Each XML file represents a unique variable value 
combination as an experiment. These files can be used with the NetLogo switch 
`--setup-file`, e.g. to run the first value combination:

    netlogo-headless.sh --model model.nlogo --setup-file experiment_0.xml

The XML files are always given the name of the experiment plus a sequence 
number. If you want to prefix the file name for some reason you can use the 
`--output_prefix` option when calling `split_nlogo_experiment`. If you want the 
XML files output in some other directory than the current use the 
`--output_dir` option. For instance:

    split_nlogo_experiment --output_dir /tmp --output_prefix my_model.nlogo experiment

will cause the XML files to be saved in the directory `/tmp` and be named 
`experiment_<XYZ>.xml` where `<XYZ>` is, as before, a number from 1 up to N, N 
being the number of possible variable value combinations.

Note that all the output directory must exist and be writable. If not an error 
is produced and the program exits.

### How many XML files are generated?

Short answer: as many as you have unique combinations of variable values in 
your BehaviorSpace times the number of repetitions you decide to 'break out' 
using the --repetitions_per_run switch. 

For example if you have two variables `a`, and `b`, and you have configured 
your BehaviorSpace so that `[a 1 2 3]` and `[b 4 5]`, That is, there are three 
possible values for `a` (1, 2, or 3), and two for `b` (4 or 5). There are six 
combinations of individual values for `a`, and `b`. (`a=1`, `b=4`) (`a=1`, 
`b=5`), (`a=2`, `b=4`), etc. `split_nlogo_experiment` will construct one XML 
file for each of these combinations and number them from `1` to `6`.

Further, assume that you have set the number of repetitions in your 
BehaviorSpace experiment to be 10. By default `split_nlogo_experiment` will 
preserve this so that you end up with 6 unique files, each creating a run 
repeating 10 times. However if you had invoked `split_nlogo_experiment` with 
the switch `--repetitions_per_run 2`, you would end up with 30 files (6 
variable combinations, each copied 5 times) set up to run the experiment 2 
times each. Likewise using `--repetitions_per_run 5` would create 12 files, 
each repeating the run 5 times.

### Start script templating functionality

Computing clusters usually have a queuing mechanism where some job script is 
submitted in order to run a job. If the BehaviorSpace experiment results in a 
large number of simulations, this can be a very tedious process if one needs an 
individual script for each simulation. 

`split_nlogo_experiment` has a very basic templating mechanism that may be used 
to produce a single job-array script which deals with every simulation XML 
file. The option `--create_script` takes a file name as parameter. This file is 
read and a specialized version having key names replaced with current values 
are saved for each XML file. Allowed keys are:

* `{model}`
  * The value of the parameter nlogofile.
* `{modelname}`
  * The model name, i.e. .nlogo filename without the extension.
* `{experiment}`
  * The value of the parameter experiment.
* `{csvfpath}`
  * Directory where CSV files will be placed.
* `{numexps}`
  * Total number of experiments.

As an example consider constructing a Slurm script for each experiment. This 
script will issue special Slurm commands creating log files, setting the job 
name, and finally run `netlogo-headless.sh` with the right commands. To do this 
create a template file looking like:

```bash
#!/bin/bash
#SBATCH --job-name={experiment}
#SBATCH --output=%x-%A_%2a.out
#SBATCH --error=%x-%A_%2a.err
#SBATCH --array=1-{numexps}
#SBATCH --mem=40G
    
ne={numexps}
formatstr="%0${#ne}d"
my_task_id=$( printf $formatstr $SLURM_ARRAY_TASK_ID )

netlogo-headless.sh \
    --model {model} \
    --setup-file {experiment}_${my_task_id}.xml \
    --table {csvfpath}/{experiment}_${my_task_id}.csv
```

Assume this file is called `template_slurm.sh`, then calling 
`split_nlogo_experiment` as:

    split_nlogo_experiment --create_script template_slurm.sh model.nlogo experiment

will, in addition to creating the `experiment_<XYZ>.xml` files also create 
files called `experiment_script.sh` (file ending will always be the same as for 
the template file). In these files the keys `{xxx}` will be replaced according 
to the list above. An annotated example template is included in this source 
repository.

`split_nlogo_experiment` looks up the absolute path to any file and directory 
given and use this for the keys. The reason for doing so is that the 
`netlogo-headless.sh` script make the simulation always run in the netlogo 
directory. This has the side effect that relative paths will not work. As a 
work around the script translates all paths to absolute paths. If you want to 
suppress this behavior and always use the file names and paths as given when 
calling `split_nlogo_experiment` use the `--no_path_translation` switch.


## Appendix

### The problem

When constructing simulations it is often desirable to run them with a range of 
different parameter values in order to investigate each parameter's impact on 
the overall process. In NetLogo such runs are easily configured using the 
Behavioral space editor where variables can be assigns arbitrary value ranges. 
Each possible value of variable values result in an unique simulation run 
however, and for scientific experiments the number of runs can easily grow 
huge. NetLogo can run these simulations in parallel threads, but does currently 
not have native support to distribute them over a grid of computers. This must 
be done by hand. Neither is there functionality to generate individual setup 
files from the BehaviorSpace editor.

`split_nlogo_experiment` was written to do just that.


### Technicalities

`split_nlogo_experiment` searches the experiment XML description for 
`enumeratedValueSet` tags with more than one value as well as `steppedValueSet` 
tags. The XML of these nodes are parsed, and the values for the associated 
variable stored. Following this, one new experiment for every possible 
variable-value combination is built where the multi-valued tags have been 
replaced by `enumeratedValueSet` tags carrying a single possible value. These 
are saved to XML files.

Please note that as the program constructs all possible combinations of 
variable values it is necessary to expand the value sets in the original 
experiment. (Value sets are the variables you give on a `[start step stop]` 
form.) There is a general problem with rounding errors programming such 
functions in any language, and this leads to a somewhat different behavior for 
integers and floating point value sets in NetLogo experiments. For an example 
try the ranges `[0 2 12]` and `[0 0.2 1.2]` for some variable in the 
BehaviorSpace editor of NetLogo 4.1.3. The former range will give you 7 runs, 
while the latter only yields 6. I have made an effort to mimic this behavior 
when I expand the value sets and build experiments. As it is two different 
implementations and two different programming languages however, there could be 
cases when you do not get the number of runs NetLogo tells you. If so, please 
let me know about it.

