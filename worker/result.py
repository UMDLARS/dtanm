# Set up database connection
import os
POSTGRES_USER = os.environ.get('POSTGRES_USER', 'postgres')
POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'postgres')
POSTGRES_DB = os.environ.get('POSTGRES_DB', 'postgres')
SQLALCHEMY_DATABASE_URI = f'postgresql://{POSTGRES_USER}@{POSTGRES_HOST}/{POSTGRES_DB}'

from sqlalchemy import create_engine
engine = create_engine(SQLALCHEMY_DATABASE_URI)
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()

# Define mapping
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

# Set up result class
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Boolean, Text, Float
from sqlalchemy.sql import func
from sqlalchemy.schema import Table
class Result(Base):
    __table__ = Table('result', Base.metadata,
                      autoload=True, autoload_with=engine)
