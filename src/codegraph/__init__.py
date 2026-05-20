from .models import *
from .db import *

def init_db():
    """
    Initialize the codegraph database and/or bind the engine.
    """
    Base.metadata.create_all(bind=engine)