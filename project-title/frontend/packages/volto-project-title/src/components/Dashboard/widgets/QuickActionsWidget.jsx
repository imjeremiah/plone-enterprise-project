/**
 * Quick Actions Widget for Teacher Dashboard
 * 
 * Provides quick access to common classroom management tasks:
 * - Issue new hall pass
 * - Create/modify seating chart
 * - Use random student picker
 * - Generate substitute folder
 * - Start lesson timer
 */

import React from 'react';
import PropTypes from 'prop-types';
import { Segment, Header, Icon, Button, Grid } from 'semantic-ui-react';

const QuickActionsWidget = ({ contentUrl }) => {
  /**
   * Handle quick action clicks
   */
  const handleAction = (action) => {
    switch (action) {
      case 'hall_pass':
        // Navigate to hall pass creation
        window.open('/hall-pass-manager', '_blank');
        break;
      case 'seating':
        // Navigate to seating chart
        window.open('/seating-chart', '_blank');
        break;
      case 'picker':
        // Navigate to random picker
        window.open('/random-picker', '_blank');
        break;
      case 'substitute':
        // Navigate to substitute folder generator
        window.open('/substitute-folder', '_blank');
        break;
      case 'timer':
        // Navigate to timer
        window.open('/timer', '_blank');
        break;
      default:
        console.log('Unknown action:', action);
    }
  };

  return (
    <Segment className="dashboard-widget quick-actions-widget">
      <Header as="h3">
        <Icon name="lightning" color="yellow" />
        <Header.Content>
          Quick Actions
          <Header.Subheader>Common classroom tasks</Header.Subheader>
        </Header.Content>
      </Header>

      <Grid columns={2} stackable>
        <Grid.Column>
          <Button 
            fluid 
            size="small" 
            color="orange"
            onClick={() => handleAction('hall_pass')}
            style={{ marginBottom: '8px' }}
          >
            <Icon name="id card" />
            Issue Hall Pass
          </Button>
        </Grid.Column>
        
        <Grid.Column>
          <Button 
            fluid 
            size="small" 
            color="blue"
            onClick={() => handleAction('seating')}
            style={{ marginBottom: '8px' }}
          >
            <Icon name="users" />
            Seating Chart
          </Button>
        </Grid.Column>

        <Grid.Column>
          <Button 
            fluid 
            size="small" 
            color="purple"
            onClick={() => handleAction('picker')}
            style={{ marginBottom: '8px' }}
          >
            <Icon name="random" />
            Pick Student
          </Button>
        </Grid.Column>

        <Grid.Column>
          <Button 
            fluid 
            size="small" 
            color="green"
            onClick={() => handleAction('timer')}
            style={{ marginBottom: '8px' }}
          >
            <Icon name="clock" />
            Start Timer
          </Button>
        </Grid.Column>

        <Grid.Column width={16}>
          <Button 
            fluid 
            size="small" 
            color="teal"
            onClick={() => handleAction('substitute')}
          >
            <Icon name="folder" />
            Generate Substitute Folder
          </Button>
        </Grid.Column>
      </Grid>

      {/* Usage Hints */}
      <div style={{ marginTop: '10px', fontSize: '0.75em', color: '#666', textAlign: 'center' }}>
        <Icon name="info circle" />
        Quick access to all tools
      </div>
    </Segment>
  );
};

QuickActionsWidget.propTypes = {
  contentUrl: PropTypes.string
};

export default QuickActionsWidget; 