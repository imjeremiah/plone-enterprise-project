/**
 * Teacher's Daily Command Center Dashboard
 * 
 * Real-time classroom management dashboard that aggregates data from all features:
 * - Current seating arrangements and student counts
 * - Active hall passes with duration tracking and alerts
 * - Participation statistics and fairness scores
 * - Classroom alerts and notifications
 * - Quick action widgets for common tasks
 * 
 * Updates every 30 seconds for real-time monitoring.
 */

import React, { useState, useEffect } from 'react';
import { Grid, Segment, Statistic, Message, Loader, Container, Header, Icon } from 'semantic-ui-react';

// Import dashboard widgets
import SeatingWidget from './widgets/SeatingWidget';
import HallPassWidget from './widgets/HallPassWidget';
import ParticipationWidget from './widgets/ParticipationWidget';
import AlertsWidget from './widgets/AlertsWidget';
import QuickActionsWidget from './widgets/QuickActionsWidget';
import TimerWidget from './widgets/TimerWidget';
import SubstituteWidget from './widgets/SubstituteWidget';
import PerformanceMonitor from './PerformanceMonitor';

import './TeacherDashboard.css';

const TeacherDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  
  // Get backend URL from environment - support both dev and Docker modes
  const getApiUrl = () => {
    // If we're on project-title.localhost (Docker), use relative path via Traefik
    if (typeof window !== 'undefined' && window.location.hostname === 'project-title.localhost') {
      return '/Plone'; // Relative path - Traefik will route to backend
    }
    // Otherwise use localhost fallback for development
    return 'http://localhost:8080/Plone';
  };
  
  const contentUrl = getApiUrl();

  useEffect(() => {
    // Initial load
    fetchDashboardData();
    
    // Set up polling for real-time updates every 30 seconds
    const interval = setInterval(fetchDashboardData, 30000);
    
    return () => clearInterval(interval);
  }, []);

  /**
   * Fetch dashboard data from backend API
   */
  const fetchDashboardData = async () => {
    try {
      const response = await fetch(`${contentUrl}/@@teacher-dashboard?ajax_update=1`, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setDashboardData(data);
        setLastUpdate(new Date());
        setError(null);
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
    } catch (error) {
      console.error('Dashboard update failed:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Determine color for hall pass count statistic
   */
  const getHallPassColor = (count) => {
    if (count > 3) return 'red';
    if (count > 1) return 'yellow';
    return 'green';
  };

  /**
   * Determine color for participation fairness score
   */
  const getFairnessColor = (score) => {
    if (score >= 80) return 'green';
    if (score >= 60) return 'yellow';
    return 'red';
  };

  if (loading && !dashboardData) {
    return (
      <Container style={{ padding: '40px 0' }}>
        <Segment>
          <Loader active inline="centered" size="large">
            Loading classroom dashboard...
          </Loader>
        </Segment>
      </Container>
    );
  }

  if (error && !dashboardData) {
    return (
      <Container style={{ padding: '40px 0' }}>
        <Message negative>
          <Message.Header>Dashboard Load Error</Message.Header>
          <p>Failed to load dashboard data: {error}</p>
        </Message>
      </Container>
    );
  }

  const { quick_stats, alerts, seating, hall_passes, participation } = dashboardData || {};

  return (
    <div className="teacher-dashboard">
      <Container fluid style={{ padding: '15px' }}>
        {/* Dashboard Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <div style={{ flex: 1 }}>
          </div>
          
          <div style={{ textAlign: 'center', flex: 2 }}>
            <Header as="h1" style={{ margin: '0 0 5px 0' }}>
              <Icon name="dashboard" color="blue" />
              Classroom Command Center
            </Header>
            <div style={{ 
              color: '#666', 
              fontSize: '0.9em', 
              fontWeight: 'normal',
              marginBottom: '0'
            }}>
              Real-time classroom management dashboard • Last updated: {lastUpdate?.toLocaleTimeString()}
            </div>
          </div>
          
          <div style={{ flex: 1, display: 'flex', justifyContent: 'flex-end' }}>
            <PerformanceMonitor />
          </div>
        </div>

        {/* Quick Stats Bar */}
        <Segment className="stats-bar" style={{ marginBottom: '20px' }}>
          <Statistic.Group size="small" widths="five">
            <Statistic>
              <Statistic.Value>
                <Icon name="users" />
                {quick_stats?.students_present || 0}
              </Statistic.Value>
              <Statistic.Label>Students Present</Statistic.Label>
            </Statistic>
            
            <Statistic color={getHallPassColor(quick_stats?.active_passes || 0)}>
              <Statistic.Value>
                <Icon name="id card" />
                {quick_stats?.active_passes || 0}
              </Statistic.Value>
              <Statistic.Label>Active Passes</Statistic.Label>
            </Statistic>
            
            <Statistic color={getFairnessColor(quick_stats?.fairness_score || 100)}>
              <Statistic.Value>
                {quick_stats?.fairness_score || 100}%
              </Statistic.Value>
              <Statistic.Label>Participation Fairness</Statistic.Label>
            </Statistic>
            
            <Statistic>
              <Statistic.Value>
                <Icon name="clock" />
                {quick_stats?.current_time || '--:--'}
              </Statistic.Value>
              <Statistic.Label>Current Time</Statistic.Label>
            </Statistic>

            <Statistic>
              <Statistic.Value>
                <Icon name="calendar" />
                {quick_stats?.day_of_week || 'Today'}
              </Statistic.Value>
              <Statistic.Label>{quick_stats?.current_date || 'Date'}</Statistic.Label>
            </Statistic>
          </Statistic.Group>
        </Segment>

        {/* Alerts Section */}
        {alerts && alerts.length > 0 && (
          <AlertsWidget alerts={alerts} />
        )}

        {/* Main Dashboard Grid - Compact 2 Column Layout */}
        <Grid columns={2} stackable style={{ margin: '0' }}>
          {/* Left Column - Monitoring & Status */}
          <Grid.Column width={8}>
            <SeatingWidget data={seating} />
            <HallPassWidget data={hall_passes} />
            <ParticipationWidget data={participation} />
          </Grid.Column>

          {/* Right Column - Tools & Actions */}
          <Grid.Column width={8}>
            <QuickActionsWidget contentUrl={contentUrl} />
            <TimerWidget />
            <SubstituteWidget contentUrl={contentUrl} />
          </Grid.Column>
        </Grid>

        {/* Footer with last update info */}
        <div style={{ textAlign: 'center', marginTop: '20px', color: '#666' }}>
          <small>
            Dashboard auto-refreshes every 30 seconds • 
            Last update: {lastUpdate ? lastUpdate.toLocaleString() : 'Never'}
            {error && (
              <span style={{ color: 'red' }}> • Warning: {error}</span>
            )}
          </small>
        </div>
      </Container>
    </div>
  );
};

export default TeacherDashboard; 