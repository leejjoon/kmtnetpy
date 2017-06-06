from base64 import encodestring
import StringIO

import numpy as np
import astropy.io.fits as pyfits
from scipy.spatial import KDTree

from kmtnetpy.utils.file_helper import (get_data_dir, get_root, get_filename)


ksp_source_class_bits = 2**np.arange(32)


def get_diff_cat_from_key(filename_key, xy_list, return_cat=False,
                          base64=False):
    """
    return FitsTable by default.
    """
    fn = get_filename(get_root(filename_key),
                      get_data_dir(filename_key,
                                   subdir="B_Filter/Subtraction"),
                      ".nh.REF-SUB.cat*")

    # fn = get_filename(get_root(filename_key),
    #                   get_data_dir(filename_key),
    #                   ".nh.sub.cat*")

    f = pyfits.open(fn)
    d = f[2].data

    xy = np.vstack([d["XWIN_IMAGE"], d["YWIN_IMAGE"]]).T
    tree = KDTree(xy)

    distance, indices = tree.query(xy_list)

    r = dict(distance=distance.tolist(),
             indices=indices.tolist(),
             fn=fn)

    if return_cat:
        keys = set(d.dtype.names).difference(["KSP_SOURCE_CLASS", "VIGNET"])

        cat = []
        for i in indices:
            row = dict((k, d[i][k]) for k in keys)
            _bits = ksp_source_class_bits * d[i]["KSP_SOURCE_CLASS"]
            row["KSP_SOURCE_CLASS"] = np.sum(_bits)
            cat.append(row)

        r["cat"] = cat

    else:
        new_hdu = pyfits.BinTableHDU(data=d[indices])

        col_dist = pyfits.Column(name='MATCH_DIST', format='D',
                                 array=distance)
        col_indx = pyfits.Column(name='MATCH_INDEX', format='I',
                                 array=indices)

        added_columns = pyfits.ColDefs([col_dist, col_indx])

        hdu = pyfits.BinTableHDU.from_columns(new_hdu.columns + added_columns)
        # hdu = pyfits.BinTableHDU(header=)
        fout = StringIO.StringIO()
        hdu.writeto(fout)

        s = fout.getvalue()

        if base64:
            r["fits_string"] = encodestring(s)
        else:
            r["fits_string"] = s

    return r
