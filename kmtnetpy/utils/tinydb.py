from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware


def get_db(json_name):
    db = TinyDB(json_name, storage=CachingMiddleware(JSONStorage))
    return db


    # Entry = Query()

    # with  as db:

    #     table = db.table('obslog')

    #     while True:
    #         fn, o = yield
    #         table.remove(Entry.logname == fn)
    #         table.insert(o)
