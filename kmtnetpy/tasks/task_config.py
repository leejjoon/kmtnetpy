import os


_celery_conf = dict(backend='rpc://')


def set_celery_conf(**kw):
    _celery_conf.update(kw)


def get_celery_conf():
    if ("broker" not in _celery_conf) and ("KSP_CELERY_BROKER" in os.environ):
        _celery_conf["broker"] = os.environ["KSP_CELERY_BROKER"]
    c = dict(broker='amqp://guest@localhost:5673//',
             backend='rpc://')

    return c
