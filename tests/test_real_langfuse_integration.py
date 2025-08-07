#!/usr/bin/env python3
"""
Real Langfuse integration tests using actual test environment
Tests with real API calls to validate .env functionality end-to-end
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

def test_real_langfuse_prompts_list():
    """Test coaia fuse prompts list with real Langfuse environment"""
    print("Testing real Langfuse prompts list...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        old_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Copy the .env.tests file as .env
            env_tests_path = '/app/.env.tests'
            if not os.path.exists(env_tests_path):
                print("WARNING: .env.tests file not found, skipping real Langfuse tests")
                return True
                
            with open(env_tests_path, 'r') as f:
                env_content = f.read()
            
            with open('.env', 'w') as f:
                f.write(env_content)
            
            # Reset config to load from .env
            import coaiapy.coaiamodule
            coaiapy.coaiamodule.config = None
            
            # Test prompts list with table output
            result = subprocess.run([
                sys.executable, '-m', 'coaiapy.coaiacli', 'fuse', 'prompts', 'list'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, 
              cwd='/app', timeout=30)
            
            if result.returncode == 0:
                output = result.stdout
                # Check for table format indicators
                if '+' in output and '|' in output and 'Name' in output:
                    print("OK: Real Langfuse prompts list returns table format")
                elif 'No prompts found' in output:
                    print("OK: Real Langfuse prompts list works (no prompts found)")
                else:
                    print(f"OK: Real Langfuse prompts list works: {output[:100]}...")
            else:
                print(f"ERROR: Real prompts list failed: {result.stderr[:200]}")
                return False
            
            # Test prompts list with JSON output
            result = subprocess.run([
                sys.executable, '-m', 'coaiapy.coaiacli', 'fuse', 'prompts', 'list', '--json'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, 
              cwd='/app', timeout=30)
            
            if result.returncode == 0:
                try:
                    json_output = json.loads(result.stdout)
                    if isinstance(json_output, list):
                        print("OK: Real Langfuse prompts list --json returns valid JSON array")
                    else:
                        print(f"OK: Real Langfuse prompts list --json works: {type(json_output)}")
                except json.JSONDecodeError:
                    print(f"WARNING: JSON output not valid: {result.stdout[:100]}")
            else:
                print(f"ERROR: Real prompts list --json failed: {result.stderr[:200]}")
                return False
                
            return True
            
        except subprocess.TimeoutExpired:
            print("ERROR: Real Langfuse test timed out (network/API issue)")
            return False
        except Exception as e:
            print(f"ERROR: Real Langfuse test failed: {e}")
            return False
        finally:
            os.chdir(old_cwd)

def test_real_langfuse_datasets_list():
    """Test coaia fuse datasets list with real Langfuse environment"""
    print("Testing real Langfuse datasets list...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        old_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Copy the .env.tests file as .env
            env_tests_path = '/app/.env.tests'
            if not os.path.exists(env_tests_path):
                print("WARNING: .env.tests file not found, skipping")
                return True
                
            with open(env_tests_path, 'r') as f:
                env_content = f.read()
            
            with open('.env', 'w') as f:
                f.write(env_content)
            
            # Reset config
            import coaiapy.coaiamodule
            coaiapy.coaiamodule.config = None
            
            # Test datasets list
            result = subprocess.run([
                sys.executable, '-m', 'coaiapy.coaiacli', 'fuse', 'datasets', 'list'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, 
              cwd='/app', timeout=30)
            
            if result.returncode == 0:
                output = result.stdout
                if '+' in output and '|' in output:
                    print("OK: Real Langfuse datasets list returns table format")
                elif 'No datasets found' in output or len(output.strip()) == 0:
                    print("OK: Real Langfuse datasets list works (empty)")
                else:
                    print(f"OK: Real Langfuse datasets list works: {output[:100]}...")
                return True
            else:
                print(f"ERROR: Real datasets list failed: {result.stderr[:200]}")
                return False
                
        except subprocess.TimeoutExpired:
            print("ERROR: Real datasets test timed out")
            return False
        except Exception as e:
            print(f"ERROR: Real datasets test failed: {e}")
            return False
        finally:
            os.chdir(old_cwd)

def test_real_langfuse_traces_commands():
    """Test coaia fuse traces commands with real Langfuse environment"""
    print("Testing real Langfuse traces commands...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        old_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Copy the .env.tests file as .env
            env_tests_path = '/app/.env.tests'
            if not os.path.exists(env_tests_path):
                print("WARNING: .env.tests file not found, skipping")
                return True
                
            with open(env_tests_path, 'r') as f:
                env_content = f.read()
            
            with open('.env', 'w') as f:
                f.write(env_content)
            
            # Reset config
            import coaiapy.coaiamodule
            coaiapy.coaiamodule.config = None
            
            # Test traces help (should work)
            result = subprocess.run([
                sys.executable, '-m', 'coaiapy.coaiacli', 'fuse', 'traces', '--help'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, 
              cwd='/app', timeout=30)
            
            if result.returncode == 0:
                print("OK: Real Langfuse traces --help works")
                # Check what commands are available
                if 'add' in result.stdout:
                    print("OK: Real Langfuse traces add command available")
                else:
                    print(f"OK: Real Langfuse traces help: {result.stdout[:100]}...")
                return True
            else:
                print(f"ERROR: Real traces help failed: {result.stderr[:200]}")
                return False
                
        except subprocess.TimeoutExpired:
            print("ERROR: Real traces test timed out")
            return False
        except Exception as e:
            print(f"ERROR: Real traces test failed: {e}")
            return False
        finally:
            os.chdir(old_cwd)

def test_real_langfuse_config_validation():
    """Test that .env.tests loads correctly into configuration"""
    print("Testing real Langfuse configuration loading...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        old_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Copy the .env.tests file as .env
            env_tests_path = '/app/.env.tests'
            if not os.path.exists(env_tests_path):
                print("WARNING: .env.tests file not found")
                return True
                
            with open(env_tests_path, 'r') as f:
                env_content = f.read()
            
            with open('.env', 'w') as f:
                f.write(env_content)
            
            # Reset config and load
            import coaiapy.coaiamodule
            coaiapy.coaiamodule.config = None
            config = coaiapy.coaiamodule.read_config()
            
            # Validate Langfuse config
            secret_key = config.get('langfuse_secret_key', '')
            public_key = config.get('langfuse_public_key', '')
            host = config.get('langfuse_base_url', '')
            
            if secret_key.startswith('sk-lf-'):
                print("OK: Real Langfuse secret key loaded correctly")
            else:
                print(f"ERROR: Invalid secret key: {secret_key[:15]}...")
                return False
                
            if public_key.startswith('pk-lf-'):
                print("OK: Real Langfuse public key loaded correctly")
            else:
                print(f"ERROR: Invalid public key: {public_key[:15]}...")
                return False
                
            if 'langfuse.com' in host:
                print("OK: Real Langfuse host loaded correctly")
            else:
                print(f"ERROR: Invalid host: {host}")
                return False
                
            return True
            
        except Exception as e:
            print(f"ERROR: Real config validation failed: {e}")
            return False
        finally:
            os.chdir(old_cwd)

def run_real_langfuse_integration_tests():
    """Run all real Langfuse integration tests"""
    print("=" * 70)
    print("REAL LANGFUSE INTEGRATION TESTS (.env.tests)")
    print("=" * 70)
    
    tests = [
        test_real_langfuse_config_validation,
        test_real_langfuse_prompts_list,
        test_real_langfuse_datasets_list,
        test_real_langfuse_traces_commands
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
    print("=" * 70)
    if failed == 0:
        print(f"SUCCESS: ALL REAL LANGFUSE TESTS PASSED! ({passed}/{total})")
    else:
        print(f"FAILURE: {failed}/{total} REAL LANGFUSE TESTS FAILED")
    print("=" * 70)
    
    return failed == 0

if __name__ == '__main__':
    success = run_real_langfuse_integration_tests()
    sys.exit(0 if success else 1)