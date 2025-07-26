/**
 * Lesson Timer Widget for Classroom Management
 *
 * Provides visual and audio alerts for classroom activities with
 * localStorage persistence and fullscreen mode for easy visibility.
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import PropTypes from 'prop-types';
import {
  Button,
  Progress,
  Modal,
  Input,
  Grid,
  Icon,
  Label,
  Dropdown,
  Segment,
  Header,
  Message,
} from 'semantic-ui-react';
import './LessonTimer.css';

// Client-only wrapper to prevent SSR issues
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

const LessonTimerComponent = ({
  presets = [],
  contentUrl,
  compact = false,
}) => {
  const [duration, setDuration] = useState(300); // 5 min default
  const [remaining, setRemaining] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  const [showFullscreen, setShowFullscreen] = useState(false);
  const [customMinutes, setCustomMinutes] = useState(5);
  const [timerPresets, setTimerPresets] = useState([]);
  const [soundEnabled, setSoundEnabled] = useState(true);

  const intervalRef = useRef(null);
  const lastUpdateRef = useRef(Date.now());

  // Default presets if none provided
  const defaultPresets = [
    { name: 'Quick Activity', duration: 300, description: '5 minutes' },
    { name: 'Group Work', duration: 600, description: '10 minutes' },
    { name: 'Individual Work', duration: 900, description: '15 minutes' },
    { name: 'Test/Quiz', duration: 1200, description: '20 minutes' },
  ];

  /**
   * Load timer presets from backend
   */
  const loadPresets = useCallback(async () => {
    if (!contentUrl) {
      setTimerPresets(defaultPresets);
      return;
    }

    try {
      const response = await fetch(`${contentUrl}/@@timer-presets`, {
        method: 'GET',
        credentials: 'include',
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setTimerPresets(data.presets);
        } else {
          setTimerPresets(defaultPresets);
        }
      }
    } catch (error) {
      console.warn('Failed to load timer presets:', error);
      setTimerPresets(defaultPresets);
    }
  }, [contentUrl]);

  /**
   * Load saved timer state from localStorage
   */
  useEffect(() => {
    const saved = localStorage.getItem('lessonTimer');
    if (saved) {
      try {
        const {
          remaining: savedRemaining,
          isRunning: wasRunning,
          duration: savedDuration,
          lastUpdate,
        } = JSON.parse(saved);

        if (savedRemaining > 0) {
          // Calculate time elapsed since last update
          const now = Date.now();
          const elapsed = Math.floor((now - lastUpdate) / 1000);
          const adjustedRemaining = Math.max(0, savedRemaining - elapsed);

          setDuration(savedDuration || 300);
          setRemaining(adjustedRemaining);

          if (wasRunning && adjustedRemaining > 0) {
            startTimer();
          }
        }
      } catch (e) {
        console.warn('Failed to restore timer state:', e);
      }
    }

    loadPresets();
  }, [loadPresets]);

  /**
   * Save timer state to localStorage
   */
  useEffect(() => {
    const timerState = {
      remaining,
      isRunning,
      duration,
      lastUpdate: Date.now(),
    };
    localStorage.setItem('lessonTimer', JSON.stringify(timerState));
  }, [remaining, isRunning, duration]);

  /**
   * Start the timer
   */
  const startTimer = useCallback(() => {
    if (remaining === 0) {
      setRemaining(duration);
    }

    setIsRunning(true);
    lastUpdateRef.current = Date.now();

    intervalRef.current = setInterval(() => {
      setRemaining((prev) => {
        if (prev <= 1) {
          setIsRunning(false);
          endTimer();
          return 0;
        }

        // Warning alerts
        if (prev === 120 && soundEnabled) playSound('warning'); // 2 min
        if (prev === 60 && soundEnabled) playSound('warning'); // 1 min

        return prev - 1;
      });
    }, 1000);
  }, [remaining, duration, soundEnabled]);

  /**
   * Pause the timer
   */
  const pauseTimer = useCallback(() => {
    setIsRunning(false);
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  /**
   * End timer with alerts
   */
  const endTimer = useCallback(() => {
    pauseTimer();

    if (soundEnabled) {
      playSound('complete');
    }

    // Visual alert - flash the page
    document.body.classList.add('timer-complete');
    setTimeout(() => {
      document.body.classList.remove('timer-complete');
    }, 3000);

    // Browser notification if supported
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification('Timer Complete!', {
        body: 'The lesson timer has finished.',
        icon: '/++resource++project.title/timer-icon.png',
      });
    }
  }, [pauseTimer, soundEnabled]);

  /**
   * Reset timer to initial state
   */
  const resetTimer = useCallback(() => {
    pauseTimer();
    setRemaining(0);
  }, [pauseTimer]);

  /**
   * Play audio alert
   */
  const playSound = (type) => {
    if (!soundEnabled) return;

    try {
      const audio = new Audio(`/++resource++project.title/sounds/${type}.mp3`);
      audio.volume = 0.3;
      audio.play().catch((e) => {
        console.log('Audio play failed (this is normal in some browsers):', e);
      });
    } catch (error) {
      console.log('Audio not available:', error);
    }
  };

  /**
   * Format time for display
   */
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  /**
   * Get progress bar color based on remaining time
   */
  const getProgressColor = () => {
    const percent = remaining / duration;
    if (percent > 0.5) return 'green';
    if (percent > 0.2) return 'yellow';
    return 'red';
  };

  /**
   * Set timer from preset
   */
  const selectPreset = (preset) => {
    if (!isRunning) {
      setDuration(preset.duration);
      setRemaining(preset.duration);
    }
  };

  /**
   * Set custom duration
   */
  const setCustomDuration = () => {
    const seconds = customMinutes * 60;
    if (seconds > 0 && !isRunning) {
      setDuration(seconds);
      setRemaining(seconds);
    }
  };

  /**
   * Request notification permission
   */
  const requestNotificationPermission = () => {
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }
  };

  /**
   * Toggle fullscreen mode
   */
  const toggleFullscreen = () => {
    setShowFullscreen(!showFullscreen);
  };

  // Preset options for dropdown
  const presetOptions = timerPresets.map((preset) => ({
    key: preset.name,
    text: `${preset.name} (${Math.floor(preset.duration / 60)}m)`,
    value: preset,
    description: preset.description,
  }));

  if (compact) {
    return (
      <div className="lesson-timer compact">
        <div className="timer-display-compact">
          <span className={`time-compact ${remaining < 60 ? 'urgent' : ''}`}>
            {formatTime(remaining || duration)}
          </span>
          <Progress
            percent={((duration - remaining) / duration) * 100}
            color={getProgressColor()}
            size="tiny"
          />
        </div>
        <div className="timer-controls-compact">
          {!isRunning ? (
            <Button size="mini" primary onClick={startTimer}>
              <Icon name="play" />
            </Button>
          ) : (
            <Button size="mini" secondary onClick={pauseTimer}>
              <Icon name="pause" />
            </Button>
          )}
          <Button size="mini" basic onClick={resetTimer}>
            <Icon name="stop" />
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="lesson-timer">
      <Segment className="timer-main">
        <div style={{ textAlign: 'center', width: '100%' }}>
          <h3 style={{ textAlign: 'center', margin: '0 auto', width: '100%' }}>
            Lesson Timer
          </h3>
        </div>

        <div className="timer-display">
          <h1
            className={`time ${remaining < 60 ? 'urgent' : ''} ${isRunning ? 'running' : ''}`}
          >
            {formatTime(remaining || duration)}
          </h1>
          <Progress
            percent={
              duration > 0 ? ((duration - remaining) / duration) * 100 : 0
            }
            color={getProgressColor()}
            size="small"
          />

          {remaining > 0 && (
            <div className="timer-info">
              <Label size="small">
                {isRunning ? 'Running' : 'Paused'} •{' '}
                {Math.floor(remaining / 60)}m {remaining % 60}s remaining
              </Label>
            </div>
          )}
        </div>

        {!isRunning && remaining === 0 && (
          <div className="duration-setup">
            <Header as="h4">Set Timer Duration</Header>

            <Grid columns={2} stackable>
              <Grid.Column>
                <div className="custom-duration">
                  <label>Custom Duration (minutes):</label>
                  <Input
                    type="number"
                    min="1"
                    max="120"
                    value={customMinutes}
                    onChange={(e, { value }) =>
                      setCustomMinutes(parseInt(value) || 1)
                    }
                    action={{
                      content: 'Set',
                      onClick: setCustomDuration,
                    }}
                    size="small"
                  />
                </div>
              </Grid.Column>

              <Grid.Column>
                <div className="preset-selector">
                  <label>Or choose preset:</label>
                  <Dropdown
                    placeholder="Select activity preset"
                    fluid
                    selection
                    options={presetOptions}
                    onChange={(e, { value }) => selectPreset(value)}
                  />
                </div>
              </Grid.Column>
            </Grid>
          </div>
        )}

        <div className="timer-controls">
          <Grid columns={3} stackable textAlign="center">
            <Grid.Column>
              {!isRunning ? (
                <Button
                  primary
                  size="large"
                  onClick={startTimer}
                  disabled={duration === 0}
                >
                  <Icon name="play" />
                  Start Timer
                </Button>
              ) : (
                <Button secondary size="large" onClick={pauseTimer}>
                  <Icon name="pause" />
                  Pause
                </Button>
              )}
            </Grid.Column>

            <Grid.Column>
              <Button basic size="large" onClick={resetTimer}>
                <Icon name="stop" />
                Reset
              </Button>
            </Grid.Column>

            <Grid.Column>
              <Button
                basic
                size="large"
                onClick={toggleFullscreen}
                title="Fullscreen Mode"
              >
                <Icon name="expand" />
                Full Screen
              </Button>
            </Grid.Column>
          </Grid>
        </div>

        <div className="timer-options">
          <Grid columns={1}>
            <Grid.Column textAlign="center">
              {'Notification' in window &&
                Notification.permission === 'default' && (
                  <Button
                    basic
                    size="small"
                    onClick={requestNotificationPermission}
                  >
                    <Icon name="bell" />
                    Enable Notifications
                  </Button>
                )}
            </Grid.Column>
          </Grid>
        </div>
      </Segment>

      {/* Fullscreen Modal */}
      <Modal
        open={showFullscreen}
        onClose={() => setShowFullscreen(false)}
        size="fullscreen"
        className="timer-fullscreen"
      >
        <Modal.Content>
          <div className="fullscreen-timer">
            <div className="fullscreen-time-display">
              <h1 className={`huge-time ${remaining < 60 ? 'urgent' : ''}`}>
                {formatTime(remaining || duration)}
              </h1>

              <div className="fullscreen-progress">
                <Progress
                  percent={
                    duration > 0 ? ((duration - remaining) / duration) * 100 : 0
                  }
                  color={getProgressColor()}
                  size="medium"
                />
              </div>

              <div className="fullscreen-status">
                <Label size="big" basic>
                  {isRunning ? 'RUNNING' : 'PAUSED'}
                </Label>
              </div>
            </div>

            <div className="fullscreen-controls">
              {!isRunning ? (
                <Button huge primary onClick={startTimer}>
                  Start
                </Button>
              ) : (
                <Button huge secondary onClick={pauseTimer}>
                  Pause
                </Button>
              )}

              <Button huge onClick={resetTimer}>
                Reset
              </Button>

              <Button huge onClick={() => setShowFullscreen(false)}>
                Exit
              </Button>
            </div>
          </div>
        </Modal.Content>
      </Modal>
    </div>
  );
};

LessonTimerComponent.propTypes = {
  presets: PropTypes.arrayOf(
    PropTypes.shape({
      name: PropTypes.string.isRequired,
      duration: PropTypes.number.isRequired,
      description: PropTypes.string,
    }),
  ),
  contentUrl: PropTypes.string,
  compact: PropTypes.bool,
};

// Wrapper with client-only rendering
const LessonTimer = (props) => (
  <ClientOnly
    fallback={
      <Segment>
        <Header as="h3" textAlign="center">
          <Icon name="clock" />
          Lesson Timer Loading...
        </Header>
      </Segment>
    }
  >
    <LessonTimerComponent {...props} />
  </ClientOnly>
);

export default LessonTimer;
