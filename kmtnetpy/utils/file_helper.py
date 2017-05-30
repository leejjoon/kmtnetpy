import os
import re
import glob

_p = re.compile(r"\.(Q\d)\.")

PROCESSED_ROOT = "./PROCESSED"


def get_processed_root():
    return PROCESSED_ROOT


def get_data_dir(filename_key, qn=None, rootdir=None, subdir=None):
    if rootdir is None:
        rootdir = get_processed_root()

    field_name = filename_key[0]
    field_name0 = field_name.split("-")[0]

    if qn is None:
        qn_string = filename_key[1]
    else:
        qn_string = "Q%d" % qn

    data_dir = os.path.join(rootdir, field_name0, field_name, qn_string)

    if subdir is not None:
        data_dir = os.path.join(data_dir, subdir)

    return data_dir


def get_root(filename_key, qn=None):
    filename_key = list(filename_key)
    root = ".".join(filename_key)
    if qn is not None:
        root = _p.sub(".Q%d." % qn, root)

    return root


def get_filename(root, data_dir, ext_pattern, subdir=None):
    fn0 = "".join([root, "*", ext_pattern])
    if subdir is None:
        fl = glob.glob(os.path.join(data_dir, fn0))
    else:
        fl = glob.glob(os.path.join(data_dir, subdir, fn0))

    if len(fl) == 1:
        fn = fl[0]
        return fn
    elif len(fl) == 0:
        raise RuntimeError("no file found: %s" % fn0)
    else:
        raise RuntimeError("miltiple file found: %s" % fn0)
