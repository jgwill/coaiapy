"""
Mobile Workflow Integration Tests

Tests for complete mobile workflows and real-world usage scenarios
in Pythonista and mobile development environments.
"""

import unittest
import json
import tempfile
import os
from pathlib import Path
from coaiapy.pipeline import TemplateLoader, TemplateRenderer
from coaiapy.mobile_template import MobileTemplateEngine


class TestiOSDataSyncWorkflows(unittest.TestCase):
    """Test iOS data synchronization workflows"""
    
    def setUp(self):
        """Set up iOS data sync test fixtures"""
        self.loader = TemplateLoader()
        self.renderer = TemplateRenderer()
    
    def test_photo_backup_workflow(self):
        """Test complete photo backup to iCloud workflow"""
        template = self.loader.load_template("ios-data-sync")
        
        variables = {
            'sync_name': 'Daily Photo Backup',
            'cloud_service': 'iCloud',
            'data_type': 'photos'
        }
        
        observations = self.renderer.render_template(template, variables)
        
        # Verify workflow structure
        self.assertEqual(len(observations), 4)
        
        # Check main span
        main_span = observations[0]
        self.assertEqual(main_span['name'], 'Sync Preparation')
        self.assertEqual(main_span['type'], 'SPAN')
        self.assertIn('photos sync with iCloud', main_span['description'])
        
        # Verify mobile metadata
        self.assertTrue(main_span['metadata']['mobile_optimized'])
        self.assertIn('mobile_', main_span['variables']['device_id'])
        
        # Check authentication step
        auth_step = next((obs for obs in observations if 'Authentication' in obs['name']), None)
        self.assertIsNotNone(auth_step)
        self.assertEqual(auth_step['variables']['auth_method'], 'mobile_oauth')
        self.assertEqual(auth_step['metadata']['security_level'], 'mobile_secure')
        
        # Check upload step
        upload_step = next((obs for obs in observations if 'Upload' in obs['name']), None)
        self.assertIsNotNone(upload_step)
        self.assertEqual(upload_step['variables']['data_type'], 'photos')
        self.assertTrue(upload_step['metadata']['battery_efficient'])
    
    def test_document_sync_to_dropbox(self):
        """Test document synchronization to Dropbox"""
        template = self.loader.load_template("ios-data-sync")
        
        variables = {
            'sync_name': 'Work Documents',
            'cloud_service': 'Dropbox',
            'data_type': 'documents'
        }
        
        observations = self.renderer.render_template(template, variables)
        
        # Verify cloud service configuration
        auth_step = next((obs for obs in observations if 'Authentication' in obs['name']), None)
        self.assertEqual(auth_step['variables']['service'], 'Dropbox')
        
        upload_step = next((obs for obs in observations if 'Upload' in obs['name']), None)
        self.assertEqual(upload_step['variables']['destination'], 'Dropbox')
        
        completion_step = observations[-1]
        self.assertIn('Dropbox', completion_step['variables']['output'])


