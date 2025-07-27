/**
 * Hall Pass Manager Component for Classroom Management
 *
 * Provides interface for issuing, tracking, and managing digital hall passes
 * with QR codes and real-time time tracking.
 */

import React, { useState, useEffect, useCallback } from 'react';
import PropTypes from 'prop-types';
import {
  Container,
  Segment,
  Header,
  Button,
  Grid,
  Icon,
  Message,
  Label,
  Modal,
  Form,
  Card,
  Statistic,
  List,
  Alert,
} from 'semantic-ui-react';
import PassCard from './PassCard';
import './HallPassManager.css';

// Client-only wrapper to prevent SSR issues
const ClientOnly = ({ children, fallback = null }) => {
  const [hasMounted, setHasMounted] = useState(false);

  useEffect(() => {
    setHasMounted(true);
  }, []);

  if (!hasMounted) {
    return fallback;
  }

  return children;
};

const HallPassManagerComponent = ({
  contentUrl,
  title = 'Digital Hall Pass Manager',
}) => {
  const [activePasses, setActivePasses] = useState([]);
  const [recentPasses, setRecentPasses] = useState([]);
  const [alerts, setAlerts] = useState([]);

  // Get proper base URL for API calls - support both dev and Docker modes
  const getBaseUrl = () => {
    if (contentUrl) {
      return contentUrl;
    }
    
    // If we're on project-title.localhost (Docker), use relative path via Traefik
    if (
      typeof window !== 'undefined' &&
      window.location.hostname === 'project-title.localhost'
    ) {
      return '/Plone'; // Relative path - Traefik will route to backend
    }
    
    // Otherwise use localhost fallback for development
    return 'http://localhost:8080/Plone';
  };

  const baseUrl = getBaseUrl();
  const [showIssueModal, setShowIssueModal] = useState(false);
  const [newPass, setNewPass] = useState({
    student_name: '',
    destination: 'Restroom',
    expected_duration: 5,
    notes: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(null);

  // Destination options
  const destinationOptions = [
    { key: 'restroom', value: 'Restroom', text: 'Restroom' },
    { key: 'office', value: 'Office', text: 'Main Office' },
    { key: 'nurse', value: 'Nurse', text: "Nurse's Office" },
    { key: 'library', value: 'Library', text: 'Library' },
    { key: 'guidance', value: 'Guidance', text: 'Guidance Counselor' },
    { key: 'principal', value: 'Principal', text: "Principal's Office" },
    { key: 'locker', value: 'Locker', text: 'Locker' },
    { key: 'water', value: 'Water', text: 'Water Fountain' },
    { key: 'technology', value: 'Technology', text: 'Technology Support' },
    { key: 'other', value: 'Other', text: 'Other (see notes)' },
  ];

  /**
   * Load hall pass data from backend
   */
  const loadPassData = useCallback(async () => {
    if (!baseUrl) return;

    try {
      const response = await fetch(`${baseUrl}/@@hall-pass-data?ajax_data=1`, {
        method: 'GET',
        headers: { Accept: 'application/json' },
        credentials: 'include',
      });

      if (response.ok) {
        const data = await response.json();
        setActivePasses(data.active_passes || []);
        setRecentPasses(data.recent_passes || []);
        setAlerts(data.alerts || []);
        setLastUpdate(new Date());
      }
    } catch (error) {
      console.warn('Failed to load hall pass data:', error);
      // Set empty state on error
      setActivePasses([]);
      setRecentPasses([]);
      setAlerts([]);
    }
  }, [baseUrl]);

  // Initial load and periodic refresh
  useEffect(() => {
    loadPassData();

    // Refresh every 30 seconds
    const interval = setInterval(loadPassData, 30000);

    return () => clearInterval(interval);
  }, [loadPassData]);

  /**
   * Issue a new hall pass
   */
  const issuePass = async () => {
    if (!newPass.student_name.trim()) {
      alert('Please enter a student name');
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch(`${baseUrl}/@@hall-pass-manager`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        body: JSON.stringify(newPass),
        credentials: 'include',
      });

      if (response.ok) {
        const result = await response.json();

        if (result.success) {
          // Add new pass to active passes
          setActivePasses((prev) => [result.pass, ...prev]);

          // Reset form
          setNewPass({
            student_name: '',
            destination: 'Restroom',
            expected_duration: 5,
            notes: '',
          });

          setShowIssueModal(false);

          // Play success sound
          playNotificationSound('pass-issued');
        } else {
          alert(`Failed to issue pass: ${result.error}`);
        }
      } else {
        alert('Failed to issue pass. Please try again.');
      }
    } catch (error) {
      console.error('Error issuing pass:', error);
      alert('Error issuing pass. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Return a hall pass
   */
  const returnPass = async (passData) => {
    if (!baseUrl || !passData?.id) {
      console.error('Missing baseUrl or pass ID');
      alert('Invalid pass data. Please refresh and try again.');
      return;
    }

    try {
      const response = await fetch(`${baseUrl}/@@return-pass`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        body: JSON.stringify({ pass_id: passData.id }),
        credentials: 'include',
      });

      if (response.ok) {
        const result = await response.json();

        if (result.success) {
          // Remove from active passes
          setActivePasses((prev) => prev.filter((p) => p.id !== passData.id));

          // Add to recent passes
          setRecentPasses((prev) => [result.pass, ...prev.slice(0, 9)]);

          // Play return sound
          playNotificationSound('pass-returned');
        } else {
          alert(`Failed to return pass: ${result.error || 'Unknown error'}`);
        }
      } else {
        console.error('Server error returning pass:', response.status);
        alert('Server error. Please try again.');
      }
    } catch (error) {
      console.error('Error returning pass:', error);
      alert('Network error. Please try again.');
    }
  };

  /**
   * Play notification sounds - DISABLED (sounds not needed)
   */
  const playNotificationSound = (type) => {
    // Sound functionality disabled - no sounds needed
    return;
  };

  /**
   * Get alert color
   */
  const getAlertColor = (type) => {
    switch (type) {
      case 'danger':
        return 'red';
      case 'warning':
        return 'yellow';
      case 'info':
        return 'blue';
      default:
        return 'grey';
    }
  };

  /**
   * Render statistics
   */
  const renderStatistics = () => {
    const overdueCount = activePasses.filter(
      (p) => p.alert_level === 'red',
    ).length;

    // Calculate average duration safely
    const validDurations = activePasses
      .map((p) => p.duration_minutes)
      .filter((d) => d !== undefined && d !== null && !isNaN(d));

    const averageDuration =
      validDurations.length > 0
        ? Math.round(
            validDurations.reduce((sum, d) => sum + d, 0) /
              validDurations.length,
          )
        : 0;

    return (
      <Segment>
        <Header as="h3">
          <Icon name="chart bar" />
          Hall Pass Statistics
        </Header>

        <Statistic.Group widths="three" size="small">
          <Statistic color="blue">
            <Statistic.Value>{activePasses.length}</Statistic.Value>
            <Statistic.Label>Active</Statistic.Label>
          </Statistic>

          <Statistic color={overdueCount > 0 ? 'red' : 'green'}>
            <Statistic.Value>{overdueCount}</Statistic.Value>
            <Statistic.Label>Overdue</Statistic.Label>
          </Statistic>

          <Statistic>
            <Statistic.Value>{averageDuration || 0}</Statistic.Value>
            <Statistic.Label>Avg. Minutes</Statistic.Label>
          </Statistic>
        </Statistic.Group>

        {lastUpdate && (
          <div className="last-update">
            <Icon name="refresh" />
            Last updated: {lastUpdate.toLocaleTimeString()}
          </div>
        )}
      </Segment>
    );
  };

  /**
   * Render alerts
   */
  const renderAlerts = () => {
    if (alerts.length === 0) return null;

    return (
      <Segment color="orange">
        <Header as="h4">
          <Icon name="warning" />
          Alerts
        </Header>

        <List>
          {alerts.map((alert, index) => (
            <List.Item key={index}>
              <Label color={getAlertColor(alert.type)} size="small">
                {alert.type.toUpperCase()}
              </Label>
              {alert.message}
            </List.Item>
          ))}
        </List>
      </Segment>
    );
  };

  /**
   * Render issue pass modal
   */
  const renderIssueModal = () => (
    <Modal open={showIssueModal} onClose={() => setShowIssueModal(false)}>
      <Modal.Header>
        <Icon name="plus" />
        Issue Hall Pass
      </Modal.Header>

      <Modal.Content>
        <Form>
          <Form.Input
            label="Student Name"
            value={newPass.student_name}
            onChange={(e, { value }) =>
              setNewPass({ ...newPass, student_name: value })
            }
            placeholder="Enter student name"
            required
          />

          <Form.Select
            label="Destination"
            value={newPass.destination}
            options={destinationOptions}
            onChange={(e, { value }) =>
              setNewPass({ ...newPass, destination: value })
            }
          />

          <Form.Input
            label="Expected Duration (minutes)"
            type="number"
            value={newPass.expected_duration}
            onChange={(e, { value }) =>
              setNewPass({
                ...newPass,
                expected_duration: parseInt(value) || 5,
              })
            }
            min={1}
            max={60}
          />

          <Form.TextArea
            label="Notes (optional)"
            value={newPass.notes}
            onChange={(e, { value }) =>
              setNewPass({ ...newPass, notes: value })
            }
            placeholder="Any additional notes..."
            rows={2}
          />
        </Form>
      </Modal.Content>

      <Modal.Actions>
        <Button onClick={() => setShowIssueModal(false)}>Cancel</Button>
        <Button primary loading={isLoading} onClick={issuePass}>
          <Icon name="plus" />
          Issue Pass
        </Button>
      </Modal.Actions>
    </Modal>
  );

  return (
    <Container fluid className="hall-pass-manager">
      <div className="main-header">
        <h1 className="main-title">
          <Icon name="id card" />
          {title}
        </h1>
        <p className="main-subtitle">
          Digital hall pass system with QR codes and time tracking
        </p>
        <hr className="title-divider" />
      </div>

      <Grid columns={2} stackable centered>
        <Grid.Column width={10}>
          {/* Issue Pass Button */}
          <Segment clearing>
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
            >
              <Header as="h3" style={{ margin: 0 }}>
                Active Hall Passes
              </Header>
              <Button
                primary
                size="large"
                onClick={() => setShowIssueModal(true)}
              >
                <Icon name="plus" />
                Issue Hall Pass
              </Button>
            </div>
          </Segment>

          {/* Alerts */}
          {renderAlerts()}

          {/* Active Passes */}
          {activePasses.length > 0 ? (
            <div className="active-passes">
              {activePasses.map((pass) => (
                <PassCard
                  key={pass.id}
                  pass={pass}
                  onReturn={() => returnPass(pass)}
                />
              ))}
            </div>
          ) : (
            <Message info>
              <Icon name="info circle" />
              No active hall passes
            </Message>
          )}

          {/* Recent Passes */}
          {recentPasses.length > 0 && (
            <Segment>
              <Header as="h3">Recently Returned</Header>
              <div className="recent-passes">
                {recentPasses.slice(0, 5).map((pass) => (
                  <PassCard
                    key={pass.id}
                    pass={pass}
                    showReturnButton={false}
                    compact={true}
                  />
                ))}
              </div>
            </Segment>
          )}
        </Grid.Column>

        <Grid.Column width={6}>{renderStatistics()}</Grid.Column>
      </Grid>

      {renderIssueModal()}
    </Container>
  );
};

HallPassManagerComponent.propTypes = {
  contentUrl: PropTypes.string,
  title: PropTypes.string,
};

// Wrapper with client-only rendering
const HallPassManager = (props) => (
  <ClientOnly
    fallback={
      <Container fluid style={{ textAlign: 'center', padding: '40px' }}>
        <Header as="h1" dividing textAlign="center">
          <Icon name="id card" />
          <Header.Content>
            Digital Hall Pass Manager
            <Header.Subheader>Loading...</Header.Subheader>
          </Header.Content>
        </Header>
      </Container>
    }
  >
    <HallPassManagerComponent {...props} />
  </ClientOnly>
);

export default HallPassManager;
