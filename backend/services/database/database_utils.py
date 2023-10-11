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
from backend.models.models import Base

# Initialize Database
def get_engine(db_uri=DB_URI):
    return create_engine(db_uri)

def initialize_database(db_uri=DB_URI):
    engine = get_engine()
    Base.metadata.create_all(engine)
    return engine

engine = initialize_database()

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
    session = get_session(engine)
    
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
