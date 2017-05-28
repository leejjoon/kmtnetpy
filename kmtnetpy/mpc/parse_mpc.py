import StringIO
from HTMLParser import HTMLParser
import pandas as pd
from astropy import coordinates as coords


class PreHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self._pre_started = False
        self._table_started = False
        self.data = []

    def handle_starttag(self, tag, attrs):
        if tag == "pre":
            self._pre_started = True

    def handle_endtag(self, tag):
        if tag == "pre":
            self._pre_started = False

    def handle_data(self, data):
        if self._pre_started:
            if "Object designation" in data:
                self._table_started = True

            if self._table_started:
                self.data.append(data)


def parse_result(s):
    p = PreHTMLParser()
    p.feed(s)

    if not len(p.data):
        return None

    # skip blank lines
    l1 = [l for l in "".join(p.data).split("\n") if l.strip()]

    ll = StringIO.StringIO("\n".join(l1))

    header = ["name", "radec", "Vmag", "offset", "motion"]
    colspec = [(0, 24), (25, 45), (47, 51), (52, 65), (66, 79)]

    df = pd.read_fwf(ll, colspec, skiprows=2, names=header)

    c = coords.SkyCoord(list(df["radec"]), unit=("hour", "degree"))
    df["ra"] = c.ra.deg
    df["dec"] = c.dec.deg

    return df


if __name__ == "__main__":

    s = open("test.html").read()

    df = parse_result(s)
