import numpy as np
from fitsio_helper import FitsioHelper


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


if 0:
    fn = "PROCESSED/E489/E489-1/Q0/E489-1.Q0.B.160125_0529.C.049062.061920N2336.0060.nh.fits.fz"
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