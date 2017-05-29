import os


_celery_conf = dict(backend='rpc://')


def set_celery_conf(**kw):
    _celery_conf.update(kw)


def get_celery_conf():
    c = _celery_conf.copy()
    if ("broker" not in c) and ("KSP_CELERY_BROKER" in os.environ):
        c["broker"] = os.environ["KSP_CELERY_BROKER"]

    return c
