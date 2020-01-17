#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
##############################################
### N.E.Py.H. - Network Engineer Python Helper ###
##############################################

This program uses a Database in YAML format and a Template in Jinja2 format in order to generate configuration.
It's mandatory that the YAML file start with a list.
Mainly though for Network Elements, the render is done by creating a file for each dictionary in the list.
The filename is the value of the first dictionary found in the list.

### Source code info:
This code follow PEP 8 style guide and it use 4 spaces for indentation.
"""
import os # import OS module to create directory
import errno
import sys
import time
import types
import shutil
from jinja2 import Environment, FileSystemLoader #Import necessary functions from Jinja2 module
import yaml

__author__ = "Emanuele Rossi a.k.a. cyb3rw0lf"
__credits__ = ["cyb3rw0lf"]

__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "cyb3rw0lf"
__homepage__ = "https://github.com/cyb3rw0lf/nepyh"
__email__ = "cyb3rw0lf@protonmail.com"
__issues__ = "https://github.com/cyb3rw0lf/nepyh/issues"
__status__ = "Production"
__usage__ = "Chose a Database file in YAML format and a Template file in Jinja2 format. It's mandatory that YAML file start with a list."

file_tp = "templates/sample_tp.j2"
file_db = "sample_db.yml"
output_dir = "."

#Load data from YAML into Python dictionary
config_data = yaml.load(open(file_db), Loader=yaml.FullLoader)

#Load Jinja2 template
env = Environment(loader = FileSystemLoader(searchpath="."), trim_blocks=True, lstrip_blocks=True)
template = env.get_template(file_tp)

#Render the template with data and print the output
print("Creating templates...")
for entry in input_db:
    result = input_tp.render(entry)
    out_file = open(os.path.join(out_path, next(iter(entry.values())) + fileExt), "w")
    out_file.write(result)
    out_file.close()
    print("Configuration '%s' created..." % (next(iter(entry.values())) + fileExt))
print("DONE")
