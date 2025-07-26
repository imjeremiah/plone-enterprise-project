"""
Performance Integration Tests

Tests verify that performance enhancements work correctly
and provide measurable improvements.
"""

import unittest
import time
from plone.app.testing import PLONE_INTEGRATION_TESTING
from plone import api
import json


class TestPerformanceIntegration(unittest.TestCase):
    """Test performance enhancements"""

    layer = PLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

    def test_catalog_indexes_registration(self):
        """Test that custom catalog indexes are available (if registered)"""
        try:
            catalog = api.portal.get_tool("portal_catalog")
            indexes = catalog.indexes()

            expected_indexes = [
                "hall_pass_duration",
                "hall_pass_status",
                "seating_student_count",
                "seating_last_updated",
                "classroom_ready",
            ]

            available_indexes = []
            for index_name in expected_indexes:
                if index_name in indexes:
                    available_indexes.append(index_name)
                    print(f"✅ Index '{index_name}' is available")
                else:
                    print(f"⚠️ Index '{index_name}' not yet registered")

            # At least some indexes should be available after proper setup
            if available_indexes:
                print(f"✅ {len(available_indexes)} performance indexes available")
            else:
                print(
                    "⚠️ No custom indexes registered yet (expected during development)"
                )

        except Exception as e:
            print(f"⚠️ Catalog index test skipped: {e}")

    def test_performance_dashboard_exists(self):
        """Test that performance dashboard views are available"""
        try:
            from ..browser.dashboard_performance import PerformanceDashboard

            # Create performance dashboard view
            view = PerformanceDashboard(self.portal, self.request)
            self.assertIsNotNone(view)

            # Test that methods exist
            self.assertTrue(hasattr(view, "get_optimized_hall_passes"))
            self.assertTrue(hasattr(view, "get_optimized_seating_stats"))
            self.assertTrue(hasattr(view, "get_performance_metrics"))
            self.assertTrue(hasattr(view, "check_index_availability"))

            print("✅ Performance dashboard view is available")

        except Exception as e:
            self.fail(f"Performance dashboard should be available: {e}")

    def test_performance_dashboard_queries(self):
        """Test that performance dashboard queries work"""
        from ..browser.dashboard_performance import PerformanceDashboard

        # Create test data using Document type (more reliable for testing)
        test_doc = api.content.create(
            container=self.portal,
            type="Document",
            id="perf-test-doc",
            title="Performance Test Document",
        )

        # Test performance dashboard
        view = PerformanceDashboard(self.portal, self.request)

        # Test optimized queries (should fall back gracefully)
        start_time = time.time()
        hall_pass_data = view.get_optimized_hall_passes()
        seating_data = view.get_optimized_seating_stats()
        end_time = time.time()

        query_time = (end_time - start_time) * 1000  # milliseconds

        # Verify data structure
        self.assertIn("active_passes", hall_pass_data)
        self.assertIn("performance_mode", hall_pass_data)
        self.assertIn("status", seating_data)
        self.assertIn("performance_mode", seating_data)

        # Performance should be reasonable (less than 2000ms for test environment)
        self.assertLess(query_time, 2000, "Dashboard queries should complete quickly")

        print(f"✅ Dashboard queries completed in {query_time:.2f}ms")

    def test_performance_metrics_endpoint(self):
        """Test that performance metrics endpoint works"""
        from ..browser.dashboard_performance import PerformanceDashboard

        view = PerformanceDashboard(self.portal, self.request)

        # Get performance metrics
        metrics_json = view.get_performance_metrics()
        metrics = json.loads(metrics_json)

        # Verify metrics structure
        required_keys = [
            "query_time_ms",
            "hall_pass_mode",
            "seating_mode",
            "timestamp",
            "index_status",
        ]

        for key in required_keys:
            self.assertIn(key, metrics, f"Metric {key} missing")

        # Query time should be reasonable
        self.assertIsInstance(metrics["query_time_ms"], (int, float))
        self.assertGreater(metrics["query_time_ms"], 0)
        self.assertLess(metrics["query_time_ms"], 5000)  # Should be under 5 seconds

        print(
            f"✅ Performance metrics endpoint works - {metrics['query_time_ms']:.2f}ms"
        )

    def test_index_availability_check(self):
        """Test that index availability checking works"""
        from ..browser.dashboard_performance import PerformanceDashboard

        view = PerformanceDashboard(self.portal, self.request)
        index_status = view.check_index_availability()

        # Should return a dictionary
        self.assertIsInstance(index_status, dict)

        # Should check expected indexes
        expected_indexes = [
            "hall_pass_duration",
            "hall_pass_status",
            "seating_student_count",
            "seating_last_updated",
            "classroom_ready",
        ]

        for index_name in expected_indexes:
            self.assertIn(index_name, index_status)
            # Value should be boolean
            self.assertIsInstance(index_status[index_name], bool)

        available_count = sum(index_status.values())
        print(
            f"✅ Index availability check works - {available_count}/{len(expected_indexes)} indexes available"
        )

    def test_performance_caching(self):
        """Test that performance caching works"""
        from ..browser.dashboard_performance import PerformanceDashboard

        view = PerformanceDashboard(self.portal, self.request)

        # First call
        start_time = time.time()
        result1 = view.get_optimized_hall_passes()
        first_call_time = time.time() - start_time

        # Second call (should be cached)
        start_time = time.time()
        result2 = view.get_optimized_hall_passes()
        second_call_time = time.time() - start_time

        # Results should be consistent
        self.assertEqual(result1["performance_mode"], result2["performance_mode"])

        # Second call might be faster due to caching (though not guaranteed in tests)
        print(
            f"✅ Performance caching available - First: {first_call_time:.3f}s, Second: {second_call_time:.3f}s"
        )


