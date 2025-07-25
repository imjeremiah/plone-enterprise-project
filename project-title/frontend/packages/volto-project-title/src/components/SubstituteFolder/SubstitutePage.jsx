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
  const contentUrl = process.env.RAZZLE_API_PATH || 'http://localhost:8080/Plone';

  return (
    <Container style={{ padding: '20px 0' }}>
        <Header as="h1" icon textAlign="center" style={{ marginBottom: '30px' }}>
          <Icon name="folder open" color="blue" />
          <Header.Content>
            Substitute Folder Generator
            <Header.Subheader>
              Emergency Preparation Tool for Classroom Management
            </Header.Subheader>
          </Header.Content>
        </Header>

        <Message info>
          <Message.Header>
            <Icon name="info circle" />
            Quick Emergency Preparation
          </Message.Header>
          <p>
            When you're feeling unwell or need to call in a substitute, this tool creates 
            a comprehensive folder containing everything a substitute teacher needs to successfully 
            manage your classroom. Generated folders include current schedules, seating charts, 
            lesson plans, emergency procedures, and important contact information.
          </p>
        </Message>

        <SubstituteGenerator contentUrl={contentUrl} />
      </Container>
  );
};

export default SubstitutePage; 