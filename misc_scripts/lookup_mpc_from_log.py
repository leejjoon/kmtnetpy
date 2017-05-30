import os
import pandas as pd

obsdate = "20170402"
logname = "kmtc.%s.report.logs.json" % obsdate
logdir = "/home/jjlee/work/kmtnet/kmtnet_report"
df_log = pd.read_json(os.path.join(logdir, logname)).sort_index()


msk_projid = (df_log["PROJID"] == "SN")
msk_filter = (df_log["FILT"] == "V")
msk_exp = (df_log["EXP"] > 30)
msk = msk_projid & msk_filter & msk_exp

df_log_masked = df_log[msk]


if 1:
    from lookup_mpc import lookMP
    from astropy.time import Time

    from astropy.coordinates import SkyCoord
    from parse_mpc import parse_result

    searchradius = 108  # arcmin

    for i, row in df_log_masked.iterrows():

        fn = row["FILENAME"]
        print(fn)
        c = SkyCoord(row["RA"], row["DEC"], unit=("hour", "deg"))
        MJD = row["MIDJD"]
        t = Time(MJD, format="jd")

        # r = lookMP(c, t, searchradius, dryrun=True)
        r = lookMP(c, t, searchradius)

        df = parse_result(r)

        if (df is not None) and (len(df) > 0):
            outname = fn.replace(".fits", ".mpc.json")
            df.to_json(outname)
