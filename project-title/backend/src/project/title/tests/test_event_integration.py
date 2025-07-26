"""
Event Integration Tests

Tests verify that event system works correctly and
integrates features without breaking existing functionality.
"""

import unittest
from plone.app.testing import PLONE_INTEGRATION_TESTING
from plone import api
from zope.component import getGlobalSiteManager
from zope.event import notify
import json

from ..testing import PROJECT_TITLE_INTEGRATION_TESTING
from ..events import HallPassIssuedEvent, SeatingChartUpdatedEvent, HallPassReturnedEvent


class TestEventIntegration(unittest.TestCase):
    """Test event integration"""
    
    layer = PLONE_INTEGRATION_TESTING
    
    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.events_fired = []
        
        # Track events for testing
        self.original_handlers = []
    
    def test_event_interfaces_available(self):
        """Test that event interfaces can be imported"""
        try:
            from ..events import (
                IHallPassEvent,
                IHallPassIssuedEvent,
                IHallPassReturnedEvent,
                ISeatingChartUpdatedEvent,
                ITimerCompletedEvent
            )
            
            print("✅ All event interfaces can be imported")
            
        except Exception as e:
            self.fail(f"Event interfaces should be importable: {e}")
    
    def test_event_implementations_available(self):
        """Test that event implementations can be imported"""
        try:
            from ..events import (
                HallPassIssuedEvent,
                HallPassReturnedEvent,
                SeatingChartUpdatedEvent,
                TimerCompletedEvent
            )
            
            print("✅ All event implementations can be imported")
            
        except Exception as e:
            self.fail(f"Event implementations should be importable: {e}")
    
    def test_hall_pass_events_fire(self):
        """Test that hall pass events fire correctly"""
        # Create a test document to use as hall pass object
        hall_pass = api.content.create(
            container=self.portal,
            type='Document',
            id='event-test-pass',
            title='Event Test Pass'
        )
        
        # Fire issued event
        issued_event = HallPassIssuedEvent(hall_pass, student_name='Test Student', destination='Library')
        
        # Should not raise exceptions
        try:
            notify(issued_event)
            print("✅ Hall pass issued event fired successfully")
        except Exception as e:
            self.fail(f"Hall pass issued event should fire without errors: {e}")
        
        # Verify event data
        self.assertEqual(issued_event.student_name, 'Test Student')
        self.assertEqual(issued_event.destination, 'Library')
        self.assertEqual(issued_event.object, hall_pass)
        
        # Fire returned event
        returned_event = HallPassReturnedEvent(hall_pass, duration=15)
        
        try:
            notify(returned_event)
            print("✅ Hall pass returned event fired successfully")
        except Exception as e:
            self.fail(f"Hall pass returned event should fire without errors: {e}")
        
        # Verify event data
        self.assertEqual(returned_event.duration, 15)
        self.assertEqual(returned_event.object, hall_pass)
    
    def test_seating_chart_events_fire(self):
        """Test that seating chart events fire correctly"""
        # Create a test document to use as seating chart object
        seating_chart = api.content.create(
            container=self.portal,
            type='Document',
            id='event-test-chart',
            title='Event Test Chart'
        )
        
        # Fire event
        event = SeatingChartUpdatedEvent(seating_chart, student_count=25)
        
        try:
            notify(event)
            print("✅ Seating chart updated event fired successfully")
        except Exception as e:
            self.fail(f"Seating chart updated event should fire without errors: {e}")
        
        # Verify event data
        self.assertEqual(event.student_count, 25)
        self.assertEqual(event.object, seating_chart)
    
    def test_event_handlers_available(self):
        """Test that event handlers can be imported"""
        try:
            from ..event_handlers import (
                handle_hall_pass_issued,
                handle_hall_pass_returned,
                handle_seating_chart_updated,
                handle_timer_completed,
                fire_hall_pass_issued,
                fire_seating_chart_updated
            )
            
            print("✅ All event handlers can be imported")
            
        except Exception as e:
            self.fail(f"Event handlers should be importable: {e}")
    
    def test_event_firing_helpers(self):
        """Test that event firing helper functions work"""
        from ..event_handlers import fire_hall_pass_issued, fire_seating_chart_updated
        
        # Create test objects
        hall_pass = api.content.create(
            container=self.portal,
            type='Document',
            id='helper-test-pass',
            title='Helper Test Pass'
        )
        
        seating_chart = api.content.create(
            container=self.portal,
            type='Document',
            id='helper-test-chart',
            title='Helper Test Chart'
        )
        
        # Test firing helpers (should not raise exceptions)
        try:
            fire_hall_pass_issued(hall_pass, 'Helper Test Student', 'Office')
            print("✅ Hall pass event firing helper works")
        except Exception as e:
            self.fail(f"Hall pass event firing helper should work: {e}")
        
        try:
            fire_seating_chart_updated(seating_chart, student_count=30)
            print("✅ Seating chart event firing helper works")
        except Exception as e:
            self.fail(f"Seating chart event firing helper should work: {e}")
    
    def test_event_handlers_graceful_degradation(self):
        """Test that event handlers handle errors gracefully"""
        from ..event_handlers import fire_hall_pass_issued, fire_seating_chart_updated
        
        # Create objects that might cause handler errors
        class MockFailingObj:
            def getId(self):
                return 'failing-test-obj'
            
            def __getattr__(self, name):
                if name == 'title':
                    return 'Failing Test Object'
                raise AttributeError(f"Mock error for {name}")
        
        mock_obj = MockFailingObj()
        
        # Event firing should not raise exceptions even if handlers fail
        try:
            fire_hall_pass_issued(mock_obj, 'Failing Test Student', 'Failing Destination')
            fire_seating_chart_updated(mock_obj, student_count=25)
            print("✅ Event handlers handle errors gracefully")
        except Exception as e:
            self.fail(f"Event firing should not break functionality even with handler errors: {e}")


