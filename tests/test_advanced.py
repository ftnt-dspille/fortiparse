"""
Advanced tests for FortiParse with more complex configurations.
"""

import json

from fortiparse import FortiParser

# A more complex configuration snippet
COMPLEX_CONFIG = """
config firewall address
    edit "all"
        set uuid fd9673a6-f880-51ef-69b0-d15d1f9e2b2e
    next
    edit "FIREWALL_AUTH_PORTAL_ADDRESS"
        set uuid f6995300-e8bf-51ef-f5af-c6ef162b6cab
    next
    edit "FABRIC_DEVICE"
        set uuid f69963b8-e8bf-51ef-5cb9-fd3d376f3937
        set comment "IPv4 addresses of Fabric Devices."
    next
    edit "SSLVPN_TUNNEL_ADDR1"
        set uuid f69c514a-e8bf-51ef-4e30-75640c437da4
        set type iprange
        set start-ip 10.212.134.200
        set end-ip 10.212.134.210
    next
    edit "DMZ_Host001"
        set uuid b6d29b16-f93e-51ef-e24c-9c4c582a92ec
        set subnet 192.168.50.100 255.255.255.255
    next
    edit "DatabaseServer"
        set uuid b6d30394-f93e-51ef-f9f7-aa146af702bb
        set subnet 10.20.30.40 255.255.255.255
    next
    edit "special\\chars"
        set uuid 76d5d534-05c1-51f0-752a-0e79d94a4a84
        set comment "Address with \"quotes\" and \\backslashes\\"
        set subnet 192.168.1.0 255.255.255.0
    next
end

config firewall address6
    edit "SSLVPN_TUNNEL_IPv6_ADDR1"
        set uuid f69c60b8-e8bf-51ef-f9f3-f03a2093233c
        set ip6 fdff:ffff::/120
    next
    edit "all"
        set uuid f5572e90-e8bf-51ef-00d9-b46c60ef98f2
    next
end

config firewall addrgrp
    edit "grp-src-CHG00005"
        set uuid 544001b4-faba-51ef-a87b-b1d7e9373eed
        set member "range-192-168-2-50-192-168-2-60" "IP-10.20.0.0/16" "IP-172.16.0.0/20" "IP-192.168.1.0/24"
        set comment "CHG00005 -Created by FortiSOAR"
    next
end

config system admin
    edit "admin"
        set accprofile "super_admin"
        set vdom "root"
        config gui-dashboard
            edit 1
                set name "Status"
                set vdom "root"
                set permanent enable
                config widget
                    edit 1
                        set width 1
                        set height 1
                    next
                    edit 2
                        set type licinfo
                        set x-pos 1
                        set width 1
                        set height 1
                    next
                end
            next
        end
        set password ENC SH2/15tGAUKCPmQxglzmAKSQlpekOc5pLcLA5DzZKZtF9S77xCRIMpqkO1HQWA=
    next
end
"""

# Configuration with unset statements
UNSET_CONFIG = """
config firewall profile-protocol-options
    edit "default"
        set comment "All default services."
        config http
            set ports 80
            unset options
            unset post-lang
        end
        config ftp
            set ports 21
            set options splice
        end
    next
end

config firewall address
    edit "Network_10.0.0.0"
        set subnet 10.0.0.0 255.0.0.0
        set comment "Class A private network"
    next
    edit "Server_Group"
        set subnet 192.168.10.0 255.255.255.0
        set color 2
    next
end
"""


class TestAdvancedParsing:
    """Test suite for more complex FortiGate configurations."""

    def test_complex_address_parsing(self):
        """Test parsing of complex firewall address configurations."""
        parser = FortiParser(config_text=COMPLEX_CONFIG)
        config = parser.parse()

        # Check firewall address objects
        addresses = config["firewall"]["address"]["edit"]
        assert "all" in addresses
        assert "FABRIC_DEVICE" in addresses
        assert "DMZ_Host001" in addresses

        # Check a specific address with subnet
        dmz_host = addresses["DMZ_Host001"]
        assert dmz_host["subnet"] == "192.168.50.100 255.255.255.255"

        # Check address with special characters in name and comment
        special_chars = addresses["special\\chars"]
        assert special_chars["comment"] == '"Address with "quotes" and \\backslashes\\"'
        assert special_chars["subnet"] == "192.168.1.0 255.255.255.0"

        # Check IPv6 addresses
        ipv6_addresses = config["firewall"]["address6"]["edit"]
        assert "SSLVPN_TUNNEL_IPv6_ADDR1" in ipv6_addresses
        assert ipv6_addresses["SSLVPN_TUNNEL_IPv6_ADDR1"]["ip6"] == "fdff:ffff::/120"

    def test_address_group_parsing(self):
        """Test parsing of address groups with multiple members."""
        parser = FortiParser(config_text=COMPLEX_CONFIG)
        config = parser.parse()

        addrgrp = config["firewall"]["addrgrp"]["edit"]["grp-src-CHG00005"]
        assert addrgrp["comment"] == '"CHG00005 -Created by FortiSOAR"'
        assert addrgrp[
                   "member"] == '"range-192-168-2-50-192-168-2-60" "IP-10.20.0.0/16" "IP-172.16.0.0/20" "IP-192.168.1.0/24"'

    def test_nested_admin_config(self):
        """Test parsing of deeply nested admin configurations."""
        parser = FortiParser(config_text=COMPLEX_CONFIG)
        config = parser.parse()

        admin = config["system"]["admin"]["edit"]["admin"]
        assert admin["accprofile"] == '"super_admin"'
        assert admin["vdom"] == '"root"'

        # Check nested dashboard config
        dashboard = admin["gui-dashboard"]["edit"]["1"]
        assert dashboard["name"] == '"Status"'
        assert dashboard["permanent"] == "enable"

        # Check even deeper nested widget config
        widget1 = dashboard["widget"]["edit"]["1"]
        assert widget1["width"] == "1"
        assert widget1["height"] == "1"

        widget2 = dashboard["widget"]["edit"]["2"]
        assert widget2["type"] == "licinfo"
        assert widget2["x-pos"] == "1"

    def test_unset_statements(self):
        """Test parsing of unset statements."""
        parser = FortiParser(config_text=UNSET_CONFIG)
        config = parser.parse()

        # Check that unset options are captured correctly
        http_config = config["firewall"]["profile-protocol-options"]["edit"]["default"]["http"]
        assert http_config["ports"] == "80"
        assert http_config["options"] is None
        assert http_config["post-lang"] is None

    def test_to_json_complex(self):
        """Test JSON output with complex config."""
        parser = FortiParser(config_text=COMPLEX_CONFIG)
        parser.parse()

        json_str = parser.to_json()
        # Ensure we can parse it as valid JSON
        json_obj = json.loads(json_str)

        # Verify some nested structures
        assert json_obj["firewall"]["address"]["edit"]["special\\chars"][
                   "comment"] == '"Address with "quotes" and \\backslashes\\"'

        # Check the admin section
        admin_section = json_obj["system"]["admin"]["edit"]["admin"]
        assert "gui-dashboard" in admin_section
        assert "edit" in admin_section["gui-dashboard"]

        # Check the password field is preserved
        assert admin_section["password"] == "ENC SH2/15tGAUKCPmQxglzmAKSQlpekOc5pLcLA5DzZKZtF9S77xCRIMpqkO1HQWA="
