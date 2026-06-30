from sqlalchemy import create_engine
from sqlalchemy.orm import (sessionmaker, declarative_base)
from dotenv import load_dotenv
import os


load_dotenv()
DATABASE_URL = "postgresql://postgres:root%40123@localhost:5432/toprankr"
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()