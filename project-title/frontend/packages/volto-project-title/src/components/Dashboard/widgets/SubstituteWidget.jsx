/**
 * Substitute Widget for Teacher Dashboard
 *
 * Emergency preparation and substitute folder management:
 * - Quick access to substitute folder generator
 * - Reminders about preparation
 * - Status of existing substitute materials
 * - Emergency contact information
 */

import React, { useState } from 'react';
import PropTypes from 'prop-types';
import {
  Segment,
  Header,
  Icon,
  Button,
  Message,
  List,
} from 'semantic-ui-react';

const SubstituteWidget = ({ contentUrl }) => {
  const [generating, setGenerating] = useState(false);

  /**
   * Quick generate substitute folder
   */
  const quickGenerate = async () => {
    setGenerating(true);
    try {
      // Open substitute folder generator
      window.open('/substitute-folder', '_blank');
    } catch (error) {
      console.error('Failed to open substitute folder generator:', error);
    } finally {
      setGenerating(false);
    }
  };

  /**
   * Get current time-based recommendations
   */
  const getTimeBasedMessage = () => {
    const hour = new Date().getHours();

    if (hour >= 15) {
      // After 3 PM
      return {
        type: 'info',
        icon: 'clock',
        title: 'End of Day Reminder',
        message: 'Consider preparing substitute materials for tomorrow.',
        urgent: false,
      };
    } else if (hour >= 12) {
      // Afternoon
      return {
        type: 'info',
        icon: 'folder',
        title: 'Preparation Tip',
        message: 'Having substitute materials ready reduces stress.',
        urgent: false,
      };
    } else {
      return {
        type: 'positive',
        icon: 'checkmark',
        title: 'Ready to Go',
        message: 'Classroom management tools are available when needed.',
        urgent: false,
      };
    }
  };

  const timeMessage = getTimeBasedMessage();

  return (
    <Segment className="dashboard-widget substitute-widget">
      <Header as="h3">
        <Icon name="folder open" color="teal" />
        <Header.Content>
          Emergency Prep
          <Header.Subheader>Substitute teacher materials</Header.Subheader>
        </Header.Content>
      </Header>

      {/* Time-based Message */}
      <Message
        size="small"
        info={timeMessage.type === 'info'}
        positive={timeMessage.type === 'positive'}
        style={{ marginBottom: '10px' }}
      >
        <Message.Header>
          <Icon name={timeMessage.icon} />
          {timeMessage.title}
        </Message.Header>
        <p>{timeMessage.message}</p>
      </Message>

      {/* Quick Actions */}
      <div style={{ marginBottom: '10px' }}>
        <Button
          primary
          fluid
          size="small"
          loading={generating}
          onClick={quickGenerate}
          style={{ marginBottom: '10px' }}
        >
          <Icon name="magic" />
          Generate Substitute Folder
        </Button>

        <Button
          basic
          fluid
          size="small"
          onClick={() => window.open('/substitute-folder', '_blank')}
        >
          <Icon name="settings" />
          Advanced Options
        </Button>
      </div>

      {/* What's Included Preview */}
      <div style={{ fontSize: '0.8em' }}>
        <strong style={{ color: '#666' }}>Emergency folder includes:</strong>
        <List size="small" style={{ marginTop: '5px' }}>
          <List.Item>
            <List.Icon name="calendar" />
            <List.Content>Daily schedule & timing</List.Content>
          </List.Item>
          <List.Item>
            <List.Icon name="users" />
            <List.Content>Current seating arrangements</List.Content>
          </List.Item>
          <List.Item>
            <List.Icon name="warning sign" />
            <List.Content>Emergency procedures</List.Content>
          </List.Item>
          <List.Item>
            <List.Icon name="phone" />
            <List.Content>Important contacts</List.Content>
          </List.Item>
        </List>
      </div>

      {/* Emergency Note */}
      <div
        style={{
          marginTop: '10px',
          padding: '6px',
          backgroundColor: '#fff3cd',
          borderRadius: '4px',
          fontSize: '0.7em',
          textAlign: 'center',
          color: '#856404',
        }}
      >
        <Icon name="heart" />
        Preparation reduces stress
      </div>
    </Segment>
  );
};

SubstituteWidget.propTypes = {
  contentUrl: PropTypes.string,
};

export default SubstituteWidget;
