import sqlite3
import psycopg2
from psycopg2 import sql


class Database:
    def __init__(self, info_str, db_type='sqlite3'):
        self.conn = None
        self.db_type = db_type
        
        if db_type == 'sqlite3':
            self.conn = sqlite3.connect(info_str)
        elif db_type == 'postgres':
            self.conn = psycopg2.connect(info_str)
        else:
            raise ValueError('Invalid `db_type`: ' + db_type)
        
    def __del__(self):
        self.conn.close()
    
    @property
    def sql(self):
        if self.db_type == 'postgres':
            return sql
        else:
            return None
        
