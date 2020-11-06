import sep
import os
import sys
import astropy.io.fits as fits
import matplotlib.pyplot as plt
import numpy as np
from IPython import embed


def usage(code):
    """ Prints help message and quits. """
    print 'Usage: python all_frames.py frame amp'
    sys.exit(code)


def main(argv):
    # Parse arguments
    try:
        data = np.genfromtxt('./gain_tbl.txt', names=True, dtype=None)
        amp = argv[2]
        frame = '%03d' % int(argv[1])
        file_str = './camera1/lbl1.'+frame+'/lbl1.'+frame
        if amp.lower() == 'a':
            file_str = file_str+'00.fits'
            gain = data['gaina'][int(frame)]
        elif amp.lower() == 'b':
            file_str = file_str+'01.fits'
            gain = data['gainb'][int(frame)]
        else:
            file_str = 'wrong'
        if gain == 0:
            print 'Bad frame (no gain measured).'
            usage(1)
        fname = os.path.abspath(file_str)
        fits_img = fits.open(fname)
        img = fits_img[0].data
        fits_img.close()
    except IndexError:
        print 'You must specify an amplifier (a or b) and frame'
        usage(1)
    except IOError:
        print 'I/O error. Check frame and amplifier files.'
        usage(1)

    img = img * gain
    bg = sep.Background(img)
    bg.subfrom(img)
    thresh = 5 * bg.globalrms
    objs = sep.extract(img, thresh, minarea=0)
    objs = np.array(filter(lambda x: x['flag'] == 0, objs))
    objs = np.array(filter(lambda x: 1-x['b']/x['a'] <= 0.2, objs))
    sing_pix = np.array(filter(lambda x: x['tnpix'] == 1, objs))
    plt.scatter(objs['y'], objs['flux'],s=2,lw=0,alpha=0.3)
    plt.xlim(1400,2600)
    plt.ylim(0,2000)
    plt.show()

main(sys.argv)
