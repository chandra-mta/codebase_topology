import os
from pathlib import Path
from sqlalchemy import create_engine, event, func
from sqlalchemy.orm import Session, sessionmaker, object_mapper

TOPOLOGY_DB_NAME = os.getenv("TOPOLOGY_DB_NAME", "mta_codebase.db")
TOPOLOGY_DB_DIR = os.getenv("TOPOLOGY_DB_DIR")
_echo = bool(os.getenv('ECHO', False))
if TOPOLOGY_DB_DIR is None:
    #: Relative Path
    DB_URL = f"sqlite:///{TOPOLOGY_DB_NAME}"
else:
    DB_URL = f"sqlite:///{Path(TOPOLOGY_DB_DIR, TOPOLOGY_DB_NAME)}"

engine = create_engine(DB_URL, echo=_echo)
SessionLocal = sessionmaker(bind=engine)

def get_session():
    return SessionLocal()

#: Automatically update the polymorphic base class for any Node or Edge with a last_updated time stamp,
#: based off of listening to when a session will flush data to the database.
@event.listens_for(Session, "before_flush")
def propagate_last_updates(session, *_):
    for obj in session.dirty:
        mapper = object_mapper(obj)
        
        #: Walk up inheritance
        while mapper.inherits is not None:
            mapper = mapper.inherits

        if hasattr(obj, "last_updated"):
            obj.last_updated = func.now()