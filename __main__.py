"""
Main module entry point for FortiParse.

This allows running FortiParse as:
python -m fortiparse [args]
"""

from .fortigate_parse import main

if __name__ == "__main__":
    main()
