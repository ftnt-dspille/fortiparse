"""
Tests for the FortiParse command-line interface.
"""

import os
import json
import sys
import tempfile
import subprocess
import pytest
from unittest.mock import patch
from io import StringIO

from fortiparse.fortiparse import main


# Sample configuration for CLI testing
SIMPLE_CONFIG = """
config system global
    set hostname "TestFirewall"
    set timezone "UTC"
end
"""


class TestCLI:
    """Test suite for the command-line interface."""

    @pytest.fixture
    def config_file(self):
        """Create a temporary file with a simple configuration."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write(SIMPLE_CONFIG)
            temp_filename = f.name
        
        yield temp_filename
        
        # Cleanup
        os.unlink(temp_filename)
    
    def test_cli_stdout(self, config_file):
        """Test CLI with output to stdout."""
        with patch('sys.argv', ['fortiparse', config_file]), \
             patch('sys.stdout', new=StringIO()) as fake_out:
            
            # This should run without errors
            main()
            
            # Get the captured output
            output = fake_out.getvalue()
            
            # Verify it's valid JSON
            json_obj = json.loads(output)
            assert "system" in json_obj
            assert "global" in json_obj["system"]
            assert json_obj["system"]["global"]["hostname"] == 'TestFirewall'
    
    def test_cli_file_output(self, config_file, tmpdir):
        """Test CLI with output to a file."""
        output_file = os.path.join(tmpdir, "output.json")
        
        with patch('sys.argv', ['fortiparse', config_file, '-o', output_file]), \
             patch('sys.stdout', new=StringIO()) as fake_out:
            
            # This should run without errors
            main()
            
            # Verify the output message
            output = fake_out.getvalue()
            assert f"Configuration saved to {output_file}" in output
            
            # Verify the file exists and contains valid JSON
            assert os.path.exists(output_file)
            with open(output_file, 'r') as f:
                json_obj = json.loads(f.read())
            
            assert "system" in json_obj
            assert "global" in json_obj["system"]
            assert json_obj["system"]["global"]["hostname"] == 'TestFirewall'
    
    def test_cli_indentation(self, config_file):
        """Test CLI with custom indentation."""
        with patch('sys.argv', ['fortiparse', config_file, '-i', '4']), \
             patch('sys.stdout', new=StringIO()) as fake_out:
            
            # This should run without errors
            main()
            
            # Get the captured output
            output = fake_out.getvalue()
            
            # Verify indentation (space at beginning of line after first line)
            lines = output.strip().split('\n')
            assert lines[1].startswith('    ')  # 4-space indentation
    
    def test_cli_error_handling(self):
        """Test CLI error handling with nonexistent file."""
        with patch('sys.argv', ['fortiparse', 'nonexistent_file.conf']), \
             patch('sys.stderr', new=StringIO()) as fake_err, \
             patch('sys.exit') as mock_exit:
            
            # This should attempt to run but fail
            main()
            
            # Verify the error message
            error_output = fake_err.getvalue()
            assert "Error:" in error_output
            
            # Verify that sys.exit was called with error code
            mock_exit.assert_called_once_with(1)


def test_module_execution():
    """Test running the module as a script."""
    # Create a temporary file with a simple configuration
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write(SIMPLE_CONFIG)
        temp_filename = f.name
    
    try:
        # Run the module as a script
        result = subprocess.run(
            [sys.executable, '-m', 'fortiparse', temp_filename],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Verify output
        assert result.returncode == 0
        
        # Parse JSON output
        json_obj = json.loads(result.stdout)
        assert "system" in json_obj
        assert "global" in json_obj["system"]
        assert json_obj["system"]["global"]["hostname"] == 'TestFirewall'
    
    finally:
        # Cleanup
        os.unlink(temp_filename)
