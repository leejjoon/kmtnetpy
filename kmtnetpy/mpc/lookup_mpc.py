import urllib2  # open webpages
from ClientForm import ParseResponse  # online forms
import numpy as np


def lookMP(c, t, searchradius, verbose=False, dryrun=False):

    # convert to HMS sDMS
    RAhr, RAmin, RAsec = c.ra.hms
    DECs_, DECdeg, DECmin, DECsec = c.dec.signed_dms
    DECs = "+" if DECs_ >= 0 else "-"

    # convert MJD to obsyear obsmonth obsday
    # obstime = DateTimeFromMJD(float(MJD))

    obstime = t.utc.to_datetime()
    obsyear = obstime.year
    obsmonth = obstime.month
    day_frac = ((obstime.second / 60. + obstime.minute)
                / 60. + obstime.hour) / 24.
    obsday = obstime.day + day_frac

    # fail
    MPfail = False

    if verbose:
        print("Searching for asteroids with MPChecker (RA: %02i %02i %6.3f [hms], DEC: %s%02i %02i %5.3f [dms], Date: %i %i %f, %s arcmin radius)..." % (RAhr, RAmin, RAsec, DECs, DECdeg, DECmin, DECsec, obsyear, obsmonth, obsday, searchradius))

    # check whether website is up
    # MPurl = "http://scully.cfa.harvard.edu/cgi-bin/checkmp.cgi"
    MPurl = "http://www.minorplanetcenter.net/cgi-bin/checkmp.cgi"
    try:
        MPaddress = urllib2.urlopen(MPurl)
        try:
            forms = ParseResponse(MPaddress, backwards_compat=False)
        except IOError:
            MPfail = True
    except ValueError:
        MPfail = True
    except urllib2.URLError:
        MPfail = True

    if MPfail:
        print('WARNING: Cannot find MP checker address in %s' % (MPurl))
        return None

    form = forms[1]  # back to original in 2014-07-17
    # updated on 2013-07-31 from forms[0] after change in MP checker webpage

    # Fill online form using first candidate as reference
    form["year"] = "%04i" % obsyear  # observation year "2012"
    form["month"] = "%02i" % obsmonth  # observation month "01"
    form["day"] = "%04.2f" % obsday  # observation day "03"
    form["ra"] = "%02i %02i %04.1f" % (RAhr, RAmin, RAsec)
    # right ascencion "11 24 26.670"
    form["decl"] = "%s%02i %02i %04.1f" % (DECs, DECdeg, DECmin, DECsec)
    # declination "03 18 31.58"
    form["oc"] = "807"  # Tololo observatory code
    form["radius"] = "%i" % max(5, np.ceil(searchradius))
    # search radius in arcmin (minimum is 5 arcmin)
    form["limit"] = "23.0"  # search limit magnitude

    # form["mot"] = ["m"]  # motion in minute

    if dryrun:
        print(form["year"], form["month"], form["day"])
        print(form["ra"], form["decl"])
        print(form["oc"], form["radius"], form["limit"])
    else:
        # submit filled form
        MPresults = urllib2.urlopen(form.click()).read()

        return MPresults


if __name__ == "__main__":
    from astropy.time import Time

    # RA, DEC = 94.827859, -23.59922
    ra, dec = 94.827859, -23.59922  # degree
    from astropy.coordinates import SkyCoord
    # c = SkyCoord(ra, dec, unit="deg")
    c = SkyCoord("01 00 00", "-01 00 00", unit=("hour", "deg"))
    searchradius = 65  # arcmin
    # MJD = 57754
    MJD = 57817.11540509015
    t = Time(MJD, format="mjd")
    # RA, DEC = c.ra.hour, c.dec.deg # hour, degree
    # lookMP(RA, DEC, MJD, searchradius, verbose=False)
    r = lookMP(c, t, searchradius, verbose=False)
