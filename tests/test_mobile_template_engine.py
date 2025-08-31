"""
Test Suite for Mobile Template Engine

Comprehensive tests for the pure-Python template engine that replaces Jinja2
for Pythonista compatibility.
"""

import unittest
import uuid
import re
from datetime import datetime
from coaiapy.mobile_template import MobileTemplateEngine, MobileEnvironment, MobileTemplate


class TestMobileTemplateEngine(unittest.TestCase):
    """Test the core MobileTemplateEngine functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.engine = MobileTemplateEngine()
        self.test_vars = {
            'user_name': 'JohnDoe',
            'project_id': '12345',
            'environment': 'production',
            'debug_mode': True,
            'count': 42,
            'empty_value': '',
            'none_value': None
        }
    
    def test_simple_variable_substitution(self):
        """Test basic {{variable}} substitution"""
        template = "Hello {{user_name}}, your project is {{project_id}}"
        result = self.engine.render_template_content(template, self.test_vars)
        self.assertEqual(result, "Hello JohnDoe, your project is 12345")
    
    def test_missing_variable_handling(self):
        """Test handling of missing variables"""
        template = "Hello {{missing_var}}, your project is {{project_id}}"
        result = self.engine.render_template_content(template, self.test_vars)
        self.assertEqual(result, "Hello [missing_var], your project is 12345")
    
    def test_variable_with_or_fallback(self):
        """Test 'variable or default' expressions"""
        template = "Status: {{status or 'unknown'}}, Debug: {{debug_mode or 'false'}}"
        result = self.engine.render_template_content(template, self.test_vars)
        self.assertEqual(result, "Status: unknown, Debug: True")
    
    def test_builtin_functions(self):
        """Test built-in mobile functions"""
        template = "ID: {{uuid4()}}, Time: {{now()}}, Mobile: {{mobile_id()}}"
        result = self.engine.render_template_content(template, {})
        
        # Check UUID format
        uuid_match = re.search(r'ID: ([a-f0-9-]{36})', result)
        self.assertIsNotNone(uuid_match)
        
        # Check timestamp format
        time_match = re.search(r'Time: (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z)', result)
        self.assertIsNotNone(time_match)
        
        # Check mobile ID format
        mobile_match = re.search(r'Mobile: (mobile_[a-f0-9]{8})', result)
        self.assertIsNotNone(mobile_match)
    
    def test_filters(self):
        """Test variable filters like |title, |upper, |lower"""
        template = "Title: {{user_name|title}}, Upper: {{environment|upper}}, Lower: {{user_name|lower}}"
        result = self.engine.render_template_content(template, self.test_vars)
        self.assertEqual(result, "Title: Johndoe, Upper: PRODUCTION, Lower: johndoe")
    
    def test_conditionals_simple(self):
        """Test simple conditional blocks"""
        template = "{% if debug_mode %}Debug is enabled{% endif %}"
        result = self.engine.render_template_content(template, self.test_vars)
        self.assertEqual(result, "Debug is enabled")
        
        template = "{% if not debug_mode %}Debug is disabled{% endif %}"
        result = self.engine.render_template_content(template, self.test_vars)
        self.assertEqual(result, "")
    
    def test_conditionals_equality(self):
        """Test conditional equality comparisons"""
        template = '{% if environment == "production" %}PROD MODE{% endif %}'
        result = self.engine.render_template_content(template, self.test_vars)
        self.assertEqual(result, "PROD MODE")
        
        template = '{% if environment != "development" %}NOT DEV{% endif %}'
        result = self.engine.render_template_content(template, self.test_vars)
        self.assertEqual(result, "NOT DEV")
    
    def test_truthiness_evaluation(self):
        """Test mobile-friendly truthiness evaluation"""
        test_cases = [
            ({'value': True}, True),
            ({'value': False}, False),
            ({'value': 1}, True),
            ({'value': 0}, False),
            ({'value': 'yes'}, True),
            ({'value': 'false'}, False),
            ({'value': 'off'}, False),
            ({'value': 'disabled'}, False),
            ({'value': ''}, False),
            ({'value': None}, False),
            ({'value': []}, False),
        ]
        
        for variables, expected in test_cases:
            result = self.engine._is_truthy(variables.get('value'))
            self.assertEqual(result, expected, f"Failed for value: {variables.get('value')}")
    
    def test_recursive_dict_rendering(self):
        """Test recursive rendering of dictionary structures"""
        data = {
            'user': {
                'name': '{{user_name}}',
                'project': '{{project_id}}',
                'settings': {
                    'env': '{{environment}}',
                    'debug': '{{debug_mode}}'
                }
            }
        }
        
        result = self.engine.render_dict(data, self.test_vars)
        expected = {
            'user': {
                'name': 'JohnDoe',
                'project': '12345',
                'settings': {
                    'env': 'production',
                    'debug': 'True'
                }
            }
        }
        
        self.assertEqual(result, expected)
    
    def test_recursive_list_rendering(self):
        """Test recursive rendering of list structures"""
        data = ['{{user_name}}', '{{project_id}}', {'env': '{{environment}}'}]
        result = self.engine.render_list(data, self.test_vars)
        expected = ['JohnDoe', '12345', {'env': 'production'}]
        
        self.assertEqual(result, expected)


class TestMobileEnvironmentCompatibility(unittest.TestCase):
    """Test Jinja2 API compatibility layer"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.env = MobileEnvironment()
    
    def test_from_string_api(self):
        """Test Jinja2 from_string API compatibility"""
        template = self.env.from_string("Hello {{name}}")
        result = template.render(name="World")
        self.assertEqual(result, "Hello World")
    
    def test_globals_integration(self):
        """Test built-in globals are available"""
        template = self.env.from_string("UUID: {{uuid4()}}")
        result = template.render()
        
        # Check UUID is generated
        uuid_pattern = r'UUID: [a-f0-9-]{36}'
        self.assertIsNotNone(re.match(uuid_pattern, result))
    
    def test_template_object_api(self):
        """Test MobileTemplate object API compatibility"""
        template_obj = MobileTemplate("{{message}}", self.env.engine)
        result = template_obj.render(message="Test Message")
        self.assertEqual(result, "Test Message")


