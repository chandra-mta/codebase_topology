"""
This module stores the mta_codebase.db SQLAlchemy ORM classes.

Alembic is use to iterate schema developmetns and database migrations, meaning that
if you want to add an additional attribute to a database entry, use alembic

To allow for the documentation of this codebase to be interpretable as a digraph, we use two fundamental base tables and subclass them

- Node(Base): A node constitutes a persistent entity on our system, typically a file or a cronjob.
- Edge(Base): A relationship between files is directed edge on the graph,
    this relationship could that one file reads another, writes another, or calls another as a script, ect.

Tables outside of the Node and Edge constructs are for storing metadata information and context documentation which help inform the nodes and edges.
"""
import re
from pprint import pformat
import enum
import warnings
from sqlalchemy import Column, String, Integer, ForeignKey, JSON, DateTime, Enum, Float, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship, validates, hybrid_property

VAR_PATTERN = re.compile(r'\$\{([A-Za-z_]\w*)\}|\$([A-Za-z_]\w*)')

#: Configure a validator warning for any data file schema not previously considered, but allow injection.
_FILE_SCHEMA = (
    None,
    'custom',
    'json',
    'ecsv',
    'csv',
    'tab_delimited',
    'fits',
    'hdf5',
    'sql',
    'pickle',
    'html',
    'xml',
    'css',
    'png',
    'jpg',
    'gif',
)


def _validator_template(key,value):
    if value is None:
        return value
    if not VAR_PATTERN.search(value):
        raise ValueError(f"Template '{value}' must contain at least one variable reference like $VAR or ${{VAR}}.")

def _validator_schema(key,value):
    if value not in _FILE_SCHEMA:
        warnings.warn(f"Injected schema '{value}' not previously identified. Check for errors.")
    return value

Base = declarative_base()

def resolve(template: str, env: dict) -> str:
    if template is None:
        return None

    def replacer(match):
        # group(1) = ${VAR}, group(2) = $VAR
        var_name = match.group(1) if match.group(1) is not None else match.group(2)

        if var_name in env:
            return env[var_name]

        # leave untouched if not found
        return match.group(0)

    return VAR_PATTERN.sub(replacer, template)

class FileType(str,enum.Enum):
    regular = "regular"
    directory = "directory"
    symbolic_link = "symbolic_link"
    socket = "socket"
    fifo_special = "fifo_special"
    block_special = "block_special"
    character_special = "character_special"

class RelationType(str,enum.Enum):
    #: Defines behavior between nodes. Role attribute provides secondary nuance if desired.
    
    #: Read File I/O operation
    reads = "reads" #: Example roles: 'input' entire data file, 'lookup' specific value
    
    #: Write File I/O operation
    writes = "writes" #: Example roles: 'append' to a persistently growing file, 'temp' for a temporary file, 'overwrite' for always rewriting the file

    #: Start process execution
    triggers = "triggers" #: Example roles: 'scheduled' by periodic cronjob, 'manual' for user trigger, 'event' for asynchronous event trigger from listener.

    #: Continue process execution
    calls = "calls" #: Example roles:

    #: Dependency
    requires = "requires" #: Example roles: 'library', 'config', 'credential'

    #: Handle pathing variability between entities. Symlink?
    resolves_to = "resolves_to"

    #: mirroring relationship between nodes, for example a backup file or secondary instance of a cronjob on another machine for redundancy.
    mirrors = "mirrors"

