"""
Test Suite for Pipeline Template Rendering

Tests for pipeline template creation, rendering, and mobile-optimized workflows.
"""

import unittest
import json
import uuid
import re
from pathlib import Path
from coaiapy.pipeline import TemplateLoader, TemplateRenderer, PipelineTemplate


class TestPipelineTemplateRendering(unittest.TestCase):
    """Test pipeline template rendering functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.renderer = TemplateRenderer()
        self.loader = TemplateLoader()
    
    def test_simple_trace_template_rendering(self):
        """Test rendering of simple-trace template"""
        template = self.loader.load_template("simple-trace")
        self.assertIsNotNone(template)
        
        variables = {
            'trace_name': 'Test Trace',
            'user_id': 'test_user',
            'observation_name': 'Custom Task'
        }
        
        observations = self.renderer.render_template(template, variables)
        
        self.assertEqual(len(observations), 1)
        obs = observations[0]
        
        self.assertEqual(obs['name'], 'Custom Task')
        self.assertEqual(obs['description'], 'Main task observation for Test Trace')
        self.assertEqual(obs['metadata']['created_by'], 'test_user')
    
    def test_ios_data_sync_template_rendering(self):
        """Test rendering of mobile ios-data-sync template"""
        template = self.loader.load_template("ios-data-sync")
        self.assertIsNotNone(template)
        
        variables = {
            'sync_name': 'Photo Backup',
            'cloud_service': 'iCloud',
            'data_type': 'photos'
        }
        
        observations = self.renderer.render_template(template, variables)
        
        self.assertEqual(len(observations), 4)  # 4 steps in ios-data-sync
        
        # Check main span
        main_span = observations[0]
        self.assertEqual(main_span['name'], 'Sync Preparation')
        self.assertEqual(main_span['type'], 'SPAN')
        self.assertIn('photos sync with iCloud', main_span['description'])
        
        # Check parent-child relationships
        child_steps = [obs for obs in observations[1:] if obs.get('parent')]
        self.assertEqual(len(child_steps), 3)
        
        for child in child_steps:
            self.assertEqual(child['parent'], 'Sync Preparation')
    
    def test_mobile_transcription_template_rendering(self):
        """Test rendering of mobile-transcription template"""
        template = self.loader.load_template("mobile-transcription")
        self.assertIsNotNone(template)
        
        variables = {
            'audio_source': 'Meeting Recording',
            'language': 'en-US',
            'quality_preference': 'accurate',
            'recording_duration': '45 minutes'
        }
        
        observations = self.renderer.render_template(template, variables)
        
        self.assertEqual(len(observations), 5)  # 5 steps in mobile-transcription
        
        # Check conditional rendering based on recording_duration
        text_processing = next((obs for obs in observations if 'Text Processing' in obs['name']), None)
        self.assertIsNotNone(text_processing)
        
        # timestamp_markers should be true when duration is not 'unknown'
        self.assertEqual(text_processing['variables']['timestamp_markers'], 'true')
    
    def test_gesture_pipeline_template_rendering(self):
        """Test rendering of gesture-pipeline template"""
        template = self.loader.load_template("gesture-pipeline")
        self.assertIsNotNone(template)
        
        variables = {
            'gesture_type': 'long_press',
            'workflow_name': 'Quick Analysis',
            'app_context': 'Pythonista',
            'user_session': 'test_session_123'
        }
        
        observations = self.renderer.render_template(template, variables)
        
        self.assertEqual(len(observations), 5)  # 5 steps in gesture-pipeline
        
        # Check conditional feedback step for long_press
        feedback_step = next((obs for obs in observations if 'Feedback' in obs['name']), None)
        self.assertIsNotNone(feedback_step)
        self.assertEqual(feedback_step['name'], 'Haptic Feedback')  # Should be haptic for long_press
        self.assertEqual(feedback_step['variables']['feedback_type'], 'haptic_vibration')
    
    def test_quick_analysis_template_with_filters(self):
        """Test quick-analysis template with title filter"""
        template = self.loader.load_template("quick-analysis")
        self.assertIsNotNone(template)
        
        variables = {
            'data_source': 'sales.csv',
            'analysis_type': 'trends',
            'output_format': 'charts',
            'complexity_level': 'detailed'
        }
        
        observations = self.renderer.render_template(template, variables)
        
        # Find the analysis step that uses |title filter
        analysis_step = next((obs for obs in observations if 'Analysis' in obs['name']), None)
        self.assertIsNotNone(analysis_step)
        self.assertEqual(analysis_step['name'], 'Trends Analysis')  # Should be title-cased
    
    def test_template_variable_validation(self):
        """Test template variable validation"""
        template = self.loader.load_template("simple-trace")
        
        # Test missing required variable
        with self.assertRaises(ValueError) as context:
            self.renderer.render_template(template, {})  # Missing trace_name
        
        self.assertIn("validation failed", str(context.exception).lower())
    
    def test_mobile_builtin_functions_in_templates(self):
        """Test mobile built-in functions work in template rendering"""
        template = self.loader.load_template("ios-data-sync")
        
        variables = {
            'sync_name': 'Test Sync',
            'cloud_service': 'Dropbox',
            'data_type': 'documents'
            # Note: device_id defaults to {{mobile_id()}}
        }
        
        observations = self.renderer.render_template(template, variables)
        
        # Check that mobile_id() was processed
        completion_step = observations[-1]  # Last step is sync completion
        device_id = completion_step['variables']['device_id']
        
        # Should start with 'mobile_' and be 15 characters
        self.assertTrue(device_id.startswith('mobile_'))
        self.assertEqual(len(device_id), 15)
    
    def test_metadata_enrichment(self):
        """Test mobile template metadata is properly set"""
        template = self.loader.load_template("mobile-transcription")
        
        variables = {
            'audio_source': 'Voice Memo',
            'language': 'en-US',
            'quality_preference': 'balanced'
        }
        
        observations = self.renderer.render_template(template, variables)
        
        # Check main span has mobile metadata
        main_span = observations[0]
        metadata = main_span['metadata']
        
        self.assertEqual(metadata['template'], 'mobile-transcription')
        self.assertEqual(metadata['mobile_optimized'], True)
        self.assertEqual(metadata['battery_conscious'], True)
        
        # Check timestamps are properly formatted
        self.assertIn('processing_start', metadata)
        self.assertTrue(metadata['processing_start'].endswith('Z'))


class TestTemplateLoader(unittest.TestCase):
    """Test template loading functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.loader = TemplateLoader()
    
    def test_load_builtin_templates(self):
        """Test loading all built-in templates"""
        builtin_templates = [
            'simple-trace',
            'data-pipeline', 
            'llm-chain',
            'parallel-processing',
            'error-handling',
            'judge-evaluation',
            'judge-ensemble',
            # Mobile templates
            'ios-data-sync',
            'mobile-transcription',
            'quick-analysis',
            'gesture-pipeline'
        ]
        
        for template_name in builtin_templates:
            with self.subTest(template=template_name):
                template = self.loader.load_template(template_name)
                self.assertIsNotNone(template)
                self.assertIsInstance(template, PipelineTemplate)
                self.assertEqual(template.name, template_name)
    
    def test_template_list_includes_mobile(self):
        """Test that template list includes mobile templates"""
        templates = self.loader.list_templates()
        template_names = [t['name'] for t in templates]
        
        mobile_templates = ['ios-data-sync', 'mobile-transcription', 'quick-analysis', 'gesture-pipeline']
        
        for mobile_template in mobile_templates:
            self.assertIn(mobile_template, template_names)
    
    def test_mobile_template_metadata(self):
        """Test mobile templates have correct metadata"""
        mobile_templates = ['ios-data-sync', 'mobile-transcription', 'quick-analysis', 'gesture-pipeline']
        
        for template_name in mobile_templates:
            with self.subTest(template=template_name):
                template = self.loader.load_template(template_name)
                self.assertEqual(template.author, 'CoaiaPy Mobile')
                self.assertIn('mobile', template.description.lower())
    
    def test_nonexistent_template(self):
        """Test loading non-existent template returns None"""
        template = self.loader.load_template("nonexistent-template")
        self.assertIsNone(template)


