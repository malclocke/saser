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

template = env.get_template(campaign_dir + '.html')

fits_dir = os.path.join(campaign_dir, 'fits')
index_html = os.path.join(site_dir, campaign_dir, 'index.html')
zipfilename = campaign_dir + '.zip'

files = [os.path.join(fits_dir, f) for f in os.listdir(os.path.join(site_dir,fits_dir)) if f.endswith('.fit')]
hdulists = [pyfits.open(os.path.join(site_dir, f)) for f in files]
spectra = [BessSpectra(hdulist) for hdulist in hdulists]
sorted_spectra = sorted(
        zip(files, spectra), reverse=True,
        key=lambda tup: tup[1].header()['DATE-OBS'])

with open(index_html, 'w') as fh:
    fh.write(template.render(
        spectra=sorted_spectra, zipfilename=zipfilename, spectra_count=len(sorted_spectra)))
