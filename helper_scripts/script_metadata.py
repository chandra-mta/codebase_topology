"""
**script_metadata.py**: This Python module contains functions for parsing inline script metadata following the PEP 723 Specification.

:Author: W. Aaron (william.aaron@cfa.harvard.edu)
:Last Updated: Jan 16 2026

"""

import os
import re
import tomllib

PEP_723_REGEX = (
    r"(?m)^# /// (?P<type>[a-zA-Z0-9-]+)$\s(?P<content>(^#(| .*)$\s)+)^# ///$"
)


def parse_metadata(script: str) -> dict | None:
    block_find_iter = re.finditer(PEP_723_REGEX, script)
    blocks = {}
    for match in block_find_iter:
        _type = match.group("type")
        _content = "".join(
            line[2:] if line.startswith("# ") else line[1:]
            for line in match.group("content").splitlines(keepends=True)
        )
        blocks[_type] = tomllib.loads(_content)
    return blocks


def parse_file_metadata(filepath: str):
    if os.path.isfile(filepath):
        with open(filepath) as f:
            content = f.read()
        metadata = parse_metadata(content)
        return metadata
    else:
        raise FileNotFoundError(f"Couldn't path to {filepath}")
