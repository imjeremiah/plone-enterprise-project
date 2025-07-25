/**
 * Seating Widget for Teacher Dashboard
 * 
 * Displays current seating chart information including:
 * - Active seating chart details
 * - Student count and arrangement status
 * - Quick access to seating management
 */

import React from 'react';
import PropTypes from 'prop-types';
import { Segment, Header, Icon, Statistic, Button, List, Message } from 'semantic-ui-react';

const SeatingWidget = ({ data }) => {
  if (!data) {
    return (
      <Segment className="dashboard-widget seating-widget">
        <Header as="h3">
          <Icon name="users" />
          <Header.Content>Current Seating</Header.Content>
        </Header>
        <Message info>
          <p>Loading seating information...</p>
        </Message>
      </Segment>
    );
  }

  const renderContent = () => {
    switch (data.status) {
      case 'no_charts':
        return (
          <Message warning>
            <Message.Header>No Seating Charts</Message.Header>
            <p>No seating arrangements found for today.</p>
            <Button size="small" primary>
              <Icon name="plus" />
              Create Seating Chart
            </Button>
          </Message>
        );

      case 'error':
        return (
          <Message negative>
            <Message.Header>Loading Error</Message.Header>
            <p>{data.message}</p>
          </Message>
        );

      case 'active':
        const chart = data.current_chart;
        return (
          <div>
            <Statistic size="small" style={{ marginBottom: '10px' }}>
              <Statistic.Value>
                <Icon name="user" />
                {chart.student_count}
              </Statistic.Value>
              <Statistic.Label>Students Seated</Statistic.Label>
            </Statistic>

            <div style={{ marginBottom: '10px' }}>
              <strong>Active Chart:</strong> {chart.title}
              <br />
              <small style={{ color: '#666' }}>
                Last updated: {new Date(chart.last_modified).toLocaleDateString()}
              </small>
            </div>

            {data.students && data.students.length > 0 && (
              <div style={{ marginBottom: '10px' }}>
                <strong>Recent Students:</strong>
                <List size="small" style={{ marginTop: '5px' }}>
                  {data.students.slice(0, 5).map((student, index) => (
                    <List.Item key={index}>
                      <Icon name="user outline" />
                      <List.Content>{student}</List.Content>
                    </List.Item>
                  ))}
                  {data.students.length > 5 && (
                    <List.Item>
                      <List.Content style={{ fontStyle: 'italic' }}>
                        ...and {data.students.length - 5} more
                      </List.Content>
                    </List.Item>
                  )}
                </List>
              </div>
            )}

            <div style={{ display: 'flex', gap: '10px' }}>
              <Button size="small" basic>
                <Icon name="eye" />
                View Chart
              </Button>
              <Button size="small" basic>
                <Icon name="edit" />
                Modify
              </Button>
            </div>

            {data.total_charts > 1 && (
              <div style={{ marginTop: '10px', fontSize: '0.9em', color: '#666' }}>
                {data.total_charts} total seating charts available
              </div>
            )}
          </div>
        );

      default:
        return (
          <Message>
            <p>Unknown seating status</p>
          </Message>
        );
    }
  };

  return (
    <Segment className="dashboard-widget seating-widget" style={{ marginBottom: '20px' }}>
      <Header as="h3">
        <Icon name="users" color="blue" />
        <Header.Content>
          Current Seating
          <Header.Subheader>Classroom arrangement status</Header.Subheader>
        </Header.Content>
      </Header>
      {renderContent()}
    </Segment>
  );
};

SeatingWidget.propTypes = {
  data: PropTypes.shape({
    status: PropTypes.string,
    message: PropTypes.string,
    current_chart: PropTypes.shape({
      title: PropTypes.string,
      student_count: PropTypes.number,
      last_modified: PropTypes.string,
      url: PropTypes.string,
      id: PropTypes.string
    }),
    total_charts: PropTypes.number,
    students: PropTypes.arrayOf(PropTypes.string)
  })
};

export default SeatingWidget; 