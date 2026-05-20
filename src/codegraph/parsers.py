"""
This module contains helpful parsers for injesting documentation information into the codegraph database
"""

from .models import Node, CronTab, CronJob, File, LogFile, CodeFile, DataFile, WebFile, Email, Credential, Edge
from .models import _VAR_PATTERN, resolve
from .core import get_nfs_server

def _is_template(line):
    return _VAR_PATTERN.search(line) is not None

def _fill_template(string,env):
    """
    Fill in a string with variables if applicable.
    """
    if _is_template(string):
        template = string
        canonical = resolve(template, env)
    else:
        template = None
        canonical = string
    return template, canonical

def parse_cronjob_line(line, task, owner=None, env={}, crontab=None):
    """
    Input information associated with a single cronjob
    """
    def _parse_line(line):
        atemp = line.split()
        cadence = ' '.join(atemp[:5])
        btemp = line.split('>>')
        command = btemp[0].split(cadence)[1].strip()

        info = {'cadence':cadence,
                'command': command
            }
        if len(btemp)==2:
            logfile = btemp[1].replace("2>&1",'').strip()
            info['logfile'] = logfile
        return info

    info = _parse_line(line)
    
    if crontab is not None:
        owner = crontab.owner
        env = crontab.variables
        env['HOME'] = env.get('HOME', f"/home/{owner}")

    template_command, canonical_command = _fill_template(info['command'], env)
    
    orms = {}

    orms['cronjob'] = CronJob(
            owner=owner,
            cadence=info['cadence'],
            task=task,
            canonical_command=canonical_command,
            template_command=template_command,
        )

    if crontab is not None:
        #: also fill in the CronTab -> CronJob relationship
        orms['cronjob'].crontab_id = crontab.id
        trigger_edge = Edge(
            src_id=crontab.id,
            dst_id=orms['cronjob'].id,
            relation="triggers"
        )
        orms['trigger_edge'] = trigger_edge
    
    if 'logfile' in info.keys():
        logfile = info['logfile']
        template_path, canonical_path = _fill_template(logfile, env)
        nfs_server = get_nfs_server(canonical_path)

        log_file_orm = LogFile(
            canonical_path=canonical_path,
            template_path=template_path,
            file_type='regular',
            owner=owner,
            nfs_server=nfs_server
        )

        log_edge = Edge(
            src_id=orms['cronjob'].id,
            dst_id=log_file_orm.id,
            relation="writes",
            role='logs'
        )
        orms['log_file'] = log_file_orm
        orms['log_edge'] = log_edge
    
    return orms