import os
import sep
import sys
import pickle
import numpy as np
import pandas as pd
from multiprocessing import Pool
from astropy.io import fits

DARK_DIR = '/project/projectdirs/snfactry/SNIFS_from_deepsky/overscanned'

def get_data(path, amp):
    data = fits.getdata(path)
    start = 1024 * amp
    end = 1024 * (amp + 1)
    data = np.array(data[:, start:end]).byteswap().newbyteorder()
    return data

def get_objs(data):
    bg = sep.Background(data)
    bg_sub_data = data - bg.back()
    objs = sep.extract(bg_sub_data, 1.5, err=bg.globalrms)
    objs = pd.DataFrame.from_records(objs)
    # Remove objects that are flagged
    objs = objs[objs.flag == 0]
    # Ellipticity cut
    objs = objs[1-objs.b/objs.a < 0.2]
    # Avoid objects on the edge of the detector
    objs = objs[(objs.xpeak > 10) & (objs.xpeak < 1014)]
    objs = objs[(objs.ypeak > 10) & (objs.ypeak < 4086)]
    return objs.reset_index()

def get_tails(data, objs, serial=False):
    tails, peak_vals = [], []
    for _, obj in objs.iterrows():
        x = int(obj.xpeak)
        y = int(obj.ypeak)
        if serial:
            tails.append(data[y, x-10:x][::-1]-data[y, x+1:x+11])
        else:
            tails.append(data[y-10:y, x][::-1]-data[y+1:y+11, x])
        peak_vals.append(data[y, x])
    return np.array(tails), np.array(peak_vals)


def nightly(dark_dir, serial=False):
    year, night = dark_dir.split('/')[-2:]
    all_tails = {'B': {0: {}, 1: {}},
                 'R': {0: {}, 1: {}},
                 'P': {0: {}, 1: {}, 2: {}, 3: {}}}
    for fname in os.listdir(dark_dir):
        if '_25_' not in fname:
            continue
        print(fname)
        frame = int(fname.split('_')[2])
        channel = fname.split('.')[0][-1]
        path = os.path.join(dark_dir, fname)
        amp_list = range(2) if channel in 'BR' else range(4)
        for amp in amp_list:
            try:
                data = get_data(path, amp)
                objs = get_objs(data)
                tails, peak_vals = get_tails(data, objs)
                serial_tails, _ = get_tails(data, objs, serial=True)
                all_tails[channel][amp][frame] = {'tails_serial': serial_tails,
                                                  'tails_parallel': tails,
                                                  'loc_y': objs.ypeak,
                                                  'loc_x': objs.xpeak,
                                                  'peak_vals': peak_vals}
            except:
                print(frame, channel, amp)
                continue
    tail_fname = '{}_{}_serial.pkl'.format(year, night)
    tail_path = os.path.join('/global/cscratch1/sd/sdixon/cte_tails/', tail_fname)
    with open(tail_path, 'wb') as f:
        pickle.dump(all_tails, f)
        
def main(year, serial):
    year_dir = os.path.join(DARK_DIR, '{:02d}'.format(year))
    dark_dirs = [os.path.join(year_dir, night) for night in os.listdir(year_dir)]
    pool = Pool(16)
    pool.map(nightly, dark_dirs)
    
if __name__ == '__main__':
    main(int(sys.argv[1]), True)
