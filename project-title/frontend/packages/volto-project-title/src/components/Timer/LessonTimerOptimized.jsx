/**
 * OPTIMIZED Lesson Timer Widget for Phase 4 Performance Enhancement
 * 
 * Performance improvements:
 * - Uses requestAnimationFrame instead of setInterval for smooth 60fps updates
 * - React.memo to prevent unnecessary re-renders
 * - Optimized state management with useCallback and useMemo
 * - Efficient event handling and cleanup
 * - Reduced DOM manipulation for better performance
 */

import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
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
  Message
} from 'semantic-ui-react';
import './LessonTimer.css';

// Optimized ClientOnly wrapper with React.memo
const ClientOnly = React.memo(({ children, fallback = null }) => {
  const [hasMounted, setHasMounted] = useState(false);

  useEffect(() => {
    setHasMounted(true);
  }, []);

  if (!hasMounted) {
    return fallback;
  }

  return children;
});

// Optimized audio manager for better performance
const AudioManager = {
  sounds: new Map(),
  
  preloadSound(type, url) {
    if (!this.sounds.has(type)) {
      const audio = new Audio(url);
      audio.preload = 'auto';
      this.sounds.set(type, audio);
    }
  },
  
  playSound(type) {
    const audio = this.sounds.get(type);
    if (audio) {
      audio.currentTime = 0; // Reset to start
      audio.play().catch(console.warn);
    }
  }
};

// Optimized timer display component with React.memo
const TimerDisplay = React.memo(({ 
  remaining, 
  duration, 
  isRunning, 
  compact = false 
}) => {
  const minutes = Math.floor(remaining / 60);
  const seconds = remaining % 60;
  const progress = duration > 0 ? ((duration - remaining) / duration) * 100 : 0;
  
  // Memoize color calculation
  const progressColor = useMemo(() => {
    if (remaining <= 60) return 'red';
    if (remaining <= 120) return 'orange';
    return 'green';
  }, [remaining]);
  
  const displayText = `${minutes}:${seconds.toString().padStart(2, '0')}`;
  
  if (compact) {
    return (
      <div className="timer-compact">
        <Progress 
          percent={progress} 
          color={progressColor}
          size="small"
          className="timer-progress"
        />
        <span className={`timer-text ${isRunning ? 'running' : ''}`}>
          {displayText}
        </span>
      </div>
    );
  }
  
  return (
    <div className="timer-display">
      <Header as="h2" className={`timer-main ${isRunning ? 'running' : ''}`}>
        {displayText}
      </Header>
      <Progress 
        percent={progress} 
        color={progressColor}
        size="large"
        className="timer-progress"
      />
    </div>
  );
});

