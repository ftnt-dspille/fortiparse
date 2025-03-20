"""
FortiParse - A Python library to parse FortiGate configuration files into JSON format.
"""

from .fortiparse import (
    FortiParser,
    parse_file,
    parse_text,
    main
)

__all__ = [
    'FortiParser',
    'parse_file',
    'parse_text',
    'main'
]