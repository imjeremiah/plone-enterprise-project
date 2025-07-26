/**
 * Custom Homepage for Edu Plone
 *
 * SSR-safe implementation that combines standard Plone content
 * with classroom management tools widget.
 */

import React, { useState, useEffect } from 'react';
import {
  Container,
  Divider,
  Button,
  Grid,
  Header,
  Icon,
} from 'semantic-ui-react';

// Client-only wrapper to prevent hydration issues
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

// Static navigation fallback that works during SSR
const StaticClassroomNav = () => (
  <Container>
    <Header as="h2" textAlign="center" color="blue">
      <Icon name="graduation cap" />
      <Header.Content>
        Classroom Management Tools
        <Header.Subheader>
          Quick access to all classroom features
        </Header.Subheader>
      </Header.Content>
    </Header>

    <Grid stackable columns={3} style={{ marginTop: '2rem' }}>
      <Grid.Column textAlign="center">
        <Button
          as="a"
          href="/dashboard"
          primary
          size="large"
          style={{ width: '100%', marginBottom: '1rem' }}
        >
          <Icon name="dashboard" />
          Dashboard
        </Button>
      </Grid.Column>
      <Grid.Column textAlign="center">
        <Button
          as="a"
          href="/hall-pass-manager"
          color="green"
          size="large"
          style={{ width: '100%', marginBottom: '1rem' }}
        >
          <Icon name="id card" />
          Hall Pass Manager
        </Button>
      </Grid.Column>
      <Grid.Column textAlign="center">
        <Button
          as="a"
          href="/random-picker"
          color="purple"
          size="large"
          style={{ width: '100%', marginBottom: '1rem' }}
        >
          <Icon name="random" />
          Random Picker
        </Button>
      </Grid.Column>
    </Grid>

    <Grid stackable columns={3} style={{ marginTop: '1rem' }}>
      <Grid.Column textAlign="center">
        <Button
          as="a"
          href="/timer"
          color="teal"
          size="medium"
          style={{ width: '100%' }}
        >
          <Icon name="clock" />
          Lesson Timer
        </Button>
      </Grid.Column>
      <Grid.Column textAlign="center">
        <Button
          as="a"
          href="/substitute-folder"
          color="red"
          size="medium"
          style={{ width: '100%' }}
        >
          <Icon name="folder open" />
          Substitute Folder
        </Button>
      </Grid.Column>
      <Grid.Column textAlign="center">
        <Button
          as="a"
          href="/seating-charts"
          color="orange"
          size="medium"
          style={{ width: '100%' }}
        >
          <Icon name="sitemap" />
          Seating Charts
        </Button>
      </Grid.Column>
    </Grid>
  </Container>
);

const CustomHomepage = ({ content }) => {
  // Lazy load the ClassroomToolsWidget to avoid SSR issues
  const [ClassroomToolsWidget, setClassroomToolsWidget] = useState(null);

  useEffect(() => {
    // Dynamically import the widget only on client side
    import('../Dashboard/widgets/ClassroomToolsWidget')
      .then((module) => {
        setClassroomToolsWidget(() => module.default);
      })
      .catch((error) => {
        console.log(
          'ClassroomToolsWidget not available, using static navigation',
        );
      });
  }, []);

  return (
    <div className="custom-homepage">
      {/* Classroom management tools FIRST - at the top of the page */}
      <ClientOnly fallback={<StaticClassroomNav />}>
        {ClassroomToolsWidget ? (
          <ClassroomToolsWidget />
        ) : (
          <StaticClassroomNav />
        )}
      </ClientOnly>

      <Divider section />

      {/* Standard Plone homepage content - moved below classroom tools */}
      <Container>
        <div className="documentFirstHeading">
          <h1 className="documentFirstHeading">
            {content?.title || 'Edu Plone'}
          </h1>
        </div>

        {content?.description && (
          <p className="documentDescription">{content.description}</p>
        )}

        <div className="documentBody">
          <h2>Welcome to your new Plone site!</h2>
          <p>
            <strong>Find out more about Plone</strong>
          </p>
          <p>
            Plone is a powerful content management system built on a rock-solid
            application stack written in the <em>Python</em> and{' '}
            <em>JavaScript</em> programming languages.
          </p>
          <ul>
            <li>
              <a
                href="https://plone.org/features"
                target="_blank"
                rel="noopener noreferrer"
              >
                The features of Plone
              </a>
            </li>
            <li>
              <a
                href="https://docs.plone.org"
                target="_blank"
                rel="noopener noreferrer"
              >
                Plone Documentation
              </a>
            </li>
            <li>
              <a
                href="https://training.plone.org"
                target="_blank"
                rel="noopener noreferrer"
              >
                Plone Training
              </a>
            </li>
            <li>
              <a
                href="https://community.plone.org"
                target="_blank"
                rel="noopener noreferrer"
              >
                Plone Community Forum
              </a>
            </li>
            <li>
              <a
                href="https://plone.org/download/add-ons"
                target="_blank"
                rel="noopener noreferrer"
              >
                Add-ons for Plone (backend)
              </a>
            </li>
            <li>
              <a
                href="https://www.npmjs.com/search?q=%40plone"
                target="_blank"
                rel="noopener noreferrer"
              >
                Add-ons for Volto (frontend)
              </a>
            </li>
          </ul>
        </div>
      </Container>
    </div>
  );
};

export default CustomHomepage;
