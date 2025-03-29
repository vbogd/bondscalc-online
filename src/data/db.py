import datetime
import sqlite3
import logging
from sqlite3 import Connection

from .moex import BasicBondInfo, load_moex_marketdata, load_moex_securities, BondMarketData

# Useful docs:
# - https://pradyunsg-cpython-lutra-testing.readthedocs.io/en/latest/library/sqlite3.html#sqlite3-adapter-converter-recipes

_db_name = 'bonds.db'
logger = logging.getLogger(__name__)

# configure database
def _adapt_date_iso(val):
    """Adapt datetime.date to ISO 8601 date."""
    return val.isoformat()

def _convert_date_iso(val):
    """Convert ISO 8601 date to datetime.date object."""
    return datetime.date.fromisoformat(val.decode())

sqlite3.register_adapter(datetime.date, _adapt_date_iso)
sqlite3.register_converter("date", _convert_date_iso)
# end of configure database

def _db_connection() -> Connection:
    return sqlite3.connect(_db_name, detect_types=sqlite3.PARSE_DECLTYPES)


def _db_create_moex_marketdata_table(con: Connection):
    con.execute('''DROP TABLE IF EXISTS moex_marketdata''')
    con.execute('''
        CREATE TABLE moex_marketdata(
            secid      TEXT NOT NULL PRIMARY KEY,
            last_price REAL NOT NULL
        )
    ''')


def _db_create_moex_bonds_table(con: Connection):
    con.execute('''DROP TABLE IF EXISTS moex_bonds''')
    con.execute('''
        CREATE TABLE IF NOT EXISTS moex_bonds(
            shortname_lc TEXT NOT NULL,
            shortname TEXT NOT NULL,
            secid TEXT NOT NULL,
            isin TEXT NOT NULL,
            mat_date date,
            coupon_percent REAL,
            list_level INTEGER NOT NULL,
            coupon_value REAL,
            coupon_date date NOT NULL,
            nkd REAL NOT NULL,
            currency_id TEXT NOT NULL,
            face_unit TEXT NOT NULL,
            face_value REAL NOT NULL,
            coupon_period INTEGER NOT NULL,
            issue_size INTEGER NOT NULL,
            offer_date date,
            prev_price REAL,
            reg_number TEXT
        )
    ''')


def moex_bonds_db_update(bonds: list[BasicBondInfo]):
    con = _db_connection()
    try:
        with con:
            con.execute("DELETE FROM moex_bonds")
            for b in bonds:
                con.execute('''
                        INSERT INTO moex_bonds
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''',
                   (b.shortname.casefold(),) + tuple(b)
               )
        logger.info(f'Updated {len(bonds)} records in moex_bonds table')
    except Exception as e:
        logger.error(f"Failed to update moex_bonds table:\n{e}")
    finally:
        con.close()


def moex_bonds_db_search(query: str, limit: int = 100) -> list[BasicBondInfo]:
    con = _db_connection()
    try:
        bonds = con.execute('''
                SELECT
                    shortname, moex_bonds.secid, isin, mat_date, coupon_percent,
                    list_level, coupon_value, coupon_date, nkd, currency_id,
                    face_unit, face_value, coupon_period, issue_size, offer_date,
                    ifnull(last_price, prev_price) as price,
                    reg_number
                FROM moex_bonds
                LEFT JOIN moex_marketdata ON moex_bonds.secid = moex_marketdata.secid
                WHERE (shortname_lc like ? or isin like ? or moex_bonds.secid = ?)
                ORDER BY shortname_lc
                LIMIT ?
            ''',
            (f'%{query.casefold()}%', f'%{query.upper()}%', query, limit)
        ).fetchall()
        bonds = [BasicBondInfo(*b) for b in bonds]
        return bonds
    except Exception as e:
        logger.error(f"DB search failed. Query: {query}\nError:\n{e}")
        return []
    finally:
        con.close()

def moex_bonds_db_get(secid: str) -> BasicBondInfo | None:
    bonds = moex_bonds_db_search(secid, limit=1)
    if len(bonds) == 1:
        return bonds[0]
    else:
        return None


def moex_marketdata_db_update(rows: list[BondMarketData]):
    con = _db_connection()
    try:
        with con:
            con.execute("DELETE FROM moex_marketdata")
            for r in rows:
                con.execute('''
                        INSERT OR REPLACE INTO moex_marketdata
                        VALUES(?, ?)
                    ''',
                    tuple(r)
                )
        logger.info(f'Updated {len(rows)} record(s) in moex_marketdata table')
    except Exception as e:
        logger.error(f"Failed to update moex_marketdata table:\n{e}")
    finally:
        con.close()


def db_create_tables():
    con = _db_connection()
    try:
        with con:
            _db_create_moex_marketdata_table(con)
            _db_create_moex_bonds_table(con)
    finally:
        con.close()


def update_local_bonds_db():
    logger.info(f'Loading bond securities from MOEX...')
    data = load_moex_securities()
    logger.info(f'Loaded {len(data)} bond securities from MOEX')
    moex_bonds_db_update(data)


def update_local_db_marketdata():
    logger.info(f'Loading bonds marketdata from MOEX...')
    data = load_moex_marketdata()
    logger.info(f'Loaded {len(data)} bonds marketdata from MOEX')
    moex_marketdata_db_update(data)
