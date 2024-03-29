#! /usr/bin/env python
import pyfits
import numpy as np
import matplotlib.pyplot as plt
import scipy.interpolate
import argparse
import os

class ElementLine:

    def __init__(self, angstrom, label):
        self.angstrom = angstrom
        self.label = label

    @classmethod
    def presets(cls):
        return {
            'Ha': cls(6563, r'H$\alpha$'),
            'Hb': cls(4861, r'H$\beta$'),
            'Hg': cls(4341, r'H$\gamma$'),
            'Hd': cls(4102, r'H$\delta$'),
            'CaH': cls(3968, 'Ca H'),
            'CaK': cls(3934, 'Ca K')
        }

    def __repr__(self):
        return "%f (%s)" % (self.angstrom, self.label)

    def color(self):
        return 'red'

    def plot_label(self):
        return '%s (%.02f $\AA$)' % (self.label, self.angstrom)

    def plot_onto(self, axes, offset = 0):
        bottom, top = axes.get_ylim()
        text_y = (top - bottom) * 0.1
        axes.axvline(x=self.angstrom, color=self.color())
        axes.text(self.angstrom, text_y, self.plot_label(),
                rotation='vertical', verticalalignment='bottom')


class CalibrationReference:

    def __init__(self, pixel, angstrom):
        self.pixel = pixel
        self.angstrom = angstrom

    @classmethod
    def from_string(cls, string):
        pixel, angstrom = string.split(':')

        # This could be a string, e.g. Ha, Hb or just a number.
        angstrom = cls.get_angstrom(angstrom)

        return cls(float(pixel), float(angstrom))

    @classmethod
    def get_angstrom(cls, angstrom):
        if angstrom in ElementLine.presets():
            return ElementLine.presets()[angstrom].angstrom
        else:
            return angstrom

    def __repr__(self):
        return "<Calibration reference: pixel: %d, angstrom: %f>" % (
                self.pixel, self.angstrom
        )


class DoublePointCalibration:
    def __init__(self, reference1, reference2):
        self.reference1 = reference1
        self.reference2 = reference2

    def __repr__(self):
        return "<Calibration angstrom_per_pixel: %f>" % (
                self.angstrom_per_pixel()
        )

    def angstrom(self, pixel):
        return (self.slope() * (pixel - self.reference1.pixel)) + self.reference1.angstrom

    def slope(self):
        return self.angstrom_difference() / self.pixel_difference()

    def angstrom_difference(self):
        return self.reference1.angstrom - self.reference2.angstrom

    def pixel_difference(self):
        return self.reference1.pixel - self.reference2.pixel

    def angstrom_per_pixel(self):
        return self.slope()


class SinglePointCalibration:
    def __init__(self, reference, angstrom_per_pixel):
        self.reference = reference
        self._angstrom_per_pixel = angstrom_per_pixel

    def angstrom(self, pixel):
        return (self.angstrom_per_pixel() * (pixel - self.reference.pixel)) + self.reference.angstrom

    def angstrom_per_pixel(self):
        return self._angstrom_per_pixel


class NonLinearCalibration:
    def __init__(self, references, degree = 2):
        self.references = references
        self.degree = degree
        self.poly1d = self._generate_poly1d()

    @classmethod
    def from_string(cls, string):
        references = []
        for element in string.split(','):
            references.append(CalibrationReference.from_string(element))
        return cls(references)

    def angstrom(self, pixel):
        return self.poly1d(pixel)

    def _generate_poly1d(self):
        x = []
        y = []
        for reference in self.references:
            x.append(reference.pixel)
            y.append(reference.angstrom)
        z = np.polyfit(x, y, self.degree)
        return np.poly1d(z)

    def apply_offset(self, pixel_offset):
        for reference in self.references:
            reference.pixel = reference.pixel + pixel_offset
        self.poly1d = self._generate_poly1d()

    def __repr__(self):
        return ', '.join(str(x) for x in self.references)