class TestPythonistaSpecificFeatures(unittest.TestCase):
    """Test features specifically designed for Pythonista/mobile use"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.engine = MobileTemplateEngine()
    
    def test_mobile_id_format(self):
        """Test mobile_id() generates proper format"""
        result = self.engine.builtin_functions['mobile_id']()
        self.assertTrue(result.startswith('mobile_'))
        self.assertEqual(len(result), 15)  # 'mobile_' + 8 hex chars
    
    def test_touch_timestamp_format(self):
        """Test touch_timestamp() generates local time format"""
        result = self.engine.builtin_functions['touch_timestamp']()
        # Should be HH:MM:SS format
        time_pattern = r'\d{2}:\d{2}:\d{2}'
        self.assertIsNotNone(re.match(time_pattern, result))
    
    def test_mobile_friendly_error_handling(self):
        """Test mobile-friendly error messages"""
        template = "{{missing_var}} and {{another_missing}}"
        result = self.engine.render_template_content(template, {})
        self.assertEqual(result, "[missing_var] and [another_missing]")
    
    def test_battery_conscious_processing(self):
        """Test that processing doesn't use excessive resources"""
        # Large template with many variables
        large_template = " ".join([f"{{{{var{i}}}}}" for i in range(100)])
        variables = {f'var{i}': f'value{i}' for i in range(100)}
        
        # Should complete without issues
        result = self.engine.render_template_content(large_template, variables)
        expected = " ".join([f'value{i}' for i in range(100)])
        self.assertEqual(result, expected)


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.engine = MobileTemplateEngine()
    
    def test_empty_template(self):
        """Test handling of empty templates"""
        result = self.engine.render_template_content("", {})
        self.assertEqual(result, "")
    
    def test_none_template(self):
        """Test handling of None template"""
        result = self.engine.render_string(None, {})
        self.assertEqual(result, "")
    
    def test_malformed_conditionals(self):
        """Test handling of malformed conditional syntax"""
        template = "{% if malformed condition %}content{% endif %}"
        result = self.engine.render_template_content(template, {})
        # Should not crash, may return empty or original
        self.assertIsInstance(result, str)
    
    def test_unknown_filter(self):
        """Test handling of unknown filters"""
        template = "{{value|unknown_filter}}"
        result = self.engine.render_template_content(template, {'value': 'test'})
        self.assertEqual(result, "test")  # Should return original value
    
    def test_nested_template_syntax(self):
        """Test complex nested template syntax"""
        template = "{{user_name|title}} - {% if environment == 'prod' %}{{project_id|upper}}{% endif %}"
        variables = {'user_name': 'john', 'environment': 'prod', 'project_id': 'app'}
        result = self.engine.render_template_content(template, variables)
        self.assertEqual(result, "John - APP")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)