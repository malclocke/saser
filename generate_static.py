#! /usr/bin/env python
from jinja2 import Environment, FileSystemLoader
import sys

env = Environment(loader=FileSystemLoader('templates'))

template = env.get_template(sys.argv[1])
outfile = sys.argv[2]

with open(outfile, 'w') as fh:
    fh.write(template.render())
