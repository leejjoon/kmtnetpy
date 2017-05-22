import os
import glob
from parse_log import load_log

import re
p_logdate = re.compile(r"[^\d](\d{8})\.")

telescope = "ctio"
fl = sorted(glob.glob("logs_www/kmtc.*.logs"))

rr = []
for fn in fl[:]:
    logdate = p_logdate.split(os.path.basename(fn))[1]
    # fn = os.path.join(fn)
    try:
        r = load_log(fn)
        # LOGDATE
        if r[0] is None:
            continue

        r[0]["LOGDATE"] = logdate
        r[0]["TEL"] = telescope

    except:
        print("error in", fn)
        raise
    else:
        rr.append(r)


import pandas as pd
dd = pd.concat([r[0] for r in rr if r[0] is not None], ignore_index=True)

pd.to_msgpack("kmtc_log.list.msgpack")
