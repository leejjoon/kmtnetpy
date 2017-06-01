from base64 import encodestring, decodestring
import StringIO
import numpy as np
from fitsio_helper import FitsioHelper

from ..utils.file_helper import (get_data_dir, get_root, get_filename)


def get_slices(nx, cx0, dx, dx2=None):
    if dx2 is None:
        dx1, dx2 = dx, dx
    else:
        dx1, dx2 = dx, dx2

    src_slice = slice(max(cx0 - dx1, 0), min(cx0 + dx2 + 1, nx))
    dest_slice = slice(max(dx1 - cx0, 0),
                       (dx1 + dx2 + 1) + min(nx - (cx0 + dx2 + 1), 0))
    return src_slice, dest_slice


def get_subim(hdu, cx, cy, size=64, size2=None, outim=None):

    ny, nx = hdu.get_dims()
    # header["NAXIS2"], header["NAXIS1"]

    cx0, cy0 = int(np.round(cx)), int(np.round(cy))

    dx, dy = size, size

    if size2 is None:
        dx2, dy2 = dx, dy
    else:
        dx2, dy2 = size2, size2

    if outim is None:
        outim = np.empty(((dy + dy2) + 1, (dx + dx2) + 1), dtype=float)
        outim.fill(np.nan)

    src_slice_x, dest_slice_x = get_slices(nx, cx0, dx, dx2)
    src_slice_y, dest_slice_y = get_slices(ny, cy0, dy, dy2)

    outim[dest_slice_y, dest_slice_x] = hdu.get_subim(sl_y=src_slice_y,
                                                      sl_x=src_slice_x)

    return outim


def get_subims(hdu, xy_list, size=64):
    im_list = []

    for cx, cy in xy_list:
        im = get_subim(hdu, cx, cy, size=size)
        im_list.append(im)

    return im_list


def get_stamps_from_key(filename_key, xy_list, size=64,
                        as_string=False, base64=True):

    fn = get_filename(get_root(filename_key), get_data_dir(filename_key),
                      ".nh.fits*")

    hdu_list = FitsioHelper(fn)

    if hdu_list.f[0].has_data():
        hdu = hdu_list.get_hdu(0)
    else:
        hdu = hdu_list.get_hdu(1)

    im_list = get_subims(hdu, xy_list, size)

    if as_string:
        s = imlist2string(im_list, base64=base64)
        return s
    else:
        return im_list


def imlist2string(im_list, base64=True):
    fout = StringIO.StringIO()
    np.savez_compressed(fout, *im_list)
    s = fout.getvalue()

    if base64:
        return encodestring(s)
    else:
        return s


def string2imlist(s, base64=True):
    if base64:
        fin = StringIO.StringIO(decodestring(s))
    else:
        fin = StringIO.StringIO(s)

    im_list = [v for n, v in np.load(fin).items()]

    return im_list


if 0:

    l1 = {'filename_key': (u'E489-1', 'Q0', u'B', u'160125_0529',
                           'C', u'049062'),
          'id': u'20160125-ctio-000138'}

    xy_list = [(176 - 1, 9125 - 1),
               (16 - 1, 9195 - 1)]

    im_list = get_stamps_from_key(l1["filename_key"], xy_list, size=64)


if 0:
    rootdir = "/home/jjlee/work/kmtnet/kmtnet_report"
    fn0 = "PROCESSED/E489/E489-1/Q0/E489-1.Q0.B.160125_0529.C.049062.061920N2336.0060.nh.fits.fz"
    fn = os.path.join(rootdir, fn0)
    hdu = FitsioHelper(fn).get_hdu(1)

    # cx, cy = 176 - 1, 9125 - 1
    cx, cy = 16 - 1, 9195 - 1
    # cx, cy = 92 - 1, 9116 - 1
    cx, cy = 10 - 1, 23 - 1
    cx, cy = 9197 - 1, 9219 - 1

    im = get_subim(hdu, cx, cy, size=64, size2=64)


if __name__ == "__main__":
    fn = "PROCESSED/E489/E489-1/Q0/E489-1.Q0.B.160125_0529.C.049062.061920N2336.0060.nh.fits.fz"
    hdu = FitsioHelper(fn).get_hdu(1)

    # cx, cy = 176 - 1, 9125 - 1
    cx, cy = 16 - 1, 9195 - 1
    # cx, cy = 92 - 1, 9116 - 1

    im = get_subim(hdu, cx, cy, size=64)

    xy_list = [(176 - 1, 9125 - 1),
               (16 - 1, 9195 - 1)]

    im_list = get_subims(hdu, xy_list, size=64)

    import StringIO
    fout = StringIO.StringIO()
    np.save(fout, im)
    s = fout.getvalue()

    fin = StringIO.StringIO(s)
    im2 = np.load(fin)

# result_serializer="msgpack"
