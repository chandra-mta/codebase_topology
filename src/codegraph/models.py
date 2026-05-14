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
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, JSON, DateTime
from sqlalchemy.orm import declarative_base, relationship, validates, hybrid_property

VAR_PATTERN = re.compile(r'\$\{([A-Za-z_]\w*)\}|\$([A-Za-z_]\w*)')

def _validator_template(key,value):
    if value is None:
        return value
    if not VAR_PATTERN.search(value):
        raise ValueError(f"Template '{value}' must contain at least one variable reference like $VAR or ${{VAR}}.")

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

    id = Column(Integer, ForeignKey("nodes.id"), primary_key=True)
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