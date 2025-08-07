#!/usr/bin/env python3
"""
Test suite for .env file functionality in coaiapy
"""
import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

# Add coaiapy to path for testing
sys.path.insert(0, '/app')
sys.path.insert(0, '/app/coaiapy')

try:
    from coaiapy.coaiamodule import load_env_file, read_config
    from coaiapy import coaiacli
except ImportError as e:
    print(f"Import error: {e}")
    print("Available modules:")
    print(os.listdir('/app/coaiapy'))
    sys.exit(1)

def test_load_env_file():
    """Test the load_env_file function with various scenarios"""
    print("Testing load_env_file function...")
    
    # Test 1: Basic .env file loading
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
        f.write('LANGFUSE_SECRET_KEY=test_secret_123\n')
        f.write('LANGFUSE_PUBLIC_KEY=test_public_456\n')
        f.write('LANGFUSE_HOST=https://test.langfuse.com\n')
        f.write('# Comment line\n')
        f.write('LANGFUSE_AUTH3="quoted_value"\n')
        env_file = f.name
    
    try:
        env_vars = load_env_file(env_file)
        
        assert env_vars['LANGFUSE_SECRET_KEY'] == 'test_secret_123'
        assert env_vars['LANGFUSE_PUBLIC_KEY'] == 'test_public_456' 
        assert env_vars['LANGFUSE_HOST'] == 'https://test.langfuse.com'
        assert env_vars['LANGFUSE_AUTH3'] == 'quoted_value'
        assert '# Comment line' not in env_vars
        
        print("OK: Basic .env file loading works")
    finally:
        os.unlink(env_file)
    
    # Test 2: Non-existent file
    env_vars = load_env_file('/nonexistent/file')
    assert env_vars == {}
    print("OK: Non-existent file handling works")
    
    # Test 3: Empty file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
        f.write('')
        env_file = f.name
    
    try:
        env_vars = load_env_file(env_file)
        assert env_vars == {}
        print("OK: Empty file handling works")
    finally:
        os.unlink(env_file)

def test_config_with_env_file():
    """Test configuration loading with .env file"""
    print("Testing config loading with .env file...")
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Change to temp directory
        old_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Create .env file
            with open('.env', 'w') as f:
                f.write('LANGFUSE_SECRET_KEY=env_secret_key\n')
                f.write('LANGFUSE_PUBLIC_KEY=env_public_key\n')
                f.write('LANGFUSE_HOST=https://env.langfuse.com\n')
                f.write('OPENAI_API_KEY=env_openai_key\n')
                f.write('REDIS_HOST=env_redis_host\n')
            
            # Reset the config to force reload
            import importlib
            import coaiapy.coaiamodule
            coaiapy.coaiamodule.config = None
            
            # Load config
            config = read_config()
            
            # Verify .env values are loaded
            assert config['langfuse_secret_key'] == 'env_secret_key'
            assert config['langfuse_public_key'] == 'env_public_key'
            assert config['langfuse_base_url'] == 'https://env.langfuse.com'
            assert config['openai_api_key'] == 'env_openai_key'
            assert config['jtaleconf']['host'] == 'env_redis_host'
            
            print("OK: .env file values loaded into config")
            
        finally:
            os.chdir(old_cwd)

def test_config_priority_order():
    """Test that environment variables override .env file values"""
    print("Testing configuration priority order...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        old_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Create .env file
            with open('.env', 'w') as f:
                f.write('LANGFUSE_SECRET_KEY=dotenv_secret\n')
                f.write('LANGFUSE_PUBLIC_KEY=dotenv_public\n')
            
            # Set environment variable (should override .env)
            os.environ['LANGFUSE_SECRET_KEY'] = 'system_env_secret'
            
            # Reset config
            import coaiapy.coaiamodule
            coaiapy.coaiamodule.config = None
            
            # Load config
            config = read_config()
            
            # System env should override .env
            assert config['langfuse_secret_key'] == 'system_env_secret'
            # .env should be used when system env not set
            assert config['langfuse_public_key'] == 'dotenv_public'
            
            print("OK: Priority order works: system env > .env file")
            
        finally:
            # Clean up environment
            if 'LANGFUSE_SECRET_KEY' in os.environ:
                del os.environ['LANGFUSE_SECRET_KEY']
            os.chdir(old_cwd)

def test_cli_with_env_config():
    """Test CLI functionality with environment configuration"""
    print("Testing CLI with environment configuration...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        old_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Create .env file with minimal config
            with open('.env', 'w') as f:
                f.write('LANGFUSE_SECRET_KEY=test_secret\n')
                f.write('LANGFUSE_PUBLIC_KEY=test_public\n')
                f.write('LANGFUSE_HOST=https://test.langfuse.com\n')
            
            # Reset config
            import coaiapy.coaiamodule
            coaiapy.coaiamodule.config = None
            
            # Test basic CLI help (should not crash)
            import subprocess
            import sys
            
            result = subprocess.run([
                sys.executable, '-m', 'coaiapy.coaiacli', '--help'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, cwd='/app')
            
            assert result.returncode == 0
            assert 'usage:' in result.stdout.lower()
            
            print("OK: CLI works with .env configuration")
            
        finally:
            os.chdir(old_cwd)

def run_all_tests():
    """Run all .env functionality tests"""
    print("=" * 50)
    print("Running .env Functionality Tests")
    print("=" * 50)
    
    try:
        test_load_env_file()
        test_config_with_env_file()
        test_config_priority_order()
        test_cli_with_env_config()
        
        print("\n" + "=" * 50)
        print("SUCCESS: ALL .env FUNCTIONALITY TESTS PASSED")
        print("=" * 50)
        return True
        
    except Exception as e:
        print(f"\nERROR: TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)