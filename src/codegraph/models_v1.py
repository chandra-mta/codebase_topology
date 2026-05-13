"""
This module stores the mta_codebase.db SQLAlchemy ORM classes.

Alembic is use to iterate schema developmetns and database migrations, meaning that
if you want to add an additional attribute to a database entry, such as a flag of a data source now in Maude, use alembic

To allow for the documentation of this codebase to be interpretable as a digraph, we use two fundamental base tables and subclass them

- Node(Base): A node constitutes a persistent entity on our system, typically a file or a cronjob.
    - File(Node): A file on our disk, we subclass to trace data files and executable code
        - CodeFile(File): Executable code, like a script or library
        - SymlinkFile(File): Special case to mark symlink relationships
        - DataFile(File): Stores a dataset of some type, typically a monitored data value
            - ConfigFile(DataFile): Stores specifically semi-permanent data that influences decisions of code algorithm
            - LogFile(DataFile): Stores transient logs of code operation

    - CronJob(Node): Records a cronjob on the CfA system, defined as a node to trace relationships of CodeFile execution to machine and schedule
            
- Edge(Base): A relationship between files is directed edge on the graph,
    this relationship could that one file reads another, writes another, or calls another as a script, ect.
    Relationship types overview:
    - reads: This node (eg CodeFile) reads another node (eg DataFile)
    - writes: This node (eg CodeFile) writes content to another node (eg DataFile)
        - uses_config: This node (eg CodeFile) has a special relationship depending on the persistent ConfigFile
        - logs: This node (eg CodeFile CronJob) has a special relationship for logging transient operational information to a LogFile node
    - calls: This node (eg CodeFile) invokes the operation of another node (eg CodeFile) for dependent logic. (Control Plane)
        - imports: This node (eg CodeFile) depends on another node (eg CodeFile)
        - triggers: This CronJob node triggers a command related to the File node. External initiation entry point. (Execution Plane)
    - resolves_to: Special relationship documenting a SymlinkFile node matching to a File (eg DataFile or CodeFile)
    - mirrors: Special relationship in which a primary and secondary instance of Nodes is recorded. For documented intention of completing task.

"""
from sqlalchemy import Column, String, Boolean, ForeignKey, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Node(Base):
    __tablename__ = "nodes"

    id = Column(String, primary_key=True)
    node_type = Column(String)

    __mapper_args__ = {
        "polymorphic_on": node_type,
        "polymorphic_identity": "node",
    }

class File(Node):
    __tablename__ = "files"

    id = Column(String, ForeignKey("nodes.id"), primary_key=True)
    path = Column(String, unique=True, index=True)
    owner = Column(String)

    __mapper_args__ = {
        "polymorphic_identity": "file",
    }

class CodeFile(File):
    __tablename__ = "code_files"

    id = Column(String, ForeignKey("files.id"), primary_key=True)
    language = Column(String)

    __mapper_args__ = {"polymorphic_identity": "code"}

class SymlinkFile(File):
    __tablename__ = "symlink_files"

    id = Column(String, ForeignKey("files.id"), primary_key=True)
    target = Column(String)

    __mapper_args__ = {"polymorphic_identity": "symlink"}

class DataFile(File):
    __tablename__ = "data_files"

    id = Column(String, ForeignKey("files.id"), primary_key=True)
    schema = Column(String)

    __mapper_args__ = {"polymorphic_identity": "data"}

class ConfigFile(DataFile):
    __tablename__ = "config_files"

    id = Column(ForeignKey("data_files.id"), primary_key=True)

    __mapper_args__ = {"polymorphic_identity": "config"}

class LogFile(DataFile):
    __tablename__ = "log_files"

    id = Column(ForeignKey("data_files.id"), primary_key=True)
    retention = Column(String)

    __mapper_args__ = {"polymorphic_identity": "log"}

class Edge(Base):
    __tablename__ = "edges"

    id = Column(String, primary_key=True)
    src = Column(String, ForeignKey("nodes.id"), primary_key=True)
    dst = Column(String, ForeignKey("nodes.id"), primary_key=True)
    relation = Column(String)

class CronJob(Node):
    __tablename__ = "cron_jobs"

    id = Column(String, ForeignKey("nodes.id"), primary_key=True)

    cadence = Column(String)
    user = Column(String)
    machine = Column(String)
    github_repo = Column(String)
    script_set = Column(String)
    command = Column(String)
    env = Column(JSON)

    __mapper_args__ = {"polymorphic_identity": "cron"}