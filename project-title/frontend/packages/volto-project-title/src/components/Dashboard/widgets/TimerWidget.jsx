/**
 * Timer Widget for Teacher Dashboard
 * 
 * Compact timer display and controls:
 * - Shows current timer status if running
 * - Quick timer presets for common activities
 * - Link to full timer interface
 * - Persistent timer state across page refreshes
 */

import React, { useState, useEffect } from 'react';
import { Segment, Header, Icon, Button, Progress, Statistic } from 'semantic-ui-react';

const TimerWidget = () => {
  const [timerState, setTimerState] = useState(null);

  useEffect(() => {
    // Load timer state from localStorage
    loadTimerState();
    
    // Update timer every second if running
    const interval = setInterval(loadTimerState, 1000);
    
    return () => clearInterval(interval);
  }, []);

  /**
   * Load timer state from localStorage
   */
  const loadTimerState = () => {
    try {
      const saved = localStorage.getItem('lessonTimer');
      if (saved) {
        const state = JSON.parse(saved);
        const now = Date.now();
        const elapsed = Math.floor((now - (state.lastUpdate || now)) / 1000);
        
        if (state.isRunning && state.remaining > 0) {
          const newRemaining = Math.max(0, state.remaining - elapsed);
          setTimerState({
            ...state,
            remaining: newRemaining,
            isRunning: newRemaining > 0
          });
        } else {
          setTimerState(state);
        }
      }
    } catch (error) {
      console.warn('Failed to load timer state:', error);
    }
  };

  /**
   * Format time for display
   */
  const formatTime = (seconds) => {
    if (!seconds) return '00:00';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  /**
   * Start a quick timer
   */
  const startQuickTimer = (minutes) => {
    const duration = minutes * 60;
    const newState = {
      duration,
      remaining: duration,
      isRunning: true,
      lastUpdate: Date.now()
    };
    
    localStorage.setItem('lessonTimer', JSON.stringify(newState));
    setTimerState(newState);
    
    // Open timer page for full control
    window.open('/timer', '_blank');
  };

  /**
   * Get progress percentage
   */
  const getProgress = () => {
    if (!timerState || !timerState.duration) return 0;
    return ((timerState.duration - timerState.remaining) / timerState.duration) * 100;
  };

  /**
   * Get progress color based on remaining time
   */
  const getProgressColor = () => {
    if (!timerState || !timerState.duration) return 'blue';
    const percent = timerState.remaining / timerState.duration;
    if (percent > 0.5) return 'green';
    if (percent > 0.2) return 'yellow';
    return 'red';
  };

  return (
    <Segment className="dashboard-widget timer-widget">
      <Header as="h3">
        <Icon name="clock" color="green" />
        <Header.Content>
          Lesson Timer
          <Header.Subheader>Activity timing & alerts</Header.Subheader>
        </Header.Content>
      </Header>

      {/* Current Timer Status */}
      {timerState && timerState.remaining > 0 ? (
        <div style={{ textAlign: 'center', marginBottom: '10px' }}>
          <Statistic size="small" color={timerState.isRunning ? undefined : 'grey'}>
            <Statistic.Value>
              <Icon name={timerState.isRunning ? 'play' : 'pause'} />
              {formatTime(timerState.remaining)}
            </Statistic.Value>
            <Statistic.Label>
              {timerState.isRunning ? 'Running' : 'Paused'}
            </Statistic.Label>
          </Statistic>
          
          <Progress 
            percent={getProgress()} 
            color={getProgressColor()}
            size="small"
            style={{ marginTop: '10px' }}
          />
          
          <Button 
            size="small" 
            basic 
            onClick={() => window.open('/timer', '_blank')}
            style={{ marginTop: '10px' }}
          >
            <Icon name="expand" />
            Open Full Timer
          </Button>
        </div>
      ) : (
        <div>
          <div style={{ textAlign: 'center', marginBottom: '10px' }}>
            <Icon name="clock outline" size="large" style={{ color: '#ccc' }} />
            <div style={{ color: '#666', fontSize: '0.9em' }}>No active timer</div>
          </div>

          {/* Quick Timer Presets */}
          <div>
            <div style={{ marginBottom: '10px', fontSize: '0.9em', fontWeight: 'bold' }}>
              Quick Timers:
            </div>
            <Button.Group size="small" fluid>
              <Button onClick={() => startQuickTimer(5)}>5 min</Button>
              <Button onClick={() => startQuickTimer(10)}>10 min</Button>
              <Button onClick={() => startQuickTimer(15)}>15 min</Button>
            </Button.Group>
            
            <Button 
              size="small" 
              basic 
              fluid
              onClick={() => window.open('/timer', '_blank')}
              style={{ marginTop: '10px' }}
            >
              <Icon name="clock" />
              Open Timer
            </Button>
          </div>
        </div>
      )}
    </Segment>
  );
};

export default TimerWidget; 