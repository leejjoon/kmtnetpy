import re
import os

import numpy as np
import pandas as pd
from astropy import coordinates as coords
from astropy.time import Time, TimeDelta

# p = re.compile("(\-+)")
p_sep = re.compile(r"(\s+)")
p_fileid = re.compile(r"[^\d](\d{6})\.")


def get_fileid(s):
    try:
        r = p_fileid.split(s)[1]
    except:
        return None
    else:
        return r


def convert_to_coord(ra_list, dec_list):
    ras, decs = [], []
    for ra, dec in zip(ra_list, dec_list):
        try:
            c = coords.SkyCoord(ra, dec, unit=["hour", "deg"])
        except ValueError:
            c = coords.SkyCoord(np.nan, np.nan, unit=["hour", "deg"])
        ras.append(c.ra.hour)
        decs.append(c.dec.deg)

    return coords.SkyCoord(ras, decs, unit=["hour", "deg"])


def load_fields():
    df2 = pd.read_table("ksp_fields_coordinates.txt", sep="\s+",
                        names=["OBJECT", "RA", "DEC"])

    fields_coord = coords.SkyCoord(zip(df2["RA"], df2["DEC"]),
                                   unit=("hour", "deg"))

    return df2, fields_coord


header_replace_dict = dict(EXPTIME="EXP", IMAGETYPE="IMGTYPE", FILTER="FILT")


def load_log(fn):
    ll = open(fn.strip()).readlines()

    if len(ll) > 3:
        l = ll[1].strip()
        names = l.split()
        # colspec = [(m.start(), m.end()) for m in p.finditer(l)]
    elif len(ll) == 0:
        return None, None
    else:
        raise RuntimeError("log file corrupted: %s" % fn)

    names = [header_replace_dict.get(n, n) for n in names]

    # df = pd.read_fwf(fn, colspec=colspec, skiprows=[0, 2], comment="=")
    df = pd.read_table(fn, sep=r"\s+",
                       names=names, skipinitialspace=True,
                       skiprows=3, na_values=["-----"])

    df = df.iloc[:-1]
    # g_sn = df.groupby("PROJID").get_group("SN")

    # MIDJD
    if "MIDJD" not in df:
        t1 = Time(list(df["DATE-OBS"]), format="isot")
        t2 = t1 + TimeDelta(df["EXP"].fillna(0.), format="sec")
        df["MIDJD"] = .5 * (t1.jd + t2.jd)

    # UTDATE
    df["UTDATE"] = pd.to_datetime(df["DATE-OBS"]).dt.strftime("%Y%m%d")

    # FILEID
    df["FILEID"] = df["FILENAME"].apply(get_fileid)

    try:
        obs_coord = coords.SkyCoord(zip(df["RA"], df["DEC"]),
                                    unit=("hour", "deg"))
    except ValueError:
        obs_coord = convert_to_coord(df["RA"], df["DEC"])

    return df, obs_coord


def merge(df_log, obs_coord, df_field, fields_coord):

    df = df_log.copy()
    df2 = df_field

    m = obs_coord.match_to_catalog_sky(fields_coord)

    nearest_fieldname = df2["OBJECT"][m[0]].reset_index(drop=True)
    nearest_fieldname[m[1].arcmin > 30.] = ""

    df["NEAREST_FIELD"] = nearest_fieldname

    df["NEAREST_ARCMIN"] = m[1].arcmin
    df.loc[df["NEAREST_ARCMIN"] > 30., "NEAREST_ARCMIN"] = np.nan

    select_exptime = df["EXP"] > 30  # focuses are usually EXP = 10
    select_matched = (df["NEAREST_ARCMIN"] < 1) & select_exptime
    select_projid = (df["PROJID"] == "SN") & select_exptime

    select_name = df["OBJECT"].str.upper() == df["NEAREST_FIELD"].str.upper()

    # select_good = select_matched & select_projid
    select_bad_name = select_matched & ~select_name
    select_bad_projid = select_matched & ~select_projid
    select_bad_coord = ~select_matched & select_projid

    tags = [[] for row in range(len(df))]

    tags = [(t + ["BAD_NAME"] if f else t) for (t, f) in
            zip(tags, select_bad_name)]

    tags = [(t + ["BAD_COORD"] if f else t) for (t, f) in
            zip(tags, select_bad_coord)]

    tags = [(t + ["BAD_PROJID"] if f else t) for (t, f) in
            zip(tags, select_bad_projid)]

    df["TAGS"] = [" ".join(t) for t in tags]

    df["FILEID"] = [".".join(s.split(".")[1:3]) for s in df["FILENAME"]]

    return df

#columns = ("FILEID PROJID RA DEC FILT OBJECT NEAREST_FIELD "
#           "NEAREST_ARCMIN TAGS").split()


# if __name__ == "__main__":

class LogConverter():
    def __init__(self):
        self.df_fields, self.coords_fields = load_fields()

    _column_names = ("FILEID PROJID RA DEC FILT EXP OBJECT NEAREST_"
                     "FIELD NEAREST_ARCMIN TAGS").split()

    @staticmethod
    def _get_mask(df):
        if len(df) == 0:
            return slice(None)

        select_exptime = df["EXP"] > 30  # focuses are usually EXP = 10
        select_matched = df["NEAREST_ARCMIN"] < 1
        select_projid = df["PROJID"] == "SN"

        return select_exptime & (select_matched | select_projid)

    @staticmethod
    def _highlight_tagged_row(row):
        # print row
        if row["TAGS"]:
            return ['background-color: yellow'] * len(row)
        else:
            return [""] * len(row)

    def read(self, fn):
        # fn = "kmtc.20170402.report.logs"
        df_log, coords_log = load_log(fn)

        if df_log is not None:
            df_merged = merge(df_log, coords_log,
                              self.df_fields, self.coords_fields)

            return df_merged
        else:
            return pd.DataFrame(dict((c, []) for c in self._column_names))

    def get_style(self, df_merged):
        msk_to_show = self._get_mask(df_merged)
        df_selected = df_merged[msk_to_show].loc[:, self._column_names]
        style = df_selected.style.apply(self._highlight_tagged_row,
                                        axis=1)

        return style

    def get_summary(self, df_merged):
        s = df_merged.groupby("TAGS")["FILEID"].count()
        o = s.to_dict()
        o["nobs"] = o.pop("", 0)

        return o


def load_obslog_db():
    from tinydb import TinyDB, Query
    from tinydb.storages import JSONStorage
    from tinydb.middlewares import CachingMiddleware

    Entry = Query()

    with TinyDB('ksp_obs_log.json',
                storage=CachingMiddleware(JSONStorage)) as db:

        table = db.table('obslog')

        while True:
            fn, o = yield
            table.remove(Entry.logname == fn)
            table.insert(o)


def main(*kl):

    gen_db = load_obslog_db()
    gen_db.send(None)

    log_converter = LogConverter()

    try:
        for fn in kl:
            print(fn)
            fn0 = os.path.basename(fn)
            df_merged = log_converter.read(fn)
            style = log_converter.get_style(df_merged)

            df_merged.to_json("%s.json" % fn0)
            open("%s_table.html" % fn0, "w").write(style.render())

            o = log_converter.get_summary(df_merged)
            o["logname"] = fn0

            gen_db.send((fn, o))
    finally:
        gen_db.close()


if __name__ == "__main__":
    import sys
    kl = sys.argv[1:]
    main(*kl)
