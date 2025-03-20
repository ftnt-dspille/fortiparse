"""
Tests for the FortiParse module.
"""

import os
import json
import tempfile
import pytest
from fortiparse import FortiParser, parse_file, parse_text


# Sample FortiGate configuration for testing
SAMPLE_CONFIG = """
#config-version=FGVMK6-7.4.4-FW-build2662-240514:opmode=0:vdom=0:user=admin
config system global
    set admintimeout 120
    set alias "FG1"
    set hostname "Branch1"
    set timezone "US/Pacific"
end
config system interface
    edit "port1"
        set vdom "root"
        set ip 192.168.0.3 255.255.255.0
        set allowaccess ping https ssh snmp http fgfm fabric
        set type physical
        set snmp-index 1
    next
    edit "port2"
        set vdom "root"
        set ip 100.100.101.101 255.255.255.0
        set allowaccess ping fgfm
        set type physical
        set snmp-index 2
    next
end
config firewall policy
    edit 1
        set srcintf "port5"
        set dstintf "port1"
        set action accept
        set srcaddr "Users_Subnet"
        set dstaddr "all"
        set schedule "always"
        set service "ALL"
        set logtraffic all
    next
    edit 2
        set srcintf "port5"
        set dstintf "port2"
        set action accept
        set srcaddr "Users_Subnet"
        set dstaddr "Server001"
        set schedule "always"
        set service "HTTP" "HTTPS"
        set logtraffic all
    next
end
"""


