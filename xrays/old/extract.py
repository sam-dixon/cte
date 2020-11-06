import sep
import os
import sys
import astropy.io.fits as fits
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import leastsq
from scipy.stats import binned_statistic as binned


def lin(p,x):
    """ Linear function for fitting """
    return p[0]+np.dot(p[1],x)


def resid(p,x,y,e):
    """ Returns linear residuals """
    return (y-lin(p,x))/e


def usage(code):
    """ Prints help message and quits. """
    print 'Usage: python extract.py frame_number amp'
    sys.exit(code)


def std(arr):
    return np.std(arr)

def main(argv):
    # Parse arguments
    try:
        data = np.genfromtxt('./gain_tbl.txt', names=True, dtype=None)
        frame = argv[1]
        amp = argv[2]
        file_str = './camera1/lbl1.'+frame+'/lbl1.'+frame
        if amp.lower() == 'a':
            file_str = file_str+'00.fits'
            gain = data['gaina'][int(frame)]
        elif amp.lower() == 'b':
            file_str = file_str+'01.fits'
            gain = data['gainb'][int(frame)]
        if gain == 0:
            print 'Bad frame. Choose another.'
            sys.exit()
        print gain
        fname = os.path.abspath(file_str)
        fits_img = fits.open(fname)
        data = fits_img[0].data
    except IndexError:
        print 'Two inputs required.'
        usage(1)
    except IOError as e:
        print e
        print 'Make sure the frame number and amplifier (A or B) are correct.'
        usage(1)

    bg = sep.Background(data)
    bg.subfrom(data)
    data = data * gain

    objs = sep.extract(data, 10, minarea=0)
    objs = filter(lambda x: x['flag']==0, objs)
    sing_pix = filter(lambda x: x['tnpix']==1, objs)
    kab = filter(lambda x: x['flux']>1500 and x['flux']<2000, sing_pix)
    ka = filter(lambda x: x['flux']<1700, kab)
    kb = filter(lambda x: x['flux']>1700, kab)
    row = np.array([obj['y'] for obj in ka])
    val = np.array([obj['flux'] for obj in ka])
    plt.scatter(row, val, s=2, lw=0, alpha=0.5)

    nbins = 20
    n, _ = np.histogram(row, bins=nbins)
    sy, _ = np.histogram(row, bins=nbins, weights=val)
    sy2, _ = np.histogram(row, bins=nbins, weights=val*val)

    mean = sy / n
    std = np.sqrt(sy2/n - mean*mean)/np.sqrt(n)

    plt.errorbar((_[1:] + _[:-1])/2, mean, xerr=(_[1]-_[0])/2, yerr=std, fmt='r.')

    popt, pcov, info, mesg, ier = leastsq(resid, [1600, -0.000002],
                                          args=((_[1:] + _[:-1])/2, mean, std),
                                          full_output=True)
    print popt[0], popt[1]
    print np.sqrt(pcov[0, 0]), np.sqrt(pcov[1, 1])
    x = np.linspace(min(row),max(row),max(row)-min(row))
    plt.plot(x,lin(popt, x),'k-')
    print -np.log10(np.abs(popt[1]/1620.))
    plt.show()

main(sys.argv)