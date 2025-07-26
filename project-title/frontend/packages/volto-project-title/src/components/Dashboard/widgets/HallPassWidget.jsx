/**
 * Hall Pass Widget for Teacher Dashboard
 *
 * Displays active hall passes with real-time duration tracking:
 * - List of students currently out of class
 * - Duration each student has been out
 * - Color-coded alert levels for long durations
 * - Quick statistics on daily pass usage
 */

import React from 'react';
import PropTypes from 'prop-types';
import {
  Segment,
  Header,
  Icon,
  Label,
  List,
  Message,
  Statistic,
} from 'semantic-ui-react';

const HallPassWidget = ({ data }) => {
  if (!data) {
    return (
      <Segment className="dashboard-widget hall-pass-widget">
        <Header as="h3">
          <Icon name="id card" />
          <Header.Content>Active Hall Passes</Header.Content>
        </Header>
        <Message info>
          <p>Loading hall pass information...</p>
        </Message>
      </Segment>
    );
  }

  /**
   * Get color for pass duration label
   */
  const getDurationColor = (alertLevel) => {
    switch (alertLevel) {
      case 'red':
        return 'red';
      case 'yellow':
        return 'yellow';
      case 'green':
      default:
        return 'green';
    }
  };

  /**
   * Format duration for display
   */
  const formatDuration = (minutes) => {
    if (minutes < 60) {
      return `${minutes} min`;
    }
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    return `${hours}h ${remainingMinutes}m`;
  };

  const { active_count, total_today, passes } = data;

  return (
    <Segment
      className="dashboard-widget hall-pass-widget"
      style={{ marginBottom: '20px' }}
    >
      <Header as="h3">
        <Icon name="id card" color="orange" />
        <Header.Content>
          Active Hall Passes
          <Header.Subheader>Students currently out of class</Header.Subheader>
        </Header.Content>
      </Header>

      {/* Quick Stats */}
      <div style={{ marginBottom: '10px', display: 'flex', gap: '15px' }}>
        <Statistic size="mini">
          <Statistic.Value>{active_count}</Statistic.Value>
          <Statistic.Label>Currently Out</Statistic.Label>
        </Statistic>
        <Statistic size="mini">
          <Statistic.Value>{total_today}</Statistic.Value>
          <Statistic.Label>Issued Today</Statistic.Label>
        </Statistic>
      </div>

      {/* Active Passes List */}
      {active_count === 0 ? (
        <Message positive>
          <Icon name="check circle" />
          All students are in class
        </Message>
      ) : (
        <div>
          <List divided relaxed>
            {passes.map((pass) => (
              <List.Item key={pass.id}>
                <List.Content>
                  <List.Header
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                    }}
                  >
                    <span>
                      <Icon name="user" />
                      {pass.student}
                    </span>
                    <Label
                      color={getDurationColor(pass.alert_level)}
                      size="small"
                    >
                      {formatDuration(pass.duration)}
                    </Label>
                  </List.Header>
                  <List.Description style={{ marginTop: '5px' }}>
                    <Icon name="map marker" />
                    {pass.destination}
                    <span style={{ marginLeft: '15px', color: '#666' }}>
                      <Icon name="clock" />
                      Since{' '}
                      {new Date(pass.issue_time).toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </span>
                  </List.Description>
                </List.Content>
              </List.Item>
            ))}
          </List>

          {/* Alert Summary */}
          {data.alerts && data.alerts.length > 0 && (
            <Message warning style={{ marginTop: '10px' }}>
              <Message.Header>
                <Icon name="warning sign" />
                Attention Required
              </Message.Header>
              <p>
                {data.alerts.length} student{data.alerts.length > 1 ? 's' : ''}{' '}
                ha{data.alerts.length > 1 ? 've' : 's'} been out for an extended
                time.
              </p>
            </Message>
          )}
        </div>
      )}
    </Segment>
  );
};

HallPassWidget.propTypes = {
  data: PropTypes.shape({
    active_count: PropTypes.number,
    total_today: PropTypes.number,
    passes: PropTypes.arrayOf(
      PropTypes.shape({
        id: PropTypes.string,
        student: PropTypes.string,
        destination: PropTypes.string,
        duration: PropTypes.number,
        alert_level: PropTypes.string,
        issue_time: PropTypes.string,
        url: PropTypes.string,
      }),
    ),
    alerts: PropTypes.array,
  }),
};

export default HallPassWidget;
