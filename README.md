# FortiParse

A Python library to parse FortiGate configuration files into JSON format.

## Installation

```bash
pip install fortiparse
```

## Usage

### Basic Usage

```python
from fortiparse import FortiParser

# Parse from a file
parser = FortiParser(config_file="path/to/fortigate.conf")
config_json = parser.parse()

# Parse from a string
config_text = """
config system interface
    edit "port1"
        set vdom "root"
        set ip 192.168.1.1 255.255.255.0
        set allowaccess ping https ssh
        set type physical
    next
end
"""
parser = FortiParser(config_text=config_text)
config_json = parser.parse()

# Convert to JSON string
json_str = parser.to_json(indent=4)
print(json_str)

# Save to a file
parser.save_json("output.json")
```

### Command Line Usage

FortiParse can also be used from the command line:

```bash
python -m fortiparse my_config.conf -o output.json
```

### Extracting Specific Sections

```python
from fortiparse import FortiParser

parser = FortiParser(config_file="fortigate.conf")
parser.parse()

# Get a specific section
interfaces = parser.get_section("system", "interface")

# Extract all firewall policies
policies = parser.extract_policies()

# Extract all interfaces
interfaces_list = parser.extract_interfaces()
```

## Key Features

- Parse FortiGate configuration files into structured JSON
- Extract specific configuration sections
- Easily convert between configuration formats
- Helper functions for common extraction tasks

## Requirements

- Python 3.7+

## License

This project is licensed under the MIT License - see the LICENSE file for details.