class TestMobileTranscriptionWorkflows(unittest.TestCase):
    """Test mobile audio transcription workflows"""
    
    def setUp(self):
        """Set up mobile transcription test fixtures"""
        self.loader = TemplateLoader()
        self.renderer = TemplateRenderer()
    
    def test_meeting_transcription_workflow(self):
        """Test complete meeting transcription workflow"""
        template = self.loader.load_template("mobile-transcription")
        
        variables = {
            'audio_source': 'Board Meeting',
            'recording_duration': '90 minutes',
            'language': 'en-US',
            'quality_preference': 'accurate',
            'user_id': 'exec_assistant'
        }
        
        observations = self.renderer.render_template(template, variables)
        
        # Verify workflow structure
        self.assertEqual(len(observations), 5)
        
        # Check main processing span
        main_span = observations[0]
        self.assertEqual(main_span['name'], 'Mobile Recording Processing')
        self.assertEqual(main_span['type'], 'SPAN')
        self.assertIn('Board Meeting', main_span['description'])
        self.assertTrue(main_span['metadata']['battery_conscious'])
        
        # Check preprocessing step
        preprocess_step = next((obs for obs in observations if 'Preprocessing' in obs['name']), None)
        self.assertIsNotNone(preprocess_step)
        self.assertTrue(preprocess_step['variables']['mobile_optimization'])
        
        # Check transcription step
        transcription_step = next((obs for obs in observations if 'Transcription' in obs['name']), None)
        self.assertIsNotNone(transcription_step)
        self.assertEqual(transcription_step['variables']['language'], 'en-US')
        self.assertEqual(transcription_step['variables']['quality'], 'accurate')
        
        # Check text processing with timestamps
        text_step = next((obs for obs in observations if 'Text Processing' in obs['name']), None)
        self.assertIsNotNone(text_step)
        self.assertEqual(text_step['variables']['timestamp_markers'], 'true')  # Duration not 'unknown'
        
        # Check mobile results
        results_step = observations[-1]
        self.assertEqual(results_step['variables']['user_id'], 'exec_assistant')
        self.assertTrue(results_step['variables']['mobile_formatted'])
    
    def test_voice_memo_transcription(self):
        """Test quick voice memo transcription"""
        template = self.loader.load_template("mobile-transcription")
        
        variables = {
            'audio_source': 'Voice Memo',
            'language': 'es-ES',
            'quality_preference': 'fast'
            # No recording_duration - should default to 'unknown'
        }
        
        observations = self.renderer.render_template(template, variables)
        
        # Check Spanish language processing
        transcription_step = next((obs for obs in observations if 'Transcription' in obs['name']), None)
        self.assertEqual(transcription_step['variables']['language'], 'es-ES')
        self.assertEqual(transcription_step['variables']['quality'], 'fast')
        
        # Check text processing without timestamps (duration is 'unknown')
        text_step = next((obs for obs in observations if 'Text Processing' in obs['name']), None)
        self.assertEqual(text_step['variables']['timestamp_markers'], '')  # Should be empty for 'unknown'


class TestQuickAnalysisWorkflows(unittest.TestCase):
    """Test quick data analysis workflows for mobile"""
    
    def setUp(self):
        """Set up quick analysis test fixtures"""
        self.loader = TemplateLoader()
        self.renderer = TemplateRenderer()
    
    def test_sales_data_analysis(self):
        """Test sales data analysis workflow"""
        template = self.loader.load_template("quick-analysis")
        
        variables = {
            'data_source': 'monthly_sales.csv',
            'analysis_type': 'trends',
            'output_format': 'charts',
            'complexity_level': 'intermediate',
            'analyst_id': 'sales_manager'
        }
        
        observations = self.renderer.render_template(template, variables)
        
        # Verify workflow structure
        self.assertEqual(len(observations), 5)
        
        # Check main data loading span
        main_span = observations[0]
        self.assertEqual(main_span['name'], 'Mobile Data Loading')
        self.assertIn('trends analysis on mobile device', main_span['description'])
        self.assertTrue(main_span['metadata']['battery_efficient'])
        
        # Check validation step
        validation_step = next((obs for obs in observations if 'Validation' in obs['name']), None)
        self.assertIsNotNone(validation_step)
        self.assertEqual(validation_step['variables']['validation_type'], 'mobile_quick_check')
        
        # Check analysis step with filter
        analysis_step = next((obs for obs in observations if 'Analysis' in obs['name']), None)
        self.assertIsNotNone(analysis_step)
        self.assertEqual(analysis_step['name'], 'Trends Analysis')  # |title filter applied
        self.assertEqual(analysis_step['variables']['complexity'], 'intermediate')
        self.assertTrue(analysis_step['variables']['touch_optimized'])
        
        # Check mobile formatting
        format_step = next((obs for obs in observations if 'Formatting' in obs['name']), None)
        self.assertIsNotNone(format_step)
        self.assertEqual(format_step['variables']['format_type'], 'charts')
        self.assertTrue(format_step['variables']['screen_size_optimized'])
        
        # Check completion
        completion_step = observations[-1]
        self.assertEqual(completion_step['variables']['analyst_id'], 'sales_manager')
        self.assertTrue(completion_step['variables']['shareable'])
    
    def test_simple_stats_analysis(self):
        """Test simple statistics analysis for quick insights"""
        template = self.loader.load_template("quick-analysis")
        
        variables = {
            'data_source': 'survey_responses.json',
            'analysis_type': 'summary_stats',
            'output_format': 'text_summary',
            'complexity_level': 'simple'
        }
        
        observations = self.renderer.render_template(template, variables)
        
        # Check analysis step
        analysis_step = next((obs for obs in observations if 'Analysis' in obs['name']), None)
        self.assertEqual(analysis_step['name'], 'Summary_Stats Analysis')  # |title filter
        self.assertEqual(analysis_step['variables']['complexity'], 'simple')
        
        # Check output format
        format_step = next((obs for obs in observations if 'Formatting' in obs['name']), None)
        self.assertEqual(format_step['variables']['format_type'], 'text_summary')


