/**
 * Simple Login Component for Project Title
 * 
 * Uses traditional username/password authentication - no OAuth complexity.
 * Perfect for immediate testing and production use.
 */

import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useHistory } from 'react-router-dom';
import { login } from '@plone/volto/actions';
import { Button, Form, Input, Message, Container, Header, Divider, Grid } from 'semantic-ui-react';
import config from '@plone/volto/registry';

const Login = () => {
  const dispatch = useDispatch();
  const loginRequest = useSelector((state) => state.userSession.login);
  const loginError = loginRequest?.error;
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
      await dispatch(login(formData.login, formData.password));
      
      // On successful login, redirect to home or return URL
      const returnUrl = new URLSearchParams(window.location.search).get('return_url') || '/';
      history.push(returnUrl);
      
    } catch (error) {
      console.error('Login failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Handle Google SSO login (demo/optional)
   */
  const handleGoogleLogin = () => {
    // Store current location for return after OAuth
    sessionStorage.setItem('oauth_return_url', window.location.href);
    sessionStorage.setItem('oauth_in_progress', 'true');
    
    // Use the working authomatic endpoint
    const baseUrl = config.settings.apiPath || '';
    const redirectUrl = `${baseUrl}/@@authomatic-handler/google`;
    
    // Redirect to Google OAuth
    window.location.href = redirectUrl;
  };

  return (
    <Container style={{ marginTop: '4rem', maxWidth: '400px' }}>
      <Header as="h1" textAlign="center" color="blue">
        🎓 Edu Plone
      </Header>
      <Header as="h3" textAlign="center" color="grey">
        Educational Platform for K-12 Teachers
      </Header>
      
      <Form onSubmit={handleSubmit} error={!!loginError} style={{ marginTop: '2rem' }}>
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
            size="large"
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
            size="large"
          />
        </Form.Field>
        
        <Button
          type="submit"
          color="blue"
          fluid
          size="large"
          loading={isLoading}
          disabled={!formData.login || !formData.password || isLoading}
          style={{ marginTop: '1rem' }}
        >
          🚀 Sign In
        </Button>
        
        <div style={{ textAlign: 'center', marginTop: '1.5rem' }}>
          <a href="/passwordreset" style={{ color: '#4183c4' }}>
            Forgot your password?
          </a>
        </div>
      </Form>

      {/* Divider for alternative login methods */}
      <Divider horizontal style={{ margin: '2rem 0' }}>
        <span style={{ color: '#999', fontSize: '0.9rem' }}>or</span>
      </Divider>

      {/* Google SSO Option */}
      <div style={{ textAlign: 'center' }}>
        <Button
          color="google plus"
          size="large"
          fluid
          icon="google"
          content="🚀 Continue with Google"
          onClick={handleGoogleLogin}
          disabled={isLoading}
          style={{ 
            marginBottom: '1rem',
            background: '#db4437',
            color: 'white'
          }}
        />
      </div>
      
      <Message info style={{ marginTop: '1rem' }}>
        <Message.Header>✨ For Teachers</Message.Header>
        <p>
          <strong>Quick Demo Login:</strong><br/>
          Username: <code>admin</code><br/>
          Password: <code>admin</code>
        </p>
      </Message>
      
      <div style={{ textAlign: 'center', marginTop: '1rem', color: '#666' }}>
        <small>🔒 Secure • 🚀 Fast • 📚 Educational</small>
      </div>
    </Container>
  );
};

export default Login; 