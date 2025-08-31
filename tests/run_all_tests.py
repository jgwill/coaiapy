#!/usr/bin/env python3
"""
Comprehensive Test Runner for CoaiaPy Mobile Template Engine

Runs all test suites and provides detailed reporting on:
- Mobile template engine functionality
- Pipeline template rendering
- Pythonista compatibility
- Performance benchmarks
- Mobile workflow integration
"""

import unittest
import sys
import time
import os
from pathlib import Path


def run_test_suite():
    """Run comprehensive test suite with detailed reporting"""
    
    print("🚀 CoaiaPy Mobile Template Engine Test Suite")
    print("=" * 70)
    print("Testing zero-build Pythonista compatibility and performance")
    print()
    
    # Add tests directory to path
    tests_dir = Path(__file__).parent
    if str(tests_dir) not in sys.path:
        sys.path.insert(0, str(tests_dir))
    
    # Test suite configuration
    test_modules = [
        ('test_mobile_template_engine', 'Mobile Template Engine Core'),
        ('test_pipeline_templates', 'Pipeline Template Rendering'),
        ('test_pythonista_compatibility', 'Pythonista Compatibility'),
        ('test_performance_benchmarks', 'Performance Benchmarks'),
        ('test_mobile_workflows', 'Mobile Workflow Integration')
    ]
    
    total_start_time = time.time()
    results = {}
    
    for module_name, description in test_modules:
        print(f"📋 Running: {description}")
        print("-" * 50)
        
        try:
            # Import and run test module
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromName(module_name)
            
            # Run tests with custom result handler
            runner = unittest.TextTestRunner(
                verbosity=2,
                stream=sys.stdout,
                buffer=True
            )
            
            start_time = time.time()
            result = runner.run(suite)
            end_time = time.time()
            
            # Store results
            results[description] = {
                'tests_run': result.testsRun,
                'failures': len(result.failures),
                'errors': len(result.errors),
                'skipped': len(result.skipped) if hasattr(result, 'skipped') else 0,
                'duration': end_time - start_time,
                'success': result.wasSuccessful()
            }
            
            print(f"✅ Completed in {end_time - start_time:.2f}s")
            print()
            
        except ImportError as e:
            print(f"❌ Failed to import {module_name}: {e}")
            results[description] = {
                'tests_run': 0,
                'failures': 0,
                'errors': 1,
                'skipped': 0,
                'duration': 0,
                'success': False
            }
        except Exception as e:
            print(f"❌ Error running {module_name}: {e}")
            results[description] = {
                'tests_run': 0,
                'failures': 0,
                'errors': 1,
                'skipped': 0,
                'duration': 0,
                'success': False
            }
    
    total_end_time = time.time()
    total_duration = total_end_time - total_start_time
    
    # Print comprehensive summary
    print("📊 TEST SUITE SUMMARY")
    print("=" * 70)
    
    total_tests = sum(r['tests_run'] for r in results.values())
    total_failures = sum(r['failures'] for r in results.values())
    total_errors = sum(r['errors'] for r in results.values())
    total_skipped = sum(r['skipped'] for r in results.values())
    
    for description, result in results.items():
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"{status} {description}")
        print(f"     Tests: {result['tests_run']}, "
              f"Failures: {result['failures']}, "
              f"Errors: {result['errors']}, "
              f"Skipped: {result['skipped']}")
        print(f"     Duration: {result['duration']:.2f}s")
        print()
    
    print("OVERALL RESULTS:")
    print(f"📈 Total Tests: {total_tests}")
    print(f"✅ Passed: {total_tests - total_failures - total_errors}")
    print(f"❌ Failed: {total_failures}")
    print(f"⚠️  Errors: {total_errors}")
    print(f"⏭️  Skipped: {total_skipped}")
    print(f"⏱️  Total Duration: {total_duration:.2f}s")
    
    # Overall success determination
    overall_success = all(r['success'] for r in results.values())
    
    if overall_success:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ CoaiaPy Mobile Template Engine is ready for Pythonista!")
        print("✅ Zero build dependencies confirmed")
        print("✅ Mobile optimizations validated")
        print("✅ Performance benchmarks met")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("Review failed tests above for details")
        return 1


def run_specific_test_category(category):
    """Run a specific test category"""
    categories = {
        'engine': 'test_mobile_template_engine',
        'templates': 'test_pipeline_templates', 
        'compatibility': 'test_pythonista_compatibility',
        'performance': 'test_performance_benchmarks',
        'workflows': 'test_mobile_workflows'
    }
    
    if category not in categories:
        print(f"Unknown category: {category}")
        print(f"Available categories: {', '.join(categories.keys())}")
        return 1
    
    module_name = categories[category]
    
    print(f"🎯 Running specific test category: {category}")
    print(f"📋 Module: {module_name}")
    print("-" * 50)
    
    try:
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName(module_name)
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return 0 if result.wasSuccessful() else 1
        
    except Exception as e:
        print(f"❌ Error running {module_name}: {e}")
        return 1


def run_quick_validation():
    """Run quick validation tests for CI/CD"""
    print("⚡ Quick Validation Test")
    print("-" * 30)
    
    try:
        # Test core imports
        print("Testing core imports...")
        from coaiapy.mobile_template import MobileTemplateEngine
        from coaiapy.pipeline import TemplateLoader, TemplateRenderer
        
        # Test basic functionality
        print("Testing basic functionality...")
        engine = MobileTemplateEngine()
        result = engine.render_template_content("Hello {{name}}", {'name': 'World'})
        assert result == "Hello World", f"Basic rendering failed: {result}"
        
        # Test template loading
        print("Testing template loading...")
        loader = TemplateLoader()
        template = loader.load_template("simple-trace")
        assert template is not None, "Failed to load simple-trace template"
        
        # Test mobile templates
        print("Testing mobile templates...")
        mobile_template = loader.load_template("ios-data-sync")
        assert mobile_template is not None, "Failed to load ios-data-sync template"
        
        print("✅ Quick validation PASSED!")
        return 0
        
    except Exception as e:
        print(f"❌ Quick validation FAILED: {e}")
        return 1


if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        
        if arg == 'quick':
            exit_code = run_quick_validation()
        elif arg in ['engine', 'templates', 'compatibility', 'performance', 'workflows']:
            exit_code = run_specific_test_category(arg)
        else:
            print("Usage:")
            print("  python run_all_tests.py              # Run all tests")
            print("  python run_all_tests.py quick        # Quick validation")
            print("  python run_all_tests.py engine       # Mobile template engine tests")
            print("  python run_all_tests.py templates    # Pipeline template tests")
            print("  python run_all_tests.py compatibility # Pythonista compatibility tests")
            print("  python run_all_tests.py performance  # Performance benchmark tests")
            print("  python run_all_tests.py workflows    # Mobile workflow tests")
            exit_code = 1
    else:
        exit_code = run_test_suite()
    
    sys.exit(exit_code)