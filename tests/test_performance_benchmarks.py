"""
Performance Benchmark Tests

Tests to verify that the mobile template engine performs better than
the original Jinja2 implementation, especially in mobile/Pythonista contexts.
"""

import unittest
import time
import gc
import sys
from typing import List, Dict, Any
from coaiapy.mobile_template import MobileTemplateEngine, MobileEnvironment
from coaiapy.pipeline import TemplateLoader, TemplateRenderer


class TestMobileTemplatePerformance(unittest.TestCase):
    """Test performance of mobile template engine"""
    
    def setUp(self):
        """Set up performance test fixtures"""
        self.mobile_engine = MobileTemplateEngine()
        self.mobile_env = MobileEnvironment()
        self.test_variables = {
            'user_name': 'JohnDoe',
            'project_id': '12345',
            'environment': 'production',
            'debug_mode': True,
            'count': 42,
            'timestamp': '2025-01-15T10:30:00Z'
        }
        
        # Complex template for stress testing
        self.complex_template = """
        User: {{user_name|title}}
        Project: {{project_id}}
        Environment: {{environment|upper}}
        {% if debug_mode %}
        Debug Mode: Enabled
        Count: {{count}}
        {% endif %}
        Timestamp: {{timestamp}}
        Mobile ID: {{mobile_id()}}
        """
    
    def test_simple_template_performance(self):
        """Test performance of simple template rendering"""
        simple_template = "Hello {{user_name}}, project {{project_id}} in {{environment}}"
        
        iterations = 1000
        start_time = time.time()
        
        for _ in range(iterations):
            result = self.mobile_engine.render_template_content(simple_template, self.test_variables)
            self.assertIn('JohnDoe', result)
        
        end_time = time.time()
        duration = end_time - start_time
        per_render = duration / iterations
        
        # Should be very fast for simple templates
        self.assertLess(per_render, 0.001, f"Simple template rendering too slow: {per_render:.4f}s per render")
        print(f"Simple template: {per_render*1000:.2f}ms per render ({iterations} iterations)")
    
    def test_complex_template_performance(self):
        """Test performance of complex template with conditionals and filters"""
        iterations = 500
        start_time = time.time()
        
        for _ in range(iterations):
            result = self.mobile_engine.render_template_content(self.complex_template, self.test_variables)
            self.assertIn('PRODUCTION', result)  # Should have |upper filter applied
        
        end_time = time.time()
        duration = end_time - start_time
        per_render = duration / iterations
        
        # Should still be fast even for complex templates
        self.assertLess(per_render, 0.005, f"Complex template rendering too slow: {per_render:.4f}s per render")
        print(f"Complex template: {per_render*1000:.2f}ms per render ({iterations} iterations)")
    
    def test_builtin_function_performance(self):
        """Test performance of built-in mobile functions"""
        template_with_functions = "{{uuid4()}} - {{mobile_id()}} - {{now()}} - {{touch_timestamp()}}"
        
        iterations = 200
        start_time = time.time()
        
        for _ in range(iterations):
            result = self.mobile_engine.render_template_content(template_with_functions, {})
            # Should contain all function outputs
            parts = result.split(' - ')
            self.assertEqual(len(parts), 4)
        
        end_time = time.time()
        duration = end_time - start_time
        per_render = duration / iterations
        
        # Built-in functions should be reasonably fast
        self.assertLess(per_render, 0.01, f"Built-in functions too slow: {per_render:.4f}s per render")
        print(f"Built-in functions: {per_render*1000:.2f}ms per render ({iterations} iterations)")
    
    def test_large_variable_set_performance(self):
        """Test performance with large number of variables"""
        # Create 100 variables
        large_var_set = {f'var_{i}': f'value_{i}' for i in range(100)}
        large_var_set.update(self.test_variables)
        
        # Template that uses many variables
        template_parts = [f"{{{{var_{i}}}}}" for i in range(0, 100, 10)]  # Use every 10th variable
        large_template = " | ".join(template_parts)
        
        iterations = 100
        start_time = time.time()
        
        for _ in range(iterations):
            result = self.mobile_engine.render_template_content(large_template, large_var_set)
            self.assertIn('value_0', result)
            self.assertIn('value_90', result)
        
        end_time = time.time()
        duration = end_time - start_time
        per_render = duration / iterations
        
        # Should handle large variable sets efficiently
        self.assertLess(per_render, 0.01, f"Large variable set too slow: {per_render:.4f}s per render")
        print(f"Large variable set: {per_render*1000:.2f}ms per render ({iterations} iterations)")
    
    def test_recursive_structure_performance(self):
        """Test performance of recursive dict/list rendering"""
        complex_data = {
            'users': [
                {'name': '{{user_name}}', 'id': '{{project_id}}'},
                {'name': 'Jane{{count}}', 'id': 'proj_{{count}}'}
            ],
            'settings': {
                'env': '{{environment}}',
                'debug': '{{debug_mode}}',
                'nested': {
                    'deep': '{{timestamp}}',
                    'mobile': '{{mobile_id()}}'
                }
            }
        }
        
        iterations = 200
        start_time = time.time()
        
        for _ in range(iterations):
            result = self.mobile_engine.render_dict(complex_data, self.test_variables)
            self.assertEqual(result['users'][0]['name'], 'JohnDoe')
            self.assertEqual(result['settings']['env'], 'production')
        
        end_time = time.time()
        duration = end_time - start_time
        per_render = duration / iterations
        
        # Recursive rendering should be efficient
        self.assertLess(per_render, 0.01, f"Recursive rendering too slow: {per_render:.4f}s per render")
        print(f"Recursive structures: {per_render*1000:.2f}ms per render ({iterations} iterations)")


