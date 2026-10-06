"""Download CRSP daily data for the ETFs from WRDS.

Needs a WRDS account. Put the password in ~/.pgpass (chmod 600):
    wrds-pgdata.wharton.upenn.edu:9737:wrds:<username>:<password>
and run:  WRDS_USER=<username> python src/download_wrds.py

Pulls both the CIZ table (crsp.dsf_v2, current) and the legacy SIZ table
(crsp.dsf, frozen at end-2024) with every column, so nothing has to be
re-downloaded when choosing fields later.
"""
import os

import pandas as pd
import psycopg

from config import PERMNOS, RAW, START

CONN = dict(
    host="wrds-pgdata.wharton.upenn.edu",
    port=9737,
    dbname="wrds",
    sslmode="require",
)


def query(conn, sql, params=None):
    with conn.cursor() as cur:
        cur.execute(sql, params)
        cols = [d.name for d in cur.description]
        return pd.DataFrame(cur.fetchall(), columns=cols)


def main():
    user = os.environ.get("WRDS_USER")
    if not user:
        raise SystemExit("Set WRDS_USER to your WRDS username (password goes in ~/.pgpass)")
    RAW.mkdir(parents=True, exist_ok=True)
    permnos = list(PERMNOS.values())

    with psycopg.connect(user=user, **CONN) as conn:
        names = query(
            conn,
            "select permno, ticker, comnam, namedt, nameenddt from crsp.stocknames "
            "where permno = any(%s) order by permno, namedt",
            (permnos,),
        )
        print(names.to_string(index=False))
        for t, p in PERMNOS.items():
            if t not in set(names.loc[names.permno == p, "ticker"]):
                raise SystemExit(f"PERMNO {p} is not listed under ticker {t}; check config.PERMNOS")

        for table, date_col, out in [
            ("crsp.dsf_v2", "dlycaldt", "crsp_dsf_v2.parquet"),
            ("crsp.dsf", "date", "crsp_dsf.parquet"),
        ]:
            try:
                df = query(
                    conn,
                    f"select * from {table} where permno = any(%s) and {date_col} >= %s "
                    f"order by permno, {date_col}",
                    (permnos, START),
                )
            except psycopg.Error as e:
                conn.rollback()
                print(f"{table}: skipped ({e.__class__.__name__}: {e})")
                continue
            df.to_parquet(RAW / out)
            print(f"{table}: {len(df)} rows, {df[date_col].min()} to {df[date_col].max()} -> {out}")


if __name__ == "__main__":
    main()
