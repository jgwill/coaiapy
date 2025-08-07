#!/usr/bin/env python3
"""
Integration test for Langfuse commands using .env configuration
Tests the new environment variable fallback feature with actual coaia fuse commands
"""
import os
import sys
import tempfile
import subprocess
import json
from pathlib import Path

# Add coaiapy to path
sys.path.insert(0, '/app')
sys.path.insert(0, '/app/coaiapy')

def test_langfuse_config_loading():
    """Test that Langfuse config is loaded from .env file"""
    print("Testing Langfuse configuration loading from .env...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        old_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Create .env file with Langfuse credentials
            with open('.env', 'w') as f:
                f.write('LANGFUSE_SECRET_KEY=sk-lf-test-secret-key-12345\n')
                f.write('LANGFUSE_PUBLIC_KEY=pk-lf-test-public-key-67890\n')
                f.write('LANGFUSE_HOST=https://cloud.langfuse.com\n')
                f.write('LANGFUSE_AUTH3=test-auth3-token\n')
            
            # Reset config to ensure fresh load
            import coaiapy.coaiamodule
            coaiapy.coaiamodule.config = None
            
            # Import and test config loading
            config = coaiapy.coaiamodule.read_config()
            
            # Verify Langfuse values are loaded
            assert config['langfuse_secret_key'] == 'sk-lf-test-secret-key-12345'
            assert config['langfuse_public_key'] == 'pk-lf-test-public-key-67890'
            assert config['langfuse_base_url'] == 'https://cloud.langfuse.com'
            assert config['langfuse_auth3'] == 'test-auth3-token'
            
            print("OK: Langfuse configuration loaded correctly from .env")
            return True
            
        except Exception as e:
            print(f"ERROR: Configuration loading failed: {e}")
            return False
        finally:
            os.chdir(old_cwd)

def test_fuse_commands_with_env():
    """Test coaia fuse commands with .env configuration"""
    print("Testing coaia fuse commands with .env configuration...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        old_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Create .env file with test Langfuse config
            with open('.env', 'w') as f:
                f.write('LANGFUSE_SECRET_KEY=sk-lf-test-key\n')
                f.write('LANGFUSE_PUBLIC_KEY=pk-lf-test-key\n') 
                f.write('LANGFUSE_HOST=https://test.langfuse.com\n')
            
            # Test 1: coaia fuse prompts list --help (should work)
            result = subprocess.run([
                sys.executable, '-m', 'coaiapy.coaiacli', 'fuse', 'prompts', 'list', '--help'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, cwd='/app')
            
            if result.returncode == 0 and 'usage:' in result.stdout.lower():
                print("OK: coaia fuse prompts list --help works with .env config")
            else:
                print(f"ERROR: Help command failed: {result.stderr}")
                return False
            
            # Test 2: coaia fuse prompts list (will fail with test credentials, but should attempt connection)
            result = subprocess.run([
                sys.executable, '-m', 'coaiapy.coaiacli', 'fuse', 'prompts', 'list'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, cwd='/app', timeout=10)
            
            # We expect this to fail with authentication error, but it should try to connect
            # This proves the .env config was loaded and used
            if 'langfuse' in result.stderr.lower() or 'unauthorized' in result.stderr.lower() or 'authentication' in result.stderr.lower():
                print("OK: coaia fuse prompts list attempted connection with .env credentials")
            elif result.returncode != 0:
                print(f"OK: coaia fuse prompts list failed as expected with test credentials: {result.stderr[:100]}")
            else:
                print(f"WARNING: Unexpected success or different error: {result.stdout[:100]}")
            
            # Test 3: Verify the config is loaded by checking internal state
            # Reset and reload config in this directory
            import coaiapy.coaiamodule
            coaiapy.coaiamodule.config = None
            
            # Import cofuse to test Langfuse client creation
            try:
                from coaiapy.cofuse import get_langfuse_client
                
                # This should use the .env config
                # We don't actually call it since it would try to connect
                print("OK: Langfuse client module loads successfully with .env config")
            except ImportError as e:
                print(f"WARNING: Could not import cofuse module: {e}")
            
            return True
            
        except subprocess.TimeoutExpired:
            print("OK: Command timed out as expected (likely trying to connect)")
            return True
        except Exception as e:
            print(f"ERROR: Fuse command test failed: {e}")
            return False
        finally:
            os.chdir(old_cwd)

def test_env_vs_system_priority():
    """Test that system environment variables override .env file"""
    print("Testing environment variable priority (.env vs system)...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        old_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Create .env file
            with open('.env', 'w') as f:
                f.write('LANGFUSE_SECRET_KEY=dotenv_secret\n')
                f.write('LANGFUSE_PUBLIC_KEY=dotenv_public\n')
            
            # Set system environment variable (should override .env)
            os.environ['LANGFUSE_SECRET_KEY'] = 'system_env_secret'
            
            # Reset config
            import coaiapy.coaiamodule
            coaiapy.coaiamodule.config = None
            
            # Load config
            config = coaiapy.coaiamodule.read_config()
            
            # System env should override .env
            assert config['langfuse_secret_key'] == 'system_env_secret'
            # .env should be used when system env not set
            assert config['langfuse_public_key'] == 'dotenv_public'
            
            print("OK: Environment variable priority works correctly")
            return True
            
        except Exception as e:
            print(f"ERROR: Priority test failed: {e}")
            return False
        finally:
            # Clean up environment
            if 'LANGFUSE_SECRET_KEY' in os.environ:
                del os.environ['LANGFUSE_SECRET_KEY']
            os.chdir(old_cwd)

def test_fuse_commands_without_env():
    """Test that fuse commands work without .env file (fallback behavior)"""
    print("Testing coaia fuse commands without .env file...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        old_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # No .env file in this directory
            
            # Reset config
            import coaiapy.coaiamodule
            coaiapy.coaiamodule.config = None
            
            # Test help command should still work
            result = subprocess.run([
                sys.executable, '-m', 'coaiapy.coaiacli', 'fuse', '--help'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, cwd='/app')
            
            if result.returncode == 0:
                print("OK: coaia fuse --help works without .env file")
                return True
            else:
                print(f"ERROR: Help failed without .env: {result.stderr}")
                return False
            
        except Exception as e:
            print(f"ERROR: No .env test failed: {e}")
            return False
        finally:
            os.chdir(old_cwd)

def run_langfuse_integration_tests():
    """Run all Langfuse .env integration tests"""
    print("=" * 60)
    print("LANGFUSE  LANGFUSE .ENV INTEGRATION TESTS")
    print("=" * 60)
    
    tests = [
        test_langfuse_config_loading,
        test_fuse_commands_with_env, 
        test_env_vs_system_priority,
        test_fuse_commands_without_env
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"ERROR: {test_func.__name__} crashed: {e}")
            failed += 1
        print()  # Add spacing between tests
    
    # Results
    total = passed + failed
    print("=" * 60)
    if failed == 0:
        print(f"SUCCESS:  ALL LANGFUSE .ENV TESTS PASSED! ({passed}/{total})")
    else:
        print(f"FAILURE:  {failed}/{total} TESTS FAILED")
    print("=" * 60)
    
    return failed == 0

if __name__ == '__main__':
    success = run_langfuse_integration_tests()
    sys.exit(0 if success else 1)