class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True)
    node_type = Column(String) #: Discriminator column for SQLAlchemy class mapping.
    last_updated = Column(DateTime) #: ISO 8601 String
    documentation = Column(String) #: Short description of detailed docs of node information
    owner = Column(String) #: Categorical owner of Node. Unix file user ‘mta’, ‘cus’ or more general team/source like ‘DSOps’, ‘ACIS’, ‘MAUDE’.

    __mapper_args__ = {
        "polymorphic_on": node_type,
        "polymorphic_identity": "node",
    }

    outgoing_edges = relationship(
        "Edge",
        foreign_keys="Edge.src",
        back_populates="src",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    incoming_edges = relationship(
        "Edge",
        foreign_keys="Edge.dst",
        back_populates="dst",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    metadata = relationship(
        "NodeMetaData",
        foreign_keys="NodeMetaData.node_id",
        back_populates="node",
        cascade="all, delete-orphan"
    )

    @hybrid_property
    def edges(self):
        return self.outgoing_edges + self.incoming_edges
    
    @hybrid_property
    def successors(self):
        return [edge.dst for edge in self.outgoing_edges]

    @hybrid_property
    def predecessors(self):
        return [edge.src for edge in self.incoming_edges]

    def __repr__(self):
        return f"Node({self.id!r}, {self.node_type!r}, {self.last_updated!r})"

class CronTab(Node):
    __tablename__ = "cron_tables"

    machine = Column(String) #: computing host
    name = Column(String, unique=True) #: name of table, Official operating table is owner@machine
    variables = Column(JSON) #: Environment variables as key-value pairs

    jobs = relationship("CronJob", back_populates="crontab")

    __mapper_args__ = {"polymorphic_identity": "crontable"}

    def __repr__(self):
        return f"CronTab({self.id!r}, {self.name!r}, variables=\n{pformat(self.variables)})"

class CronJob(Node):
    __tablename__ = "cron_jobs"

    crontab_id = Column(Integer, ForeignKey("cron_tables.id")) #: Match individual cronjob to context table

    cadence = Column(String) #: Crontab five-field time string
    template_command = Column(String) #: Command run by cron daemon with environment variables.
    canonical_command = Column(String) #: Command run by cron daemon with environment variables.

    @hybrid_property
    def command(self):
        return self.resolve_command() or self.canonical_command

    crontab = relationship("CronTab", back_populates='jobs')

    __mapper_args__ = {"polymorphic_identity": "cronjob"}

    @validates("template_command")
    def validate_command(self, key, value):
        return _validator_template(key, value)

    def resolve_command(self):
        """
        Fetch related crontab to fill environment variables and resolve template_command.
        """
        if not self.template_command:
            return None

        env = self.crontab.variables if self.crontab else {}

        return resolve(self.template_command, env)

    def __repr__(self):
        return f"CronJob({self.id!r}, {self.crontab.name!r}, {self.cadence!r}, {self.command!r})"

class Credential(Node):
    """
    Documents a need for authentication as a dependency
    """
    __tablename__ = "credentials"

    name = Column(String) #: Name of authentication
    auth_type = Column(String) #: Authentication protocol verification method

    __mapper_args__ = {"polymorphic_identity": "credential"}

class Email(Node):
    """
    Documents a message sent to personnel
    """
    __tablename__ = "emails"

    reciever = Column(String) #: Reciever address
    sender = Column(String) #: Sender address
    subject = Column(String) #: Subject Line

    __mapper_args__ = {"polymorphic_identity": "email"}

class File(Node):
    """
    Unix File base class
    https://en.wikipedia.org/wiki/Unix_file_types
    """
    __tablename__ = "files"

    template_path = Column(String) #: File path with environment variable templates like $HOME or ${HOME}
    canonical_path = Column(String) #: File path with environment variable templates resolved to absolute paths
    nfs_server = Column(String) #: NFS server name
    file_type = Column(Enum(FileType)) #: Unix File Type

    @hybrid_property
    def path(self):
        return self.template_path or self.canonical_path

    @hybrid_property
    def filename(self):
        return self.path.split("/")[-1]

    __mapper_args__ = {"polymorphic_identity": "file"}

    @validates("template_path")
    def validate_path(self, key, value):
        return _validator_template(key, value)

    def __repr__(self):
        return f"File({self.id!r}, {self.file_type!r}, {self.filename!r})"

class CodeFile(File):
    """
    Executable codefile. Purpose is scripts for execution, not every file that can be executed (directories)
    """

    __tablename__ = "code_files"

    language = Column(String) #: programming language
    github_repo = Column(String) #: URL to source code

    __mapper_args__ = {"polymorphic_identity": "code_file"}

class LogFile(File):
    """
    Human-readable log of system events
    """

    __tablename__ = "log_files"

    retention = Column(Float) #: Number of days. Fractional days possible.

    __mapper_args__ = {"polymorphic_identity": "log_file"}

class DataFile(File):
    """
    Record of data, parseable by software.

    Note that certain data files are text files with parsing that is customized such that
    only the influencing software is configured to parse it, meaning that the file has no structure
    parseable by third party libraries. In these cases, the schema is denoted as 'custom'.
    """

    __tablename__ = "data_files"

    schema = Column(String) #: Encoding scheme of data

    @validates('schema')
    def validate_schema(self,key,value):
        return _validator_schema(key,value)

    __mapper_args__ = {"polymorphic_identity": "data_file"}

class WebFile(DataFile):
    """
    Documents a web file, both for downloading and writing our web pages.
    """

    __tablename__ = "web_files"

    protocol = Column(String) #: http, https, ftp
    domain = Column(String) #: www.example.com

    @hybrid_property
    def url(self):
        return f"{self.protocol}://{self.domain}{self.path}"

    __mapper_args__ = {"polymorphic_identity": "web_file"}

class Edge(Base):
    """
    Defines node association table for relationship types between all nodes.
    """

    __tablename__ = "edges"

    id = Column(Integer, primary_key=True)
    src = Column(Integer, ForeignKey("nodes.id", ondelete="CASCADE"))
    dst = Column(Integer, ForeignKey("nodes.id", ondelete="CASCADE"))
    relation = Column(Enum(RelationType)) #: Type of relationship between nodes. See Relation
    role = Column(String) #: Secondary descriptor of relationship, for example 'input' vs 'lookup' for a read relationship.
    last_updated = Column(DateTime) #: ISO 8601 String

    src = relationship("Node", foreign_keys=[src], back_populates="outgoing_edges")
    dst = relationship("Node", foreign_keys=[dst], back_populates="incoming_edges")

    metadata = relationship(
        "EdgeMetaData",
        foreign_keys="EdgeMetaData.edge_id",
        back_populates="edge",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    @validates("role")
    def validate_role(self, key, value):
        if value is None:
            return value
        else:
            return value.lower()

    __table_args__ = (
            UniqueConstraint("src", "dst", "relation", name="unique_edge"),
    )

class NodeMetaData(Base):
    """
    Stores metadata information about nodes, such as documentation and context information.
    """

    __tablename__ = "node_metadata"

    id = Column(Integer, primary_key=True)
    node_id = Column(Integer, ForeignKey("nodes.id", ondelete="CASCADE"))
    key = Column(String)
    value = Column(JSON)

    node = relationship(
        "Node",
        foreign_keys=[node_id],
        back_populates="metadata"
    )

class EdgeMetaData(Base):
    """
    Stores metadata information about nodes, such as documentation and context information.
    """

    __tablename__ = "edge_metadata"

    id = Column(Integer, primary_key=True)
    edge_id = Column(Integer, ForeignKey("edges.id", ondelete="CASCADE"))
    key = Column(String)
    value = Column(JSON)

    edge = relationship(
        "Edge",
        foreign_keys=[edge_id],
        back_populates="metadata"
    )