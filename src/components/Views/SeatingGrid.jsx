/**
 * Seating Grid Component with Drag-Drop (react-dnd v5)
 * 
 * Interactive grid for drag-drop student positioning in classroom seating charts.
 * Uses react-dnd v5 HOC approach for compatibility with Volto core.
 */

import React from 'react';
import PropTypes from 'prop-types';
import { DragSource, DropTarget } from 'react-dnd';
import { Icon } from 'semantic-ui-react';

const STUDENT_TYPE = 'student';

/**
 * Drag source specification for students
 */
const studentSource = {
  beginDrag(props) {
    return {
      student: props.student,
    };
  },
  canDrag(props) {
    return props.editable;
  },
};

/**
 * Drag source collection function
 */
const collectSource = (connect, monitor) => ({
  connectDragSource: connect.dragSource(),
  isDragging: monitor.isDragging(),
});

/**
 * Individual draggable student component
 */
const DraggableStudentComponent = ({ student, editable, connectDragSource, isDragging }) => {
  return connectDragSource(
    <div
      className={`student-token ${isDragging ? 'dragging' : ''} ${editable ? 'draggable' : ''}`}
      style={{
        opacity: isDragging ? 0.5 : 1,
        cursor: editable ? 'move' : 'default',
      }}
    >
      <Icon name="user" size="small" />
      <span className="student-name">{student}</span>
    </div>
  );
};

const DraggableStudent = DragSource(STUDENT_TYPE, studentSource, collectSource)(DraggableStudentComponent);

/**
 * Drop target specification for desk slots
 */
const deskTarget = {
  drop(props, monitor) {
    const item = monitor.getItem();
    if (props.editable && props.onDrop && !props.isEmpty) {
      props.onDrop(item.student, props.row, props.col);
    }
  },
  canDrop(props) {
    return props.editable && !props.isEmpty;
  },
};

/**
 * Drop target collection function
 */
const collectTarget = (connect, monitor) => ({
  connectDropTarget: connect.dropTarget(),
  isOver: monitor.isOver(),
  canDrop: monitor.canDrop(),
});

/**
 * Droppable desk slot component
 */
const DeskSlotComponent = ({ 
  row, 
  col, 
  student, 
  editable, 
  isEmpty, 
  connectDropTarget, 
  isOver, 
  canDrop 
}) => {
  let deskClass = 'desk-slot';
  if (student) deskClass += ' occupied';
  if (isEmpty) deskClass += ' empty-desk';
  if (editable) deskClass += ' editable';
  if (isOver && canDrop) deskClass += ' drag-over';
  if (!canDrop && isOver) deskClass += ' drag-invalid';

  return connectDropTarget(
    <div
      className={deskClass}
      data-row={row}
      data-col={col}
    >
      {student && (
        <DraggableStudent 
          student={student} 
          editable={editable}
        />
      )}
      {isEmpty && (
        <div className="empty-label">
          <Icon name="ban" color="grey" />
          <span>Empty</span>
        </div>
      )}
      {!student && !isEmpty && editable && (
        <div className="available-slot">
          <Icon name="plus" color="grey" />
          <span>Drop Here</span>
        </div>
      )}
      {!student && !isEmpty && !editable && (
        <div className="available-slot">
          <Icon name="circle outline" color="grey" />
        </div>
      )}
    </div>
  );
};

const DeskSlot = DropTarget(STUDENT_TYPE, deskTarget, collectTarget)(DeskSlotComponent);

/**
 * Main seating grid with drag-drop functionality
 */
const SeatingGrid = ({ gridData, students, rows, cols, onMove, editable }) => {
  /**
   * Find student at specific grid position
   */
  const getStudentAt = (row, col) => {
    const positionKey = `${row},${col}`;
    return gridData.students[positionKey] || null;
  };

  /**
   * Check if position is marked as empty desk
   */
  const isEmptyDesk = (row, col) => {
    const positionKey = `${row},${col}`;
    return gridData.empty_desks.includes(positionKey);
  };

  /**
   * Render the grid layout
   */
  const renderGrid = () => {
    const slots = [];
    for (let row = 0; row < rows; row++) {
      for (let col = 0; col < cols; col++) {
        const student = getStudentAt(row, col);
        const isEmpty = isEmptyDesk(row, col);
        
        slots.push(
          <DeskSlot
            key={`${row}-${col}`}
            row={row}
            col={col}
            student={student}
            isEmpty={isEmpty}
            onDrop={onMove}
            editable={editable}
          />
        );
      }
    }
    return slots;
  };

  /**
   * Render unassigned students (available for dragging)
   */
  const renderUnassignedStudents = () => {
    if (!editable || !students) return null;

    const assignedStudents = Object.values(gridData.students);
    const unassigned = students.filter(student => !assignedStudents.includes(student));

    if (unassigned.length === 0) return null;

    return (
      <div className="unassigned-students">
        <div className="unassigned-header">
          <Icon name="users" />
          <strong>Unassigned Students ({unassigned.length})</strong>
        </div>
        <div className="student-pool">
          {unassigned.map(student => (
            <DraggableStudent
              key={student}
              student={student}
              editable={editable}
            />
          ))}
        </div>
      </div>
    );
  };

  const gridStyle = {
    display: 'grid',
    gridTemplateColumns: `repeat(${cols}, 1fr)`,
    gap: '10px',
    maxWidth: '800px',
    margin: '0 auto',
    padding: '20px',
  };

  return (
    <div className="seating-grid-container">
      {/* Teacher's Desk Indicator */}
      <div className="teacher-area">
        <Icon name="graduation cap" size="large" />
        <span>Teacher's Desk</span>
      </div>

      {/* Main Seating Grid */}
      <div className="seating-grid" style={gridStyle}>
        {renderGrid()}
      </div>

      {/* Unassigned Students Pool */}
      {renderUnassignedStudents()}

      {/* Grid Instructions */}
      {editable && (
        <div className="grid-instructions">
          <Icon name="info circle" color="blue" />
          <span>
            Drag students from the pool below or between desks to arrange seating. 
            Works on tablets and desktop!
          </span>
        </div>
      )}
    </div>
  );
};

SeatingGrid.propTypes = {
  gridData: PropTypes.shape({
    students: PropTypes.object.isRequired,
    empty_desks: PropTypes.array.isRequired,
    notes: PropTypes.object,
  }).isRequired,
  students: PropTypes.arrayOf(PropTypes.string).isRequired,
  rows: PropTypes.number.isRequired,
  cols: PropTypes.number.isRequired,
  onMove: PropTypes.func.isRequired,
  editable: PropTypes.bool.isRequired,
};

DraggableStudentComponent.propTypes = {
  student: PropTypes.string.isRequired,
  editable: PropTypes.bool.isRequired,
  connectDragSource: PropTypes.func.isRequired,
  isDragging: PropTypes.bool.isRequired,
};

DeskSlotComponent.propTypes = {
  row: PropTypes.number.isRequired,
  col: PropTypes.number.isRequired,
  student: PropTypes.string,
  editable: PropTypes.bool.isRequired,
  isEmpty: PropTypes.bool,
  connectDropTarget: PropTypes.func.isRequired,
  isOver: PropTypes.bool.isRequired,
  canDrop: PropTypes.bool.isRequired,
  onDrop: PropTypes.func,
};

export default SeatingGrid; 