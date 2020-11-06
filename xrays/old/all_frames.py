import sep
import os
import sys
import astropy.io.fits as fits
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import leastsq
from IPython import embed


def lin(p, x):
    """ Linear function for fitting """
    return p[0]+np.dot(p[1], x)


def resid(p, x, y, e):
    """ Returns linear residuals """
    return (y-lin(p, x))/e


def usage(code):
    """ Prints help message and quits. """
    print 'Usage: python all_frames.py amp'
    sys.exit(code)


def main(argv):
    # Parse arguments
    try:
        data = np.genfromtxt('./gain_tbl.txt', names=True, dtype=None)
        amp = argv[1]
    except IndexError:
        print 'You must specify an amplifier (a or b).'
        usage(1)

    row = []
    col = []
    val = []
    row_all = []
    col_all = []
    val_all = []
    for frame in data['frame']:
        frame = '%03d' % frame
        print frame
        file_str = './camera1/lbl1.'+frame+'/lbl1.'+frame
        if amp.lower() == 'a':
            file_str = file_str+'00.fits'
            gain = data['gaina'][int(frame)]
        elif amp.lower() == 'b':
            file_str = file_str+'01.fits'
            gain = data['gainb'][int(frame)]
        if gain == 0 or frame == '012':
            print 'Bad frame'
            continue
        fname = os.path.abspath(file_str)
        fits_img = fits.open(fname)
        img = fits_img[0].data
        fits_img.close()

        bg = sep.Background(img)
        bg.subfrom(img)
        img = img * gain
        thresh = 5 * bg.globalrms
        objs = sep.extract(img, thresh, minarea=0)
        objs = filter(lambda x: x['flag'] == 0, objs)
        sing_pix = filter(lambda x: x['tnpix'] == 1, objs)
        kab = filter(lambda x: x['flux'] > 1500 and x['flux'] < 2000, sing_pix)
        ka = filter(lambda x: x['flux'] < 1700, kab)
        amp_edge = filter(lambda x: x['x']<980, ka)

        row_all = row_all + [obj['y'] for obj in sing_pix]
        col_all = col_all + [obj['x'] for obj in sing_pix]
        val_all = val_all + [obj['flux'] for obj in sing_pix]
        row = row + [obj['y'] for obj in amp_edge]
        col = col + [obj['x'] for obj in amp_edge]
        val = val + [obj['flux'] for obj in amp_edge]

    row = np.array(row)
    col = np.array(col)
    val = np.array(val)
    plt.scatter(row_all, val_all, s=2, lw=0, alpha=0.3)

    # nbins = 11
    # n, _ = np.histogram(row, bins=nbins, range=(1400, 2600))
    # sy, _ = np.histogram(row, bins=nbins, weights=val, range=(1400, 2048))
    # sy2, _ = np.histogram(row, bins=nbins, weights=val*val, range=(1400, 2048))

    # mean = sy / n
    # std = np.sqrt(sy2/n - mean*mean)/np.sqrt(n)

    # plt.errorbar((_[1:] + _[:-1])/2, mean, xerr=(_[1]-_[0])/2,
    #              yerr=std, fmt='r.')

    popt, pcov, info, mesg, ier = leastsq(resid, [1620, -0.00002],
                                          args=(row, val, 1),
                                          maxfev=1000, full_output=True)
    print popt[0], popt[1]
    print np.sqrt(pcov[0, 0]), np.sqrt(pcov[1, 1])
    x = np.linspace(0,4096)
    plt.plot(x, lin(popt, x), 'k-')
    print -np.log10(np.abs(popt[1]/lin(popt,2048.)))
    plt.ion()
    embed()


main(sys.argv)