class TestMobileTemplateFeatures(unittest.TestCase):
    """Test mobile-specific template features"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.renderer = TemplateRenderer()
        self.loader = TemplateLoader()
    
    def test_touch_timestamp_in_templates(self):
        """Test touch_timestamp() function works in templates"""
        template = self.loader.load_template("ios-data-sync")
        
        variables = {
            'sync_name': 'Test Sync',
            'cloud_service': 'iCloud'
        }
        
        observations = self.renderer.render_template(template, variables)
        
        # Find metadata with touch_timestamp
        main_span = observations[0]
        sync_timestamp = main_span['metadata']['sync_timestamp']
        
        # Should be HH:MM:SS format
        time_pattern = r'\d{2}:\d{2}:\d{2}'
        self.assertIsNotNone(re.match(time_pattern, sync_timestamp))
    
    def test_battery_efficient_flags(self):
        """Test battery-efficient processing flags in mobile templates"""
        mobile_templates = ['ios-data-sync', 'mobile-transcription', 'quick-analysis']
        
        for template_name in mobile_templates:
            with self.subTest(template=template_name):
                template = self.loader.load_template(template_name)
                variables = {
                    'sync_name': 'Test',
                    'audio_source': 'Test Audio',
                    'data_source': 'test.csv'
                }
                
                observations = self.renderer.render_template(template, variables)
                
                # Check for battery efficiency indicators
                main_span = observations[0]
                metadata = main_span['metadata']
                
                battery_flags = ['battery_efficient', 'battery_conscious', 'mobile_optimized']
                has_battery_flag = any(flag in metadata for flag in battery_flags)
                self.assertTrue(has_battery_flag, f"No battery efficiency flag found in {template_name}")
    
    def test_mobile_network_awareness(self):
        """Test mobile network awareness in templates"""
        template = self.loader.load_template("ios-data-sync")
        
        variables = {
            'sync_name': 'Network Test',
            'cloud_service': 'Google Drive',
            'data_type': 'audio'
        }
        
        observations = self.renderer.render_template(template, variables)
        
        # Find data upload step
        upload_step = next((obs for obs in observations if 'Upload' in obs['name']), None)
        self.assertIsNotNone(upload_step)
        
        # Should have mobile network metadata
        self.assertEqual(upload_step['metadata']['mobile_network'], 'cellular_or_wifi')
    
    def test_ios_integration_metadata(self):
        """Test iOS-specific integration metadata"""
        template = self.loader.load_template("gesture-pipeline")
        
        variables = {
            'gesture_type': 'tap',
            'workflow_name': 'Quick Action',
            'app_context': 'Shortcuts'
        }
        
        observations = self.renderer.render_template(template, variables)
        
        # Check for iOS-specific metadata
        context_step = next((obs for obs in observations if 'Context' in obs['name']), None)
        self.assertIsNotNone(context_step)
        self.assertEqual(context_step['metadata']['ios_native_integration'], True)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)