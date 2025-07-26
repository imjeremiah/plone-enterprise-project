/**
 * Participation Widget for Teacher Dashboard
 *
 * Displays participation statistics from the random student picker:
 * - Fairness score showing distribution balance
 * - Total picks and unique students called
 * - Most and least picked students
 * - Visual indicators for participation equity
 */

import React from 'react';
import PropTypes from 'prop-types';
import {
  Segment,
  Header,
  Icon,
  Progress,
  Statistic,
  List,
  Message,
  Button,
} from 'semantic-ui-react';

const ParticipationWidget = ({ data }) => {
  if (!data) {
    return (
      <Segment className="dashboard-widget participation-widget">
        <Header as="h3">
          <Icon name="balance scale" />
          <Header.Content>Participation Tracking</Header.Content>
        </Header>
        <Message info>
          <p>Loading participation data...</p>
        </Message>
      </Segment>
    );
  }

  /**
   * Get color for fairness score
   */
  const getFairnessColor = (score) => {
    if (score >= 80) return 'green';
    if (score >= 60) return 'yellow';
    return 'red';
  };

  /**
   * Get progress color for fairness bar
   */
  const getProgressColor = (score) => {
    if (score >= 80) return 'green';
    if (score >= 60) return 'orange';
    return 'red';
  };

  const renderContent = () => {
    switch (data.status) {
      case 'no_data':
        return (
          <Message info>
            <Message.Header>No Data Yet</Message.Header>
            <p>
              No students have been picked today. Use the random picker to start
              tracking participation.
            </p>
            <Button size="small" primary>
              <Icon name="random" />
              Open Random Picker
            </Button>
          </Message>
        );

      case 'error':
        return (
          <Message negative>
            <Message.Header>Error Loading Data</Message.Header>
            <p>Unable to load participation statistics.</p>
          </Message>
        );

      case 'active':
        return (
          <div>
            {/* Fairness Score */}
            <div style={{ marginBottom: '15px', textAlign: 'center' }}>
              <Statistic
                size="small"
                color={getFairnessColor(data.fairness_score)}
              >
                <Statistic.Value>{data.fairness_score}%</Statistic.Value>
                <Statistic.Label>Fairness Score</Statistic.Label>
              </Statistic>
              <Progress
                percent={data.fairness_score}
                color={getProgressColor(data.fairness_score)}
                size="small"
                style={{ marginTop: '10px' }}
              />
            </div>

            {/* Quick Stats */}
            <div
              style={{
                marginBottom: '10px',
                display: 'flex',
                gap: '15px',
                justifyContent: 'center',
              }}
            >
              <Statistic size="mini">
                <Statistic.Value>{data.total_picks}</Statistic.Value>
                <Statistic.Label>Total Picks</Statistic.Label>
              </Statistic>
              <Statistic size="mini">
                <Statistic.Value>{data.unique_students}</Statistic.Value>
                <Statistic.Label>Students Called</Statistic.Label>
              </Statistic>
            </div>

            {/* Most/Least Picked */}
            {(data.most_picked || data.least_picked) && (
              <div style={{ marginBottom: '10px' }}>
                <List size="small">
                  {data.most_picked && (
                    <List.Item>
                      <List.Icon name="arrow up" color="red" />
                      <List.Content>
                        <List.Header>Most Called</List.Header>
                        <List.Description>
                          {data.most_picked.name} ({data.most_picked.count}{' '}
                          times)
                        </List.Description>
                      </List.Content>
                    </List.Item>
                  )}
                  {data.least_picked && (
                    <List.Item>
                      <List.Icon name="arrow down" color="green" />
                      <List.Content>
                        <List.Header>Least Called</List.Header>
                        <List.Description>
                          {data.least_picked.name} ({data.least_picked.count}{' '}
                          times)
                        </List.Description>
                      </List.Content>
                    </List.Item>
                  )}
                </List>
              </div>
            )}

            {/* Fairness Assessment */}
            {data.fairness_score < 70 && (
              <Message warning size="small">
                <Icon name="balance scale" />
                Consider using the random picker more to improve participation
                balance.
              </Message>
            )}

            {data.fairness_score >= 90 && (
              <Message positive size="small">
                <Icon name="checkmark" />
                Excellent participation balance!
              </Message>
            )}

            {/* Distribution Preview */}
            {data.distribution && Object.keys(data.distribution).length > 0 && (
              <div style={{ marginTop: '10px' }}>
                <small style={{ color: '#666' }}>
                  <strong>Today's Distribution:</strong>
                </small>
                <div style={{ marginTop: '5px', fontSize: '0.8em' }}>
                  {Object.entries(data.distribution)
                    .slice(0, 3)
                    .map(([name, count]) => (
                      <span
                        key={name}
                        style={{ marginRight: '10px', color: '#666' }}
                      >
                        {name}: {count}
                      </span>
                    ))}
                  {Object.keys(data.distribution).length > 3 && '...'}
                </div>
              </div>
            )}
          </div>
        );

      default:
        return (
          <Message>
            <p>Unknown participation status</p>
          </Message>
        );
    }
  };

  return (
    <Segment
      className="dashboard-widget participation-widget"
      style={{ marginBottom: '20px' }}
    >
      <Header as="h3">
        <Icon name="balance scale" color="purple" />
        <Header.Content>
          Participation Tracking
          <Header.Subheader>
            Random picker fairness & engagement
          </Header.Subheader>
        </Header.Content>
      </Header>
      {renderContent()}
    </Segment>
  );
};

ParticipationWidget.propTypes = {
  data: PropTypes.shape({
    status: PropTypes.string,
    total_picks: PropTypes.number,
    unique_students: PropTypes.number,
    fairness_score: PropTypes.number,
    most_picked: PropTypes.shape({
      name: PropTypes.string,
      count: PropTypes.number,
    }),
    least_picked: PropTypes.shape({
      name: PropTypes.string,
      count: PropTypes.number,
    }),
    distribution: PropTypes.object,
  }),
};

export default ParticipationWidget;
