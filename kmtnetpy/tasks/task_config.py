import os


# _celery_conf_old = dict(backend='rpc://',
#                         result_serializer='msgpack')


_celery_conf = dict(result_backend='rpc://',
                    result_serializer='msgpack',
                    # result_serializer='json',
                    accept_content=["json", "msgpack"])


def set_celery_conf(**kw):
    _celery_conf.update(kw)


def get_celery_conf():
    c = _celery_conf.copy()
    if ("broker_url" not in c) and ("KSP_CELERY_BROKER" in os.environ):
        c["broker_url"] = os.environ["KSP_CELERY_BROKER"]

    return c
