import os
import glob
import pandas as pd
import astropy.io.fits as pyfits
from astropy.wcs import WCS, NoConvergence
from astropy.coordinates import SkyCoord

PROCESSED_ROOT = "./PROCESSED"

def get_data_dir(filename_key, qn, rootdir=None):
    field_name = filename_key[0]
    field_name0 = field_name.split("-")[0]

    data_dir = os.path.join(field_name0, field_name, "Q%d" % qn)
    if rootdir is not None:
        data_dir = os.path.join(rootdir, data_dir)

    return data_dir


def get_root(filename_key, qn):
    filename_key = list(filename_key)
    root = ".".join(filename_key).replace(".Q0.", ".Q%d." % qn)

    return root


def get_wcs(root, data_dir):
    fn0 = "".join([root, ".*", ".nh.fits*"])
    fl = glob.glob(os.path.join(data_dir, fn0))

    if len(fl) == 1:
        fn = fl[0]
        f = pyfits.open(fn)

        wcs = WCS(f[-1].header)
        return wcs
    elif len(fl) == 0:
        raise RuntimeError("no file found: %s" % fn0)
    else:
        raise RuntimeError("miltiple file found: %s" % fn0)


def get_diff_cat(root, data_dir):

    fn0 = "".join([root, ".*", ".nh.REF-SUB.cat"])
    fl = glob.glob(os.path.join(data_dir, fn0))

    if len(fl) == 1:
        fn = fl[0]
        f = pyfits.open(fn)

        table = f[2].data
        return table
    elif len(fl) == 0:
        raise RuntimeError("no file found: %s" % fn0)
    else:
        raise RuntimeError("miltiple file found: %s" % fn0)


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
                        get_data_dir(filename_key, qn,
                                     rootdir=PROCESSED_ROOT))
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