class TestGesturePipelineWorkflows(unittest.TestCase):
    """Test gesture-triggered workflow scenarios"""
    
    def setUp(self):
        """Set up gesture pipeline test fixtures"""
        self.loader = TemplateLoader()
        self.renderer = TemplateRenderer()
    
    def test_tap_gesture_workflow(self):
        """Test simple tap gesture workflow"""
        template = self.loader.load_template("gesture-pipeline")
        
        variables = {
            'gesture_type': 'tap',
            'workflow_name': 'Quick Analysis',
            'app_context': 'Pythonista',
            'gesture_data': 'single_tap_center',
            'user_session': 'mobile_session_123'
        }
        
        observations = self.renderer.render_template(template, variables)
        
        # Verify workflow structure
        self.assertEqual(len(observations), 5)
        
        # Check gesture recognition
        main_span = observations[0]
        self.assertEqual(main_span['name'], 'Gesture Recognition')
        self.assertIn('tap gesture for Quick Analysis', main_span['description'])
        self.assertTrue(main_span['metadata']['touch_responsive'])
        
        # Check context analysis
        context_step = next((obs for obs in observations if 'Context' in obs['name']), None)
        self.assertIsNotNone(context_step)
        self.assertEqual(context_step['variables']['app_state'], 'Pythonista')
        self.assertEqual(context_step['variables']['gesture_interpretation'], 'tap_in_Pythonista')
        
        # Check workflow trigger
        trigger_step = next((obs for obs in observations if 'Trigger' in obs['name']), None)
        self.assertIsNotNone(trigger_step)
        self.assertEqual(trigger_step['variables']['workflow'], 'Quick Analysis')
        self.assertTrue(trigger_step['variables']['immediate_response'])
        
        # Check visual feedback (not haptic for tap)
        feedback_step = next((obs for obs in observations if 'Feedback' in obs['name']), None)
        self.assertIsNotNone(feedback_step)
        self.assertEqual(feedback_step['name'], 'Visual Feedback')
        self.assertEqual(feedback_step['variables']['feedback_type'], 'visual_highlight')
        
        # Check completion
        completion_step = observations[-1]
        self.assertEqual(completion_step['variables']['user_session'], 'mobile_session_123')
    
    def test_long_press_gesture_workflow(self):
        """Test long press gesture with haptic feedback"""
        template = self.loader.load_template("gesture-pipeline")
        
        variables = {
            'gesture_type': 'long_press',
            'workflow_name': 'Context Menu',
            'app_context': 'Files',
            'user_session': 'file_browser_session'
        }
        
        observations = self.renderer.render_template(template, variables)
        
        # Check haptic feedback for long_press
        feedback_step = next((obs for obs in observations if 'Feedback' in obs['name']), None)
        self.assertIsNotNone(feedback_step)
        self.assertEqual(feedback_step['name'], 'Haptic Feedback')
        self.assertEqual(feedback_step['variables']['feedback_type'], 'haptic_vibration')
        
        # Check Files app context
        context_step = next((obs for obs in observations if 'Context' in obs['name']), None)
        self.assertEqual(context_step['variables']['app_state'], 'Files')
    
    def test_swipe_gesture_workflow(self):
        """Test swipe gesture workflow"""
        template = self.loader.load_template("gesture-pipeline")
        
        variables = {
            'gesture_type': 'swipe_right',
            'workflow_name': 'Navigate Back',
            'app_context': 'Safari',
            'gesture_data': 'velocity_high_x200'
        }
        
        observations = self.renderer.render_template(template, variables)
        
        # Check gesture data processing
        main_span = observations[0]
        self.assertEqual(main_span['variables']['gesture_details'], 'velocity_high_x200')
        
        # Check Safari context
        context_step = next((obs for obs in observations if 'Context' in obs['name']), None)
        self.assertEqual(context_step['variables']['app_state'], 'Safari')
        self.assertEqual(context_step['variables']['gesture_interpretation'], 'swipe_right_in_Safari')


