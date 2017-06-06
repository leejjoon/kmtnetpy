tel_dict = dict(ctio="C", saao="S", aao="A")


def get_key(log, qname="Q0", ensure_upper_keynames=False):
    # filedname, Q#, filt, datetime, telescope, fileid

    if ensure_upper_keynames:
        log = dict((k.upper(), v) for k, v in log.iteritems())

    # log["FILT"]
    _d, _t = log["DATE-OBS"].split("T")
    dd = "".join(_d.split("-"))[2:]
    tt = "".join(_t.split(":"))[:4]
    # log["FILEID"]

    k = (log["NEAREST_FIELD"], qname, log["FILT"], "%s_%s" % (dd, tt),
         tel_dict.get(log["TEL"], ""), log["FILEID"])

    return k


def make_filename_key_dict(filename_key, logid):
    d = dict(zip(["fieldname", "qn", "filt", "obstime", "tel", "obsid"],
                 filename_key))
    del d["qn"]
    d["logid"] = logid

    return d


# def make_filename_key_from_dict(d, qname=None, ensure_lower_keynames=True):

#     if ensure_lower_keynames:
#         d = dict((k.lower(), v) for k, v in d.iteritems())

#     if qname is not None:
#         d["qn"] = qname

#     keys = ["fieldname", "qn", "filt", "obstime", "tel", "obsid"]
#     filename_key = [d[k] for k in keys]

#     return filename_key

def dict_to_filename_key(d, qn=None):
    keys = ["fieldname", "filt", "obstime", "tel", "obsid"]
    r = list(d[k] for k in keys)

    if qn is None:
        qn_string = d.get("qn", "Q0")
    else:
        qn_string = "Q%d" % qn

    r.insert(1, qn_string)

    return r


def filename_set_qn(filename_key, qn):
    filename_key = list(filename_key)
    filename_key[1] = "Q%d" % qn
    return filename_key
