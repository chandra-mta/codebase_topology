"""
Certain core variables
"""

from pathlib import Path

_MOUNT_DIRECTORIES = {
    Path("/home/mta"): "remus",
    Path("/data/mta"): "remus",
    Path("/data/mta4"): "numa10g",
    Path("/data/mta_www"): "remus",
    Path("/proj/sot"): "numa10g",
    Path("/proj/cm"): "romulus",
    Path("/soft/SYBASE16.0"): "numa.cfa.harvard.edu",
    Path("/stage/pool14"): "romulus",
    Path("/proj/rac"): "remus",
    Path("/home/ascds"): "numa",
    Path("/home/ascdsops"): "remus",
    Path("/data/chandra_caldb"): "remus",
    Path("/proj/web-cxc"): "numa2",
    Path("/proj/web-icxc"): "numa2",
    Path("/home/cus"): "remus",
    Path("/dsops/critical"): "remus"
}

def get_nfs_server(file_path: str) -> str:
    """
    Get the NFS server for a given file path.
    """
    file_path = Path(file_path)
    #: When finding the NFS of a file, use Path class and run file.is_relative_to(mount_directory)
    for mount_directory, nfs_server in _MOUNT_DIRECTORIES.items():
        if file_path.is_relative_to(mount_directory):
            return nfs_server
    return None