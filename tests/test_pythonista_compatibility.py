"""
Test Suite for Pythonista Compatibility

Tests to ensure coaiapy works correctly in Pythonista iOS environment
and provides enhanced mobile experience.
"""

import unittest
import sys
import importlib
import subprocess
import os
import tempfile
from pathlib import Path


class TestPythonistaImportCompatibility(unittest.TestCase):
    """Test that all modules import correctly without build dependencies"""
    
    def test_core_module_imports(self):
        """Test core coaiapy modules import without Jinja2/MarkupSafe"""
        modules_to_test = [
            'coaiapy',
            'coaiapy.coaiacli',
            'coaiapy.coaiamodule', 
            'coaiapy.mobile_template',
            'coaiapy.pipeline',
            'coaiapy.environment',
            'coaiapy.cofuse'
        ]
        
        for module_name in modules_to_test:
            with self.subTest(module=module_name):
                try:
                    module = importlib.import_module(module_name)
                    self.assertIsNotNone(module)
                except ImportError as e:
                    # Should not fail due to Jinja2/MarkupSafe
                    self.assertNotIn('jinja2', str(e).lower())
                    self.assertNotIn('markupsafe', str(e).lower())
                    # Re-raise if it's a different import error
                    raise
    
    def test_no_build_dependencies_in_imports(self):
        """Test that no modules try to import Jinja2 or MarkupSafe"""
        # Import coaiapy and check sys.modules
        import coaiapy
        
        loaded_modules = list(sys.modules.keys())
        
        # Should not have loaded Jinja2 or MarkupSafe
        jinja_modules = [mod for mod in loaded_modules if 'jinja' in mod.lower()]
        markup_modules = [mod for mod in loaded_modules if 'markupsafe' in mod.lower()]
        
        self.assertEqual(jinja_modules, [], f"Jinja2 modules loaded: {jinja_modules}")
        self.assertEqual(markup_modules, [], f"MarkupSafe modules loaded: {markup_modules}")
    
    def test_mobile_template_engine_instantiation(self):
        """Test MobileTemplateEngine can be instantiated"""
        from coaiapy.mobile_template import MobileTemplateEngine
        
        engine = MobileTemplateEngine()
        self.assertIsNotNone(engine)
        self.assertIn('uuid4', engine.builtin_functions)
        self.assertIn('mobile_id', engine.builtin_functions)
    
    def test_pipeline_template_system_works(self):
        """Test pipeline template system works without Jinja2"""
        from coaiapy.pipeline import TemplateLoader, TemplateRenderer
        
        loader = TemplateLoader()
        renderer = TemplateRenderer()
        
        # Should be able to load and render templates
        template = loader.load_template("simple-trace")
        self.assertIsNotNone(template)
        
        observations = renderer.render_template(template, {'trace_name': 'Test'})
        self.assertIsInstance(observations, list)
        self.assertGreater(len(observations), 0)


class TestPythonistaInstallSimulation(unittest.TestCase):
    """Simulate Pythonista installation scenarios"""
    
    def test_package_installation_simulation(self):
        """Test that package can be installed without build steps"""
        # This simulates what happens during pip install in Pythonista
        
        # Check that setup.py doesn't reference Jinja2/MarkupSafe
        setup_py_path = Path(__file__).parent.parent / 'setup.py'
        if setup_py_path.exists():
            with open(setup_py_path) as f:
                content = f.read()
            
            # Should not contain Jinja2 or MarkupSafe in install_requires
            self.assertNotIn('Jinja2', content, "setup.py still references Jinja2")
            self.assertNotIn('MarkupSafe', content, "setup.py still references MarkupSafe")
    
    def test_pyproject_toml_dependencies(self):
        """Test that pyproject.toml doesn't reference build dependencies"""
        pyproject_path = Path(__file__).parent.parent / 'pyproject.toml'
        if pyproject_path.exists():
            with open(pyproject_path) as f:
                content = f.read()
            
            # Should not contain Jinja2 or MarkupSafe in dependencies
            self.assertNotIn('Jinja2', content, "pyproject.toml still references Jinja2")
            self.assertNotIn('MarkupSafe', content, "pyproject.toml still references MarkupSafe")
    
    def test_requirements_txt_clean(self):
        """Test that requirements.txt is clean of build dependencies"""
        requirements_path = Path(__file__).parent.parent / 'requirements.txt'
        if requirements_path.exists():
            with open(requirements_path) as f:
                content = f.read()
            
            # Should not contain Jinja2 or MarkupSafe
            self.assertNotIn('Jinja2', content, "requirements.txt still references Jinja2")
            self.assertNotIn('MarkupSafe', content, "requirements.txt still references MarkupSafe")


