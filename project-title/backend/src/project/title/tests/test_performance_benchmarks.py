"""
Phase 3 Performance Benchmarks - Real-time Updates

Measures performance of all real-time dashboard updates and feature interactions
to ensure they meet the requirements specified in Phase 3:
- Dashboard data aggregation < 500ms
- Timer updates < 50ms response
- Hall pass tracking < 100ms
- Substitute folder generation < 2s
- Participation calculations < 200ms
"""

import unittest
import time
import statistics
from datetime import datetime, timedelta
from plone.app.testing import PLONE_INTEGRATION_TESTING
from plone import api
from zope.annotation.interfaces import IAnnotations


class TestPerformanceBenchmarks(unittest.TestCase):
    """Performance benchmarks for Phase 3 real-time features"""

    layer = PLONE_INTEGRATION_TESTING

    def setUp(self):
        """Set up test environment with realistic data load"""
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

        # Create multiple seating charts for realistic testing
        for i in range(5):
            chart = api.content.create(
                container=self.portal,
                type="SeatingChart",
                id=f"chart-{i}",
                title=f"Classroom {i+1}",
                students=[f"Student{j}" for j in range(25)],  # 25 students per chart
            )

        # Create multiple hall passes
        now = datetime.now()
        for i in range(10):
            hall_pass = api.content.create(
                container=self.portal,
                type="HallPass",
                id=f"pass-{i}",
                title=f"Hall Pass {i}",
            )
            # Simulate various durations
            setattr(hall_pass, "student_name", f"Student{i}")
            setattr(hall_pass, "destination", f"Destination{i}")
            setattr(hall_pass, "issue_time", now - timedelta(minutes=i * 2))
            if i % 3 == 0:  # Some passes returned
                setattr(hall_pass, "return_time", now - timedelta(minutes=i))
            else:
                setattr(hall_pass, "return_time", None)

        # Create realistic participation data
        portal_annotations = IAnnotations(self.portal)
        today_key = f"participation_{datetime.now().date()}"
        participation_data = {}
        for i in range(30):  # 30 students
            participation_data[f"Student{i}"] = i % 7  # Varied participation
        portal_annotations[today_key] = participation_data

    def benchmark_function(self, func, iterations=10):
        """Utility function to benchmark a function call"""
        times = []
        for _ in range(iterations):
            start = time.time()
            result = func()
            end = time.time()
            times.append(end - start)

        return {
            "min": min(times),
            "max": max(times),
            "mean": statistics.mean(times),
            "median": statistics.median(times),
            "times": times,
            "result": result,
        }

    def test_dashboard_aggregation_performance(self):
        """Benchmark dashboard data aggregation performance"""
        dashboard_view = self.portal.restrictedTraverse("@@teacher-dashboard")
        self.request["ajax_update"] = "1"

        def get_dashboard_data():
            return dashboard_view()

        benchmark = self.benchmark_function(get_dashboard_data, iterations=20)

        # Dashboard should aggregate all data in under 500ms
        self.assertLess(
            benchmark["mean"],
            0.5,
            f"Dashboard aggregation took {benchmark['mean']:.3f}s on average, "
            f"should be < 0.5s",
        )

        # 95th percentile should be under 1 second
        times_sorted = sorted(benchmark["times"])
        p95_time = times_sorted[int(0.95 * len(times_sorted))]
        self.assertLess(
            p95_time,
            1.0,
            f"95th percentile dashboard time {p95_time:.3f}s should be < 1.0s",
        )

        print(f"📊 Dashboard Performance:")
        print(f"  Mean: {benchmark['mean']:.3f}s")
        print(f"  Median: {benchmark['median']:.3f}s")
        print(f"  95th percentile: {p95_time:.3f}s")
        print(f"  Range: {benchmark['min']:.3f}s - {benchmark['max']:.3f}s")

    def test_hall_pass_tracking_performance(self):
        """Benchmark hall pass duration tracking performance"""
        dashboard_view = self.portal.restrictedTraverse("@@teacher-dashboard")

        def get_hall_pass_data():
            return dashboard_view.get_active_passes()

        benchmark = self.benchmark_function(get_hall_pass_data, iterations=15)

        # Hall pass tracking should be under 100ms
        self.assertLess(
            benchmark["mean"],
            0.1,
            f"Hall pass tracking took {benchmark['mean']:.3f}s on average, "
            f"should be < 0.1s",
        )

        print(f"🆔 Hall Pass Tracking Performance:")
        print(f"  Mean: {benchmark['mean']:.3f}s")
        print(f"  Max: {benchmark['max']:.3f}s")

    def test_participation_calculation_performance(self):
        """Benchmark participation fairness calculation performance"""
        dashboard_view = self.portal.restrictedTraverse("@@teacher-dashboard")

        def get_participation_stats():
            return dashboard_view.get_participation_stats()

        benchmark = self.benchmark_function(get_participation_stats, iterations=15)

        # Participation calculation should be under 200ms
        self.assertLess(
            benchmark["mean"],
            0.2,
            f"Participation calculation took {benchmark['mean']:.3f}s on average, "
            f"should be < 0.2s",
        )

        print(f"⚖️ Participation Calculation Performance:")
        print(f"  Mean: {benchmark['mean']:.3f}s")
        print(f"  Max: {benchmark['max']:.3f}s")

    def test_substitute_folder_generation_performance(self):
        """Benchmark substitute folder generation performance"""
        sub_folder_view = self.portal.restrictedTraverse("@@substitute-folder-info")

        def generate_substitute_folder():
            self.request.method = "POST"
            self.request.form = {"notes": "Performance test notes"}
            return sub_folder_view()

        benchmark = self.benchmark_function(generate_substitute_folder, iterations=5)

        # Substitute folder generation should be under 2 seconds
        self.assertLess(
            benchmark["mean"],
            2.0,
            f"Substitute folder generation took {benchmark['mean']:.3f}s on average, "
            f"should be < 2.0s",
        )

        print(f"📁 Substitute Folder Generation Performance:")
        print(f"  Mean: {benchmark['mean']:.3f}s")
        print(f"  Max: {benchmark['max']:.3f}s")

    def test_seating_chart_query_performance(self):
        """Benchmark seating chart data retrieval performance"""
        dashboard_view = self.portal.restrictedTraverse("@@teacher-dashboard")

        def get_seating_data():
            return dashboard_view.get_current_seating()

        benchmark = self.benchmark_function(get_seating_data, iterations=15)

        # Seating chart queries should be under 100ms
        self.assertLess(
            benchmark["mean"],
            0.1,
            f"Seating chart query took {benchmark['mean']:.3f}s on average, "
            f"should be < 0.1s",
        )

        print(f"👥 Seating Chart Query Performance:")
        print(f"  Mean: {benchmark['mean']:.3f}s")
        print(f"  Max: {benchmark['max']:.3f}s")

    def test_timer_presets_api_performance(self):
        """Benchmark timer API performance"""
        timer_view = self.portal.restrictedTraverse("@@timer-presets")

        def get_timer_presets():
            return timer_view()

        benchmark = self.benchmark_function(get_timer_presets, iterations=20)

        # Timer API should respond in under 50ms
        self.assertLess(
            benchmark["mean"],
            0.05,
            f"Timer presets API took {benchmark['mean']:.3f}s on average, "
            f"should be < 0.05s",
        )

        print(f"⏰ Timer Presets API Performance:")
        print(f"  Mean: {benchmark['mean']:.3f}s")
        print(f"  Max: {benchmark['max']:.3f}s")

    def test_caching_effectiveness(self):
        """Test that caching improves performance for repeated requests"""
        dashboard_view = self.portal.restrictedTraverse("@@teacher-dashboard")
        self.request["ajax_update"] = "1"

        # First call (cold cache)
        start = time.time()
        dashboard_view()
        cold_time = time.time() - start

        # Second call (warm cache)
        start = time.time()
        dashboard_view()
        warm_time = time.time() - start

        # Cached call should be significantly faster
        improvement_ratio = cold_time / warm_time if warm_time > 0 else float("inf")

        print(f"🚀 Caching Performance:")
        print(f"  Cold cache: {cold_time:.3f}s")
        print(f"  Warm cache: {warm_time:.3f}s")
        print(f"  Improvement: {improvement_ratio:.1f}x faster")

        # Cache should provide at least 2x improvement
        self.assertGreater(
            improvement_ratio,
            2.0,
            f"Cache should provide at least 2x improvement, got {improvement_ratio:.1f}x",
        )

    def test_concurrent_request_performance(self):
        """Test performance under simulated concurrent load"""
        import threading
        import queue

        dashboard_view = self.portal.restrictedTraverse("@@teacher-dashboard")
        self.request["ajax_update"] = "1"

        results = queue.Queue()
        num_threads = 5
        requests_per_thread = 4

        def make_requests():
            thread_times = []
            for _ in range(requests_per_thread):
                start = time.time()
                dashboard_view()
                thread_times.append(time.time() - start)
            results.put(thread_times)

        # Start concurrent threads
        threads = []
        start_time = time.time()

        for _ in range(num_threads):
            thread = threading.Thread(target=make_requests)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        total_time = time.time() - start_time

        # Collect all timing results
        all_times = []
        while not results.empty():
            thread_times = results.get()
            all_times.extend(thread_times)

        mean_response_time = statistics.mean(all_times)
        total_requests = num_threads * requests_per_thread

        print(f"🔄 Concurrent Load Performance:")
        print(f"  Total requests: {total_requests}")
        print(f"  Total time: {total_time:.3f}s")
        print(f"  Mean response time: {mean_response_time:.3f}s")
        print(f"  Requests per second: {total_requests/total_time:.1f}")

        # Under concurrent load, mean response should still be reasonable
        self.assertLess(
            mean_response_time,
            1.0,
            f"Mean response time under load {mean_response_time:.3f}s should be < 1.0s",
        )

    def test_memory_usage_stability(self):
        """Test that repeated operations don't cause memory leaks"""
        import gc
        import psutil
        import os

        process = psutil.Process(os.getpid())

        # Get baseline memory usage
        gc.collect()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        dashboard_view = self.portal.restrictedTraverse("@@teacher-dashboard")
        self.request["ajax_update"] = "1"

        # Perform many operations
        for _ in range(100):
            dashboard_view()

        # Check memory usage after operations
        gc.collect()
        final_memory = process.memory_info().rss / 1024 / 1024  # MB

        memory_increase = final_memory - initial_memory

        print(f"💾 Memory Usage Stability:")
        print(f"  Initial memory: {initial_memory:.1f} MB")
        print(f"  Final memory: {final_memory:.1f} MB")
        print(f"  Increase: {memory_increase:.1f} MB")

        # Memory increase should be minimal (under 50MB for 100 operations)
        self.assertLess(
            memory_increase,
            50,
            f"Memory increased by {memory_increase:.1f}MB, should be < 50MB",
        )


def run_all_benchmarks():
    """Run all performance benchmarks and generate a report"""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPerformanceBenchmarks)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 60)
    print("PHASE 3 PERFORMANCE BENCHMARK SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")

    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")

    success_rate = (
        (result.testsRun - len(result.failures) - len(result.errors))
        / result.testsRun
        * 100
    )
    print(f"\nSuccess Rate: {success_rate:.1f}%")

    if success_rate >= 95:
        print("✅ PHASE 3 PERFORMANCE TARGETS MET")
    else:
        print("❌ PHASE 3 PERFORMANCE TARGETS NOT MET")

    return result.wasSuccessful()


if __name__ == "__main__":
    run_all_benchmarks()
