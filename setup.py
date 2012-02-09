

from split_nlogo_experiment import __version__, __author__, __license__

from split_nlogo_experiment import __doc__ as doclines

import sys

import os

from distutils.core import setup

import shutil



if __name__ == "__main__":
    # This is probably not a pretty way of doing things, but I want the 
    # installed script to be without file name, but the source file to have 
    # the .py extension.
    # I could not find any information in the distutils documentation about 
    # changing names when installing so instead I create a copy with a new name
    # and let the setup script work on this. Should be OK for sdists and
    # installations.
    # Probably there's a much better way.
    if not os.path.exists("./scripts/") :
        os.mkdir("./scripts")

    shutil.copy2("split_nlogo_experiment.py", "./scripts/split_nlogo_experiment")


    setup(
        name = "split_nlogo_experiment",
        description = doclines.replace('\n',' '),
        author = "Lukas Ahrenberg",
        author_email = "lukas@ahrenberg.se",
        url = "https://github.com/ahrenberg/split_nlogo_experiment",
        license = __license__,
        version = __version__,
        scripts = ["scripts/split_nlogo_experiment"]
        )
