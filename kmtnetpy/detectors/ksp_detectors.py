import os
import glob
import pandas as pd
import astropy.io.fits as pyfits
from astropy.wcs import WCS, NoConvergence
from astropy.coordinates import SkyCoord

from ..utils.file_helper import (get_data_dir, get_root, get_filename)


def get_wcs(root, data_dir):
    fn = get_filename(root, data_dir, ".nh.fits*")

    f = pyfits.open(fn)
    wcs = WCS(f[-1].header)

    return wcs


def get_diff_cat(root, data_dir):
    fn = get_filename(root, data_dir, ".nh.REF-SUB.cat", subdir="Sub")

    f = pyfits.open(fn)
    table = f[2].data

    return table


def check_on_detector(wcs, c):
    try:
        x, y = c.to_pixel(wcs, mode="all")
    except NoConvergence:
        return False

    on_chip = (0 < x) & (x < wcs._naxis1) & (0 < y) & (y < wcs._naxis2)

    if on_chip:
        return (float(x), float(y))
    else:
        return False


def _find1_on_detectors(wcs_list, c):
    for (qn, wcs) in enumerate(wcs_list):
        xy = check_on_detector(wcs, c)
        if xy is not False:
            return qn, xy

    return None


def find_on_detectors(wcs_list, coords):
    qn_xy_list = [_find1_on_detectors(wcs_list, c) for c in coords]

    return qn_xy_list


def get_wcs_list_from_files(filename_key):
    wcs_list = [get_wcs(get_root(filename_key, qn),
                        get_data_dir(filename_key, qn))
                for qn in range(4)]

    return wcs_list


def find(filename_key, ra_list, dec_list):
    coords = SkyCoord(ra_list, dec_list, unit="deg")
    wcs_list = get_wcs_list_from_files(filename_key)

    kk = find_on_detectors(wcs_list, coords)
    return kk


if __name__ == "__main__":

    l1 = {'filename_key': (u'E489-1', 'Q0', u'B', u'160125_0529',
                           'C', u'049062'),
          'id': u'20160125-ctio-000138'}

    df_mpc = pd.read_json(l1["id"] + ".json", orient="record")
    coords_mpc = SkyCoord(df_mpc["ra"], df_mpc["dec"], unit="deg")

    kk = find(l1["filename_key"], df_mpc["ra"], df_mpc["dec"])

    assert kk == [3, 3, 0, 3, None]
