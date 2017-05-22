import os
import urllib2
import datetime


def fetch_log(year, month, day, telescope="c"):
    date_to_fetch = "%04d%02d%02d" % (year, month, day)

    fn = "kmt{}.{}.report.logs".format(telescope, date_to_fetch)

    if os.path.exists(fn):
        print("{}: file exists".format(fn))
        return

    if year == 2017:
        url = "http://kmtnet.kasi.re.kr/tmp/site-report/" + fn
    else:
        url_tmpl = "http://kmtnet.kasi.re.kr/data_access/{}/site-report/{}"
        url = url_tmpl.format(year, fn)

    try:
        f = urllib2.urlopen(url)
        s = f.read()
        open(fn, "w").write(s)
    except urllib2.HTTPError:
        print("{}: HTTP error".format(fn))
    except:
        print("{}: Other error".format(fn))
    else:
        print("{}: OK".format(fn))

# for d in range(1, 32):
#     date_to_fetch = "201704%02d" % d



ds = datetime.date(2015, 3, 1)
de = datetime.date(2017, 5, 1)

ordinal_range = range(ds.toordinal(), de.toordinal())

for o in ordinal_range:
    d = datetime.date.fromordinal(o)
    # date_to_fetch = "%04d%02d%02d" % (d.year, d.month, d.day)

    fetch_log(d.year, d.month, d.day, telescope="a")
