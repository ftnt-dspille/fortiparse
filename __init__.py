"""
FortiParse - A Python library to parse FortiGate configuration files into JSON.
"""

__version__ = "0.1.0"

from .fortigate_parse import (
    FortiParser,
    parse_file,
    parse_text
)

__all__ = [
    'FortiParser',
    'parse_file',
    'parse_text',
]
