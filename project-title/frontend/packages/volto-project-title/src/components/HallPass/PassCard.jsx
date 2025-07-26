/**
 * Pass Card Component for Digital Hall Pass Display
 * 
 * Displays individual hall pass information including QR code,
 * time tracking, and return functionality.
 */

import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import {
  Card,
  Button,
  Label,
  Icon,
  Image,
  Modal,
  Header,
  Grid,
  Statistic
} from 'semantic-ui-react';
import WorkflowStatus from './WorkflowStatus';
import './PassCard.css';

const PassCard = ({ 
  pass, 
  onReturn, 
  showReturnButton = true, 
  compact = false 
}) => {
  const [showQRModal, setShowQRModal] = useState(false);
  
  // Calculate initial duration safely
  const calculateDuration = () => {
    if (pass.return_time) {
      const issueTime = new Date(pass.issue_time);
      const returnTime = new Date(pass.return_time);
      return Math.floor((returnTime - issueTime) / (1000 * 60));
    }
    
    if (pass.duration_minutes !== undefined && pass.duration_minutes !== null) {
      return pass.duration_minutes;
    }
    
    // Calculate from issue_time if duration_minutes is missing
    const issueTime = new Date(pass.issue_time);
    const now = new Date();
    return Math.floor((now - issueTime) / (1000 * 60));
  };
  
  const [currentDuration, setCurrentDuration] = useState(calculateDuration);
  const [workflowState, setWorkflowState] = useState('unknown');

  // Determine workflow state from pass data (fallback-first approach)
  const getWorkflowStateFromPass = (passData) => {
    // Use existing pass data to determine workflow state
    if (passData.return_time) return 'returned';
    if (passData.issue_time) return 'issued';
    return 'draft';
  };

  // Optional: Try to fetch enhanced workflow state from backend
  const fetchWorkflowState = async (passId) => {
    try {
      // TEMPORARILY DISABLED: Backend workflow support causing 500 errors
      // TODO: Re-enable once backend event system is restored
      /*
      const response = await fetch(`http://localhost:8080/Plone/@@workflow-support`, {
        headers: { 'Accept': 'application/json' }
      });
      if (response.ok) {
        const data = await response.json();
        return data.workflow_state || getWorkflowStateFromPass(pass);
      }
      */
    } catch (error) {
      // Workflow endpoint not available - use fallback
    }
    
    // Use fallback workflow state determination
    return getWorkflowStateFromPass(pass);
  };

  // Update duration every 30 seconds for active passes
  useEffect(() => {
    // Calculate current duration
    const calculateCurrentDuration = () => {
      if (pass.return_time) {
        const issueTime = new Date(pass.issue_time);
        const returnTime = new Date(pass.return_time);
        return Math.floor((returnTime - issueTime) / (1000 * 60));
      }
      
      if (pass.duration_minutes !== undefined && pass.duration_minutes !== null) {
        return pass.duration_minutes;
      }
      
      // Calculate from issue_time if duration_minutes is missing
      const issueTime = new Date(pass.issue_time);
      const now = new Date();
      return Math.floor((now - issueTime) / (1000 * 60));
    };
    
    // Set initial duration
    setCurrentDuration(calculateCurrentDuration());
    
    // Set initial workflow state from pass data (immediate)
    const initialState = getWorkflowStateFromPass(pass);
    setWorkflowState(initialState);
    
    // Try to enhance with backend workflow state (optional)
    if (pass.id) {
      fetchWorkflowState(pass.id).then(state => {
        if (state !== initialState) {
          setWorkflowState(state);
        }
      });
    }
    
    if (!pass.is_active) return;

    const interval = setInterval(() => {
      setCurrentDuration(calculateCurrentDuration());
    }, 30000); // Update every 30 seconds

    return () => clearInterval(interval);
  }, [pass.is_active, pass.issue_time, pass.duration_minutes, pass.return_time]);

  /**
   * Get time difference display
   */
  const getTimeDifference = () => {
    const duration = currentDuration || 0;
    
    if (duration === 0) {
      return "just now";
    } else if (duration === 1) {
      return "1 minute";
    } else {
      return `${duration} minutes`;
    }
  };

  /**
   * Get alert level color and text
   */
  const getAlertLevel = () => {
    if (pass.return_time) {
      return { color: 'green', text: 'Returned' };
    }
    
    const duration = currentDuration;
    const expected = pass.expected_duration || 5;
    
    if (duration > expected + 10) {
      return { color: 'red', text: 'Very Overdue' };
    } else if (duration > expected + 5) {
      return { color: 'red', text: 'Overdue' };
    } else if (duration > expected) {
      return { color: 'yellow', text: 'Past Expected' };
    } else {
      return { color: 'green', text: 'On Time' };
    }
  };

  /**
   * Format time for display
   */
  const formatTime = (timeString) => {
    if (!timeString) return 'Unknown';
    
    const time = new Date(timeString);
    return time.toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  /**
   * Render QR code modal
   */
  const renderQRModal = () => (
    <Modal 
      open={showQRModal} 
      onClose={() => setShowQRModal(false)}
      size="small"
    >
      <Modal.Header>
        <Icon name="qrcode" />
        Hall Pass QR Code
      </Modal.Header>
      
      <Modal.Content style={{ textAlign: 'center' }}>
        <Grid centered>
          <Grid.Column width={8}>
            {pass.qr_code && (
              <Image 
                src={pass.qr_code} 
                alt="Hall Pass QR Code"
                style={{ 
                  maxWidth: '200px', 
                  margin: '0 auto',
                  border: '2px solid #ddd',
                  borderRadius: '8px'
                }}
              />
            )}
          </Grid.Column>
          <Grid.Column width={8}>
            <Statistic.Group size="mini">
              <Statistic>
                <Statistic.Value>{pass.student_name}</Statistic.Value>
                <Statistic.Label>Student</Statistic.Label>
              </Statistic>
              
              <Statistic>
                <Statistic.Value>{pass.destination}</Statistic.Value>
                <Statistic.Label>Destination</Statistic.Label>
              </Statistic>
              
              <Statistic>
                <Statistic.Value>{pass.pass_code}</Statistic.Value>
                <Statistic.Label>Pass Code</Statistic.Label>
              </Statistic>
              
              <Statistic>
                <Statistic.Value>{formatTime(pass.issue_time)}</Statistic.Value>
                <Statistic.Label>Issued</Statistic.Label>
              </Statistic>
            </Statistic.Group>
          </Grid.Column>
        </Grid>
        
        <div style={{ marginTop: '15px', fontSize: '0.9em', color: '#666' }}>
          Show this QR code to verify the hall pass
        </div>
      </Modal.Content>
      
      <Modal.Actions>
        <Button onClick={() => setShowQRModal(false)}>
          <Icon name="close" />
          Close
        </Button>
      </Modal.Actions>
    </Modal>
  );

  const alertLevel = getAlertLevel();

  if (compact) {
    return (
      <>
        <Card className={`pass-card compact ${alertLevel.color}`}>
          <Card.Content>
            <Card.Header style={{ fontSize: '0.9em' }}>
              {pass.student_name}
            </Card.Header>
            <Card.Meta style={{ fontSize: '0.8em' }}>
              {pass.destination} • {getTimeDifference()}
            </Card.Meta>
            {pass.return_time && (
              <Card.Description style={{ fontSize: '0.8em', color: 'green' }}>
                Returned at {formatTime(pass.return_time)}
              </Card.Description>
            )}
          </Card.Content>
        </Card>
        {renderQRModal()}
      </>
    );
  }

  return (
    <>
      <Card className={`pass-card ${alertLevel.color}`} color={alertLevel.color}>
        <Card.Content>
          <Card.Header>
            <Icon name="user" />
            {pass.student_name}
            <div style={{ float: 'right' }}>
              <WorkflowStatus 
                workflowState={workflowState} 
                duration={currentDuration} 
              />
              <Label 
                color={alertLevel.color} 
                size="small"
                style={{ marginLeft: '5px' }}
              >
                {alertLevel.text}
              </Label>
            </div>
          </Card.Header>
          
          <Card.Meta>
            <Icon name="map marker" />
            {pass.destination}
          </Card.Meta>
          
          <Card.Description>
            <div className="pass-details">
              <div className="time-info">
                <Icon name="clock" />
                <strong>Duration:</strong> {getTimeDifference()}
                {pass.expected_duration && (
                  <span className="expected">
                    {' '}(expected {pass.expected_duration} min)
                  </span>
                )}
              </div>
              
              <div className="issue-time">
                <Icon name="calendar" />
                <strong>Issued:</strong> {formatTime(pass.issue_time)}
              </div>
              
              {pass.return_time && (
                <div className="return-time">
                  <Icon name="check circle" color="green" />
                  <strong>Returned:</strong> {formatTime(pass.return_time)}
                </div>
              )}
              
              {pass.notes && (
                <div className="notes">
                  <Icon name="sticky note" />
                  <strong>Notes:</strong> {pass.notes}
                </div>
              )}
              
              <div className="pass-code">
                <Icon name="key" />
                <strong>Pass Code:</strong> {pass.pass_code}
              </div>
            </div>
          </Card.Description>
        </Card.Content>
        
        <Card.Content extra>
          <div className="pass-actions">
            <Button 
              size="small"
              onClick={() => setShowQRModal(true)}
            >
              <Icon name="qrcode" />
              Show QR Code
            </Button>
            
            {showReturnButton && pass.is_active && onReturn && (
              <Button 
                color={alertLevel.color === 'red' ? 'red' : 'green'}
                size="small"
                onClick={onReturn}
              >
                <Icon name="undo" />
                Mark Returned
              </Button>
            )}
            
            {!pass.is_active && (
              <Label color="green" size="small">
                <Icon name="check" />
                Completed
              </Label>
            )}
          </div>
        </Card.Content>
      </Card>
      
      {renderQRModal()}
    </>
  );
};

PassCard.propTypes = {
  pass: PropTypes.shape({
    id: PropTypes.string.isRequired,
    student_name: PropTypes.string.isRequired,
    destination: PropTypes.string.isRequired,
    issue_time: PropTypes.string.isRequired,
    return_time: PropTypes.string,
    expected_duration: PropTypes.number,
    duration_minutes: PropTypes.number,
    is_overdue: PropTypes.bool,
    is_active: PropTypes.bool,
    pass_code: PropTypes.string,
    qr_code: PropTypes.string,
    notes: PropTypes.string,
    url: PropTypes.string
  }).isRequired,
  onReturn: PropTypes.func,
  showReturnButton: PropTypes.bool,
  compact: PropTypes.bool
};

export default PassCard; 