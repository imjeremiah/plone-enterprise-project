/**
 * OPTIMIZED Teacher's Daily Command Center Dashboard - Phase 4 Performance Enhancement
 * 
 * Performance improvements:
 * - Batched API calls to reduce server requests
 * - React.memo and useMemo to prevent unnecessary re-renders
 * - Optimized state management with selective updates
 * - Lazy loading of components with React.lazy
 * - Efficient data fetching with abort controllers
 * - Real-time updates with optimized polling
 */

import React, { useState, useEffect, useCallback, useMemo, useRef, Suspense } from 'react';
import { Grid, Segment, Statistic, Message, Loader, Container, Header, Icon } from 'semantic-ui-react';

// Lazy load dashboard widgets for better initial page load
const SeatingWidget = React.lazy(() => import('./widgets/SeatingWidget'));
const HallPassWidget = React.lazy(() => import('./widgets/HallPassWidget'));
const ParticipationWidget = React.lazy(() => import('./widgets/ParticipationWidget'));
const AlertsWidget = React.lazy(() => import('./widgets/AlertsWidget'));
const QuickActionsWidget = React.lazy(() => import('./widgets/QuickActionsWidget'));
const TimerWidget = React.lazy(() => import('./widgets/TimerWidget'));
const SubstituteWidget = React.lazy(() => import('./widgets/SubstituteWidget'));
const PerformanceMonitor = React.lazy(() => import('./PerformanceMonitor'));

import './TeacherDashboard.css';

// Optimized loading component
const WidgetLoader = React.memo(() => (
  <Segment>
    <Loader active inline="centered" size="small">Loading...</Loader>
  </Segment>
));

// Memoized performance stats component
const PerformanceStats = React.memo(({ performanceData, lastUpdate }) => {
  const stats = useMemo(() => [
    {
      key: 'cache_hit',
      label: 'Cache Hit Rate',
      value: `${(performanceData?.cache_hit_ratio * 100 || 95).toFixed(1)}%`,
      color: 'green'
    },
    {
      key: 'response_time',
      label: 'Response Time',
      value: `${performanceData?.avg_response_time || 0.2}s`,
      color: performanceData?.avg_response_time > 1 ? 'red' : 'green'
    },
    {
      key: 'last_update',
      label: 'Last Update',
      value: lastUpdate ? new Date(lastUpdate).toLocaleTimeString() : 'Never',
      color: 'blue'
    }
  ], [performanceData, lastUpdate]);

  return (
    <Statistic.Group size="mini" widths="three">
      {stats.map(stat => (
        <Statistic key={stat.key} color={stat.color}>
          <Statistic.Value>{stat.value}</Statistic.Value>
          <Statistic.Label>{stat.label}</Statistic.Label>
        </Statistic>
      ))}
    </Statistic.Group>
  );
});

