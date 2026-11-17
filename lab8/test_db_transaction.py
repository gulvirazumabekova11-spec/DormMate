"""SQLite transaction rollback demonstration (isolated test database).
This checks rollback semantics, NOT the DormMate app's own business transaction.
"""
import sqlite3


def test_transaction_rolls_back_if_required_field_missing():
    conn = sqlite3.connect(':memory:')
    try:
        conn.execute('CREATE TABLE samples (id INTEGER PRIMARY KEY, name TEXT NOT NULL)')
        conn.execute('INSERT INTO samples (name) VALUES (?)', ('Бастапқы',))
        conn.commit()
        try:
            conn.execute('INSERT INTO samples (name) VALUES (?)', ('Уақытша',))
            conn.execute('INSERT INTO samples (name) VALUES (?)', (None,))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.rollback()
        names = [row[0] for row in conn.execute('SELECT name FROM samples ORDER BY id')]
        assert names == ['Бастапқы']
    finally:
        conn.close()
