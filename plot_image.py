#! /usr/bin/env python

import pyfits
import sys
import argparse
from specreduce.specreduce import BessSpectra
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

parser = argparse.ArgumentParser(description='Plot FITS spectrum to file')
parser.add_argument('infile', type=str, help='FITS filename')
parser.add_argument('outfile', type=str, help='output image filename')
parser.add_argument('--width', '-W', type=int, default=640, help='image width')
parser.add_argument('--height', '-H', type=int, default=480, help='image height')
parser.add_argument('--compact', '-c', action='store_true')

args = parser.parse_args()

hdulist = pyfits.open(args.infile)
spectrum = BessSpectra(hdulist)

outfile = open(args.outfile, 'w')

style=None
dpi = 72. 

x, y = (args.width, args.height)
x = x / dpi 
y = y / dpi 

fig=Figure(figsize=(x,y), dpi=dpi, facecolor='white') 
ax=fig.add_subplot(111) 

if args.compact: 
    ax.autoscale_view('tight') 
    ax.get_xaxis().set_visible(False) 
    ax.get_yaxis().set_visible(False) 

spectrum.plot_onto(ax) 
canvas=FigureCanvas(fig) 
canvas.print_png(outfile)