class TestMobileWorkflowIntegration(unittest.TestCase):
    """Test integration between different mobile workflows"""
    
    def setUp(self):
        """Set up integration test fixtures"""
        self.loader = TemplateLoader()
        self.renderer = TemplateRenderer()
    
    def test_workflow_chaining_scenario(self):
        """Test scenario where workflows are chained together"""
        # Step 1: Gesture triggers data analysis
        gesture_template = self.loader.load_template("gesture-pipeline")
        gesture_vars = {
            'gesture_type': 'double_tap',
            'workflow_name': 'Data Analysis',
            'app_context': 'Pythonista'
        }
        gesture_obs = self.renderer.render_template(gesture_template, gesture_vars)
        
        # Step 2: Quick analysis is performed
        analysis_template = self.loader.load_template("quick-analysis")
        analysis_vars = {
            'data_source': 'user_data.csv',
            'analysis_type': 'correlations',
            'output_format': 'mobile_friendly'
        }
        analysis_obs = self.renderer.render_template(analysis_template, analysis_vars)
        
        # Step 3: Results are synced to cloud
        sync_template = self.loader.load_template("ios-data-sync")
        sync_vars = {
            'sync_name': 'Analysis Results',
            'cloud_service': 'Google Drive',
            'data_type': 'json_data'
        }
        sync_obs = self.renderer.render_template(sync_template, sync_vars)
        
        # Verify all workflows completed successfully
        self.assertGreater(len(gesture_obs), 0)
        self.assertGreater(len(analysis_obs), 0)
        self.assertGreater(len(sync_obs), 0)
        
        # Verify workflow progression
        self.assertIn('Data Analysis', gesture_obs[-1]['variables']['output'])
        self.assertIn('Correlations Analysis', [obs['name'] for obs in analysis_obs])
        self.assertIn('Analysis Results', sync_obs[-1]['variables']['output'])
    
    def test_mobile_metadata_consistency(self):
        """Test that mobile metadata is consistent across templates"""
        mobile_templates = ['ios-data-sync', 'mobile-transcription', 'quick-analysis', 'gesture-pipeline']
        
        for template_name in mobile_templates:
            with self.subTest(template=template_name):
                template = self.loader.load_template(template_name)
                
                # Use appropriate variables for each template
                test_vars = {
                    'sync_name': 'Test', 'cloud_service': 'iCloud', 'data_type': 'photos',
                    'audio_source': 'Test', 'language': 'en-US',
                    'data_source': 'test.csv', 'analysis_type': 'trends',
                    'gesture_type': 'tap', 'workflow_name': 'Test', 'app_context': 'Pythonista'
                }
                
                observations = self.renderer.render_template(template, test_vars)
                main_span = observations[0]
                
                # All mobile templates should have mobile-optimized metadata
                metadata = main_span['metadata']
                mobile_indicators = [
                    'mobile_optimized', 'battery_conscious', 'battery_efficient',
                    'touch_responsive', 'mobile_interaction'
                ]
                
                has_mobile_indicator = any(indicator in metadata for indicator in mobile_indicators)
                self.assertTrue(has_mobile_indicator, 
                              f"{template_name} missing mobile optimization indicators")


