import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_DIR = os.getenv("DB_DIR")
_echo = bool(os.getenv('ECHO', False))
if DB_DIR is None:
    #: Relative Path
    DB_URL = "sqlite:///mta_codebase.db"
else:
    DB_URL = f"sqlite:///{Path(DB_DIR, "mta_codebase.db")}"

engine = create_engine(DB_URL, echo=_echo)
SessionLocal = sessionmaker(bind=engine)

def get_session():
    return SessionLocal()