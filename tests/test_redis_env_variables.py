#!/usr/bin/env python3
"""
Test suite for Redis environment variable handling in coaiapy
Tests the fix for UPSTASH_REDIS_REST_URL and UPSTASH_REDIS_REST_TOKEN support
"""
import pytest
import os
import sys
import tempfile
from unittest.mock import patch, MagicMock

# Import from installed package or local source
try:
    from coaiapy.coaiamodule import read_config, load_env_file
except ImportError:
    # Fallback for development mode
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from coaiapy.coaiamodule import read_config, load_env_file


class TestUpstashEnvironmentVariables:
    """Test Upstash REST API environment variable support"""
    
    def setup_method(self):
        """Reset config before each test"""
        import coaiapy.coaiamodule
        coaiapy.coaiamodule.config = None
    
    def test_upstash_rest_url_parsing(self):
        """Test that UPSTASH_REDIS_REST_URL is correctly parsed"""
        with patch.dict(os.environ, {
            'UPSTASH_REDIS_REST_URL': 'https://test-instance.upstash.io',
            'UPSTASH_REDIS_REST_TOKEN': 'test_token_123'
        }, clear=False):
            config = read_config()
            
            assert config['jtaleconf']['host'] == 'test-instance.upstash.io'
            assert config['jtaleconf']['port'] == 6379
            assert config['jtaleconf']['password'] == 'test_token_123'
            assert config['jtaleconf']['ssl'] is True
    
    def test_upstash_rest_url_with_custom_port(self):
        """Test that custom port in UPSTASH_REDIS_REST_URL is respected"""
        with patch.dict(os.environ, {
            'UPSTASH_REDIS_REST_URL': 'https://test-instance.upstash.io:6380',
            'UPSTASH_REDIS_REST_TOKEN': 'test_token_456'
        }, clear=False):
            config = read_config()
            
            assert config['jtaleconf']['host'] == 'test-instance.upstash.io'
            assert config['jtaleconf']['port'] == 6380
            assert config['jtaleconf']['password'] == 'test_token_456'
            assert config['jtaleconf']['ssl'] is True
    
    def test_upstash_http_url_no_ssl(self):
        """Test that http:// URLs disable SSL"""
        with patch.dict(os.environ, {
            'UPSTASH_REDIS_REST_URL': 'http://test-instance.upstash.io',
            'UPSTASH_REDIS_REST_TOKEN': 'test_token_789'
        }, clear=False):
            config = read_config()
            
            assert config['jtaleconf']['host'] == 'test-instance.upstash.io'
            assert config['jtaleconf']['ssl'] is False
    
    def test_redis_env_vars_fallback(self):
        """Test fallback to REDIS_* environment variables when UPSTASH_* not present"""
        # Create environment without UPSTASH variables
        env_without_upstash = {
            'REDIS_HOST': 'redis.example.com',
            'REDIS_PORT': '6380',
            'REDIS_PASSWORD': 'redis_password'
        }
        # Ensure UPSTASH variables are explicitly not included
        keys_to_exclude = ['UPSTASH_REDIS_REST_URL', 'UPSTASH_REDIS_REST_TOKEN']
        
        with patch.dict(os.environ, env_without_upstash, clear=False):
            # Temporarily remove UPSTASH keys if they exist
            saved_values = {}
            for key in keys_to_exclude:
                if key in os.environ:
                    saved_values[key] = os.environ.pop(key)
            
            try:
                config = read_config()
                
                assert config['jtaleconf']['host'] == 'redis.example.com'
                assert config['jtaleconf']['port'] == 6380
                assert config['jtaleconf']['password'] == 'redis_password'
            finally:
                # Restore saved values
                for key, value in saved_values.items():
                    os.environ[key] = value
    
    def test_upstash_takes_priority_over_redis_vars(self):
        """Test that UPSTASH_REDIS_REST_* takes priority over REDIS_*"""
        with patch.dict(os.environ, {
            'UPSTASH_REDIS_REST_URL': 'https://upstash-instance.upstash.io',
            'UPSTASH_REDIS_REST_TOKEN': 'upstash_token',
            'REDIS_HOST': 'redis.example.com',
            'REDIS_PASSWORD': 'redis_password'
        }, clear=False):
            config = read_config()
            
            # UPSTASH should take priority
            assert config['jtaleconf']['host'] == 'upstash-instance.upstash.io'
            assert config['jtaleconf']['password'] == 'upstash_token'
            assert config['jtaleconf']['ssl'] is True


