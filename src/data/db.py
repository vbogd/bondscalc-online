import sqlite3
import logging

from .moex import BasicBondInfo, load_moex_bonds


_db_name = 'bonds.db'
logger = logging.getLogger(__name__)


def moex_bonds_db_create():
    connection = sqlite3.connect(_db_name)
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS moex_bonds
        (
            shortname_lc TEXT NOT NULL,
            shortname TEXT NOT NULL,
            secid TEXT NOT NULL,
            isin TEXT NOT NULL,
            mat_date TEXT NOT NULL,
            coupon_percent REAL,
            list_level INTEGER NOT NULL,
            coupon_value REAL NOT NULL,
            coupon_date TEXT NOT NULL,
            nkd REAL NOT NULL,
            currency_id TEXT NOT NULL,
            face_unit TEXT NOT NULL,
            face_value REAL NOT NULL,
            coupon_period INTEGER NOT NULL,
            issue_size INTEGER NOT NULL,
            offer_date DATE
        )
    ''')
    connection.commit()
    connection.close()


def moex_bonds_db_update(bonds: list[BasicBondInfo]):
    connection = sqlite3.connect(_db_name)
    cursor = connection.cursor()
    cursor.execute("DELETE FROM moex_bonds")
    for b in bonds:
        cursor.execute('''
                INSERT INTO moex_bonds
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
           (b.shortname.casefold(),) + tuple(b)
       )
    connection.commit()
    connection.close()


def moex_bonds_db_search(query: str, limit: int = 100) -> list[BasicBondInfo]:
    con = sqlite3.connect(_db_name)
    try:
        bonds = con.cursor().execute('''
                SELECT *
                FROM moex_bonds
                WHERE (shortname_lc like ? or isin like ?)
                ORDER BY shortname_lc
                LIMIT ?
            ''',
            (f'%{query.casefold()}%', f'%{query.upper()}%', limit)
        ).fetchall()
        bonds = [BasicBondInfo(*b[1:]) for b in bonds]
        return bonds
    except Exception as e:
        logger.error(f"DB search failed. Query: {query}\nError:\n{e}")
        return []
    finally:
        con.close()


def update_local_bonds_db():
    moex_bonds_db_create()
    logger.info(f'Loading bonds from MOEX...')
    data = load_moex_bonds()
    logger.info(f'Loaded {len(data)} bonds from MOEX')
    moex_bonds_db_update(data)
    logger.info(f'Updated {len(data)} bonds in db')
