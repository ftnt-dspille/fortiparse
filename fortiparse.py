"""
FortiParse - A Python library to parse FortiGate configuration files into JSON format.

This module provides a simple interface to convert FortiGate configurations into
structured JSON objects that can be easily manipulated with Python.
"""

import json
import re
from typing import Dict, List, Optional, Any


class FortiParser:
    """Parser for FortiGate configuration files."""

    def __init__(self, config_text: Optional[str] = None, config_file: Optional[str] = None):
        """
        Initialize the FortiParser with either a string or file path.

        Args:
            config_text: String containing FortiGate configuration
            config_file: Path to FortiGate configuration file
        
        Raises:
            ValueError: If neither config_text nor config_file is provided
        """
        if config_text is not None:
            self.config_text = config_text
        elif config_file is not None:
            with open(config_file, 'r', encoding='utf-8') as f:
                self.config_text = f.read()
        else:
            raise ValueError("Either config_text or config_file must be provided")

        self.config_json = {}
        self._parse_state = []  # Used to track the current parsing level

    def parse(self) -> Dict[str, Any]:
        """
        Parse the FortiGate configuration into a JSON object.

        Returns:
            Dict containing the parsed configuration
        """
        self.config_json = {}
        self._parse_state = []

        lines = self.config_text.split('\n')
        current_section = self.config_json
        section_stack = [current_section]
        path_stack = []  # Track the section path

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Skip empty lines and comments
            if not line or line.startswith('#'):
                i += 1
                continue

            # Handle config section starts
            if line.startswith('config '):
                # Extract section name (e.g., "system interface")
                section_full_name = line[7:].strip()
                section_parts = section_full_name.split()

                # For proper nesting, we need to create hierarchical path
                for part in section_parts:
                    # Create or get the section if it doesn't exist
                    if part not in current_section:
                        current_section[part] = {}

                    # Update current section and stack
                    current_section = current_section[part]
                    path_stack.append(part)

                # Update section stack with current section
                section_stack.append(current_section)
                i += 1
                continue

            # Handle "edit" statements
            if line.startswith('edit '):
                key_match = re.match(r'edit\s+"?([^"]+)"?', line)
                if key_match:
                    edit_key = key_match.group(1)

                    # Initialize empty dict for this edit block if not already set
                    if "edit" not in current_section:
                        current_section["edit"] = {}

                    # Create nested dict for this edit key
                    if edit_key not in current_section["edit"]:
                        current_section["edit"][edit_key] = {}

                    current_section = current_section["edit"][edit_key]
                    section_stack.append(current_section)
                    i += 1
                    continue

            # Handle "set" statements
            if line.startswith('set '):
                key_value_match = re.match(r'set\s+([^\s]+)\s+(.+)', line)
                if key_value_match:
                    key = key_value_match.group(1)
                    value = key_value_match.group(2).strip()

                    # Special handling for space-separated quoted values (like members)
                    # This keeps the original formatting with quotes
                    if value.count('"') > 2 or ('"' in value and value.count('"') % 2 == 0):
                        # Keep the value as is with quotes preserved
                        current_section[key] = value
                    else:
                        # Regular single value, remove surrounding quotes if present
                        if (value.startswith('"') and value.endswith('"')) or \
                                (value.startswith("'") and value.endswith("'")):
                            value = value[1:-1]
                        current_section[key] = value

                    i += 1
                    continue

            # Handle "unset" statements
            if line.startswith('unset '):
                key_match = re.match(r'unset\s+([^\s]+)', line)
                if key_match:
                    key = key_match.group(1)
                    current_section[key] = None
                    i += 1
                    continue

            # Handle "next" - go up one level
            if line == 'next':
                section_stack.pop()  # Remove current section
                if section_stack:  # Ensure the stack is not empty
                    current_section = section_stack[-1]  # Set current to parent
                i += 1
                continue

            # Handle "end" - go back up the config hierarchy
            if line == 'end':
                # Go back up to the previous config level
                if path_stack:
                    path_stack.pop()  # Remove last path segment

                # Reset current section to appropriate level
                section_stack.pop()  # Remove current section
                if section_stack:  # Ensure the stack is not empty
                    current_section = section_stack[-1]
                i += 1
                continue

            # Default case - just move to next line
            i += 1

        return self.config_json

    def to_json(self, indent: int = 2) -> str:
        """
        Convert the parsed configuration to a JSON string.

        Args:
            indent: Number of spaces for indentation (default: 2)

        Returns:
            JSON string representation of the configuration
        """
        if not self.config_json:
            self.parse()

        return json.dumps(self.config_json, indent=indent)

    def save_json(self, output_file: str, indent: int = 2) -> None:
        """
        Save the parsed configuration to a JSON file.

        Args:
            output_file: Path to output JSON file
            indent: Number of spaces for indentation (default: 2)
        """
        if not self.config_json:
            self.parse()

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.config_json, f, indent=indent)

    def get_section(self, *path: str) -> Any:
        """
        Get a specific section of the configuration.

        Args:
            *path: Path to the section, as a sequence of keys

        Returns:
            The requested section, or None if not found
        """
        if not self.config_json:
            self.parse()

        current = self.config_json
        for key in path:
            if key in current:
                current = current[key]
            else:
                return None

        return current

    def extract_policies(self) -> List[Dict[str, Any]]:
        """
        Extract firewall policies as a simplified list.

        Returns:
            List of dictionaries containing policy information
        """
        policies = []

        if not self.config_json:
            self.parse()

        firewall_policy = self.get_section("firewall", "policy")
        if not firewall_policy or "edit" not in firewall_policy:
            return policies

        for policy_id, policy_data in firewall_policy["edit"].items():
            policy = {"id": policy_id}
            policy.update(policy_data)
            policies.append(policy)

        return policies

    def extract_interfaces(self) -> List[Dict[str, Any]]:
        """
        Extract interface configurations as a simplified list.

        Returns:
            List of dictionaries containing interface information
        """
        interfaces = []

        if not self.config_json:
            self.parse()

        system_interface = self.get_section("system", "interface")
        if not system_interface or "edit" not in system_interface:
            return interfaces

        for intf_name, intf_data in system_interface["edit"].items():
            intf = {"name": intf_name}
            intf.update(intf_data)
            interfaces.append(intf)

        return interfaces


def parse_file(filename: str) -> Dict[str, Any]:
    """
    Parse a FortiGate configuration file and return as a dictionary.

    Args:
        filename: Path to the FortiGate configuration file

    Returns:
        Dictionary containing parsed configuration
    """
    parser = FortiParser(config_file=filename)
    return parser.parse()


def parse_text(config_text: str) -> Dict[str, Any]:
    """
    Parse a FortiGate configuration string and return as a dictionary.

    Args:
        config_text: String containing FortiGate configuration

    Returns:
        Dictionary containing parsed configuration
    """
    parser = FortiParser(config_text=config_text)
    return parser.parse()


def main():
    """Main entry point for the command-line interface."""
    import argparse
    import sys

    arg_parser = argparse.ArgumentParser(description='Parse FortiGate configuration files to JSON')
    arg_parser.add_argument('input_file', help='FortiGate configuration file to parse')
    arg_parser.add_argument('-o', '--output', help='Output JSON file (default: stdout)')
    arg_parser.add_argument('-i', '--indent', type=int, default=2, help='JSON indentation (default: 2)')

    args = arg_parser.parse_args()

    try:
        parser = FortiParser(config_file=args.input_file)
        result = parser.parse()

        if args.output:
            parser.save_json(args.output, args.indent)
            print(f"Configuration saved to {args.output}")
        else:
            print(parser.to_json(args.indent))

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
