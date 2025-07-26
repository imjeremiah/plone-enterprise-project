"""
Phase 3 Integration Tests - Feature Synergies & Integration Points

Tests that verify all classroom management features work together seamlessly:
- Timer state persistence across page refreshes
- Dashboard aggregates data from all features
- Substitute folder includes current seating charts
- Hall pass alerts appear on dashboard
- Cross-feature data integrity and performance
"""

import unittest
import json
import time
from datetime import datetime, timedelta
from plone.app.testing import PLONE_INTEGRATION_TESTING
from plone.testing import z2
from plone import api
from zope.annotation.interfaces import IAnnotations
from project.title.testing import PROJECT_TITLE_INTEGRATION_TESTING


class TestFeatureIntegration(unittest.TestCase):
    """Integration tests for Phase 3 feature synergies"""
    
    layer = PROJECT_TITLE_INTEGRATION_TESTING
    
    def setUp(self):
        """Set up test environment with sample data"""
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        
        # Create test seating chart
        self.seating_chart = api.content.create(
            container=self.portal,
            type='SeatingChart',
            id='test-seating-chart',
            title='Test Classroom Layout',
            students=['Alice', 'Bob', 'Charlie', 'Diana', 'Eve']
        )
        
        # Create test hall pass
        self.hall_pass = api.content.create(
            container=self.portal,
            type='HallPass',
            id='test-hall-pass',
            title='Test Hall Pass'
        )
        
        # Set up participation data
        portal_annotations = IAnnotations(self.portal)
        today_key = f"participation_{datetime.now().date()}"
        portal_annotations[today_key] = {
            'Alice': 3,
            'Bob': 2,
            'Charlie': 1,
            'Diana': 4,
            'Eve': 1
        }
    
    def test_dashboard_aggregates_all_features(self):
        """Test that dashboard successfully pulls data from all features"""
        # Get dashboard view
        dashboard_view = self.portal.restrictedTraverse('@@teacher-dashboard')
        
        # Test AJAX data endpoint
        self.request['ajax_update'] = '1'
        response_data = dashboard_view()
        data = json.loads(response_data)
        
        # Verify all feature data is present
        self.assertIn('seating', data)
        self.assertIn('hall_passes', data)
        self.assertIn('participation', data)
        self.assertIn('alerts', data)
        self.assertIn('quick_stats', data)
        self.assertIn('system_status', data)
        
        # Verify seating data includes our test chart
        seating_data = data['seating']
        self.assertEqual(seating_data['status'], 'active')
        self.assertEqual(seating_data['current_chart']['title'], 'Test Classroom Layout')
        self.assertEqual(seating_data['current_chart']['student_count'], 5)
        
        # Verify participation data is aggregated
        participation_data = data['participation']
        self.assertEqual(participation_data['status'], 'active')
        self.assertEqual(participation_data['total_picks'], 11)  # 3+2+1+4+1
        self.assertEqual(participation_data['unique_students'], 5)
        
        # Verify system status shows available features
        system_status = data['system_status']
        self.assertTrue(system_status['features_available']['seating_charts'])
        self.assertTrue(system_status['features_available']['hall_passes'])
        self.assertTrue(system_status['features_available']['random_picker'])
        self.assertTrue(system_status['features_available']['timer'])
        self.assertTrue(system_status['features_available']['substitute_folder'])
    
    def test_substitute_folder_includes_seating_charts(self):
        """Test that substitute folder generator includes current seating charts"""
        # Get substitute folder view
        sub_folder_view = self.portal.restrictedTraverse('@@substitute-folder-info')
        
        # Test POST request for generation
        self.request.method = 'POST'
        self.request.form['notes'] = 'Test integration notes'
        
        response_data = sub_folder_view()
        data = json.loads(response_data)
        
        # Verify generation succeeded
        self.assertTrue(data['success'])
        self.assertIn('sections_data', data)
        
        # Verify seating chart section is included
        sections = data['sections_data']
        self.assertIn('Seating Charts', sections)
        
        # Verify seating chart content includes our test chart
        seating_content = sections['Seating Charts']
        self.assertIn('Test Classroom Layout', seating_content)
        self.assertIn('Alice', seating_content)
        self.assertIn('Bob', seating_content)
    
    def test_hall_pass_alerts_on_dashboard(self):
        """Test that hall pass duration alerts appear on dashboard"""
        # Create a hall pass with extended duration
        old_time = datetime.now() - timedelta(minutes=25)  # 25 minutes ago
        
        # Set hall pass issue time to 25 minutes ago (should trigger red alert)
        setattr(self.hall_pass, 'student_name', 'Test Student')
        setattr(self.hall_pass, 'destination', 'Library')
        setattr(self.hall_pass, 'issue_time', old_time)
        setattr(self.hall_pass, 'return_time', None)  # Not returned
        
        # Get dashboard data
        dashboard_view = self.portal.restrictedTraverse('@@teacher-dashboard')
        self.request['ajax_update'] = '1'
        response_data = dashboard_view()
        data = json.loads(response_data)
        
        # Verify hall pass shows in active passes
        hall_passes = data['hall_passes']
        self.assertGreater(hall_passes['active_count'], 0)
        
        # Verify alert is generated for long duration
        alerts = data['alerts']
        hall_pass_alerts = [alert for alert in alerts if alert['category'] == 'hall_pass']
        self.assertGreater(len(hall_pass_alerts), 0)
        
        # Verify alert has correct properties
        alert = hall_pass_alerts[0]
        self.assertEqual(alert['priority'], 'high')
        self.assertIn('Test Student', alert['message'])
    
    def test_timer_presets_api_integration(self):
        """Test that timer presets API integrates with frontend"""
        # Test timer presets endpoint
        timer_view = self.portal.restrictedTraverse('@@timer-presets')
        response_data = timer_view()
        presets = json.loads(response_data)
        
        # Verify default presets are available
        self.assertIsInstance(presets, list)
        self.assertGreater(len(presets), 0)
        
        # Verify preset structure
        preset = presets[0]
        self.assertIn('name', preset)
        self.assertIn('duration', preset)
        
        # Test timer sounds endpoint
        sounds_view = self.portal.restrictedTraverse('@@timer-sounds')
        sounds_data = sounds_view()
        sounds = json.loads(sounds_data)
        
        # Verify sound options are available
        self.assertIn('warning', sounds)
        self.assertIn('complete', sounds)
        self.assertIn('urgent', sounds)
    
    def test_participation_fairness_calculation(self):
        """Test that participation fairness algorithm works correctly"""
        dashboard_view = self.portal.restrictedTraverse('@@teacher-dashboard')
        participation_data = dashboard_view.get_participation_stats()
        
        # Verify fairness score calculation
        # With picks [3,2,1,4,1], there's imbalance, so score should be < 100
        self.assertLess(participation_data['fairness_score'], 100)
        self.assertGreater(participation_data['fairness_score'], 0)
        
        # Verify most/least picked identification
        self.assertEqual(participation_data['most_picked']['name'], 'Diana')
        self.assertEqual(participation_data['most_picked']['count'], 4)
        
        # Eve or Charlie should be least picked (both have 1)
        least_picked_name = participation_data['least_picked']['name']
        self.assertIn(least_picked_name, ['Eve', 'Charlie'])
        self.assertEqual(participation_data['least_picked']['count'], 1)
    
    def test_feature_performance_benchmarks(self):
        """Test that all features meet performance requirements"""
        # Test dashboard data aggregation performance
        start_time = time.time()
        dashboard_view = self.portal.restrictedTraverse('@@teacher-dashboard')
        self.request['ajax_update'] = '1'
        dashboard_view()
        dashboard_time = time.time() - start_time
        
        # Dashboard should load in under 500ms (generous for testing)
        self.assertLess(dashboard_time, 0.5, 
                       f"Dashboard took {dashboard_time:.3f}s, should be < 0.5s")
        
        # Test substitute folder generation performance
        start_time = time.time()
        sub_folder_view = self.portal.restrictedTraverse('@@substitute-folder-info')
        self.request.method = 'POST'
        sub_folder_view()
        sub_folder_time = time.time() - start_time
        
        # Substitute folder should generate in under 2 seconds
        self.assertLess(sub_folder_time, 2.0,
                       f"Substitute folder took {sub_folder_time:.3f}s, should be < 2.0s")
    
    def test_cross_feature_data_integrity(self):
        """Test that features maintain data integrity when used together"""
        # Get initial dashboard state
        dashboard_view = self.portal.restrictedTraverse('@@teacher-dashboard')
        self.request['ajax_update'] = '1'
        initial_data = json.loads(dashboard_view())
        
        # Simulate adding participation picks
        portal_annotations = IAnnotations(self.portal)
        today_key = f"participation_{datetime.now().date()}"
        current_stats = portal_annotations[today_key]
        current_stats['Alice'] = 5  # Increase Alice's count
        portal_annotations[today_key] = current_stats
        
        # Clear cache to force fresh data
        dashboard_view.get_participation_stats.invalidate_all()
        
        # Get updated dashboard state
        updated_data = json.loads(dashboard_view())
        
        # Verify participation data updated correctly
        initial_total = initial_data['participation']['total_picks']
        updated_total = updated_data['participation']['total_picks']
        self.assertEqual(updated_total, initial_total + 2)  # Alice went from 3 to 5
        
        # Verify most picked student changed
        self.assertEqual(updated_data['participation']['most_picked']['name'], 'Alice')
        self.assertEqual(updated_data['participation']['most_picked']['count'], 5)
    
    def test_mobile_responsive_data_structure(self):
        """Test that all API endpoints return mobile-friendly data structures"""
        # Test dashboard data structure for mobile consumption
        dashboard_view = self.portal.restrictedTraverse('@@teacher-dashboard')
        self.request['ajax_update'] = '1'
        response_data = dashboard_view()
        data = json.loads(response_data)
        
        # Verify compact data structures suitable for mobile
        quick_stats = data['quick_stats']
        self.assertIn('students_present', quick_stats)
        self.assertIn('active_passes', quick_stats)
        self.assertIn('current_time', quick_stats)
        
        # Verify hall pass data includes essential info only
        if data['hall_passes']['active_count'] > 0:
            pass_data = data['hall_passes']['passes'][0]
            self.assertIn('student', pass_data)
            self.assertIn('duration', pass_data)
            self.assertIn('alert_level', pass_data)
    
    def test_error_handling_and_graceful_degradation(self):
        """Test that features handle errors gracefully and don't break each other"""
        # Test dashboard with corrupted participation data
        portal_annotations = IAnnotations(self.portal)
        today_key = f"participation_{datetime.now().date()}"
        portal_annotations[today_key] = "invalid_data"  # Corrupt the data
        
        # Dashboard should still work with other features
        dashboard_view = self.portal.restrictedTraverse('@@teacher-dashboard')
        self.request['ajax_update'] = '1'
        response_data = dashboard_view()
        data = json.loads(response_data)
        
        # Verify dashboard still returns data structure
        self.assertIn('seating', data)
        self.assertIn('hall_passes', data)
        self.assertIn('system_status', data)
        
        # Participation should return error state gracefully
        participation = data['participation']
        self.assertEqual(participation['status'], 'error')
        
        # Other features should be unaffected
        self.assertNotEqual(data['seating']['status'], 'error')


if __name__ == '__main__':
    unittest.main() 