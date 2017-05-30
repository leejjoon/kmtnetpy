import fitsio
from fitsio.fitslib import ImageHDU

import astropy.wcs as pywcs


def get_hdu(fn, extnum=0):
    f = fitsio.FITS(fn)
    hdu = ImageHDU(f._FITS, extnum)

    return hdu


def get_subim(hdu, sl_x=None, sl_y=None):
    #tbl = TableHDU(fits._FITS, 1)
    if sl_x is None:
        sl_x = slice(None, None)

    if sl_y is None:
        sl_y = slice(None, None)

    subim = hdu._read_image_slice((sl_y, sl_x))

    return subim


class FitsioHelper(object):
    def __init__(self, fn):
        self.f = fitsio.FITS(fn)

    def get_hdu(self, extnum=0):
        hdu = FitsioImageHDU(self.f._FITS, extnum)
        return hdu


def lazyprop(fn):
    attr_name = '_lazy_' + fn.__name__

    @property
    def _lazyprop(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)
    return _lazyprop


class FitsioImageHDU(ImageHDU):

    @lazyprop
    def header(self):
        header = self.read_header()

        return header

    @lazyprop
    def wcs(self):
        wcs = pywcs.WCS(self.header)

        return wcs

    def get_subim(self, sl_x=None, sl_y=None):
        return get_subim(self, sl_x=sl_x, sl_y=sl_y)


if __name__ == "__main__":
    fn = "test.fits"
    f = FitsioHelper(fn)
    hdu = f.get_hdu(extnum=0)

    wcs = hdu.wcs

    from astropy import units as u
    from astropy.coordinates import SkyCoord
    c = SkyCoord('18:41:27.09 -4:54:47.97', unit=(u.hourangle, u.deg))
    xy = wcs.all_world2pix([(c.ra.deg, c.dec.deg)], 0)

    subim = hdu.get_subim(sl_y=slice(50, 100))