class TestDotEnvFileLoading:
    """Test .env file loading for Redis credentials"""
    
    def setup_method(self):
        """Reset config before each test"""
        import coaiapy.coaiamodule
        coaiapy.coaiamodule.config = None
    
    def test_env_file_with_upstash_vars(self):
        """Test loading UPSTASH_* variables from .env file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            old_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Create .env file with Upstash credentials
                with open('.env', 'w') as f:
                    f.write('UPSTASH_REDIS_REST_URL=https://env-file-instance.upstash.io\n')
                    f.write('UPSTASH_REDIS_REST_TOKEN=env_file_token\n')
                
                # Clear any existing environment variables
                for key in ['UPSTASH_REDIS_REST_URL', 'UPSTASH_REDIS_REST_TOKEN', 'REDIS_HOST', 'REDIS_PASSWORD']:
                    if key in os.environ:
                        del os.environ[key]
                
                config = read_config()
                
                assert config['jtaleconf']['host'] == 'env-file-instance.upstash.io'
                assert config['jtaleconf']['password'] == 'env_file_token'
                assert config['jtaleconf']['ssl'] is True
            finally:
                os.chdir(old_cwd)
    
    def test_system_env_takes_priority_over_env_file(self):
        """Test that system environment variables take priority over .env file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            old_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Create .env file
                with open('.env', 'w') as f:
                    f.write('UPSTASH_REDIS_REST_URL=https://env-file-instance.upstash.io\n')
                    f.write('UPSTASH_REDIS_REST_TOKEN=env_file_token\n')
                
                # Set system environment variable (should take priority)
                with patch.dict(os.environ, {
                    'UPSTASH_REDIS_REST_URL': 'https://system-env-instance.upstash.io',
                    'UPSTASH_REDIS_REST_TOKEN': 'system_env_token'
                }, clear=False):
                    config = read_config()
                    
                    # System env should take priority
                    assert config['jtaleconf']['host'] == 'system-env-instance.upstash.io'
                    assert config['jtaleconf']['password'] == 'system_env_token'
            finally:
                os.chdir(old_cwd)


class TestBackwardCompatibility:
    """Test that existing functionality is not broken"""
    
    def setup_method(self):
        """Reset config before each test"""
        import coaiapy.coaiamodule
        coaiapy.coaiamodule.config = None
    
    def test_default_config_still_works(self):
        """Test that default config is loaded when no env vars are set"""
        # Clear all Redis-related env vars using patch.dict
        env_keys_to_clear = [
            'UPSTASH_REDIS_REST_URL', 'UPSTASH_REDIS_REST_TOKEN',
            'REDIS_HOST', 'REDIS_PORT', 'REDIS_PASSWORD',
            'UPSTASH_HOST', 'UPSTASH_PASSWORD'
        ]
        
        # Save current values
        saved_values = {}
        for key in env_keys_to_clear:
            if key in os.environ:
                saved_values[key] = os.environ.pop(key)
        
        try:
            config = read_config()
            
            # Should have default values
            assert 'jtaleconf' in config
            assert 'host' in config['jtaleconf']
            assert 'port' in config['jtaleconf']
            assert 'password' in config['jtaleconf']
            assert 'ssl' in config['jtaleconf']
        finally:
            # Restore saved values
            for key, value in saved_values.items():
                os.environ[key] = value


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