class TestRealWorldMobileScenarios(unittest.TestCase):
    """Test real-world mobile usage scenarios"""
    
    def setUp(self):
        """Set up real-world scenario fixtures"""
        self.loader = TemplateLoader()
        self.renderer = TemplateRenderer()
    
    def test_field_research_workflow(self):
        """Test field research data collection and processing"""
        # Scenario: Researcher in the field using iPhone
        
        # 1. Record interview
        transcription_vars = {
            'audio_source': 'Field Interview',
            'recording_duration': '45 minutes',
            'language': 'en-US',
            'quality_preference': 'balanced',  # Balance between quality and battery
            'user_id': 'field_researcher'
        }
        
        transcription_template = self.loader.load_template("mobile-transcription")
        transcription_obs = self.renderer.render_template(transcription_template, transcription_vars)
        
        # 2. Quick analysis of transcribed data
        analysis_vars = {
            'data_source': 'interview_transcript.txt',
            'analysis_type': 'summary_stats',
            'output_format': 'mobile_friendly',
            'complexity_level': 'simple',  # Simple for mobile context
            'analyst_id': 'field_researcher'
        }
        
        analysis_template = self.loader.load_template("quick-analysis")
        analysis_obs = self.renderer.render_template(analysis_template, analysis_vars)
        
        # 3. Sync to cloud for team access
        sync_vars = {
            'sync_name': 'Field Research Data',
            'cloud_service': 'OneDrive',
            'data_type': 'documents'
        }
        
        sync_template = self.loader.load_template("ios-data-sync")
        sync_obs = self.renderer.render_template(sync_template, sync_vars)
        
        # Verify complete workflow
        self.assertTrue(transcription_obs[0]['metadata']['battery_conscious'])
        self.assertTrue(analysis_obs[0]['metadata']['battery_efficient'])
        self.assertTrue(sync_obs[0]['metadata']['mobile_optimized'])
        
        # Check field-appropriate settings
        transcription_main = transcription_obs[0]
        self.assertEqual(transcription_main['variables']['device_type'], 'mobile')
        
        analysis_main = analysis_obs[0]
        self.assertEqual(analysis_main['variables']['mobile_context'], True)
        
    def test_business_mobile_workflow(self):
        """Test business user mobile workflow"""
        # Scenario: Business executive using iPad for presentations
        
        # 1. Gesture-triggered data analysis
        gesture_vars = {
            'gesture_type': 'pinch',
            'workflow_name': 'Sales Dashboard',
            'app_context': 'Pythonista',
            'gesture_data': 'zoom_in_gesture'
        }
        
        gesture_template = self.loader.load_template("gesture-pipeline")
        gesture_obs = self.renderer.render_template(gesture_template, gesture_vars)
        
        # 2. Detailed sales analysis
        analysis_vars = {
            'data_source': 'quarterly_sales.xlsx',
            'analysis_type': 'trends',
            'output_format': 'charts',
            'complexity_level': 'detailed',
            'analyst_id': 'sales_executive'
        }
        
        analysis_template = self.loader.load_template("quick-analysis")
        analysis_obs = self.renderer.render_template(analysis_template, analysis_vars)
        
        # Verify business-appropriate configurations
        gesture_completion = gesture_obs[-1]
        self.assertIn('Sales Dashboard', gesture_completion['variables']['output'])
        
        analysis_format = next((obs for obs in analysis_obs if 'Formatting' in obs['name']), None)
        self.assertEqual(analysis_format['variables']['format_type'], 'charts')
        self.assertTrue(analysis_format['variables']['screen_size_optimized'])


if __name__ == '__main__':
    print("Running Mobile Workflow Integration Tests...")
    print("=" * 60)
    
    # Run tests with verbose output
    unittest.main(verbosity=2, buffer=True)