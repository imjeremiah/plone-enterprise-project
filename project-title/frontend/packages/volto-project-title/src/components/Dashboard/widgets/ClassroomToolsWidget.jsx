/**
 * Classroom Tools Widget for Homepage Navigation
 *
 * Provides quick access to all classroom management features
 * from the main homepage.
 */

import React from 'react';
import { Link } from 'react-router-dom';
import {
  Container,
  Grid,
  Card,
  Header,
  Icon,
  Button,
  Segment,
} from 'semantic-ui-react';
import './ClassroomToolsWidget.css';

const ClassroomToolsWidget = () => {
  const tools = [
    {
      title: 'Dashboard',
      description: 'Real-time classroom command center',
      icon: 'home',
      color: 'blue',
      url: '/dashboard',
    },
    {
      title: 'Hall Pass Manager',
      description: 'Digital hall passes with QR codes',
      icon: 'user',
      color: 'green',
      url: '/hall-pass-manager',
    },
    {
      title: 'Random Student Picker',
      description: 'Fair student selection with history',
      icon: 'random',
      color: 'purple',
      url: '/random-picker',
    },
    {
      title: 'Seating Charts',
      description: 'Interactive drag-drop seating',
      icon: 'sitemap',
      color: 'orange',
      url: '/seating-charts',
    },
    {
      title: 'Lesson Timer',
      description: 'Activity timing for classroom management',
      icon: 'clock',
      color: 'teal',
      url: '/timer',
    },
    {
      title: 'Substitute Folder',
      description: 'Emergency materials generator',
      icon: 'folder open',
      color: 'red',
      url: '/substitute-folder',
    },
  ];

  return (
    <Container className="classroom-tools-widget">
      <Segment padded="very">
        <div
          className="header-section"
          style={{ textAlign: 'center', marginBottom: '2rem' }}
        >
          <Icon name="graduation cap" size="large" color="blue" />
          <h2
            style={{
              color: '#2185d0',
              margin: '0.5rem 0',
              textAlign: 'center',
              fontSize: '1.8rem',
              fontWeight: 'bold',
            }}
          >
            Classroom Management Tools
          </h2>
          <p
            style={{
              color: '#666',
              margin: '0',
              textAlign: 'center',
              fontSize: '1rem',
            }}
          >
            Everything you need for daily classroom operations
          </p>
        </div>

        <Grid stackable columns={3} className="tools-grid">
          {tools.map((tool, index) => (
            <Grid.Column key={index}>
              <Card
                as={Link}
                to={tool.url}
                className="tool-card"
                color={tool.color}
              >
                <Card.Content textAlign="center">
                  <Icon
                    name={tool.icon}
                    size="huge"
                    color={tool.color}
                    className="tool-icon"
                  />
                  <Card.Header className="tool-title">{tool.title}</Card.Header>
                  <Card.Description className="tool-description">
                    {tool.description}
                  </Card.Description>
                </Card.Content>
                <Card.Content extra>
                  <Button
                    color={tool.color}
                    fluid
                    size="medium"
                    className="tool-button"
                  >
                    Open {tool.title}
                    <Icon name="arrow right" />
                  </Button>
                </Card.Content>
              </Card>
            </Grid.Column>
          ))}
        </Grid>
      </Segment>
    </Container>
  );
};

export default ClassroomToolsWidget;