// Main optimized timer component
const LessonTimerOptimized = React.memo(({ 
  presets = [],
  contentUrl,
  compact = false
}) => {
  const [duration, setDuration] = useState(300); // 5 min default
  const [remaining, setRemaining] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  const [showFullscreen, setShowFullscreen] = useState(false);
  const [customMinutes, setCustomMinutes] = useState(5);
  const [timerPresets, setTimerPresets] = useState([]);
  const [soundEnabled, setSoundEnabled] = useState(true);
  
  const animationFrameRef = useRef(null);
  const lastTickRef = useRef(0);
  const startTimeRef = useRef(0);
  const warningPlayedRef = useRef(new Set());

  // Memoized default presets
  const defaultPresets = useMemo(() => [
    { name: 'Quick Activity', duration: 300, description: '5 minutes' },
    { name: 'Group Work', duration: 600, description: '10 minutes' },
    { name: 'Individual Work', duration: 900, description: '15 minutes' },
    { name: 'Test/Quiz', duration: 1200, description: '20 minutes' },
  ], []);

  // Optimized timer update using requestAnimationFrame
  const updateTimer = useCallback(() => {
    const now = performance.now();
    
    // Only update once per second for timer precision
    if (now - lastTickRef.current >= 1000) {
      setRemaining(prev => {
        const newRemaining = prev - 1;
        
        if (newRemaining <= 0) {
          setIsRunning(false);
          endTimer();
          return 0;
        }
        
        // Play warning sounds (optimized with Set to prevent duplicates)
        if (soundEnabled) {
          if (newRemaining === 120 && !warningPlayedRef.current.has(120)) {
            AudioManager.playSound('warning');
            warningPlayedRef.current.add(120);
          }
          if (newRemaining === 60 && !warningPlayedRef.current.has(60)) {
            AudioManager.playSound('warning');
            warningPlayedRef.current.add(60);
          }
        }
        
        return newRemaining;
      });
      
      lastTickRef.current = now;
    }
    
    if (isRunning) {
      animationFrameRef.current = requestAnimationFrame(updateTimer);
    }
  }, [isRunning, soundEnabled]);

  // Optimized timer start function
  const startTimer = useCallback(() => {
    if (remaining === 0) {
      setRemaining(duration);
    }
    
    setIsRunning(true);
    startTimeRef.current = performance.now();
    lastTickRef.current = performance.now();
    warningPlayedRef.current.clear(); // Reset warnings for new timer session
    
    // Start the animation loop
    animationFrameRef.current = requestAnimationFrame(updateTimer);
  }, [remaining, duration, updateTimer]);

  // Optimized pause function
  const pauseTimer = useCallback(() => {
    setIsRunning(false);
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }
  }, []);

  // Optimized end timer function
  const endTimer = useCallback(() => {
    pauseTimer();
    
    if (soundEnabled) {
      AudioManager.playSound('complete');
    }
    
    // Optimized visual alert using CSS classes
    document.body.classList.add('timer-complete');
    setTimeout(() => {
      document.body.classList.remove('timer-complete');
    }, 3000);
    
    // Browser notification (optimized check)
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification('Timer Complete!', {
        body: 'The lesson timer has finished.',
        icon: '/++resource++project.title/timer-icon.png',
        silent: false
      });
    }
  }, [pauseTimer, soundEnabled]);

  // Optimized reset function
  const resetTimer = useCallback(() => {
    pauseTimer();
    setRemaining(0);
    warningPlayedRef.current.clear();
  }, [pauseTimer]);

  // Optimized preset loading
  const loadPresets = useCallback(async () => {
    if (!contentUrl) {
      setTimerPresets(defaultPresets);
      return;
    }

    try {
      const response = await fetch(`${contentUrl}/@@timer-presets`, {
        method: 'GET',
        credentials: 'include',
        cache: 'default' // Use browser cache for performance
      });

      if (response.ok) {
        const data = await response.json();
        setTimerPresets(data.success ? data.presets : defaultPresets);
      } else {
        setTimerPresets(defaultPresets);
      }
    } catch (error) {
      console.warn('Failed to load timer presets:', error);
      setTimerPresets(defaultPresets);
    }
  }, [contentUrl, defaultPresets]);

  // Optimized localStorage persistence with debouncing
  const saveTimerState = useCallback(() => {
    const timerState = {
      remaining,
      isRunning,
      duration,
      lastUpdate: Date.now()
    };
    
    // Use requestIdleCallback for non-critical localStorage updates
    if ('requestIdleCallback' in window) {
      requestIdleCallback(() => {
        localStorage.setItem('lessonTimer', JSON.stringify(timerState));
      });
    } else {
      localStorage.setItem('lessonTimer', JSON.stringify(timerState));
    }
  }, [remaining, isRunning, duration]);

  // Load saved state on mount
  useEffect(() => {
    const saved = localStorage.getItem('lessonTimer');
    if (saved) {
      try {
        const { 
          remaining: savedRemaining, 
          isRunning: wasRunning, 
          duration: savedDuration,
          lastUpdate 
        } = JSON.parse(saved);
        
        if (savedRemaining > 0) {
          const now = Date.now();
          const elapsed = Math.floor((now - lastUpdate) / 1000);
          const adjustedRemaining = Math.max(0, savedRemaining - elapsed);
          
          setDuration(savedDuration || 300);
          setRemaining(adjustedRemaining);
          
          if (wasRunning && adjustedRemaining > 0) {
            // Delay start to ensure component is fully mounted
            setTimeout(() => startTimer(), 100);
          }
        }
      } catch (e) {
        console.warn('Failed to restore timer state:', e);
      }
    }
    
    loadPresets();
    
    // Preload audio files for better performance
    AudioManager.preloadSound('warning', '/++resource++project.title/sounds/warning.mp3');
    AudioManager.preloadSound('complete', '/++resource++project.title/sounds/complete.mp3');
  }, [loadPresets]);

  // Debounced state saving
  useEffect(() => {
    const timeout = setTimeout(saveTimerState, 1000); // Debounce by 1 second
    return () => clearTimeout(timeout);
  }, [saveTimerState]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);

  // Start timer effect with optimization
  useEffect(() => {
    if (isRunning) {
      animationFrameRef.current = requestAnimationFrame(updateTimer);
    }
    
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [isRunning, updateTimer]);

  // Memoized preset options for dropdown
  const presetOptions = useMemo(() => 
    timerPresets.map(preset => ({
      key: preset.name,
      text: `${preset.name} (${preset.description})`,
      value: preset.duration
    }))
  , [timerPresets]);

  // Memoized control buttons
  const controlButtons = useMemo(() => (
    <div className="timer-controls">
      {!isRunning ? (
        <Button 
          primary 
          icon="play" 
          content="Start" 
          onClick={startTimer}
          disabled={remaining === 0 && duration === 0}
        />
      ) : (
        <Button 
          orange 
          icon="pause" 
          content="Pause" 
          onClick={pauseTimer}
        />
      )}
      <Button 
        secondary 
        icon="stop" 
        content="Reset" 
        onClick={resetTimer}
      />
      {!compact && (
        <Button 
          basic 
          icon="expand" 
          content="Fullscreen" 
          onClick={() => setShowFullscreen(true)}
        />
      )}
    </div>
  ), [isRunning, remaining, duration, compact, startTimer, pauseTimer, resetTimer]);

  if (compact) {
    return (
      <ClientOnly>
        <div className="lesson-timer-compact">
          <TimerDisplay 
            remaining={remaining} 
            duration={duration} 
            isRunning={isRunning} 
            compact={true} 
          />
          {controlButtons}
        </div>
      </ClientOnly>
    );
  }

  return (
    <ClientOnly>
      <Segment className="lesson-timer">
        <Header as="h3" icon>
          <Icon name="clock" />
          Lesson Timer
          <Header.Subheader>
            Visual and audio alerts for classroom activities
          </Header.Subheader>
        </Header>

        <TimerDisplay 
          remaining={remaining} 
          duration={duration} 
          isRunning={isRunning} 
        />

        {controlButtons}

        {!isRunning && (
          <Grid columns={2} stackable>
            <Grid.Column>
              <label>Quick Presets:</label>
              <Dropdown
                placeholder="Select preset"
                fluid
                selection
                options={presetOptions}
                onChange={(e, { value }) => {
                  setDuration(value);
                  setRemaining(0);
                }}
              />
            </Grid.Column>
            <Grid.Column>
              <label>Custom Duration:</label>
              <Input
                type="number"
                min="1"
                max="120"
                value={customMinutes}
                onChange={(e) => setCustomMinutes(parseInt(e.target.value) || 5)}
                action={{
                  content: 'Set',
                  onClick: () => {
                    const seconds = customMinutes * 60;
                    setDuration(seconds);
                    setRemaining(0);
                  }
                }}
                placeholder="Minutes"
              />
            </Grid.Column>
          </Grid>
        )}

        <div className="timer-options">
          <Label.Group>
            <Label 
              basic 
              color={soundEnabled ? 'green' : 'red'}
              onClick={() => setSoundEnabled(!soundEnabled)}
              style={{ cursor: 'pointer' }}
            >
              <Icon name={soundEnabled ? 'volume up' : 'volume off'} />
              Sound {soundEnabled ? 'On' : 'Off'}
            </Label>
          </Label.Group>
        </div>

        {/* Fullscreen Modal */}
        <Modal
          open={showFullscreen}
          onClose={() => setShowFullscreen(false)}
          basic
          size="fullscreen"
          className="timer-fullscreen"
        >
          <Modal.Content>
            <div className="fullscreen-timer">
              <Header as="h1" inverted textAlign="center">
                {Math.floor(remaining / 60)}:{(remaining % 60).toString().padStart(2, '0')}
              </Header>
              <Progress 
                percent={duration > 0 ? ((duration - remaining) / duration) * 100 : 0}
                color={remaining <= 60 ? 'red' : remaining <= 120 ? 'orange' : 'green'}
                size="huge"
              />
              <div style={{ textAlign: 'center', marginTop: '2rem' }}>
                <Button 
                  inverted 
                  icon="compress" 
                  content="Exit Fullscreen" 
                  onClick={() => setShowFullscreen(false)}
                />
              </div>
            </div>
          </Modal.Content>
        </Modal>
      </Segment>
    </ClientOnly>
  );
});

LessonTimerOptimized.propTypes = {
  presets: PropTypes.array,
  contentUrl: PropTypes.string,
  compact: PropTypes.bool
};

LessonTimerOptimized.displayName = 'LessonTimerOptimized';

export default LessonTimerOptimized; 