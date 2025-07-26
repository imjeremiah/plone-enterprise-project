/**
 * Substitute Folder Page for Classroom Management
 *
 * Main page component for the substitute folder generation tool,
 * providing teachers with an emergency preparation interface.
 */

import React from 'react';
import { Container, Header, Icon, Message } from 'semantic-ui-react';
import SubstituteGenerator from './SubstituteGenerator';

const SubstitutePage = () => {
  // Get the correct URL for browser views (not API endpoints)
  const getContentUrl = () => {
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

  const contentUrl = getContentUrl();

  return (
    <Container style={{ padding: '20px 0' }}>
      <Header
        as="h1"
        icon
        textAlign="center"
        style={{
          marginBottom: '30px',
          textAlign: 'center !important',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          width: '100%',
        }}
      >
        <Icon name="folder open" color="blue" />
        <Header.Content style={{ textAlign: 'center' }}>
          Substitute Folder Generator
        </Header.Content>
      </Header>

      <SubstituteGenerator contentUrl={contentUrl} />
    </Container>
  );
};

export default SubstitutePage;
