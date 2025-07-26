/**
 * Timer Page for Classroom Management
 *
 * Main timer interface showing both full and compact timer modes
 * for classroom time management.
 */

import React from 'react';
import { Container, Grid, Segment, Header, Message } from 'semantic-ui-react';
import LessonTimer from './LessonTimer';
import TimerWidget from './TimerWidget';

const TimerPage = () => {
  return (
    <Container fluid style={{ padding: '20px' }}>
      <Header as="h1" textAlign="center">
        Lesson Timer
      </Header>

      <Message info>
        <Message.Header>Classroom Timer Tool</Message.Header>
        <p>
          Visual and audio alerts for classroom activities with localStorage
          persistence and fullscreen mode for easy visibility.
        </p>
      </Message>

      <Grid columns={2} stackable>
        <Grid.Column>
          <Segment>
            <Header as="h2">Full Timer Mode</Header>
            <p>
              Complete timer with fullscreen mode, audio alerts, and
              persistence.
            </p>

            <div style={{ marginTop: '20px' }}>
              <LessonTimer />
            </div>
          </Segment>
        </Grid.Column>

        <Grid.Column>
          <Segment>
            <Header as="h2">Compact Widget Mode</Header>
            <p>Simplified timer for dashboard integration.</p>

            <div style={{ marginTop: '20px' }}>
              <TimerWidget title="Dashboard Timer" />
            </div>
          </Segment>
        </Grid.Column>
      </Grid>
    </Container>
  );
};

export default TimerPage;
