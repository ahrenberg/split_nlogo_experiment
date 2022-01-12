# split_nlogo_experiment installation instructions

## Using setup.py

**CAUTION** It is not recommended to use the `setup.py` file for installation.

The easiest way to install is to run the setup.py script as:

    python setup.py install

This may require super user privileges (so you may have to put a `sudo` in 
front, or run it as root). You can also install it in your own home directory 
by using the `--user` switch:

    python setup.py install --user

The above will cause split_nlogo_experiment to be installed in your home 
directory (on Un\*x/Linux systems in `~/.local/bin` by default). If you go for 
this option you may need to edit your `$PATH` variable.

Run `python setup.py --help` for many more options regarding the `setup.py` 
script.


## By hand

Simply copy the file `split_nlogo_experiment.py` to a directory in your
`PATH`. E.g. if you have `~/bin` in your `PATH`:
```
$ chmod +x split_nlogo_experiment.py
$ cp split_nlogo_experiment.py ~/bin/split_nlogo_experiment
```

N.B. we have dropped the `.py` extension: that keeps the following
documentation consistent.
