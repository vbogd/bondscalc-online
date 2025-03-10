import datetime
import sqlite3
import logging

from .moex import BasicBondInfo, load_moex_bonds

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

def _db_connection():
    return sqlite3.connect(_db_name, detect_types=sqlite3.PARSE_DECLTYPES)


def moex_bonds_db_create():
    con = _db_connection()
    try:
        with con:
            con.execute('''
                CREATE TABLE IF NOT EXISTS moex_bonds
                (
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
                    offer_date date
                )
            ''')
    finally:
        con.close()


def moex_bonds_db_update(bonds: list[BasicBondInfo]):
    con = _db_connection()
    try:
        with con:
            con.execute("DELETE FROM moex_bonds")
            for b in bonds:
                con.execute('''
                        INSERT INTO moex_bonds
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''',
                   (b.shortname.casefold(),) + tuple(b)
               )
    except Exception as e:
        logger.error(f"Failed to update bonds:\n{e}")
    finally:
        con.close()


def moex_bonds_db_search(query: str, limit: int = 100) -> list[BasicBondInfo]:
    con = _db_connection()
    try:
        bonds = con.execute('''
                SELECT *
                FROM moex_bonds
                WHERE (shortname_lc like ? or isin like ? or secid = ?)
                ORDER BY shortname_lc
                LIMIT ?
            ''',
            (f'%{query.casefold()}%', f'%{query.upper()}%', query, limit)
        ).fetchall()
        bonds = [BasicBondInfo(*b[1:]) for b in bonds]
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


def update_local_bonds_db():
    moex_bonds_db_create()
    logger.info(f'Loading bonds from MOEX...')
    data = load_moex_bonds()
    logger.info(f'Loaded {len(data)} bonds from MOEX')
    moex_bonds_db_update(data)
    logger.info(f'Updated {len(data)} bonds in db')
