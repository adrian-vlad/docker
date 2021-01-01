__all__ = ["Reader", "Writer"]

import sqlite3


class Reader(object):
    ISOLATION_LEVEL = "DEFERRED"

    def __init__(self, db_path):
        self._c = sqlite3.connect(db_path, isolation_level=self.ISOLATION_LEVEL)
        self._c.row_factory = sqlite3.Row
        self._c.execute("pragma journal_mode=wal;")

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self._c.close()

    def __del__(self):
        self._c.close()

    def read(self, query, parameters=()):
        return self._c.execute(query, parameters).fetchall()


class Writer(Reader):
    ISOLATION_LEVEL = "IMMEDIATE"

    def write(self, query, parameters=()):
        self.read(query, parameters)
        self._c.commit()
