/**
 * Random Student Picker React Component for Volto Integration
 * 
 * Provides fair random student selection with spinning animation
 * and real-time fairness tracking for classroom management.
 */

import React, { useState, useEffect, useCallback } from 'react';
import PropTypes from 'prop-types';
import {
  Container,
  Segment,
  Header,
  Button,
  Grid,
  Icon,
  Message,
  Label,
  Modal,
  Table,
  Progress,
  Statistic
} from 'semantic-ui-react';
import './RandomStudentPicker.css';

// Client-only wrapper to prevent all hydration issues
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

// Error boundary for better error handling
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('RandomStudentPicker Error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <Container fluid style={{textAlign: 'center', padding: '40px'}}>
          <Header as="h3" color="red">
            <Icon name="exclamation triangle" />
            Something went wrong with the Random Student Picker
          </Header>
          <Button onClick={() => this.setState({ hasError: false })}>
            Try Again
          </Button>
        </Container>
      );
    }

    return this.props.children;
  }
}

const RandomStudentPickerComponent = ({ 
  students = [], 
  contentUrl, 
  title = "Random Student Picker" 
}) => {
  const [isSpinning, setIsSpinning] = useState(false);
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [pickerHistory, setPickerHistory] = useState({});
  const [sessionPicks, setSessionPicks] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [fairnessScore, setFairnessScore] = useState(100);
  const [wheelRotation, setWheelRotation] = useState(0);

  // Default students for demo/testing
  const defaultStudents = [
    "Alice Johnson", "Bob Smith", "Carol Williams", "David Brown",
    "Emma Davis", "Frank Miller", "Grace Wilson", "Henry Moore",
    "Ivy Taylor", "Jack Anderson", "Kate Thomas", "Liam Jackson",
    "Maya White", "Noah Harris", "Olivia Martin", "Paul Thompson"
  ];

  const studentList = students.length > 0 ? students : defaultStudents;

  /**
   * Load picker data from backend
   */
  const loadPickerData = useCallback(async () => {
    if (!contentUrl) return;

    try {
      const response = await fetch(`${contentUrl}/@@random-picker?ajax_data=1`, {
        method: 'GET',
        headers: { 'Accept': 'application/json' },
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        setPickerHistory(data.pick_history || {});
        setSessionPicks(data.session_picks || []);
        setFairnessScore(data.fairness_score || 100);
      }
    } catch (error) {
      console.warn('Failed to load picker data:', error);
    }
  }, [contentUrl]);

  useEffect(() => {
    loadPickerData();
  }, [loadPickerData]);

  /**
   * Calculate fairness score based on pick distribution
   */
  const calculateFairnessScore = useCallback(() => {
    if (!Object.keys(pickerHistory).length) return 100;

    const picks = Object.values(pickerHistory).map(student => student.count || 0);
    if (picks.every(p => p === 0)) return 100;

    const avg = picks.reduce((sum, p) => sum + p, 0) / picks.length;
    const variance = picks.reduce((sum, p) => sum + Math.pow(p - avg, 2), 0) / picks.length;
    
    const maxVariance = Math.pow(avg, 2);
    const fairness = maxVariance > 0 ? 100 * (1 - Math.min(variance / maxVariance, 1)) : 100;
    
    return Math.round(fairness);
  }, [pickerHistory]);

  /**
   * Spin the wheel and select a student
   */
  const spinWheel = async () => {
    if (isSpinning || studentList.length === 0) return;

    setIsSpinning(true);

    try {
      // Visual spinning animation
      const spins = 3 + Math.random() * 2; // 3-5 full rotations
      const finalAngle = Math.random() * 360;
      const totalRotation = spins * 360 + finalAngle;
      
      setWheelRotation(totalRotation);

      // Wait for animation to complete
      await new Promise(resolve => setTimeout(resolve, 4000));

      // Make API call to backend for fair selection
      let result;
      if (contentUrl) {
        const response = await fetch(`${contentUrl}/@@pick-student`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
          credentials: 'include'
        });

        if (response.ok) {
          result = await response.json();
        } else {
          throw new Error('Backend selection failed');
        }
      } else {
        // Fallback local selection for demo
        const selected = studentList[Math.floor(Math.random() * studentList.length)];
        result = {
          success: true,
          selected: selected,
          timestamp: new Date().toISOString(),
          fairness_score: calculateFairnessScore()
        };
      }

      if (result.success) {
        setSelectedStudent(result.selected);
        setFairnessScore(result.fairness_score);
        
        // Add to session picks
        const newPick = {
          student: result.selected,
          timestamp: result.timestamp
        };
        setSessionPicks(prev => [...prev, newPick]);

        // Update history
        setPickerHistory(prev => ({
          ...prev,
          [result.selected]: {
            count: (prev[result.selected]?.count || 0) + 1,
            last_picked: Date.now() / 1000,
            picks: [...(prev[result.selected]?.picks || []), result.timestamp]
          }
        }));

        // Show result modal
        setShowModal(true);

        // Play success sound (optional)
        playSuccessSound();
      }

    } catch (error) {
      console.error('Selection failed:', error);
      // Still select locally as fallback
      const fallbackStudent = studentList[Math.floor(Math.random() * studentList.length)];
      setSelectedStudent(fallbackStudent);
      setShowModal(true);
    } finally {
      setIsSpinning(false);
      setWheelRotation(0); // Reset rotation
    }
  };

  /**
   * Play success sound (only when connected to backend)
   */
  const playSuccessSound = () => {
    // Only play sounds when we have a backend connection
    if (!contentUrl) {
      console.log('🔇 Sound disabled: standalone mode (no backend connection)');
      return;
    }
    
    try {
      const audio = new Audio(`${contentUrl}/++resource++project.title/sounds/success.mp3`);
      audio.volume = 0.3;
      audio.play().catch(() => {
        // Sound is optional, ignore errors
      });
    } catch (error) {
      // Sound is optional
    }
  };

  /**
   * Reset picking history
   */
  const resetHistory = async () => {
    if (!window.confirm('Reset all picking history for today? This cannot be undone.')) {
      return;
    }

    try {
      if (contentUrl) {
        const response = await fetch(`${contentUrl}/@@random-picker`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ action: 'reset_history' }),
          credentials: 'include'
        });

        if (!response.ok) {
          throw new Error('Failed to reset on server');
        }
      }

      // Reset local state
      setPickerHistory({});
      setSessionPicks([]);
      setFairnessScore(100);
      
    } catch (error) {
      console.error('Reset failed:', error);
      alert('Failed to reset history. Please try again.');
    }
  };

  /**
   * Format student name for display
   */
  const formatStudentName = (fullName) => {
    const nameParts = fullName.trim().split(' ');
    if (nameParts.length === 1) return nameParts[0];
    
    const firstName = nameParts[0];
    const lastName = nameParts[nameParts.length - 1];
    const lastInitial = lastName.charAt(0).toUpperCase();
    
    return `${firstName} ${lastInitial}.`;
  };

  /**
   * Get fairness color
   */
  const getFairnessColor = (score) => {
    if (score >= 80) return 'green';
    if (score >= 60) return 'blue';
    if (score >= 40) return 'yellow';
    return 'red';
  };

  /**
   * Render spinning wheel
   */
  const renderWheel = () => {
    const anglePerStudent = 360 / studentList.length;
    
    return (
      <div className="picker-wheel-container">
        <div 
          className={`picker-wheel ${isSpinning ? 'spinning' : ''}`}
          style={{
            transform: `rotate(${wheelRotation}deg)`,
            transition: isSpinning ? 'transform 4s cubic-bezier(0.17, 0.67, 0.83, 0.67)' : 'none'
          }}
        >
          <div className="wheel-segments">
            {studentList.map((student, index) => (
              <div
                key={student}
                className="wheel-segment"
                style={{
                  transform: `rotate(${anglePerStudent * index}deg)`,
                  background: `hsl(${(360 / studentList.length) * index}, 70%, 60%)`
                }}
              >
                <span className="segment-text">
                  {formatStudentName(student)}
                </span>
              </div>
            ))}
          </div>
          <div className="wheel-center">
            <Icon name="graduation cap" size="large" />
          </div>
        </div>
        <div className="wheel-pointer">▼</div>
      </div>
    );
  };

  /**
   * Render statistics panel
   */
  const renderStatistics = () => {
    const totalPicks = Object.values(pickerHistory).reduce((sum, student) => sum + (student.count || 0), 0);
    const recentPicks = sessionPicks.slice(-5).reverse();

    return (
      <Segment>
        <Header as="h3">
          <Icon name="chart bar" />
          Fairness Statistics
        </Header>

        <Statistic.Group widths="three" size="small">
          <Statistic>
            <Statistic.Value>{studentList.length}</Statistic.Value>
            <Statistic.Label>Students</Statistic.Label>
          </Statistic>
          
          <Statistic color={getFairnessColor(fairnessScore)}>
            <Statistic.Value>{fairnessScore}%</Statistic.Value>
            <Statistic.Label>Fairness</Statistic.Label>
          </Statistic>
          
          <Statistic>
            <Statistic.Value>{totalPicks}</Statistic.Value>
            <Statistic.Label>Total Picks</Statistic.Label>
          </Statistic>
        </Statistic.Group>

        {/* Recent Selections */}
        <Header as="h4">Recent Selections</Header>
        {recentPicks.length > 0 ? (
          <div className="recent-picks">
            {recentPicks.map((pick, index) => (
              <Label key={index} color={index === 0 ? 'green' : 'grey'}>
                {pick.student}
                <Label.Detail>
                  {new Date(pick.timestamp).toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </Label.Detail>
              </Label>
            ))}
          </div>
        ) : (
          <Message info>No selections yet today</Message>
        )}

        {/* History Table */}
        {Object.keys(pickerHistory).length > 0 && (
          <>
            <Header as="h4">Selection History</Header>
            <Table compact size="small">
              <Table.Header>
                <Table.Row>
                  <Table.HeaderCell>Student</Table.HeaderCell>
                  <Table.HeaderCell>Count</Table.HeaderCell>
                  <Table.HeaderCell>Last Picked</Table.HeaderCell>
                </Table.Row>
              </Table.Header>
              <Table.Body>
                {Object.entries(pickerHistory)
                  .sort(([,a], [,b]) => (a.count || 0) - (b.count || 0))
                  .map(([student, data]) => (
                    <Table.Row 
                      key={student}
                      warning={!data.count || data.count === 0}
                    >
                      <Table.Cell>{student}</Table.Cell>
                      <Table.Cell>{data.count || 0}</Table.Cell>
                      <Table.Cell>
                        {data.last_picked ? 
                          new Date(data.last_picked * 1000).toLocaleTimeString([], {
                            hour: '2-digit',
                            minute: '2-digit'
                          }) : 
                          'Never'
                        }
                      </Table.Cell>
                    </Table.Row>
                  ))}
              </Table.Body>
            </Table>
          </>
        )}
      </Segment>
    );
      };

  return (
    <Container fluid className="random-student-picker">
      <Header as="h1" dividing textAlign="center" className="picker-main-header">
        <Icon name="random" />
        <Header.Content>
          {title}
          <Header.Subheader>
            Fair and equitable student selection for classroom participation
          </Header.Subheader>
        </Header.Content>
      </Header>

      <Grid columns={2} stackable centered>
        <Grid.Column width={10} style={{textAlign: 'center'}}>
          <Segment style={{textAlign: 'center'}} className="wheel-section">
            {renderWheel()}
            
            <div className="picker-controls">
              <Button
                primary
                size="large"
                loading={isSpinning}
                disabled={isSpinning || studentList.length === 0}
                onClick={spinWheel}
              >
                <Icon name="play" />
                {isSpinning ? 'Spinning...' : 'Pick a Student'}
              </Button>
              
              <Button
                secondary
                onClick={resetHistory}
                disabled={isSpinning}
              >
                <Icon name="redo" />
                Reset History
              </Button>
            </div>

            {studentList.length === 0 && (
              <Message warning>
                <Icon name="warning" />
                No students available. Add students to a seating chart first.
              </Message>
            )}
          </Segment>
        </Grid.Column>

        <Grid.Column width={6} style={{textAlign: 'center'}}>
          {renderStatistics()}
        </Grid.Column>
      </Grid>

      {/* Selection Result Modal */}
      <Modal
        open={showModal}
        onClose={() => setShowModal(false)}
        size="small"
        closeIcon
      >
        <Modal.Header>
          <Icon name="trophy" color="yellow" />
          Selected Student
        </Modal.Header>
                    <Modal.Content style={{textAlign: 'center'}}>
          <div className="selected-student-display">
            <div className="student-avatar">
              <Icon name="user" size="huge" />
            </div>
            <div 
              className="student-name-container"
              style={{
                background: 'white',
                backgroundColor: 'white',
                backgroundImage: 'none',
                borderRadius: '8px',
                border: '2px solid #e9ecef',
                boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
                margin: '20px auto',
                padding: '15px 20px',
                maxWidth: '80%'
              }}
            >
              <Header 
                as="h2"
                style={{
                  color: '#2c3e50',
                  background: 'transparent',
                  backgroundColor: 'transparent',
                  backgroundImage: 'none',
                  textShadow: 'none',
                  fontWeight: '600',
                  margin: '0',
                  padding: '0',
                  border: 'none',
                  boxShadow: 'none'
                }}
              >
                {selectedStudent}
              </Header>
            </div>
            <p>
              Selected at: {new Date().toLocaleTimeString()}
            </p>
            <Label size="large">
              Fairness Score: {fairnessScore}%
            </Label>
          </div>
        </Modal.Content>
        <Modal.Actions>
          <Button onClick={() => setShowModal(false)}>
            <Icon name="check" />
            Done
          </Button>
          <Button 
            primary 
            onClick={() => {
              setShowModal(false);
              setTimeout(spinWheel, 500);
            }}
          >
            <Icon name="redo" />
            Pick Another
          </Button>
        </Modal.Actions>
      </Modal>
    </Container>
  );
};

RandomStudentPickerComponent.propTypes = {
  students: PropTypes.arrayOf(PropTypes.string),
  contentUrl: PropTypes.string,
  title: PropTypes.string,
};

// Wrapper with client-only rendering and error boundary
const RandomStudentPicker = (props) => (
  <ErrorBoundary>
    <ClientOnly fallback={
      <Container fluid style={{textAlign: 'center', padding: '40px'}}>
        <Header as="h1" dividing textAlign="center">
          <Icon name="random" />
          <Header.Content>
            Random Student Picker
            <Header.Subheader>
              Loading...
            </Header.Subheader>
          </Header.Content>
        </Header>
      </Container>
    }>
      <RandomStudentPickerComponent {...props} />
    </ClientOnly>
  </ErrorBoundary>
);

export default RandomStudentPicker; 