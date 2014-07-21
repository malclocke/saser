#! /usr/bin/env python
from jinja2 import Environment, FileSystemLoader
import os
import sys
import pyfits
import dateutil
from specreduce.specreduce import BessSpectra

env = Environment(loader=FileSystemLoader('templates'))

site_dir = 'site'
campaign_dir = sys.argv[1]
title = sys.argv[2]

template = env.get_template(campaign_dir + '.html')

fits_dir = os.path.join(campaign_dir, 'fits')
index_html = os.path.join(site_dir, campaign_dir, 'index.html')
zipfilename = campaign_dir + '.zip'

files = [os.path.join(fits_dir, f) for f in os.listdir(os.path.join(site_dir,fits_dir))]
hdulists = [pyfits.open(os.path.join(site_dir, f)) for f in files]
spectra = [BessSpectra(hdulist) for hdulist in hdulists]
sorted_spectra = sorted(
        zip(files, spectra), key=lambda tup: tup[1].header()['DATE-OBS'])

with open(index_html, 'w') as fh:
    fh.write(template.render(
        title=title, spectra=sorted_spectra, zipfilename=zipfilename))
