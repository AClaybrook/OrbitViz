from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sgp4.io import twoline2rv
from sgp4.earth_gravity import wgs72
from typing import Union, Tuple
import math
from contextlib import contextmanager
from functools import wraps
import sqlite3
import os
from config import DB_URI, DB_PATH
from backend.models.models import Base, engine

def get_engine(db_uri=DB_URI):
    return create_engine(db_uri)

def initialize_database(db_uri=DB_URI):
    engine = create_engine(db_uri, echo=True)
    Base.metadata.create_all(engine)
    print(db_uri)
    print(DB_URI)
    return engine

initialize_database()
def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()

@contextmanager
def db_session(engine):
    """
    Context manager to provide a database session.
    
    Args:
        engine (sqlalchemy.engine.base.Engine): The database engine.
    
    Yields:
        sqlalchemy.orm.Session: The database session.
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        yield session
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def with_session(func):
    """Decorator to provide a database session to a function if it does not exist.
        Passing a session is faster than creating a new one, but it is tedious to pass it every time."""
    @wraps(func)
    def wrapper(*args, session=None, **kwargs):
        if session is None:
            with db_session(engine) as session:
                return func(*args, session=session, **kwargs)
        else:
            return func(*args, session=session, **kwargs)
    return wrapper


class SQLiteConnectionManager:
    def __init__(self):
        self.database_path = DB_PATH
        self.conn = None
        self.connection_count = 0

    def __enter__(self):
        self.conn = sqlite3.connect(self.database_path)
        self.connection_count += 1
        return self.conn

    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn:
            self.conn.close()
            self.connection_count -= 1
