"""
This module stores the mta_codebase.db SQLAlchemy ORM classes.

Alembic is use to iterate schema developmetns and database migrations, meaning that
if you want to add an additional attribute to a database entry, such as a flag of a data source now in Maude, use alembic

To allow for the documentation of this codebase to be interpretable as a digraph, we use two fundamental base tables and subclass them

- File(Base): A file on our disk operates as a node on the graph, we subclass to trace data files and executable code
    - CodeFile(File): Executable code, like a script or library
    - C
    - DataFile(File): Stores a dataset of some type
    - SymlinkFile(File): Special case to mark symlink relationships

- Edge(Base): A relationship between files is directed edge on the graph,
    this relationship could that one file reads another, writes another, or calls another as a script, ect.
"""
from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class File(Base):
    __tablename__ = "files"

    path = Column(String, primary_key=True)
    file_type = Column(String)
    owner = Column(String)

    __mapper_args__ = {
        "polymorphic_on": file_type,
        "polymorphic_identity": "file",
    }


class CodeFile(File):
    __tablename__ = "code_files"

    path = Column(String, ForeignKey("files.path"), primary_key=True)
    language = Column(String)

    __mapper_args__ = {"polymorphic_identity": "code"}


class DataFile(File):
    __tablename__ = "data_files"

    path = Column(String, ForeignKey("files.path"), primary_key=True)
    schema = Column(String)
    is_from_maude = Column(Boolean, default=False)

    __mapper_args__ = {"polymorphic_identity": "data"}


class SymlinkFile(File):
    __tablename__ = "symlink_files"

    path = Column(String, ForeignKey("files.path"), primary_key=True)
    target = Column(String)

    __mapper_args__ = {"polymorphic_identity": "symlink"}


class Edge(Base):
    __tablename__ = "edges"

    src = Column(String, ForeignKey("files.path"), primary_key=True)
    dst = Column(String, ForeignKey("files.path"), primary_key=True)
    relation = Column(String, primary_key=True)