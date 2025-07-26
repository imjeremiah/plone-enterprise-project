/**
 * Seating Chart View for Classroom Management
 *
 * Interactive classroom seating arrangements with drag-drop student positioning.
 * Phase 2C: Full drag-drop functionality for classroom management.
 */

import React, { useState, useEffect, useCallback } from 'react';
import PropTypes from 'prop-types';
import { useHistory, useLocation } from 'react-router-dom';
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
  Form,
  Input,
  TextArea,
  Dropdown,
} from 'semantic-ui-react';
import { DragDropContext } from 'react-dnd';
import HTML5Backend from 'react-dnd-html5-backend';
import { TouchBackend } from 'react-dnd-touch-backend';
import SeatingGrid from './SeatingGrid';
import './SeatingChart.css';

const SeatingChartView = ({ content, location }) => {
  const history = useHistory();
  const [editMode, setEditMode] = useState(false);
  const [gridData, setGridData] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [modalType, setModalType] = useState('');
  const [modalData, setModalData] = useState({});

  useEffect(() => {
    if (content && content.grid_data) {
      try {
        const parsed = JSON.parse(content.grid_data);
        setGridData(parsed);
      } catch (e) {
        console.error('Failed to parse grid data:', e);
        setGridData({ students: {}, empty_desks: [], notes: {} });
      }
    } else {
      setGridData({ students: {}, empty_desks: [], notes: {} });
    }
  }, [content]);

  const unassignStudent = useCallback(
    (studentName) => {
      if (!editMode || !gridData) return;

      const newGridData = { ...gridData };

      // Remove student from current position
      Object.keys(newGridData.students).forEach((key) => {
        if (newGridData.students[key] === studentName) {
          delete newGridData.students[key];
        }
      });

      setGridData(newGridData);
      updateBackendGrid(newGridData);
    },
    [gridData, editMode, content],
  );

  const unassignAllStudents = useCallback(() => {
    if (!editMode || !gridData) return;

    const newGridData = {
      ...gridData,
      students: {}, // Clear all student positions
    };

    setGridData(newGridData);
    updateBackendGrid(newGridData);
  }, [gridData, editMode, content]);

  const moveStudent = useCallback(
    (studentName, targetRow, targetCol) => {
      if (!editMode || !gridData) return;

      const positionKey = `${targetRow},${targetCol}`;
      const newGridData = { ...gridData };

      // Remove student from current position
      Object.keys(newGridData.students).forEach((key) => {
        if (newGridData.students[key] === studentName) {
          delete newGridData.students[key];
        }
      });

      // Add student to new position
      newGridData.students[positionKey] = studentName;
      setGridData(newGridData);

      // Update backend
      updateBackendPosition(studentName, targetRow, targetCol, newGridData);
    },
    [gridData, editMode, content],
  );

  const autoArrangeStudents = useCallback(() => {
    if (!editMode || !content || !gridData) return;

    const students = content.students || [];
    const rows = content.grid_rows || 5;
    const cols = content.grid_cols || 6;
    const newGridData = { ...gridData, students: {} };

    let studentIndex = 0;
    for (let row = 0; row < rows && studentIndex < students.length; row++) {
      for (let col = 0; col < cols && studentIndex < students.length; col++) {
        const positionKey = `${row},${col}`;
        if (!newGridData.empty_desks.includes(positionKey)) {
          newGridData.students[positionKey] = students[studentIndex];
          studentIndex++;
        }
      }
    }

    setGridData(newGridData);
    updateBackendGrid(newGridData);
  }, [editMode, content, gridData]);

  const updateBackendPosition = async (student, row, col, updatedGrid) => {
    try {
      const response = await fetch(`${content['@id']}/@@update-position`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        body: JSON.stringify({
          student: student,
          row: row,
          col: col,
          grid_data: updatedGrid,
        }),
      });

      if (!response.ok) {
        console.error('Failed to update position');
      }
    } catch (error) {
      console.error('Error updating position:', error);
    }
  };

  const updateBackendGrid = async (updatedGrid) => {
    try {
      const response = await fetch(`${content['@id']}/@@update-grid`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        body: JSON.stringify({
          grid_data: updatedGrid,
        }),
      });

      if (!response.ok) {
        console.error('Failed to update grid');
      }
    } catch (error) {
      console.error('Error updating grid:', error);
    }
  };

  // Get students data with fallback for testing
  const getStudents = () => {
    if (content?.students && content.students.length > 0) {
      return content.students;
    }
    // Fallback test data when no students are provided
    return [
      'Alice Johnson',
      'Bob Smith',
      'Carol Williams',
      'David Brown',
      'Emma Davis',
      'Frank Miller',
      'Grace Wilson',
      'Henry Moore',
      'Ivy Taylor',
      'Jack Anderson',
      'Kate Thomas',
      'Liam Jackson',
      'Maya White',
      'Noah Harris',
      'Olivia Martin',
      'Paul Thompson',
    ];
  };

  const renderSeatingGrid = () => {
    if (!gridData) {
      return <Message>Loading seating arrangement...</Message>;
    }

    return (
      <SeatingGrid
        gridData={gridData}
        students={getStudents()}
        rows={content.grid_rows || 4}
        cols={content.grid_cols || 6}
        onMove={moveStudent}
        onUnassign={unassignStudent}
        editable={editMode}
      />
    );
  };

  const renderToolbar = () => {
    const students = getStudents();
    const assignedCount = Object.keys(gridData?.students || {}).length;

    return (
      <Segment clearing className="seating-chart-toolbar">
        <Button.Group floated="right" className="seating-chart-buttons">
          <Button
            content={editMode ? 'View Mode' : 'Edit Mode'}
            onClick={() => setEditMode(!editMode)}
            color={editMode ? 'red' : 'blue'}
            className="seating-chart-button mode-toggle-button"
          />
          <Button
            content="Auto-Arrange Students"
            disabled={!editMode}
            onClick={autoArrangeStudents}
            color="blue"
            className="seating-chart-button auto-arrange-button"
          />
          <Button
            content="Unassign All"
            disabled={!editMode || assignedCount === 0}
            onClick={unassignAllStudents}
            color="orange"
            className="seating-chart-button unassign-all-button"
          />
          <Button
            content="Settings"
            onClick={() => {
              setModalType('settings');
              setShowModal(true);
            }}
            className="seating-chart-button settings-button"
          />
        </Button.Group>

        <Label.Group>
          <Label color="blue">
            <Icon name="users" />
            {students.length} Students
          </Label>
          <Label color="green">
            <Icon name="grid layout" />
            {content.grid_rows || 4} × {content.grid_cols || 6} Grid
          </Label>
          {assignedCount > 0 && (
            <Label color="teal">
              <Icon name="checkmark" />
              {assignedCount} Assigned
            </Label>
          )}
          {editMode && (
            <Label color="orange">
              <Icon name="edit" />
              Edit Mode Active
            </Label>
          )}
        </Label.Group>
      </Segment>
    );
  };

  const renderModal = () => (
    <Modal open={showModal} onClose={() => setShowModal(false)} size="small">
      <Modal.Header>
        {modalType === 'settings'
          ? 'Seating Chart Settings'
          : 'Student Details'}
      </Modal.Header>
      <Modal.Content>
        {modalType === 'settings' ? (
          <Form>
            <Form.Field>
              <label>Grid Size</label>
              <Grid columns={2}>
                <Grid.Column>
                  <Input
                    label="Rows"
                    type="number"
                    defaultValue={content.grid_rows || 5}
                    min="1"
                    max="10"
                  />
                </Grid.Column>
                <Grid.Column>
                  <Input
                    label="Columns"
                    type="number"
                    defaultValue={content.grid_cols || 6}
                    min="1"
                    max="10"
                  />
                </Grid.Column>
              </Grid>
            </Form.Field>
          </Form>
        ) : (
          <p>Student details coming soon...</p>
        )}
      </Modal.Content>
      <Modal.Actions>
        <Button onClick={() => setShowModal(false)}>Cancel</Button>
        <Button color="blue" onClick={() => setShowModal(false)}>
          Save Changes
        </Button>
      </Modal.Actions>
    </Modal>
  );

  if (!content) {
    return <Message error>Error: No seating chart data available</Message>;
  }

  return (
    <Container fluid>
      <Header as="h1" dividing>
        <Icon name="sitemap" />
        <Header.Content>
          {content.title || 'Seating Chart'}
          <Header.Subheader>
            {content.description || 'Interactive classroom seating arrangement'}
          </Header.Subheader>
        </Header.Content>
      </Header>

      {renderToolbar()}

      <Segment>{renderSeatingGrid()}</Segment>

      {renderModal()}
    </Container>
  );
};

SeatingChartView.propTypes = {
  content: PropTypes.shape({
    '@id': PropTypes.string,
    title: PropTypes.string,
    description: PropTypes.string,
    students: PropTypes.arrayOf(PropTypes.string),
    grid_rows: PropTypes.number,
    grid_cols: PropTypes.number,
    grid_data: PropTypes.string,
  }).isRequired,
  location: PropTypes.object,
};

// Apply DragDropContext HOC with improved backend detection
const getBackend = () => {
  // Safe check for window object (SSR compatibility)
  if (typeof window === 'undefined') {
    return HTML5Backend; // Default for SSR
  }

  // Touch device detection for mobile/tablet support
  const isTouchDevice =
    'ontouchstart' in window || navigator.maxTouchPoints > 0;

  if (isTouchDevice) {
    return TouchBackend({ enableMouseEvents: true });
  }

  return HTML5Backend;
};

export default DragDropContext(getBackend())(SeatingChartView);