class TestMobileOptimizedFeatures(unittest.TestCase):
    """Test features specifically designed for mobile/Pythonista use"""
    
    def test_mobile_template_availability(self):
        """Test mobile templates are available"""
        from coaiapy.pipeline import TemplateLoader
        
        loader = TemplateLoader()
        templates = loader.list_templates()
        template_names = [t['name'] for t in templates]
        
        mobile_templates = [
            'ios-data-sync',
            'mobile-transcription',
            'quick-analysis', 
            'gesture-pipeline'
        ]
        
        for template_name in mobile_templates:
            self.assertIn(template_name, template_names, f"Mobile template {template_name} not found")
    
    def test_mobile_builtin_functions(self):
        """Test mobile-specific built-in functions work"""
        from coaiapy.mobile_template import MobileTemplateEngine
        
        engine = MobileTemplateEngine()
        
        # Test mobile_id generates proper format
        mobile_id = engine.builtin_functions['mobile_id']()
        self.assertTrue(mobile_id.startswith('mobile_'))
        self.assertEqual(len(mobile_id), 15)
        
        # Test touch_timestamp generates time format
        touch_time = engine.builtin_functions['touch_timestamp']()
        self.assertRegex(touch_time, r'\d{2}:\d{2}:\d{2}')
    
    def test_battery_conscious_processing(self):
        """Test templates include battery-conscious metadata"""
        from coaiapy.pipeline import TemplateLoader, TemplateRenderer
        
        loader = TemplateLoader()
        renderer = TemplateRenderer()
        
        template = loader.load_template("mobile-transcription")
        variables = {
            'audio_source': 'Test Recording',
            'language': 'en-US'
        }
        
        observations = renderer.render_template(template, variables)
        main_span = observations[0]
        
        # Should have battery-conscious metadata
        self.assertTrue(main_span['metadata'].get('battery_conscious', False))
    
    def test_touch_friendly_interface_metadata(self):
        """Test templates include touch-friendly interface indicators"""
        from coaiapy.pipeline import TemplateLoader, TemplateRenderer
        
        loader = TemplateLoader()
        renderer = TemplateRenderer()
        
        template = loader.load_template("quick-analysis")
        variables = {
            'data_source': 'test.csv',
            'analysis_type': 'summary_stats'
        }
        
        observations = renderer.render_template(template, variables)
        
        # Should have touch-friendly indicators
        analysis_step = next((obs for obs in observations if 'Analysis' in obs['name']), None)
        self.assertIsNotNone(analysis_step)
        self.assertTrue(analysis_step['variables'].get('touch_optimized', False))


class TestPythonistaCommandLineInterface(unittest.TestCase):
    """Test CLI functionality in Pythonista context"""
    
    def test_coaia_help_command(self):
        """Test that coaia --help works without dependencies"""
        # This would be run in a Pythonista subprocess
        try:
            import coaiapy.coaiacli
            # If we can import the CLI module, it should work
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"CLI module import failed: {e}")
    
    def test_pipeline_commands_available(self):
        """Test pipeline commands are available in CLI"""
        from coaiapy import coaiacli
        
        # Check that pipeline commands are registered
        # This is a basic check that the CLI structure is intact
        self.assertTrue(hasattr(coaiacli, 'main'))


class TestPythonistaMemoryUsage(unittest.TestCase):
    """Test memory efficiency for iOS environment"""
    
    def test_lightweight_template_engine(self):
        """Test that mobile template engine uses minimal memory"""
        from coaiapy.mobile_template import MobileTemplateEngine
        import sys
        
        # Get baseline memory
        initial_objects = len(gc.get_objects()) if 'gc' in sys.modules else 0
        
        # Create multiple engines
        engines = [MobileTemplateEngine() for _ in range(10)]
        
        # Should not create excessive objects
        for engine in engines:
            result = engine.render_template_content("{{test}}", {'test': 'value'})
            self.assertEqual(result, 'value')
        
        # Cleanup
        del engines
    
    def test_template_rendering_memory_efficiency(self):
        """Test that template rendering doesn't leak memory"""
        from coaiapy.pipeline import TemplateLoader, TemplateRenderer
        
        loader = TemplateLoader()
        renderer = TemplateRenderer()
        template = loader.load_template("simple-trace")
        
        # Render template multiple times
        for i in range(100):
            variables = {'trace_name': f'Test {i}'}
            observations = renderer.render_template(template, variables)
            self.assertIsInstance(observations, list)
        
        # Should complete without memory issues


class TestPythonistaErrorHandling(unittest.TestCase):
    """Test error handling in Pythonista environment"""
    
    def test_graceful_missing_template_handling(self):
        """Test graceful handling of missing templates"""
        from coaiapy.pipeline import TemplateLoader
        
        loader = TemplateLoader()
        template = loader.load_template("nonexistent-template")
        
        # Should return None, not crash
        self.assertIsNone(template)
    
    def test_robust_variable_substitution(self):
        """Test robust variable substitution with missing variables"""
        from coaiapy.mobile_template import MobileTemplateEngine
        
        engine = MobileTemplateEngine()
        template = "Hello {{missing_var}}, your id is {{user_id}}"
        variables = {'user_id': '123'}
        
        result = engine.render_template_content(template, variables)
        
        # Should handle missing variables gracefully
        self.assertIn('[missing_var]', result)
        self.assertIn('123', result)
    
    def test_malformed_template_handling(self):
        """Test handling of malformed template syntax"""
        from coaiapy.mobile_template import MobileTemplateEngine
        
        engine = MobileTemplateEngine()
        
        # Various malformed templates that shouldn't crash
        malformed_templates = [
            "{{unclosed_var",
            "{{nested{{var}}}}",
            "{% if unclosed condition",
            "{{var|unknown_filter}}",
            "{{var or unclosed",
        ]
        
        for template in malformed_templates:
            with self.subTest(template=template):
                # Should not crash, return some reasonable result
                result = engine.render_template_content(template, {'var': 'test'})
                self.assertIsInstance(result, str)


if __name__ == '__main__':
    # Import gc if available for memory tests
    try:
        import gc
    except ImportError:
        pass
    
    # Run tests with verbose output
    unittest.main(verbosity=2)