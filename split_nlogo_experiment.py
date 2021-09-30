#!/usr/bin/env python3

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Python script for breaking up Netlogo .nlogo models containing behavioral space
experiments with value sets and lists leading to multiple runs into XML files
containing a single value combination. Sometimes useful when setting up
experiments to run com computer clusters. 
"""

__author__ = "Lukas Ahrenberg <lukas@ahrenberg.se>"

__license__ = "GPL3"

__version__ = "0.3"


import sys

import os.path

import argparse

from xml.dom import minidom

from string import Formatter

import csv

def expandValueSets( value_tuples):
    """
    Recursive generator giving the different combinations of variable values.
    
    Parameters
    ----------
    
    value_tuples : list
       List of tuples, each tuple is on the form 
       (variable_name, [value_0, value_1, ... , value_N])
       where the value list is the possible values for that variable.
       
    Yields
    ------
       : Each yield results in a list of unique variable_name and value 
       combination for all variables listed in the original value_tuples.
    
    """
    if len(value_tuples) == 1:
        for val in value_tuples[0][1]:
            yield [(value_tuples[0][0], val)]
    else:            
        for val in value_tuples[0][1]:
            for vlist in expandValueSets(value_tuples[1:]):
                yield [(value_tuples[0][0], val)] + vlist

def steppedValueSet(first, step, last):
    """
    Tries to mimic the functionality of BehaviorSpace SteppedValueSet class.
    
    Parameters
    ----------
    
    first : float
       Start of value set.
       
    step : float
       Step length of value set.

    last : float
       Last value of the set. Inclusive in most cases, but may be exclusive 
       due to floating point rounding errors. This is as BehavioirSpace 
       implements it.


    Returns
    -------

    values : list
       The values between first and last taken with step length step.

    """
    # May look backward, but this will have the same rounding behavior
    # as the BehaviorSpace code as far as I can tell.
    n = 0
    val = first
    values = []
    while val <= last:
        values.append(val)
        n+=1
        val = first + n * step

    return values


def saveExperimentToXMLFile(experiment, xmlfile):
    """
    Given an experiment XML node saves it to a file wrapped in an experiments tag.
    The file is also furnished with DOCTYPE tag recognized by netlogo.
    File name will be the experiment name followed by the experiment number (zero padded), optionally prefixed.

    Parameters
    ----------
    
    experiment : xml node
       An experiment tag node and its children.

    xmlfile : file pointer
       File opened for writing.
    """

    xmlfile.write("""<?xml version="1.0" encoding="us-ascii"?>\n""")
    xmlfile.write("""<!DOCTYPE experiments SYSTEM "behaviorspace.dtd">\n""")
    xmlfile.write("""<experiments>\n""")
    experiment.writexml(xmlfile)
    xmlfile.write("""</experiments>\n""")
    


def createArrayScriptFile(script_fp,
                     nlogofile,
                     experiment,
                     numexps,
                     script_template,
                     csv_output_dir="."
                     ):
    """
    Create an array job script file from a template string.

    Parameters
    ----------

    script_fp : file pointer
       File opened for writing.

    nlogofile : string
       File name and path of the nlogo model file.
       This string will be accessible through the key {model}
       in the script_template string.

    experiment : string
       Name of the experiment.
       This string will be accessible through the key {experiment}
       in the script_template string.

    combination_nr : int
       The experiment combination number.
       This value will be accessible through the key {combination}
       in the script_template string.

    numexps : int
       Number of experiments.
       This value will be accessible through the key {numexps}

    script_template : str
       The script template string. This string will be cloned for each script
       but the following keys can be used and will have individual values.
       {model} - The value of the parameter nlogofile.
       {experiment} - The value of the parameter experiment.
       {csvfpath} - The value of the parameter csv_output_dir.

    csv_output_dir : str, optional
       Path to the directory containing the CSV files.
       keys.


    Returns
    -------

    file_name : str
       Name of the file name used for the script.

    """

    modelname = os.path.basename(nlogofile).split('.')[0]

    strformatter = Formatter()
    formatmap = {
        "experiment": experiment,
        "numexps": numexps,
        "model": nlogofile,
        "modelname": modelname,
        "csvfpath": csv_output_dir
        }
    # Use string formatter to go through the script template and
    # look for unknown keys. Do not replace them, but print warning.
    for _, fn, _, _ in strformatter.parse(script_template):
        if fn is not None and fn not in formatmap.keys():
            print(f"Warning: Unsupported key '{{{fn}}}' in script template. Ignoring.")
            formatmap[fn] = f"{{{fn}}}"

    script_fp.write(script_template.format(**formatmap))


                          
if __name__ == "__main__":
    aparser = argparse.ArgumentParser(description = "Split nlogo behavioral space experiments.")
    aparser.add_argument("nlogo_file", help = "Netlogo .nlogo file with the original experiment")
    aparser.add_argument("experiment", nargs = "*", help = "Name of one or more experiments in the nlogo file to expand. If none are given, --all_experiments must be set.")
    aparser.add_argument("--all_experiments", action="store_true", help = "If set all experiments in the .nlogo file will be expanded.")
    aparser.add_argument("--repetitions_per_run", type=int, nargs = 1, help="Number of repetitions per generated experiment run. If the nlogo file is set to repeat an experiment N times, these will be split into N/n individual experiment runs (each repeating n times), where n is the argument given to this switch. Note that if n does not divide N this operation will result in a lower number of total repetitions.")
    aparser.add_argument("--output_dir", default="./", help = "Path to output directory if not current directory.")
    aparser.add_argument("--output_prefix", default="", help = "Generated files are named after the experiment, if set, the value given for this option will be prefixed to that name.")
    # Scripting options.
    aparser.add_argument("--create_script", dest = "script_template_file", help = "Tell the program to generate script files (for instance PBS files) alongside the xml setup files. A template file must be provided. See the external documentation for more details.")
    aparser.add_argument("--script_output_dir", help = "Path to output directory for script files. If not specified, the same directory as for the xml setup files is used.")
    aparser.add_argument("--csv_output_dir", help = "Path to output directory where the table data from the simulations will be saved. Use with script files to set output directory for executed scripts. If not specified, the same directory as for the xml setup files is used.")
    aparser.add_argument("--create_run_table", action="store_true", help = "Create a csv file containing a table of run numbers and corresponding parameter values. Will be named as the experiment but postfixed with '_run_table.csv'.")
    aparser.add_argument("--no_path_translation", action="store_true", help = "Turn off automatic path translation when generating scripts. Advanced use. By default all file and directory paths given are translated into absolute paths, and the existence of directories are tested. (This is because netlogo-headless.sh always run in the netlogo directory, which create problems with relative paths.) However automatic path translation may cause problems for users who, for instance, want to give paths that do yet exist, or split experiments on a different file system from where the simulations will run. In such cases enabling this option preserves the paths given to the program as they are and it is up to the user to make sure these will work.")
    aparser.add_argument("-v", "--version", action = "version", version = f"split_nlogo_experiment version {__version__}")
    
    argument_ns = aparser.parse_args()


    # Check so that there's either experiments listed, or the all_experiments switch is set.
    if len(argument_ns.experiment) < 1 and argument_ns.all_experiments == False:
        print("Warning. You must either list one or more experiments to expand, or use the --all_experiments switch.")
        sys.exit(0)

    experiments_xml = ""
    try:
        with open(argument_ns.nlogo_file) as nlogof:
            # An .nlogo file contain a lot of non-xml data
            # this is a hack to ignore those lines and
            # read the experiments data into an xml string
            # that can be parsed.
            nlogo_text = nlogof.read()
            alist = nlogo_text.split("<experiments>")
            for elem in alist[1:]:
                blist = elem.split("</experiments>")
                experiments_xml += f"<experiments>{blist[0]}</experiments>\n"
    except IOError as ioe:
        sys.stderr.write(ioe.strerror + f" '{ioe.filename}'\n")
        sys.exit(ioe.errno)


    # Absolute paths.
    # We create absolute paths for some files and paths in case given relative.

    if argument_ns.no_path_translation == False:
        argument_ns.output_dir = os.path.abspath(argument_ns.output_dir)

    if argument_ns.script_output_dir == None:
        argument_ns.script_output_dir = argument_ns.output_dir
    elif argument_ns.no_path_translation == False:
        argument_ns.script_output_dir = os.path.abspath(argument_ns.script_output_dir)

    if argument_ns.csv_output_dir == None:
        argument_ns.csv_output_dir = argument_ns.output_dir
    elif argument_ns.no_path_translation == False:
        argument_ns.csv_output_dir = os.path.abspath(argument_ns.csv_output_dir)

    # This is the absolute path name of the nlogo model file.
    if argument_ns.no_path_translation == False:
        nlogo_file_abs = os.path.abspath(argument_ns.nlogo_file)
    else:
        nlogo_file_abs = argument_ns.nlogo_file

    # Check if scripts should be generated and read the template file.
    if argument_ns.script_template_file != None:
        script_extension = os.path.splitext(argument_ns.script_template_file)[1]
        try:
            with open(argument_ns.script_template_file) as pbst:
                script_template_string = pbst.read()
        except IOError as ioe:
            sys.stderr.write(ioe.strerror + f" '{ioe.filename}'\n")
            sys.exit(ioe.errno)

            sys.stdout.write(f"tst {argument_ns.repetitions_per_run}: ")
        

    # Start processing.

    original_dom = minidom.parseString(experiments_xml)
    # Need a document to create nodes.
    # Create a new experiments document to use as container.
    experimentDoc = minidom.getDOMImplementation().createDocument(None, "experiments", None)    

    # Remember which experiments were processed.
    processed_experiments = []
    
    for orig_experiment in original_dom.getElementsByTagName("experiment"):


        if argument_ns.all_experiments == True \
                or orig_experiment.getAttribute("name") \
                in argument_ns.experiment:

            processed_experiments.append(orig_experiment.getAttribute("name"))

            experiment = orig_experiment.cloneNode(deep = True)

            # Store tuples of varying variables and their possible values.
            value_tuples = []
            num_individual_runs = 1

            # Number of repetieitons.
            # In the experiment.
            # Read original value first. Default is to have all internal.
            reps_in_experiment = int(experiment.getAttribute("repetitions"));
            # Repeats of the created experiment.
            reps_of_experiment = 1;
            # Check if we should split experiments. An unset switch or value <= 0 means no splitting.
            if argument_ns.repetitions_per_run != None \
                    and argument_ns.repetitions_per_run[0] > 0:
                original_reps = int(experiment.getAttribute("repetitions"))
                if original_reps >= argument_ns.repetitions_per_run[0]:
                    reps_in_experiment = int(argument_ns.repetitions_per_run[0])
                    reps_of_experiment = int(original_reps / reps_in_experiment)
                    if(original_reps % reps_in_experiment != 0):
                        sys.stderr.write(f"Warning: Number of repetitions per experiment does not divide the number of repetitions in the nlogo file. New number of repetitions is {(reps_in_experiment*reps_of_experiment)} ({reps_in_experiment} per experiment in {reps_of_experiment} unique script(s)). Original number of repetitions per experiment: {original_reps}.\n")

            # Handle enumeratedValueSets
            for evs in experiment.getElementsByTagName("enumeratedValueSet"):
                values = evs.getElementsByTagName("value")
                # If an enumeratedValueSet has more than a single value, it should
                # be included in the value expansion tuples.
                if len(values) > 1:
                    # A tuple is the name of the variable and
                    # A list of all the values.
                    value_tuples.append((evs.getAttribute("variable"), 
                                         [val.getAttribute("value") \
                                              for val in values]
                                         )
                                        )
                    num_individual_runs *= len(value_tuples[-1][1])
                    # Remove the node.
                    experiment.removeChild(evs)
                    

            # Handle steppedValueSet
            for svs in experiment.getElementsByTagName("steppedValueSet"):
                first = float(svs.getAttribute("first"))
                last = float(svs.getAttribute("last"))
                step = float(svs.getAttribute("step"))
                # Add values to the tuple list.
                value_tuples.append((svs.getAttribute("variable"),
                                     steppedValueSet(first, step, last)
                                     )
                                    )
                num_individual_runs *= len(value_tuples[-1][1])
                # Remove node.
                experiment.removeChild(svs)

            
            # Now create the different individual runs.
            enum = 1
            # Keep track of the parameter values in a run table.
            run_table = []
            ENR_STR = "Experiment number"
            if num_individual_runs > 1:
                vsgen = expandValueSets(value_tuples)
            else:
                # If there were no experiments to expand create a dummy-
                # expansion just to make sure the single experiment is still
                # created.
                vsgen = [[]]

            for exp in vsgen:
                for exp_clone in range(reps_of_experiment):
                    # Add header in case we are on the first row.
                    if enum < 1:
                        run_table.append([ENR_STR])
                    run_table.append([enum])

                    experiment_instance = experiment.cloneNode(deep = True)
                    experiment_instance.setAttribute("repetitions",str(reps_in_experiment))
                    for evs_name, evs_value in exp:
                        evs = experimentDoc.createElement("enumeratedValueSet")
                        evs.setAttribute("variable", evs_name)
                        vnode = experimentDoc.createElement("value")
                        vnode.setAttribute("value", str(evs_value))
                        evs.appendChild(vnode)
                        experiment_instance.appendChild(evs)

                        # Add header in case we are on first pass.
                        if enum < 1:
                            run_table[0].append(evs_name)
                        # Always add the current value.
                        run_table[-1].append(evs_value)

                    # Replace some special characters (including space) with chars that may cause problems in a file name.
                    # This is NOT fail safe right now. Assuming some form of useful experiment naming practice.
                    experiment_name = experiment_instance.getAttribute("name").replace(' ', '_').replace('/', '-').replace('\\','-')
                    xml_filename = os.path.join(argument_ns.output_dir, 
                                                argument_ns.output_prefix + experiment_name
                                                + '_'
                                                + str(enum)
                                                + '.xml')
                    try:
                        with open(xml_filename, 'w') as xmlfile:
                            saveExperimentToXMLFile(experiment_instance, xmlfile)

                    except IOError as ioe:
                        sys.stderr.write(ioe.strerror + f" '{ioe.filename}'\n")
                        sys.exit(ioe.errno)

                    enum += 1
            # Check if the run table should be saved.
            if argument_ns.create_run_table == True:
                run_table_file_name = os.path.join(argument_ns.output_dir, 
                                                   argument_ns.output_prefix 
                                                   + experiment_name
                                                   + "_run_table.csv")
                try:
                    with open(run_table_file_name, 'w') as run_table_file:
                        rt_csv_writer =  csv.writer(run_table_file)
                        for row in run_table:
                            rt_csv_writer.writerow(row)
                except IOError as ioe:
                    sys.stderr.write(ioe.strerror + f" '{ioe.filename}'\n")
                    sys.exit(ioe.errno)


    # Should a script file be created?
    numexps = enum - 1
    if argument_ns.script_template_file != None:
        script_file_name = os.path.join(argument_ns.script_output_dir, 
                                        argument_ns.output_prefix 
                                        + experiment_name
                                        + "_script"
                                        + script_extension)
        try:
            print(f'DEBUG: numexps = {numexps}')
            with open(script_file_name, 'w') as scriptfile:
                createArrayScriptFile(
                    scriptfile,
                    nlogo_file_abs,
                    experiment.getAttribute("name"),
                    numexps,
                    script_template_string,
                    csv_output_dir=argument_ns.csv_output_dir,
                    )
        except IOError as ioe:
            sys.stderr.write(ioe.strerror + f" '{ioe.filename}'\n")
            sys.exit(ioe.errno)

    # Warn if some experiments could not be found in the file.
    for ename in argument_ns.experiment:
        if ename not in processed_experiments:
            print(f"Warning - Experiment named '{ename}' not found in model file '{argument_ns.nlogo_file}'")
