import pandas as pd


def save_all():
    from tinydb import TinyDB

    with TinyDB('ksp_obs_log.json') as db:

        table = db.table('obslog')

        l = table.all()

    df = pd.DataFrame(l).fillna(0)
    df2 = df.loc[:, ["logname", "nobs", "BAD_COORD", "BAD_NAME"]]

    def _highlight_row(row):
        if row.iloc[2:].sum() >= 1:
            return ['background-color: yellow'] * len(row)
        else:
            return [""] * len(row)

    def get_a(fn):
        link = "{}_table.html".format(fn)
        return "<a href='{}' target='_blank'>{}</a>".format(link, fn)

    df2["logname"] = df2["logname"].map(get_a)

    style = df2.style.apply(_highlight_row, axis=1)
    open("sum.html", "w").write(style.render())


save_all()
