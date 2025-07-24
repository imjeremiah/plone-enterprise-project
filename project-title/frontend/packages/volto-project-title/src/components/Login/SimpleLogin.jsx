/**
 * Simple Login Component - No OAuth Required
 * 
 * This component provides traditional username/password authentication
 * using Plone's built-in authentication system.
 */

import React, { useState } from 'react';
import { connect } from 'react-redux';
import { useHistory } from 'react-router-dom';
import { login } from '@plone/volto/actions';
import { Button, Form, Input, Message, Container, Header } from 'semantic-ui-react';

const SimpleLogin = ({ login, loginRequest, loginError }) => {
  const [formData, setFormData] = useState({
    login: '',
    password: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const history = useHistory();

  /**
   * Handle form input changes
   */
  const handleChange = (e, { name, value }) => {
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  /**
   * Handle form submission
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.login || !formData.password) {
      return;
    }

    setIsLoading(true);
    
    try {
      await login(formData.login, formData.password);
      
      // On successful login, redirect to home or return URL
      const returnUrl = new URLSearchParams(window.location.search).get('return_url') || '/';
      history.push(returnUrl);
      
    } catch (error) {
      console.error('Login failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Container style={{ marginTop: '2rem', maxWidth: '400px' }}>
      <Header as="h2" textAlign="center" color="blue">
        Sign In to Project Title
      </Header>
      
      <Form onSubmit={handleSubmit} error={!!loginError}>
        {loginError && (
          <Message
            error
            header="Login Failed"
            content="Please check your username and password and try again."
          />
        )}
        
        <Form.Field required>
          <label>Username or Email</label>
          <Input
            name="login"
            type="text"
            placeholder="Enter your username or email"
            value={formData.login}
            onChange={handleChange}
            icon="user"
            iconPosition="left"
            disabled={isLoading}
            autoComplete="username"
          />
        </Form.Field>
        
        <Form.Field required>
          <label>Password</label>
          <Input
            name="password"
            type="password"
            placeholder="Enter your password"
            value={formData.password}
            onChange={handleChange}
            icon="lock"
            iconPosition="left"
            disabled={isLoading}
            autoComplete="current-password"
          />
        </Form.Field>
        
        <Button
          type="submit"
          color="blue"
          fluid
          size="large"
          loading={isLoading}
          disabled={!formData.login || !formData.password || isLoading}
        >
          Sign In
        </Button>
        
        <div style={{ textAlign: 'center', marginTop: '1rem' }}>
          <a href="/passwordreset">Forgot your password?</a>
        </div>
      </Form>
      
      <Message info style={{ marginTop: '2rem' }}>
        <Message.Header>Need an account?</Message.Header>
        <p>
          Contact your school administrator to get access to the educational platform.
        </p>
      </Message>
    </Container>
  );
};

const mapStateToProps = (state) => ({
  loginRequest: state.userSession.login,
  loginError: state.userSession.login.error
});

const mapDispatchToProps = {
  login
};

export default connect(mapStateToProps, mapDispatchToProps)(SimpleLogin); 