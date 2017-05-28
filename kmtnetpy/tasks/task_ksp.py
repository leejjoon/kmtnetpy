from celery import Celery

from ..mpc.ksp_mpc import retrieve_mpc

from ..detectors.ksp_detectors import find as find_detectors


app = Celery('task_ksp', backend='rpc://', broker='amqp://guest@localhost//')


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
