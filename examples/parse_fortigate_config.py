#!/usr/bin/env python3
"""
Example script demonstrating how to use FortiParse library to analyze FortiGate configurations.

This script:
1. Parses a FortiGate configuration file
2. Extracts firewall policies and interfaces
3. Performs some basic analysis (interface IPs, policy counts)
4. Outputs results in a readable format
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to import fortiparse
sys.path.insert(0, str(Path(__file__).parent.parent))
from fortiparse import FortiParser


def format_policy(policy_data):
    """Format a firewall policy for display."""
    result = []

    # Extract key attributes
    policy_id = policy_data.get("id", "Unknown")
    src_intf = policy_data.get("srcintf", "Any")
    dst_intf = policy_data.get("dstintf", "Any")
    src_addr = policy_data.get("srcaddr", "Any")
    dst_addr = policy_data.get("dstaddr", "Any")
    action = policy_data.get("action", "Unknown")
    service = policy_data.get("service", "Any")

    # Create a formatted string
    result.append(f"Policy {policy_id}:")
    result.append(f"  - From: {src_intf} → To: {dst_intf}")
    result.append(f"  - Source: {src_addr}")
    result.append(f"  - Destination: {dst_addr}")
    result.append(f"  - Action: {action}")
    result.append(f"  - Service: {service}")

    return "\n".join(result)


def parse_and_analyze_config(config_file):
    """Parse and analyze a FortiGate configuration file."""
    print(f"Analyzing FortiGate configuration: {config_file}")
    print("-" * 60)

    # Parse the configuration
    parser = FortiParser(config_file=config_file)
    parser.parse()

    # Extract global settings
    globals_settings = parser.get_section("system", "global")
    if globals_settings:
        print("\nGlobal Settings:")
        hostname = globals_settings.get("hostname", "Unknown")
        timezone = globals_settings.get("timezone", "Unknown")
        print(f"  - Hostname: {hostname}")
        print(f"  - Timezone: {timezone}")

    # Save the full JSON for reference
    output_file = os.path.basename(config_file) + ".json"
    parser.save_json(output_file)
    print(f"\nFull parsed configuration saved to: {output_file}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python parse_fortigate_config.py <fortigate_config_file>")
        sys.exit(1)

    config_file = sys.argv[1]
    if not os.path.exists(config_file):
        print(f"Error: File '{config_file}' not found.")
        sys.exit(1)

    parse_and_analyze_config(config_file)