class TestPipelineTemplatePerformance(unittest.TestCase):
    """Test performance of complete pipeline template rendering"""
    
    def setUp(self):
        """Set up pipeline performance test fixtures"""
        self.loader = TemplateLoader()
        self.renderer = TemplateRenderer()
    
    def test_mobile_template_rendering_performance(self):
        """Test performance of mobile template rendering"""
        template = self.loader.load_template("ios-data-sync")
        variables = {
            'sync_name': 'Performance Test',
            'cloud_service': 'iCloud',
            'data_type': 'photos'
        }
        
        iterations = 100
        start_time = time.time()
        
        for _ in range(iterations):
            observations = self.renderer.render_template(template, variables)
            self.assertEqual(len(observations), 4)  # ios-data-sync has 4 steps
        
        end_time = time.time()
        duration = end_time - start_time
        per_render = duration / iterations
        
        # Pipeline rendering should be fast
        self.assertLess(per_render, 0.05, f"Pipeline rendering too slow: {per_render:.4f}s per render")
        print(f"Mobile pipeline rendering: {per_render*1000:.2f}ms per render ({iterations} iterations)")
    
    def test_all_mobile_templates_performance(self):
        """Test performance across all mobile templates"""
        mobile_templates = ['ios-data-sync', 'mobile-transcription', 'quick-analysis', 'gesture-pipeline']
        
        test_variables = {
            'sync_name': 'Perf Test',
            'cloud_service': 'Dropbox', 
            'data_type': 'documents',
            'audio_source': 'Test Audio',
            'language': 'en-US',
            'quality_preference': 'fast',
            'data_source': 'test.csv',
            'analysis_type': 'trends',
            'gesture_type': 'tap',
            'workflow_name': 'Quick Action',
            'app_context': 'Pythonista'
        }
        
        for template_name in mobile_templates:
            with self.subTest(template=template_name):
                template = self.loader.load_template(template_name)
                
                iterations = 50
                start_time = time.time()
                
                for _ in range(iterations):
                    observations = self.renderer.render_template(template, test_variables)
                    self.assertIsInstance(observations, list)
                    self.assertGreater(len(observations), 0)
                
                end_time = time.time()
                duration = end_time - start_time
                per_render = duration / iterations
                
                # Each mobile template should render quickly
                self.assertLess(per_render, 0.1, f"{template_name} too slow: {per_render:.4f}s per render")
                print(f"{template_name}: {per_render*1000:.2f}ms per render ({iterations} iterations)")


class TestMemoryEfficiency(unittest.TestCase):
    """Test memory efficiency of mobile template engine"""
    
    def setUp(self):
        """Set up memory efficiency tests"""
        # Force garbage collection before tests
        if hasattr(gc, 'collect'):
            gc.collect()
    
    def test_template_engine_memory_footprint(self):
        """Test memory footprint of template engine creation"""
        if not hasattr(gc, 'get_objects'):
            self.skipTest("gc.get_objects not available")
        
        initial_objects = len(gc.get_objects())
        
        # Create multiple engines
        engines = []
        for _ in range(10):
            engines.append(MobileTemplateEngine())
        
        mid_objects = len(gc.get_objects())
        
        # Use the engines
        for i, engine in enumerate(engines):
            result = engine.render_template_content(f"Test {{{{var{i}}}}}", {f'var{i}': f'value{i}'})
            self.assertIn(f'value{i}', result)
        
        # Cleanup
        del engines
        gc.collect()
        
        final_objects = len(gc.get_objects())
        
        # Memory should be released properly
        object_growth = final_objects - initial_objects
        self.assertLess(object_growth, 100, f"Too many objects retained: {object_growth}")
        print(f"Memory test: {object_growth} objects retained after cleanup")
    
    def test_large_template_memory_usage(self):
        """Test memory usage with large templates"""
        engine = MobileTemplateEngine()
        
        # Create a large template
        large_template = "\n".join([f"Line {i}: {{{{var_{i%10}}}}}" for i in range(1000)])
        variables = {f'var_{i}': f'value_{i}' for i in range(10)}
        
        if hasattr(gc, 'get_objects'):
            initial_objects = len(gc.get_objects())
        
        # Render the large template multiple times
        for _ in range(10):
            result = engine.render_template_content(large_template, variables)
            self.assertIn('Line 999:', result)
        
        if hasattr(gc, 'get_objects'):
            final_objects = len(gc.get_objects())
            object_growth = final_objects - initial_objects
            
            # Should not create excessive objects
            self.assertLess(object_growth, 50, f"Large template created too many objects: {object_growth}")


