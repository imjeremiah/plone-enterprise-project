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
import TouchBackend from 'react-dnd-touch-backend';
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

  const moveStudent = useCallback((studentName, targetRow, targetCol) => {
    if (!editMode || !gridData) return;

    const positionKey = `${targetRow},${targetCol}`;
    const newGridData = { ...gridData };
    
    // Remove student from current position
    Object.keys(newGridData.students).forEach(key => {
      if (newGridData.students[key] === studentName) {
        delete newGridData.students[key];
      }
    });

    // Add student to new position
    newGridData.students[positionKey] = studentName;
    setGridData(newGridData);

    // Update backend
    updateBackendPosition(studentName, targetRow, targetCol, newGridData);
  }, [gridData, editMode, content]);

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
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          student: student,
          row: row,
          col: col,
          grid_data: updatedGrid
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
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          grid_data: updatedGrid
        }),
      });

      if (!response.ok) {
        console.error('Failed to update grid');
      }
    } catch (error) {
      console.error('Error updating grid:', error);
    }
  };

  const renderSeatingGrid = () => {
    if (!gridData) {
      return <Message>Loading seating arrangement...</Message>;
    }
    return (
      <SeatingGrid
        gridData={gridData}
        students={content.students || []}
        rows={content.grid_rows || 5}
        cols={content.grid_cols || 6}
        onMove={moveStudent}
        editable={editMode}
      />
    );
  };

  const renderToolbar = () => (
    <Segment clearing>
      <Button.Group floated="right">
        <Button
          icon="edit"
          content={editMode ? "View Mode" : "Edit Mode"}
          onClick={() => setEditMode(!editMode)}
          color={editMode ? "red" : "blue"}
        />
        <Button 
          icon="shuffle" 
          content="Auto-Arrange Students" 
          disabled={!editMode}
          onClick={autoArrangeStudents}
          color="blue"
        />
        <Button
          icon="settings"
          content="Settings"
          onClick={() => { setModalType('settings'); setShowModal(true); }}
        />
      </Button.Group>
      
      <Label.Group>
        <Label color="blue">
          <Icon name="users" />
          {content.students ? content.students.length : 0} Students
        </Label>
        <Label color="green">
          <Icon name="grid layout" />
          {content.grid_rows || 5} × {content.grid_cols || 6} Grid
        </Label>
        {editMode && (
          <Label color="orange">
            <Icon name="edit" />
            Edit Mode Active
          </Label>
        )}
      </Label.Group>
    </Segment>
  );

  const renderModal = () => (
    <Modal open={showModal} onClose={() => setShowModal(false)} size="small">
      <Modal.Header>
        {modalType === 'settings' ? 'Seating Chart Settings' : 'Student Details'}
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
      
      <Segment>
        {renderSeatingGrid()}
      </Segment>

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

// Apply DragDropContext HOC with backend detection
const getBackend = () => {
  return 'ontouchstart' in window ? TouchBackend : HTML5Backend;
};

export default DragDropContext(getBackend())(SeatingChartView); 