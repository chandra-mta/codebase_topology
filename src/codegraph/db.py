import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.inspection import inspect
from sqlalchemy.ext.hybrid import hybrid_property

_ALLOWED_HYBRID_PROPERTIES = (
    'filename',
    'url'
)

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

def orm_to_dict(orm_obj):
    mapper = inspect(orm_obj).mapper

    # 1. Regular column attributes
    data = {
        attr.key: getattr(orm_obj, attr.key)
        for attr in mapper.column_attrs
    }

    # 2. Hybrid properties
    for name, descriptor in mapper.all_orm_descriptors.items():
        if name in _ALLOWED_HYBRID_PROPERTIES:
            if isinstance(descriptor, hybrid_property):
                try:
                    data[name] = getattr(orm_obj, name)
                except Exception:
                    # Skip if evaluation fails (e.g. requires unloaded relationship)
                    pass
    return data