class Plotable:

    can_plot_image = False
    grayscale = False
    linestyle = '-'

    def plot_onto(self, axes, offset = 0):
        plot_args = {'label': self.label, 'linestyle': self.linestyle}

        if self.grayscale:
            plot_args['color'] = 'k'

        data = self.data() + offset

        axes.plot(self.wavelengths(), data, **plot_args)

    def max(self):
        return self.data().max()

    def divide_by(self, other_spectra):
        divided = np.divide(self.data(), other_spectra.interpolate_to(self))
        divided[divided==np.inf]=0
        return divided

    def interpolate_to(self, spectra):
        return np.interp(spectra.wavelengths(), self.wavelengths(), self.data())


class ImageSpectra(Plotable):

    label = 'Raw data'
    calibration = False
    can_plot_image = True

    def __init__(self, data):
        self.raw = data

    def data(self):
        return self.raw.sum(axis=0)

    def set_calibration(self, calibration):
        self.calibration = calibration

    def wavelengths(self):
        if self.calibration:
            return [self.calibration.angstrom(i) for i in range(len(self.data()))]
        else:
            return range(len(self.data()))

    def plot_image_onto(self, axes):
        imgplot = axes.imshow(self.raw)
        imgplot.set_cmap('gray')

    def set_label_header(self, label_header):
        return

class BessSpectra(Plotable):

    label = 'Raw spectra'
    label_header = 'DATE-OBS'

    def __init__(self, hdulist, calibration = False):
        self.hdulist = hdulist
        if calibration:
            self.calibration = calibration
        else:
            self.calibration = SinglePointCalibration(
                CalibrationReference(self.get_header('CRPIX1'), self.get_header('CRVAL1')),
                self.get_header('CDELT1')
            )
        self.set_label()

    def set_label(self):
        if self.label_header in self.header():
            self.label = self.get_header(self.label_header)

    def set_label_header(self, label_header):
        self.label_header = label_header
        self.set_label()

    def plot_image_onto(self, axes):
        return False

    def header(self):
        return self.hdulist[0].header

    def get_header(self, header):
        return self.header()[header]

    def wavelengths(self):
        return [self.calibration.angstrom(i) for i in range(len(self.data()))]

    def data(self):
        return self.hdulist[0].data

    def r(self):
        if 'BSS_ESRP' in self.header():
            if 'BSS_SRPW' in self.header():
                return '%d @ %d' % (
                        self.get_header('BSS_ESRP'), self.get_header('BSS_SRPW')
                        )
            else:
                return self.get_header('BSS_ESRP')
        elif 'BSS_ITRP' in self.header():
            return self.get_header('BSS_ITRP')
        elif 'SPE_RPOW' in self.header():
            return self.get_header('SPE_RPOW')

class CorrectedSpectra(Plotable):

    smoothing = 20
    spacing   = 500
    k         = 1
    label     = 'Corrected'

    def __init__(self, uncorrected, reference):
        self.uncorrected = uncorrected
        self.reference = reference

    def wavelengths(self):
        return self.uncorrected.wavelengths()

    def divided(self):
        return self.uncorrected.divide_by(self.reference)

    def data(self):
        return np.divide(self.uncorrected.data(), self.smoothed())

    def smoothed(self):
        tck = scipy.interpolate.splrep(
            self.wavelengths(), self.divided(), s=self.smoothing, k=self.k
        )
        return scipy.interpolate.splev(self.wavelengths(), tck)

class ValidationError(Exception):
    pass

class IncorrectNumberOfAxesError(ValidationError):
    pass

class MissingCalibrationHeader(ValidationError):
    pass

class OneDimensionalSpectrumValidator:
    def __init__(self, hdulist):
        self.hdulist = hdulist

    def validate(self):
        headers = self.hdulist[0].header
        self.validate_naxes(headers)
        self.validate_calibration(headers)
        return True

    def validate_naxes(self, headers):
        naxis = headers['NAXIS']
        if naxis != 1:
            raise IncorrectNumberOfAxesError(
                            'Wrong number of axes, expected NAXIS=1 but was %d' % naxis)

    def validate_calibration(self, headers):
        for header in ('CRPIX1', 'CRVAL1', 'CDELT1'):
            if header not in headers:
                raise MissingCalibrationHeader(
                                'Required wavelength calibration header %s was missing' % header)