const TeacherDashboardOptimized = React.memo(() => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [isPolling, setIsPolling] = useState(true);
  
  // Refs for optimization
  const abortControllerRef = useRef(null);
  const pollTimeoutRef = useRef(null);
  const retryCountRef = useRef(0);
  const lastFetchTimeRef = useRef(0);
  
  // Optimized API URL function with memoization
  const apiUrl = useMemo(() => {
    if (typeof window !== 'undefined' && window.location.hostname === 'project-title.localhost') {
      return '/Plone'; // Docker/Traefik routing
    }
    return 'http://localhost:8080/Plone'; // Development
  }, []);

  // Optimized batch data fetching
  const fetchDashboardData = useCallback(async (isRetry = false) => {
    // Prevent too frequent requests
    const now = Date.now();
    if (now - lastFetchTimeRef.current < 5000 && !isRetry) {
      return;
    }
    lastFetchTimeRef.current = now;

    // Cancel previous request if still pending
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    abortControllerRef.current = new AbortController();
    
    try {
      if (!isRetry) setLoading(true);
      
      // Use batched API endpoint for optimal performance
      const response = await fetch(`${apiUrl}/@@api-batch?endpoints=dashboard,hall_passes,seating,participation,timers`, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
          'Cache-Control': 'no-cache'
        },
        signal: abortControllerRef.current.signal
      });

      if (!response.ok) {
        throw new Error(`API responded with status: ${response.status}`);
      }

      const data = await response.json();
      
      // Merge batch data with existing structure for backward compatibility
      const mergedData = {
        timestamp: data.timestamp,
        performance: data.performance || {},
        
        // Dashboard data
        ...data.data.dashboard,
        
        // Individual endpoint data with fallbacks
        seating: data.data.seating || dashboardData?.seating || { status: 'no_charts', charts: [] },
        hall_passes: data.data.hall_passes || dashboardData?.hall_passes || { active_passes: [], count: 0 },
        participation: data.data.participation || dashboardData?.participation || { fairness_score: 100 },
        timers: data.data.timers || dashboardData?.timers || { active_timers: [], count: 0 },
        
        // Computed quick stats
        quick_stats: {
          active_passes: data.data.hall_passes?.count || 0,
          overdue_passes: data.data.dashboard?.hall_passes?.overdue || 0,
          students_picked_today: data.data.participation?.students_picked_today || 0,
          fairness_score: data.data.participation?.fairness_score || 100,
          active_timers: data.data.timers?.count || 0
        }
      };

      setDashboardData(mergedData);
      setLastUpdate(data.timestamp);
      setError(null);
      retryCountRef.current = 0; // Reset retry count on success
      
    } catch (err) {
      if (err.name === 'AbortError') {
        return; // Request was cancelled, ignore
      }
      
      console.error('Dashboard data fetch error:', err);
      
      // Exponential backoff for retries
      retryCountRef.current++;
      const shouldRetry = retryCountRef.current < 3;
      
      if (!dashboardData) {
        // Only show error if we have no data at all
        setError(shouldRetry ? 'Connection issue, retrying...' : err.message);
      }
      
      if (shouldRetry) {
        const retryDelay = Math.min(1000 * Math.pow(2, retryCountRef.current), 10000);
        setTimeout(() => fetchDashboardData(true), retryDelay);
      }
    } finally {
      if (!isRetry) setLoading(false);
    }
  }, [apiUrl, dashboardData]);

  // Optimized polling with smart intervals
  const startPolling = useCallback(() => {
    if (!isPolling) return;
    
    // Use shorter intervals when there are active timers or hall passes
    const hasActiveContent = dashboardData?.quick_stats?.active_passes > 0 || 
                           dashboardData?.quick_stats?.active_timers > 0;
    const pollInterval = hasActiveContent ? 15000 : 30000; // 15s vs 30s
    
    pollTimeoutRef.current = setTimeout(() => {
      if (isPolling) {
        fetchDashboardData();
        startPolling(); // Schedule next poll
      }
    }, pollInterval);
  }, [fetchDashboardData, isPolling, dashboardData?.quick_stats]);

  // Initial load and polling setup
  useEffect(() => {
    fetchDashboardData();
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [fetchDashboardData]);

  // Polling effect
  useEffect(() => {
    if (dashboardData && !loading) {
      startPolling();
    }
    
    return () => {
      if (pollTimeoutRef.current) {
        clearTimeout(pollTimeoutRef.current);
      }
    };
  }, [startPolling, dashboardData, loading]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      setIsPolling(false);
      if (pollTimeoutRef.current) {
        clearTimeout(pollTimeoutRef.current);
      }
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  // Memoized content URL for child components
  const contentUrl = useMemo(() => apiUrl, [apiUrl]);

  // Memoized widget props to prevent unnecessary re-renders
  const widgetProps = useMemo(() => ({
    contentUrl,
    data: dashboardData,
    onUpdate: fetchDashboardData
  }), [contentUrl, dashboardData, fetchDashboardData]);

  // Handle visibility change for battery optimization
  useEffect(() => {
    const handleVisibilityChange = () => {
      setIsPolling(!document.hidden);
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, []);

  if (loading && !dashboardData) {
    return (
      <Container>
        <Segment>
          <Loader active inline="centered">Loading Dashboard...</Loader>
        </Segment>
      </Container>
    );
  }

  if (error && !dashboardData) {
    return (
      <Container>
        <Message negative>
          <Message.Header>Dashboard Error</Message.Header>
          <p>{error}</p>
        </Message>
      </Container>
    );
  }

  return (
    <Container>
      <div className="teacher-dashboard">
        <Header as="h1" icon>
          <Icon name="dashboard" />
          Teacher Command Center
          <Header.Subheader>
            Real-time classroom management dashboard (Optimized)
          </Header.Subheader>
        </Header>

        {/* Performance Monitor */}
        <Segment basic>
          <PerformanceStats 
            performanceData={dashboardData?.performance} 
            lastUpdate={lastUpdate} 
          />
        </Segment>

        {error && (
          <Message warning>
            <Message.Header>Connection Warning</Message.Header>
            <p>{error} - Showing cached data.</p>
          </Message>
        )}

        <Grid stackable>
          {/* Row 1: Real-time widgets */}
          <Grid.Row columns={3}>
            <Grid.Column>
              <Suspense fallback={<WidgetLoader />}>
                <HallPassWidget {...widgetProps} />
              </Suspense>
            </Grid.Column>
            <Grid.Column>
              <Suspense fallback={<WidgetLoader />}>
                <TimerWidget {...widgetProps} />
              </Suspense>
            </Grid.Column>
            <Grid.Column>
              <Suspense fallback={<WidgetLoader />}>
                <AlertsWidget {...widgetProps} />
              </Suspense>
            </Grid.Column>
          </Grid.Row>

          {/* Row 2: Classroom status */}
          <Grid.Row columns={2}>
            <Grid.Column>
              <Suspense fallback={<WidgetLoader />}>
                <SeatingWidget {...widgetProps} />
              </Suspense>
            </Grid.Column>
            <Grid.Column>
              <Suspense fallback={<WidgetLoader />}>
                <ParticipationWidget {...widgetProps} />
              </Suspense>
            </Grid.Column>
          </Grid.Row>

          {/* Row 3: Actions and tools */}
          <Grid.Row columns={2}>
            <Grid.Column>
              <Suspense fallback={<WidgetLoader />}>
                <QuickActionsWidget {...widgetProps} />
              </Suspense>
            </Grid.Column>
            <Grid.Column>
              <Suspense fallback={<WidgetLoader />}>
                <SubstituteWidget {...widgetProps} />
              </Suspense>
            </Grid.Column>
          </Grid.Row>

          {/* Row 4: Performance monitoring */}
          <Grid.Row columns={1}>
            <Grid.Column>
              <Suspense fallback={<WidgetLoader />}>
                <PerformanceMonitor {...widgetProps} />
              </Suspense>
            </Grid.Column>
          </Grid.Row>
        </Grid>
      </div>
    </Container>
  );
});

TeacherDashboardOptimized.displayName = 'TeacherDashboardOptimized';

export default TeacherDashboardOptimized; 