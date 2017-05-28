from astropy.time import Time
from astropy.coordinates import SkyCoord

from .lookup_mpc import lookMP as lookup
from .parse_mpc import parse_result as parse

searchradius = 108  # arcmin


def retrieve_mpc(ra, dec, jd):
    c = SkyCoord(ra, dec, unit=("hour", "deg"))
    t = Time(jd, format="jd")

    r = lookup(c, t, searchradius)

    df = parse(r)

    if (df is not None) and (len(df) > 0):
        df["Vmag"] = df["Vmag"].fillna(99)
        return df.to_dict(orient="record")
    else:
        return []


if __name__ == "__main__":
    ra = "06:14:34.01"
    dec = "-22:07:00.0"
    midjd = 2457845.50417824

    retrieve_mpc(ra, dec, midjd)