@pytest.fixture
def sample_config_file():
    """Create a temporary file with the sample configuration."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write(SAMPLE_CONFIG)
        temp_filename = f.name
    
    yield temp_filename
    
    # Cleanup
    os.unlink(temp_filename)


class TestFortiParser:
    """Test suite for FortiParser class."""
    
    def test_init_with_text(self):
        """Test initialization with config text."""
        parser = FortiParser(config_text=SAMPLE_CONFIG)
        assert parser.config_text == SAMPLE_CONFIG
    
    def test_init_with_file(self, sample_config_file):
        """Test initialization with config file."""
        parser = FortiParser(config_file=sample_config_file)
        assert parser.config_text.strip() == SAMPLE_CONFIG.strip()
    
    def test_init_with_neither(self):
        """Test initialization with neither text nor file raises error."""
        with pytest.raises(ValueError):
            FortiParser()
    
    def test_parse_basic_structure(self):
        """Test parsing basic structure of the configuration."""
        parser = FortiParser(config_text=SAMPLE_CONFIG)
        config = parser.parse()
        
        # Check top-level sections
        assert "system" in config
        assert "global" in config["system"]
        assert "interface" in config["system"]
        assert "firewall" in config
        assert "policy" in config["firewall"]
    
    def test_parse_global_settings(self):
        """Test parsing global settings."""
        parser = FortiParser(config_text=SAMPLE_CONFIG)
        config = parser.parse()
        
        global_settings = config["system"]["global"]
        assert global_settings["admintimeout"] == "120"
        assert global_settings["alias"] == '"FG1"'
        assert global_settings["hostname"] == '"Branch1"'
        assert global_settings["timezone"] == '"US/Pacific"'
    
    def test_parse_interfaces(self):
        """Test parsing interfaces configuration."""
        parser = FortiParser(config_text=SAMPLE_CONFIG)
        config = parser.parse()
        
        interfaces = config["system"]["interface"]["edit"]
        
        # Check port1
        assert "port1" in interfaces
        assert interfaces["port1"]["vdom"] == '"root"'
        assert interfaces["port1"]["ip"] == "192.168.0.3 255.255.255.0"
        assert interfaces["port1"]["allowaccess"] == "ping https ssh snmp http fgfm fabric"
        assert interfaces["port1"]["type"] == "physical"
        assert interfaces["port1"]["snmp-index"] == "1"
        
        # Check port2
        assert "port2" in interfaces
        assert interfaces["port2"]["vdom"] == '"root"'
        assert interfaces["port2"]["ip"] == "100.100.101.101 255.255.255.0"
        assert interfaces["port2"]["allowaccess"] == "ping fgfm"
        assert interfaces["port2"]["type"] == "physical"
        assert interfaces["port2"]["snmp-index"] == "2"
    
    def test_parse_firewall_policy(self):
        """Test parsing firewall policy configuration."""
        parser = FortiParser(config_text=SAMPLE_CONFIG)
        config = parser.parse()
        
        policies = config["firewall"]["policy"]["edit"]
        
        # Check policy 1
        assert "1" in policies
        assert policies["1"]["srcintf"] == '"port5"'
        assert policies["1"]["dstintf"] == '"port1"'
        assert policies["1"]["action"] == "accept"
        assert policies["1"]["srcaddr"] == '"Users_Subnet"'
        assert policies["1"]["dstaddr"] == '"all"'
        assert policies["1"]["schedule"] == '"always"'
        assert policies["1"]["service"] == '"ALL"'
        assert policies["1"]["logtraffic"] == "all"
        
        # Check policy 2
        assert "2" in policies
        assert policies["2"]["srcintf"] == '"port5"'
        assert policies["2"]["dstintf"] == '"port2"'
        assert policies["2"]["action"] == "accept"
        assert policies["2"]["srcaddr"] == '"Users_Subnet"'
        assert policies["2"]["dstaddr"] == '"Server001"'
        assert policies["2"]["schedule"] == '"always"'
        assert policies["2"]["service"] == '"HTTP\" \"HTTPS"'  # This is expected based on the current parser
        assert policies["2"]["logtraffic"] == "all"
    
    def test_to_json(self):
        """Test conversion to JSON string."""
        parser = FortiParser(config_text=SAMPLE_CONFIG)
        parser.parse()
        
        json_str = parser.to_json()
        # Verify it's valid JSON by parsing it
        json_obj = json.loads(json_str)
        
        assert isinstance(json_obj, dict)
        assert "system" in json_obj
        assert "firewall" in json_obj
    
    def test_save_json(self, tmpdir):
        """Test saving to JSON file."""
        output_file = os.path.join(tmpdir, "output.json")
        
        parser = FortiParser(config_text=SAMPLE_CONFIG)
        parser.parse()
        parser.save_json(output_file)
        
        # Verify file exists
        assert os.path.exists(output_file)
        
        # Verify content is valid JSON
        with open(output_file, 'r') as f:
            json_obj = json.load(f)
        
        assert isinstance(json_obj, dict)
        assert "system" in json_obj
        assert "firewall" in json_obj
    
    def test_get_section(self):
        """Test getting specific section."""
        parser = FortiParser(config_text=SAMPLE_CONFIG)
        parser.parse()
        
        # Get interface section
        interface_section = parser.get_section("system", "interface")
        assert interface_section is not None
        assert "edit" in interface_section
        assert "port1" in interface_section["edit"]
        
        # Get non-existent section
        nonexistent = parser.get_section("system", "nonexistent")
        assert nonexistent is None
    
    def test_extract_policies(self):
        """Test extracting firewall policies."""
        parser = FortiParser(config_text=SAMPLE_CONFIG)
        parser.parse()
        
        policies = parser.extract_policies()
        
        assert len(policies) == 2
        assert policies[0]["id"] == "1"
        assert policies[0]["srcintf"] == '"port5"'
        assert policies[1]["id"] == "2"
        assert policies[1]["dstintf"] == '"port2"'
    
    def test_extract_interfaces(self):
        """Test extracting interfaces."""
        parser = FortiParser(config_text=SAMPLE_CONFIG)
        parser.parse()
        
        interfaces = parser.extract_interfaces()
        
        assert len(interfaces) == 2
        assert interfaces[0]["name"] == "port1"
        assert interfaces[0]["vdom"] == '"root"'
        assert interfaces[1]["name"] == "port2"
        assert interfaces[1]["ip"] == "100.100.101.101 255.255.255.0"


def test_parse_file_function(sample_config_file):
    """Test parse_file utility function."""
    config = parse_file(sample_config_file)
    
    assert "system" in config
    assert "global" in config["system"]
    assert config["system"]["global"]["hostname"] == '"Branch1"'


def test_parse_text_function():
    """Test parse_text utility function."""
    config = parse_text(SAMPLE_CONFIG)
    
    assert "system" in config
    assert "global" in config["system"]
    assert config["system"]["global"]["hostname"] == '"Branch1"'
