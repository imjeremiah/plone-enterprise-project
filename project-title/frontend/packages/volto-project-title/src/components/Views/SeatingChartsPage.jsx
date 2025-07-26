/**
 * Standalone Seating Charts Page
 *
 * Interactive classroom seating chart manager that works without backend content.
 * Provides demo functionality for creating and managing seating arrangements.
 */

import React, { useState, useCallback, useEffect } from 'react';
import { useHistory } from 'react-router-dom';
import {
  Container,
  Segment,
  Header,
  Button,
  Grid,
  Icon,
  Message,
  Card,
  Form,
  Modal,
  Statistic,
  Label,
  Divider,
} from 'semantic-ui-react';
import { DragDropContext } from 'react-dnd';
import HTML5Backend from 'react-dnd-html5-backend';
import { TouchBackend } from 'react-dnd-touch-backend';
import SeatingGrid from './SeatingGrid';
import './SeatingChart.css';

const SeatingChartsPage = () => {
  const history = useHistory();
  const [currentChart, setCurrentChart] = useState(null);
  const [editMode, setEditMode] = useState(false);
  const [modalType, setModalType] = useState('create'); // 'create' or 'settings'
  const [modalData, setModalData] = useState({ rows: 6, cols: 8 });
  const [showModal, setShowModal] = useState(false);
  const [newChartData, setNewChartData] = useState({
    title: '',
    description: '',
    rows: 6,
    cols: 8,
  });
  const [charts, setCharts] = useState([]);

  // Load charts from localStorage on component mount
  useEffect(() => {
    const savedCharts = localStorage.getItem('seatingCharts');
    if (savedCharts) {
      try {
        setCharts(JSON.parse(savedCharts));
      } catch (e) {
        console.error('Failed to load saved charts:', e);
        setCharts(getDefaultCharts());
      }
    } else {
      setCharts(getDefaultCharts());
    }
  }, []);

  // Save charts to localStorage whenever charts change
  useEffect(() => {
    if (charts.length > 0) {
      localStorage.setItem('seatingCharts', JSON.stringify(charts));
    }
  }, [charts]);

  // Default demo charts
  const getDefaultCharts = () => [
    {
      id: 'period-1-math',
      title: 'Period 1 - Mathematics',
      description: 'Advanced Algebra Class',
      students: [
        'Alice Johnson',
        'Bob Smith',
        'Carol Davis',
        'David Wilson',
        'Eva Brown',
      ],
      grid_rows: 6,
      grid_cols: 8,
      grid_data: JSON.stringify({
        students: {
          '1,2': 'Alice Johnson',
          '1,4': 'Bob Smith',
          '2,1': 'Carol Davis',
          '2,3': 'David Wilson',
          '3,5': 'Eva Brown',
        },
        empty_desks: ['1,1', '1,3', '1,5'],
        notes: {
          '1,2': 'Needs extra help',
          '3,5': 'Good at math',
        },
      }),
      last_modified: new Date().toLocaleDateString(),
    },
    {
      id: 'period-3-english',
      title: 'Period 3 - English Literature',
      description: 'Shakespeare Unit',
      students: [
        'Frank Miller',
        'Grace Lee',
        'Henry Taylor',
        'Iris Chen',
        'Jack White',
      ],
      grid_rows: 5,
      grid_cols: 6,
      grid_data: JSON.stringify({
        students: {
          '1,1': 'Frank Miller',
          '1,3': 'Grace Lee',
          '2,2': 'Henry Taylor',
          '2,4': 'Iris Chen',
          '3,1': 'Jack White',
        },
        empty_desks: [],
        notes: {},
      }),
      last_modified: new Date().toLocaleDateString(),
    },
  ];

  const createNewChart = () => {
    const newChart = {
      id: `chart-${Date.now()}`,
      title: newChartData.title || 'New Seating Chart',
      description: newChartData.description || 'Custom seating arrangement',
      students: [],
      grid_rows: newChartData.rows,
      grid_cols: newChartData.cols,
      grid_data: JSON.stringify({
        students: {},
        empty_desks: [],
        notes: {},
      }),
      last_modified: new Date().toLocaleDateString(),
    };

    // Add to charts array
    setCharts((prevCharts) => [...prevCharts, newChart]);
    setCurrentChart(newChart);
    setEditMode(true);
    setShowModal(false);
    setNewChartData({ title: '', description: '', rows: 6, cols: 8 });
  };

  const updateGridData = useCallback(
    (newGridData) => {
      if (currentChart) {
        const updatedChart = {
          ...currentChart,
          grid_data: JSON.stringify(newGridData),
          last_modified: new Date().toLocaleDateString(),
        };

        // Update current chart state
        setCurrentChart(updatedChart);

        // Update charts array for persistence
        setCharts((prevCharts) =>
          prevCharts.map((chart) =>
            chart.id === currentChart.id ? updatedChart : chart,
          ),
        );
      }
    },
    [currentChart],
  );

  const updateCurrentChart = useCallback((updatedChart) => {
    // Update current chart state
    setCurrentChart(updatedChart);

    // Update charts array for persistence
    setCharts((prevCharts) =>
      prevCharts.map((chart) =>
        chart.id === updatedChart.id ? updatedChart : chart,
      ),
    );
  }, []);

  const handleStudentMove = useCallback(
    (student, row, col) => {
      if (!currentChart || !editMode) return;

      let gridData;
      try {
        gridData = JSON.parse(currentChart.grid_data);
      } catch (e) {
        gridData = { students: {}, empty_desks: [], notes: {} };
      }

      const newGridData = { ...gridData };

      // Remove student from any existing position
      Object.keys(newGridData.students).forEach((position) => {
        if (newGridData.students[position] === student) {
          delete newGridData.students[position];
        }
      });

      // Add student to new position in "row,col" format
      const newPosition = `${row},${col}`;
      newGridData.students[newPosition] = student;

      updateGridData(newGridData);
    },
    [currentChart, editMode, updateGridData],
  );

  const handleStudentUnassign = useCallback(
    (student) => {
      if (!currentChart || !editMode) return;

      let gridData;
      try {
        gridData = JSON.parse(currentChart.grid_data);
      } catch (e) {
        gridData = { students: {}, empty_desks: [], notes: {} };
      }

      const newGridData = { ...gridData };

      // Remove student from all positions
      Object.keys(newGridData.students).forEach((position) => {
        if (newGridData.students[position] === student) {
          delete newGridData.students[position];
        }
      });

      updateGridData(newGridData);
    },
    [currentChart, editMode, updateGridData],
  );

  const autoArrangeStudents = useCallback(() => {
    if (!currentChart || !editMode) return;

    const students = currentChart.students || [];
    const rows = currentChart.grid_rows;
    const cols = currentChart.grid_cols;

    let gridData;
    try {
      gridData = JSON.parse(currentChart.grid_data);
    } catch (e) {
      gridData = { students: {}, empty_desks: [], notes: {} };
    }

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

    updateGridData(newGridData);
  }, [currentChart, editMode, updateGridData]);

  const unassignAllStudents = useCallback(() => {
    if (!currentChart || !editMode) return;

    let gridData;
    try {
      gridData = JSON.parse(currentChart.grid_data);
    } catch (e) {
      gridData = { students: {}, empty_desks: [], notes: {} };
    }

    const newGridData = {
      ...gridData,
      students: {}, // Clear all student positions
    };

    updateGridData(newGridData);
  }, [currentChart, editMode, updateGridData]);

  const renderChartsList = () => (
    <Container>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '20px',
        }}
      >
        <div>
          <Header as="h2">
            <Icon name="sitemap" color="orange" />
            Seating Charts Manager
          </Header>
          <p style={{ color: '#666', margin: 0 }}>
            Create and manage interactive classroom seating arrangements
          </p>
        </div>
        <Button
          primary
          size="large"
          onClick={() => {
            setModalType('create');
            setModalData({ rows: 6, cols: 8 });
            setShowModal(true);
          }}
        >
          <Icon name="plus" />
          Create New Chart
        </Button>
        <Button
          color="orange"
          size="large"
          onClick={() => {
            const confirmed = window.confirm(
              'Are you sure you want to reset all charts to default demo data? This will remove all your changes.',
            );
            if (confirmed) {
              const defaultCharts = getDefaultCharts();
              setCharts(defaultCharts);
              localStorage.setItem(
                'seatingCharts',
                JSON.stringify(defaultCharts),
              );
              setCurrentChart(null);
            }
          }}
          style={{ marginLeft: '10px' }}
        >
          <Icon name="refresh" />
          Reset to Defaults
        </Button>
      </div>

      <Statistic.Group
        size="small"
        widths="three"
        style={{ marginBottom: '30px' }}
      >
        <Statistic>
          <Statistic.Value>{charts.length}</Statistic.Value>
          <Statistic.Label>Total Charts</Statistic.Label>
        </Statistic>
        <Statistic>
          <Statistic.Value>
            {charts.reduce((sum, chart) => sum + chart.students.length, 0)}
          </Statistic.Value>
          <Statistic.Label>Students Seated</Statistic.Label>
        </Statistic>
        <Statistic color="green">
          <Statistic.Value>100%</Statistic.Value>
          <Statistic.Label>Active Charts</Statistic.Label>
        </Statistic>
      </Statistic.Group>

      <Card.Group itemsPerRow={2}>
        {charts.map((chart) => (
          <Card key={chart.id} className="seating-chart-card">
            <Card.Content>
              <Card.Header>{chart.title}</Card.Header>
              <Card.Meta>{chart.description}</Card.Meta>
              <Card.Description>
                <div style={{ marginTop: '10px' }}>
                  <Label color="blue" size="small">
                    <Icon name="users" />
                    {chart.students.length} students
                  </Label>
                  <Label color="orange" size="small">
                    <Icon name="grid layout" />
                    {chart.grid_rows}×{chart.grid_cols} grid
                  </Label>
                </div>
                <div
                  style={{ marginTop: '8px', fontSize: '0.9em', color: '#666' }}
                >
                  Last modified: {chart.last_modified}
                </div>
              </Card.Description>
            </Card.Content>
            <Card.Content extra>
              <div className="ui two buttons">
                <Button
                  basic
                  color="blue"
                  onClick={() => setCurrentChart(chart)}
                >
                  <Icon name="eye" />
                  View
                </Button>
                <Button
                  basic
                  color="green"
                  onClick={() => {
                    setCurrentChart(chart);
                    setEditMode(true);
                  }}
                >
                  <Icon name="edit" />
                  Edit
                </Button>
              </div>
            </Card.Content>
          </Card>
        ))}
      </Card.Group>
    </Container>
  );

  const renderCurrentChart = () => {
    if (!currentChart) return null;

    let gridData;
    try {
      gridData = JSON.parse(currentChart.grid_data);
    } catch (e) {
      gridData = { students: {}, empty_desks: [], notes: {} };
    }

    const renderToolbar = () => {
      const students = currentChart.students || [];
      const assignedCount = Object.keys(gridData?.students || {}).length;

      return (
        <Segment
          clearing
          className="seating-chart-toolbar"
          style={{ marginBottom: '20px' }}
        >
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
                setModalData({
                  rows: currentChart.grid_rows,
                  cols: currentChart.grid_cols,
                });
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
              {currentChart.grid_rows} × {currentChart.grid_cols} Grid
            </Label>
            {assignedCount > 0 && (
              <Label color="teal">
                <Icon name="checkmark" />
                {assignedCount} Assigned
              </Label>
            )}
            <Label color={editMode ? 'red' : 'grey'}>
              <Icon name={editMode ? 'edit' : 'eye'} />
              {editMode ? 'Edit Mode' : 'View Mode'}
            </Label>
          </Label.Group>
        </Segment>
      );
    };

    return (
      <Container fluid>
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '20px',
          }}
        >
          <div>
            <Header as="h2">
              <Icon name="sitemap" color="orange" />
              {currentChart.title}
            </Header>
            <p style={{ color: '#666', margin: 0 }}>
              {currentChart.description}
            </p>
          </div>
          <div>
            <Button
              onClick={() => setCurrentChart(null)}
              style={{ marginRight: '10px' }}
            >
              <Icon name="arrow left" />
              Back to Charts
            </Button>
          </div>
        </div>

        {renderToolbar()}

        <Segment>
          <SeatingGrid
            gridData={gridData}
            students={currentChart.students || []}
            rows={currentChart.grid_rows}
            cols={currentChart.grid_cols}
            onMove={handleStudentMove}
            onUnassign={handleStudentUnassign}
            editable={editMode}
          />
        </Segment>
      </Container>
    );
  };

  const applySettings = () => {
    if (!currentChart) return;

    const newRows = modalData.rows;
    const newCols = modalData.cols;

    let gridData;
    try {
      gridData = JSON.parse(currentChart.grid_data);
    } catch (e) {
      gridData = { students: {}, empty_desks: [], notes: {} };
    }

    const newGridData = { ...gridData };

    // Remove students that are outside the new grid boundaries
    Object.keys(newGridData.students).forEach((position) => {
      const [currentRow, currentCol] = position.split(',').map(Number);
      if (currentRow >= newRows || currentCol >= newCols) {
        delete newGridData.students[position];
      }
    });

    // Update the current chart with new dimensions and grid data
    const updatedChart = {
      ...currentChart,
      grid_rows: newRows,
      grid_cols: newCols,
      grid_data: JSON.stringify(newGridData),
      last_modified: new Date().toLocaleDateString(),
    };

    updateCurrentChart(updatedChart);
    setShowModal(false);
  };

  const renderCreateModal = () => (
    <Modal open={showModal} onClose={() => setShowModal(false)}>
      <Modal.Header>
        <Icon name={modalType === 'settings' ? 'settings' : 'plus'} />
        {modalType === 'settings'
          ? 'Chart Settings'
          : 'Create New Seating Chart'}
      </Modal.Header>
      <Modal.Content>
        <Form>
          {modalType !== 'settings' && (
            <>
              <Form.Input
                label="Chart Title"
                placeholder="e.g., Period 2 - Science"
                value={newChartData.title}
                onChange={(e, { value }) =>
                  setNewChartData({ ...newChartData, title: value })
                }
              />
              <Form.Input
                label="Description"
                placeholder="e.g., Biology Lab Class"
                value={newChartData.description}
                onChange={(e, { value }) =>
                  setNewChartData({ ...newChartData, description: value })
                }
              />
            </>
          )}
          <Form.Group widths="equal">
            <Form.Input
              label="Rows"
              type="number"
              min="3"
              max="10"
              value={
                modalType === 'settings' ? modalData.rows : newChartData.rows
              }
              onChange={(e, { value }) => {
                const rows = parseInt(value) || 6;
                if (modalType === 'settings') {
                  setModalData({ ...modalData, rows });
                } else {
                  setNewChartData({ ...newChartData, rows });
                }
              }}
            />
            <Form.Input
              label="Columns"
              type="number"
              min="4"
              max="12"
              value={
                modalType === 'settings' ? modalData.cols : newChartData.cols
              }
              onChange={(e, { value }) => {
                const cols = parseInt(value) || 8;
                if (modalType === 'settings') {
                  setModalData({ ...modalData, cols });
                } else {
                  setNewChartData({ ...newChartData, cols });
                }
              }}
            />
          </Form.Group>
          {modalType === 'settings' && (
            <Message info>
              <Message.Header>Note</Message.Header>
              <p>
                Changing grid size may affect existing student placements.
                Students outside the new grid will be moved to the unassigned
                pool.
              </p>
            </Message>
          )}
        </Form>
      </Modal.Content>
      <Modal.Actions>
        <Button onClick={() => setShowModal(false)}>Cancel</Button>
        <Button
          color={modalType === 'settings' ? 'blue' : 'green'}
          onClick={modalType === 'settings' ? applySettings : createNewChart}
        >
          <Icon name={modalType === 'settings' ? 'save' : 'checkmark'} />
          {modalType === 'settings' ? 'Apply Settings' : 'Create Chart'}
        </Button>
      </Modal.Actions>
    </Modal>
  );

  return (
    <div
      className="seating-charts-page"
      style={{ padding: '20px 0', minHeight: '100vh', background: '#f8f9fa' }}
    >
      {currentChart ? renderCurrentChart() : renderChartsList()}
      {renderCreateModal()}
    </div>
  );
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

export default DragDropContext(getBackend())(SeatingChartsPage);
