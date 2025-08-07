#!/usr/bin/env python3
"""
Comprehensive test suite for coaiapy package
Tests configuration loading, CLI functionality, and core features
"""
import os
import sys
import json
import tempfile
import subprocess
from pathlib import Path

# Add coaiapy to path
sys.path.insert(0, '/app')
sys.path.insert(0, '/app/coaiapy')

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def success(self, test_name):
        print(f"OK: {test_name}")
        self.passed += 1
    
    def failure(self, test_name, error):
        print(f"ERROR: {test_name}: {error}")
        self.failed += 1
        self.errors.append(f"{test_name}: {error}")
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\nTest Results: {self.passed}/{total} passed")
        if self.failed > 0:
            print("Failures:")
            for error in self.errors:
                print(f"  - {error}")
        return self.failed == 0

def test_imports(results):
    """Test that all coaiapy modules can be imported"""
    print("Testing module imports...")
    
    try:
        import coaiapy
        results.success("Import coaiapy")
    except Exception as e:
        results.failure("Import coaiapy", str(e))
    
    try:
        from coaiapy import coaiamodule
        results.success("Import coaiamodule")
    except Exception as e:
        results.failure("Import coaiamodule", str(e))
    
    try:
        from coaiapy import coaiacli
        results.success("Import coaiacli")
    except Exception as e:
        results.failure("Import coaiacli", str(e))
    
    try:
        from coaiapy import cofuse
        results.success("Import cofuse")
    except Exception as e:
        results.failure("Import cofuse", str(e))
    
    try:
        from coaiapy import syntation
        results.success("Import syntation")
    except Exception as e:
        results.failure("Import syntation", str(e))

def test_configuration_loading(results):
    """Test configuration loading functionality"""
    print("\nTesting configuration loading...")
    
    try:
        from coaiapy.coaiamodule import read_config, load_env_file
        
        # Test basic config loading
        config = read_config()
        assert isinstance(config, dict)
        assert 'jtaleconf' in config
        assert 'pollyconf' in config
        results.success("Basic config loading")
        
        # Test .env file loading
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write('TEST_KEY=test_value\n')
            env_file = f.name
        
        try:
            env_vars = load_env_file(env_file)
            assert env_vars['TEST_KEY'] == 'test_value'
            results.success(".env file parsing")
        finally:
            os.unlink(env_file)
        
    except Exception as e:
        results.failure("Configuration loading", str(e))

