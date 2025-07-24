/**
 * Random Picker Widget for Embedding in Other Views
 * 
 * A compact version of the Random Student Picker that can be
 * embedded within seating charts or other classroom management views.
 */

import React, { useState, useCallback } from 'react';
import PropTypes from 'prop-types';
import {
  Segment,
  Header,
  Button,
  Icon,
  Modal,
  Statistic,
  Message
} from 'semantic-ui-react';

const RandomPickerWidget = ({ 
  students = [], 
  contentUrl,
  compact = false,
  onStudentSelected
}) => {
  const [isSpinning, setIsSpinning] = useState(false);
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [fairnessScore, setFairnessScore] = useState(100);

  /**
   * Quick spin without complex animation for widget use
   */
  const quickSpin = async () => {
    if (isSpinning || students.length === 0) return;

    setIsSpinning(true);

    try {
      // Quick visual feedback
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Make API call or local selection
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
        // Local fallback selection
        const selected = students[Math.floor(Math.random() * students.length)];
        result = {
          success: true,
          selected: selected,
          timestamp: new Date().toISOString(),
          fairness_score: 100
        };
      }

      if (result.success) {
        setSelectedStudent(result.selected);
        setFairnessScore(result.fairness_score);
        
        // Callback for parent component
        if (onStudentSelected) {
          onStudentSelected(result.selected, result);
        }

        // Show result
        if (compact) {
          // For compact mode, just highlight briefly
          await new Promise(resolve => setTimeout(resolve, 1500));
        } else {
          // For normal mode, show modal
          setShowModal(true);
        }
      }

    } catch (error) {
      console.error('Selection failed:', error);
      // Fallback local selection
      const fallbackStudent = students[Math.floor(Math.random() * students.length)];
      setSelectedStudent(fallbackStudent);
      
      if (onStudentSelected) {
        onStudentSelected(fallbackStudent, { selected: fallbackStudent });
      }
      
      if (!compact) {
        setShowModal(true);
      }
    } finally {
      setIsSpinning(false);
    }
  };

  /**
   * Render compact version for embedding
   */
  const renderCompact = () => (
    <div className="random-picker-widget-compact">
      <Button
        fluid
        primary
        loading={isSpinning}
        disabled={isSpinning || students.length === 0}
        onClick={quickSpin}
        size="small"
      >
        <Icon name="dice" />
        {isSpinning ? 'Selecting...' : 'Pick Random Student'}
      </Button>
      
      {selectedStudent && !isSpinning && (
        <Message positive size="small" style={{ marginTop: '10px' }}>
          <Icon name="trophy" />
          <strong>{selectedStudent}</strong> was selected!
        </Message>
      )}
      
      {students.length === 0 && (
        <Message warning size="small" style={{ marginTop: '10px' }}>
          No students available
        </Message>
      )}
    </div>
  );

  /**
   * Render full widget version
   */
  const renderFull = () => (
    <Segment className="random-picker-widget">
      <Header as="h4">
        <Icon name="dice" color="blue" />
        <Header.Content>
          Quick Student Picker
          <Header.Subheader>
            Fair random selection from {students.length} students
          </Header.Subheader>
        </Header.Content>
      </Header>

      <div className="widget-controls" style={{ textAlign: 'center', marginBottom: '15px' }}>
        <Button
          primary
          loading={isSpinning}
          disabled={isSpinning || students.length === 0}
          onClick={quickSpin}
        >
          <Icon name="play" />
          {isSpinning ? 'Selecting...' : 'Pick a Student'}
        </Button>
      </div>

      {fairnessScore < 100 && (
        <Statistic size="mini" style={{ marginTop: '10px' }}>
          <Statistic.Value>{fairnessScore}%</Statistic.Value>
          <Statistic.Label>Fairness Score</Statistic.Label>
        </Statistic>
      )}

      {students.length === 0 && (
        <Message warning>
          <Icon name="warning" />
          No students available for selection
        </Message>
      )}

      {/* Selection Result Modal */}
      <Modal
        open={showModal}
        onClose={() => setShowModal(false)}
        size="mini"
        closeIcon
      >
        <Modal.Header>
          <Icon name="trophy" color="yellow" />
          Selected Student
        </Modal.Header>
        <Modal.Content textAlign="center">
          <Header as="h3" color="blue">
            {selectedStudent}
          </Header>
          <p>Ready for participation!</p>
        </Modal.Content>
        <Modal.Actions>
          <Button primary onClick={() => setShowModal(false)}>
            <Icon name="check" />
            Got it!
          </Button>
        </Modal.Actions>
      </Modal>
    </Segment>
  );

  return compact ? renderCompact() : renderFull();
};

RandomPickerWidget.propTypes = {
  students: PropTypes.arrayOf(PropTypes.string),
  contentUrl: PropTypes.string,
  compact: PropTypes.bool,
  onStudentSelected: PropTypes.func,
};

export default RandomPickerWidget; 