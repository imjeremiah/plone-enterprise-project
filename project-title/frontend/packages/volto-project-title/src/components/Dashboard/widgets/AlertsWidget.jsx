/**
 * Alerts Widget for Teacher Dashboard
 *
 * Displays real-time classroom alerts including:
 * - Hall pass duration warnings
 * - Participation fairness notifications
 * - System reminders and end-of-day tasks
 * - Emergency or critical alerts
 */

import React from 'react';
import PropTypes from 'prop-types';
import { Message, Icon, Button, List } from 'semantic-ui-react';

const AlertsWidget = ({ alerts = [] }) => {
  /**
   * Get message color based on alert type and priority
   */
  const getMessageProps = (alert) => {
    switch (alert.type) {
      case 'warning':
        return { warning: true, icon: 'exclamation triangle' };
      case 'error':
        return { negative: true, icon: 'warning sign' };
      case 'info':
        return { info: true, icon: 'info circle' };
      default:
        return { info: true, icon: 'bell' };
    }
  };

  /**
   * Group alerts by priority for better organization
   */
  const groupedAlerts = alerts.reduce((acc, alert) => {
    const priority = alert.priority || 'medium';
    if (!acc[priority]) acc[priority] = [];
    acc[priority].push(alert);
    return acc;
  }, {});

  if (alerts.length === 0) {
    return null; // Don't render if no alerts
  }

  return (
    <div className="alerts-widget" style={{ marginBottom: '15px' }}>
      {/* High Priority Alerts */}
      {groupedAlerts.high &&
        groupedAlerts.high.map((alert, index) => (
          <Message
            key={`high-${index}`}
            {...getMessageProps(alert)}
            style={{ marginBottom: '10px' }}
          >
            <Message.Header>
              <Icon name={alert.icon || 'exclamation triangle'} />
              {alert.title}
            </Message.Header>
            <p>{alert.message}</p>
            {alert.action && (
              <Button
                size="small"
                color={alert.type === 'warning' ? 'orange' : 'blue'}
                style={{ marginTop: '5px' }}
              >
                {alert.action}
              </Button>
            )}
          </Message>
        ))}

      {/* Medium and Low Priority Alerts in Compact Format */}
      {(groupedAlerts.medium || groupedAlerts.low) && (
        <Message info style={{ marginBottom: '10px' }}>
          <Message.Header>
            <Icon name="bell" />
            Classroom Notifications
          </Message.Header>
          <List>
            {[
              ...(groupedAlerts.medium || []),
              ...(groupedAlerts.low || []),
            ].map((alert, index) => (
              <List.Item key={`other-${index}`}>
                <List.Icon name={alert.icon || 'circle'} />
                <List.Content>
                  <List.Header>{alert.title}</List.Header>
                  <List.Description>
                    {alert.message}
                    {alert.action && (
                      <span
                        style={{
                          marginLeft: '10px',
                          color: '#2185d0',
                          cursor: 'pointer',
                        }}
                      >
                        → {alert.action}
                      </span>
                    )}
                  </List.Description>
                </List.Content>
              </List.Item>
            ))}
          </List>
        </Message>
      )}
    </div>
  );
};

AlertsWidget.propTypes = {
  alerts: PropTypes.arrayOf(
    PropTypes.shape({
      type: PropTypes.oneOf(['warning', 'error', 'info']),
      priority: PropTypes.oneOf(['high', 'medium', 'low']),
      icon: PropTypes.string,
      title: PropTypes.string.isRequired,
      message: PropTypes.string.isRequired,
      action: PropTypes.string,
      timestamp: PropTypes.string,
      category: PropTypes.string,
    }),
  ),
};

export default AlertsWidget;