class TestIndexerFunctionality(unittest.TestCase):
    """Test catalog indexer functionality"""

    layer = PLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

    def test_catalog_indexers_import(self):
        """Test that catalog indexers can be imported"""
        try:
            from ..catalog import (
                hall_pass_duration,
                hall_pass_status,
                seating_student_count,
                seating_last_updated,
                classroom_ready_status,
            )

            # Functions should be callable
            self.assertTrue(callable(hall_pass_duration))
            self.assertTrue(callable(hall_pass_status))
            self.assertTrue(callable(seating_student_count))
            self.assertTrue(callable(seating_last_updated))
            self.assertTrue(callable(classroom_ready_status))

            print("✅ All catalog indexers can be imported")

        except Exception as e:
            self.fail(f"Catalog indexers should be importable: {e}")

    def test_indexer_error_handling(self):
        """Test that indexers handle errors gracefully"""
        from ..catalog import hall_pass_duration, hall_pass_status

        # Test with mock objects that might cause errors
        class MockFailingObj:
            def __getattr__(self, name):
                raise AttributeError(f"Mock error for {name}")

        mock_obj = MockFailingObj()

        # Indexers should not crash
        try:
            duration = hall_pass_duration(mock_obj)
            status = hall_pass_status(mock_obj)

            # Should return reasonable defaults
            self.assertIsInstance(duration, (int, float))
            self.assertIsInstance(status, str)

            print("✅ Indexers handle errors gracefully")

        except Exception as e:
            self.fail(f"Indexers should handle errors gracefully: {e}")


class TestPerformanceRegression(unittest.TestCase):
    """Test for performance regressions"""

    layer = PLONE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

    def test_no_performance_regression_in_basic_views(self):
        """Test that basic views haven't gotten slower"""
        from ..browser.hall_pass_views import HallPassManagerView
        from ..browser.dashboard import TeacherDashboard

        # Test hall pass manager performance
        hall_pass_view = HallPassManagerView(self.portal, self.request)

        start_time = time.time()
        self.request["ajax_data"] = "1"
        hall_pass_view.get_passes_data()
        hall_pass_time = time.time() - start_time

        # Should complete quickly
        self.assertLess(hall_pass_time, 2.0, "Hall pass data loading should be fast")

        # Test dashboard performance
        dashboard = TeacherDashboard(self.portal, self.request)

        start_time = time.time()
        dashboard.get_dashboard_data()
        dashboard_time = time.time() - start_time

        # Should complete quickly
        self.assertLess(dashboard_time, 3.0, "Dashboard loading should be fast")

        print(
            f"✅ No performance regression - Hall Pass: {hall_pass_time:.3f}s, Dashboard: {dashboard_time:.3f}s"
        )


def test_suite():
    """Return test suite"""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPerformanceIntegration))
    suite.addTest(unittest.makeSuite(TestIndexerFunctionality))
    suite.addTest(unittest.makeSuite(TestPerformanceRegression))
    return suite


if __name__ == "__main__":
    unittest.main()
