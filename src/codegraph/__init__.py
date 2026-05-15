from .models import *
from .db import *

Base.metadata.create_all(bind=engine)