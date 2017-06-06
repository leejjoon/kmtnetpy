from celery import Celery

from ..mpc.ksp_mpc import retrieve_mpc

from ..detectors.ksp_detectors import find as find_detectors
from ..stamps import (get_diff_cat_from_key,
                      get_stamps_from_key)

from .task_config import get_celery_conf


conf = get_celery_conf()
# print(conf)

app = Celery('task_ksp', config_source=conf)

# app = Celery('task_ksp', config_source=Struct(**conf))
# , backend='rpc://', broker='amqp://guest@localhost//')


@app.task
def query_mpc(entry_id, logid, groupid, ra, dec, jd):
    if logid != groupid:
        return None
    else:
        r = retrieve_mpc(ra, dec, jd)
        # fn = entry_id + ".json"
        # json.dump(r, open(fn, "w"))

        return r


@app.task
def find_detector(filename_key, ra_list, dec_list):
    return find_detectors(filename_key, ra_list, dec_list)


@app.task
def get_stamps_as_s(filename_key, xy_list, size=64, base64=True):
    s = get_stamps_from_key(filename_key, xy_list, size=size,
                            as_string=True, base64=base64)
    return s


@app.task
def get_diff_cat_as_s(filename_key, xy_list, base64=True):
    s = get_diff_cat_from_key(filename_key, xy_list, base64=base64)
    return s
