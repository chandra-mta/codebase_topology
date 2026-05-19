import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

TOPOLOGY_DB_NAME = os.getenv("TOPOLOGY_DB_NAME", "mta_codebase.db")
TOPOLOGY_DB_DIR = os.getenv("TOPOLOGY_DB_DIR")
_echo = bool(os.getenv('ECHO', False))
if TOPOLOGY_DB_DIR is None:
    #: Relative Path
    DB_URL = f"sqlite:///{TOPOLOGY_DB_NAME}"
else:
    DB_URL = f"sqlite:///{Path(TOPOLOGY_DB_DIR, TOPOLOGY_DB_NAME)}"

_engine = create_engine(DB_URL, echo=_echo)
_SessionLocal = sessionmaker(bind=_engine)

def get_session():
    return _SessionLocal()