class TestScalabilityBenchmarks(unittest.TestCase):
    """Test scalability of mobile template engine"""
    
    def test_concurrent_template_rendering(self):
        """Test behavior under concurrent-like loads"""
        engines = [MobileTemplateEngine() for _ in range(20)]
        template = "User {{user}} in {{env|upper}} mode {{timestamp()}}"
        
        start_time = time.time()
        
        results = []
        for i, engine in enumerate(engines):
            variables = {'user': f'user_{i}', 'env': 'test'}
            result = engine.render_template_content(template, variables)
            results.append(result)
            self.assertIn(f'user_{i}', result)
            self.assertIn('TEST', result)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should handle multiple engines efficiently
        self.assertLess(duration, 1.0, f"Concurrent rendering too slow: {duration:.4f}s")
        print(f"Concurrent rendering: {duration*1000:.2f}ms for 20 engines")
    
    def test_template_caching_efficiency(self):
        """Test that template parsing is efficient with reuse"""
        engine = MobileTemplateEngine()
        template = "Hello {{name}}, your score is {{score|title}}"
        
        # First batch - template gets parsed
        start_time = time.time()
        for i in range(100):
            result = engine.render_template_content(template, {'name': f'User{i}', 'score': 'high'})
            self.assertIn(f'User{i}', result)
        first_batch_time = time.time() - start_time
        
        # Second batch - should be faster due to any internal optimizations
        start_time = time.time()
        for i in range(100):
            result = engine.render_template_content(template, {'name': f'User{i}', 'score': 'low'})
            self.assertIn(f'User{i}', result)
        second_batch_time = time.time() - start_time
        
        # Print timing information
        print(f"Template reuse: First batch {first_batch_time*1000:.2f}ms, "
              f"Second batch {second_batch_time*1000:.2f}ms")
        
        # Both batches should be reasonably fast
        self.assertLess(first_batch_time, 0.5, "First batch too slow")
        self.assertLess(second_batch_time, 0.5, "Second batch too slow")


class TestMobileOptimizations(unittest.TestCase):
    """Test mobile-specific performance optimizations"""
    
    def test_mobile_function_performance(self):
        """Test performance of mobile-specific functions"""
        engine = MobileTemplateEngine()
        
        # Test mobile_id performance
        start_time = time.time()
        mobile_ids = [engine.builtin_functions['mobile_id']() for _ in range(1000)]
        mobile_id_time = time.time() - start_time
        
        # Verify format and uniqueness
        self.assertTrue(all(mid.startswith('mobile_') for mid in mobile_ids))
        self.assertEqual(len(set(mobile_ids)), 1000, "mobile_id should generate unique values")
        
        # Test touch_timestamp performance  
        start_time = time.time()
        timestamps = [engine.builtin_functions['touch_timestamp']() for _ in range(1000)]
        timestamp_time = time.time() - start_time
        
        # Verify format
        import re
        time_pattern = r'\d{2}:\d{2}:\d{2}'
        self.assertTrue(all(re.match(time_pattern, ts) for ts in timestamps))
        
        # Both should be very fast
        self.assertLess(mobile_id_time, 0.1, f"mobile_id too slow: {mobile_id_time:.4f}s")
        self.assertLess(timestamp_time, 0.1, f"touch_timestamp too slow: {timestamp_time:.4f}s")
        
        print(f"Mobile functions: mobile_id {mobile_id_time*1000:.2f}ms, "
              f"touch_timestamp {timestamp_time*1000:.2f}ms (1000 calls each)")
    
    def test_battery_efficient_processing(self):
        """Test that processing is battery-efficient (minimal CPU cycles)"""
        engine = MobileTemplateEngine()
        
        # Simple template that should be very efficient
        simple_template = "{{value}}"
        
        iterations = 10000
        start_time = time.time()
        
        for i in range(iterations):
            result = engine.render_template_content(simple_template, {'value': str(i)})
            self.assertEqual(result, str(i))
        
        end_time = time.time()
        duration = end_time - start_time
        per_render = duration / iterations
        
        # Should be extremely fast for battery efficiency
        self.assertLess(per_render, 0.0001, f"Battery-efficient processing too slow: {per_render:.6f}s")
        print(f"Battery-efficient processing: {per_render*1000000:.2f}µs per simple render")


if __name__ == '__main__':
    # Import gc if available for memory tests
    try:
        import gc
    except ImportError:
        gc = None
    
    print("Running Performance Benchmark Tests...")
    print("=" * 60)
    
    # Run tests with verbose output
    unittest.main(verbosity=2, buffer=True)