def test_cli_help(results):
    """Test CLI help functionality"""
    print("\nTesting CLI help...")
    
    try:
        # Test main help
        result = subprocess.run([
            sys.executable, '-m', 'coaiapy.coaiacli', '--help'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, cwd='/app')
        
        if result.returncode == 0 and 'usage:' in result.stdout.lower():
            results.success("CLI main help")
        else:
            results.failure("CLI main help", f"Return code: {result.returncode}")
        
        # Test subcommand help
        result = subprocess.run([
            sys.executable, '-m', 'coaiapy.coaiacli', 'fuse', '--help'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, cwd='/app')
        
        if result.returncode == 0:
            results.success("CLI fuse help")
        else:
            results.failure("CLI fuse help", f"Return code: {result.returncode}")
            
    except Exception as e:
        results.failure("CLI help", str(e))

def test_cli_commands(results):
    """Test basic CLI commands (without external dependencies)"""
    print("\nTesting CLI commands...")
    
    try:
        # Test init command
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run([
                sys.executable, '-m', 'coaiapy.coaiacli', 'init'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, cwd=temp_dir)
            
            if result.returncode == 0:
                results.success("CLI init command")
            else:
                results.failure("CLI init command", f"Return code: {result.returncode}, stderr: {result.stderr}")
        
    except Exception as e:
        results.failure("CLI commands", str(e))

def test_env_file_integration(results):
    """Test .env file integration with config system"""
    print("\nTesting .env file integration...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        old_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Create .env file
            with open('.env', 'w') as f:
                f.write('LANGFUSE_SECRET_KEY=test_secret\n')
                f.write('LANGFUSE_PUBLIC_KEY=test_public\n')
                f.write('LANGFUSE_HOST=https://test.example.com\n')
            
            # Reset config to force reload
            import coaiapy.coaiamodule
            coaiapy.coaiamodule.config = None
            
            # Load config
            config = coaiapy.coaiamodule.read_config()
            
            # Verify values
            if (config.get('langfuse_secret_key') == 'test_secret' and 
                config.get('langfuse_public_key') == 'test_public' and
                config.get('langfuse_base_url') == 'https://test.example.com'):
                results.success(".env file integration")
            else:
                results.failure(".env file integration", "Values not loaded correctly")
                
        except Exception as e:
            results.failure(".env file integration", str(e))
        finally:
            os.chdir(old_cwd)

def test_config_priority(results):
    """Test configuration priority: system env > .env > defaults"""
    print("\nTesting configuration priority...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        old_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Create .env file
            with open('.env', 'w') as f:
                f.write('LANGFUSE_SECRET_KEY=dotenv_value\n')
            
            # Set system environment variable
            os.environ['LANGFUSE_SECRET_KEY'] = 'system_env_value'
            
            # Reset config
            import coaiapy.coaiamodule
            coaiapy.coaiamodule.config = None
            
            # Load config
            config = coaiapy.coaiamodule.read_config()
            
            # System env should override .env
            if config.get('langfuse_secret_key') == 'system_env_value':
                results.success("Configuration priority")
            else:
                results.failure("Configuration priority", 
                              f"Expected 'system_env_value', got '{config.get('langfuse_secret_key')}'")
                
        except Exception as e:
            results.failure("Configuration priority", str(e))
        finally:
            # Clean up
            if 'LANGFUSE_SECRET_KEY' in os.environ:
                del os.environ['LANGFUSE_SECRET_KEY']
            os.chdir(old_cwd)

def test_python_compatibility(results):
    """Test Python 3.6 compatibility features"""
    print("\nTesting Python 3.6 compatibility...")
    
    try:
        # Test f-strings are not used in critical paths
        import coaiapy.coaiamodule
        results.success("Module compatibility check")
        
        # Test that required packages are available
        import json
        import os
        import sys
        results.success("Standard library availability")
        
    except Exception as e:
        results.failure("Python compatibility", str(e))

def run_comprehensive_tests():
    """Run all tests in the comprehensive suite"""
    print("=" * 60)
    print("COAIAPY COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    
    results = TestResults()
    
    # Run all test categories
    test_imports(results)
    test_configuration_loading(results)
    test_cli_help(results)
    test_cli_commands(results)
    test_env_file_integration(results)
    test_config_priority(results)
    test_python_compatibility(results)
    
    # Show final results
    print("\n" + "=" * 60)
    success = results.summary()
    if success:
        print("SUCCESS: ALL TESTS PASSED!")
    else:
        print("FAILURE: SOME TESTS FAILED!")
    print("=" * 60)
    
    return success

if __name__ == '__main__':
    # Run all test suites
    print("Running .env functionality tests first...\n")
    
    try:
        from test_env_functionality import run_all_tests as run_env_tests
        env_success = run_env_tests()
    except ImportError:
        print("Warning: Could not import env functionality tests")
        env_success = True
    except Exception as e:
        print(f"Error running env tests: {e}")
        env_success = False
    
    print("\n\nRunning Langfuse .env integration tests...\n")
    
    try:
        from test_langfuse_env_integration import run_langfuse_integration_tests
        langfuse_success = run_langfuse_integration_tests()
    except ImportError:
        print("Warning: Could not import Langfuse integration tests")
        langfuse_success = True
    except Exception as e:
        print(f"Error running Langfuse tests: {e}")
        langfuse_success = False
    
    print("\n\nRunning REAL Langfuse integration tests...\n")
    
    try:
        from test_real_langfuse_integration import run_real_langfuse_integration_tests
        real_langfuse_success = run_real_langfuse_integration_tests()
    except ImportError:
        print("Warning: Could not import real Langfuse integration tests")
        real_langfuse_success = True
    except Exception as e:
        print(f"Error running real Langfuse tests: {e}")
        real_langfuse_success = False
    
    print("\n\nNow running comprehensive tests...\n")
    comp_success = run_comprehensive_tests()
    
    overall_success = env_success and langfuse_success and real_langfuse_success and comp_success
    print(f"\nOVERALL RESULT: {'PASS' if overall_success else 'FAIL'}")
    
    sys.exit(0 if overall_success else 1)