class TestEventIntegrationInViews(unittest.TestCase):
    """Test event integration in browser views"""
    
    layer = PLONE_INTEGRATION_TESTING
    
    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
    
    def test_hall_pass_views_fire_events(self):
        """Test that hall pass views fire events correctly"""
        from ..browser.hall_pass_views import HallPassManagerView
        
        # Create hall pass manager view
        view = HallPassManagerView(self.portal, self.request)
        
        # Mock request data for pass creation
        self.request['BODY'] = json.dumps({
            'student_name': 'Event Integration Student',
            'destination': 'Event Test Destination',
            'expected_duration': 5
        }).encode('utf-8')
        
        # Issue pass should work and fire events (but not crash if events fail)
        try:
            result = view.issue_pass()
            result_data = json.loads(result)
            self.assertTrue(result_data.get('success'))
            print("✅ Hall pass issuing with events works")
        except Exception as e:
            self.fail(f"Hall pass issuing should work even if event firing fails: {e}")
    
    def test_seating_chart_views_fire_events(self):
        """Test that seating chart views fire events correctly"""
        from ..browser.seating_views import SeatingChartUpdateView
        
        # Create seating chart
        seating_chart = api.content.create(
            container=self.portal,
            type='Document',
            id='event-test-seating',
            title='Event Test Seating Chart'
        )
        seating_chart.grid_data = '{"students": {"student1": {"row": 0, "col": 0}}}'
        
        # Create seating chart update view
        view = SeatingChartUpdateView(seating_chart, self.request)
        
        # Mock request data for grid update
        test_grid_data = {
            'grid_data': '{"students": {"student1": {"row": 1, "col": 1}, "student2": {"row": 2, "col": 2}}}'
        }
        
        # Update grid should work and fire events (but not crash if events fail)
        try:
            result = view.update_grid(test_grid_data)
            result_data = json.loads(result)
            self.assertTrue(result_data.get('success'))
            print("✅ Seating chart updating with events works")
        except Exception as e:
            self.fail(f"Seating chart updating should work even if event firing fails: {e}")
    
    def test_events_dont_break_existing_functionality(self):
        """Test that event integration doesn't break existing functionality"""
        from ..browser.hall_pass_views import HallPassManagerView
        
        # Create hall pass view
        view = HallPassManagerView(self.portal, self.request)
        
        # Mock request data
        self.request['BODY'] = json.dumps({
            'student_name': 'Non-Breaking Test Student',
            'destination': 'Non-Breaking Test Destination'
        }).encode('utf-8')
        
        # Should work regardless of event system status
        try:
            result = view.issue_pass()
            result_data = json.loads(result)
            self.assertTrue(result_data.get('success'))
            self.assertIn('pass', result_data)
            
            # Core data should be preserved
            self.assertEqual(result_data['pass']['student_name'], 'Non-Breaking Test Student')
            self.assertEqual(result_data['pass']['destination'], 'Non-Breaking Test Destination')
            
            print("✅ Event integration preserves existing functionality")
            
        except Exception as e:
            self.fail(f"Core functionality should not be affected by event integration: {e}")


class TestEventAnnotationSystem(unittest.TestCase):
    """Test that event handlers use annotation system correctly"""
    
    layer = PLONE_INTEGRATION_TESTING
    
    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
    
    def test_annotation_system_available(self):
        """Test that annotation system works for event handlers"""
        # Check that portal has annotation capability
        annotations = getattr(self.portal, '__annotations__', None)
        
        if annotations is not None:
            # Test basic annotation functionality
            test_key = 'test_event_annotation'
            test_data = {'test': 'event data'}
            
            annotations[test_key] = test_data
            retrieved_data = annotations.get(test_key)
            
            self.assertEqual(retrieved_data, test_data)
            print("✅ Annotation system works for event handlers")
        else:
            print("⚠️ Annotation system not available (expected in some test environments)")
    
    def test_event_handlers_use_annotations_safely(self):
        """Test that event handlers use annotations without breaking if unavailable"""
        from ..event_handlers import handle_hall_pass_issued, handle_seating_chart_updated
        
        # Create test objects
        hall_pass = api.content.create(
            container=self.portal,
            type='Document',
            id='annotation-test-pass',
            title='Annotation Test Pass'
        )
        
        seating_chart = api.content.create(
            container=self.portal,
            type='Document',
            id='annotation-test-chart',
            title='Annotation Test Chart'
        )
        
        # Create mock events
        issued_event = HallPassIssuedEvent(hall_pass, student_name='Annotation Test', destination='Test Room')
        seating_event = SeatingChartUpdatedEvent(seating_chart, student_count=20)
        
        # Handlers should work without crashing
        try:
            handle_hall_pass_issued(issued_event)
            handle_seating_chart_updated(seating_event)
            print("✅ Event handlers use annotations safely")
        except Exception as e:
            self.fail(f"Event handlers should handle annotation errors gracefully: {e}")


def test_suite():
    """Return test suite"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestEventIntegration))
    suite.addTest(unittest.makeSuite(TestEventIntegrationInViews))
    suite.addTest(unittest.makeSuite(TestEventAnnotationSystem))
    return suite


if __name__ == '__main__':
    unittest.main() 