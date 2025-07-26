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
 * Format student name for display: "FirstName L." instead of truncating
 */
const formatStudentName = (fullName) => {
  if (!fullName) return '';
  
  const nameParts = fullName.trim().split(' ');
  if (nameParts.length === 1) {
    return nameParts[0]; // Just first name if only one part
  }
  
  const firstName = nameParts[0];
  const lastName = nameParts[nameParts.length - 1];
  const lastInitial = lastName.charAt(0).toUpperCase();
  
  return `${firstName} ${lastInitial}.`;
};

/**
 * Individual draggable student component
 */
const DraggableStudentComponent = ({ student, editable, connectDragSource, isDragging }) => {
  const displayName = formatStudentName(student);
  
  return connectDragSource(
    <div
      className={`student-token seating-chart-student-token ${isDragging ? 'dragging' : ''} ${editable ? 'draggable' : ''}`}
      style={{
        opacity: isDragging ? 0.5 : 1,
        cursor: editable ? 'move' : 'default',
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        textAlign: 'center'
      }}
    >
      <Icon name="user" size="small" />
      <span className="student-name seating-chart-student-name" style={{textAlign: 'center', marginLeft: '4px'}}>{displayName}</span>
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
    if (props.editable && props.onDrop) {
      props.onDrop(item.student, props.row, props.col);
    }
  },
  canDrop(props) {
    return props.editable;
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
  canDrop,
  hideInViewMode
}) => {
  // Hide empty desks in view mode by rendering invisible placeholder
  if (hideInViewMode) {
    return <div className="desk-slot hidden-empty" style={{ visibility: 'hidden' }}></div>;
  }

  let deskClass = 'desk-slot';
  if (student) deskClass += ' occupied';
  if (isEmpty && !editable) deskClass += ' empty-desk';
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
      {isEmpty && !editable && (
        <div className="empty-label">
          <Icon name="ban" color="grey" />
          <span>Empty</span>
        </div>
      )}
      {!student && editable && (
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
 * Drop target specification for the unassigned students pool
 */
const unassignedPoolTarget = {
  drop(props, monitor) {
    const item = monitor.getItem();
    if (props.editable && props.onUnassign) {
      props.onUnassign(item.student);
    }
  },
  canDrop(props) {
    return props.editable;
  },
};

/**
 * Drop target collection function for unassigned pool
 */
const collectUnassignedTarget = (connect, monitor) => ({
  connectDropTarget: connect.dropTarget(),
  isOver: monitor.isOver(),
  canDrop: monitor.canDrop(),
});

/**
 * Droppable unassigned students pool component
 */
const UnassignedStudentsPoolComponent = ({ 
  editable, 
  students, 
  gridData, 
  connectDropTarget, 
  isOver, 
  canDrop 
}) => {
  if (!editable || !students) return null;

  const assignedStudents = Object.values(gridData.students);
  const unassigned = students.filter(student => !assignedStudents.includes(student));

  if (unassigned.length === 0 && !isOver) return null;

  let poolClass = 'unassigned-students';
  if (isOver && canDrop) poolClass += ' drag-over-pool';
  if (!canDrop && isOver) poolClass += ' drag-invalid-pool';

  return connectDropTarget(
    <div className={poolClass}>
      <div className="unassigned-header">
        <Icon name="users" />
        <strong>Unassigned Students ({unassigned.length})</strong>
      </div>
      <div className="student-pool seating-chart-student-pool" style={{display: 'flex', flexWrap: 'wrap', justifyContent: 'center', alignItems: 'center', textAlign: 'center'}}>
        {unassigned.map(student => (
          <DraggableStudent
            key={student}
            student={student}
            editable={editable}
          />
        ))}
        {isOver && canDrop && unassigned.length === 0 && (
          <div className="drop-hint">Drop student here to unassign</div>
        )}
      </div>
    </div>
  );
};

const UnassignedStudentsPool = DropTarget(STUDENT_TYPE, unassignedPoolTarget, collectUnassignedTarget)(UnassignedStudentsPoolComponent);

/**
 * Main seating grid with drag-drop functionality
 */
const SeatingGrid = ({ gridData, students, rows, cols, onMove, onUnassign, editable }) => {
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
            hideInViewMode={isEmpty && !editable}
          />
        );
      }
    }
    return slots;
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

      {/* Droppable Unassigned Students Pool */}
      <UnassignedStudentsPool
        editable={editable}
        students={students}
        gridData={gridData}
        onUnassign={onUnassign}
      />

      {/* Grid Instructions */}
      {editable && (
        <div className="grid-instructions">
          <Icon name="info circle" color="blue" />
          <span>
            Drag students from the pool above or between desks to arrange seating. 
            Drag back to pool to unassign.
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
  onUnassign: PropTypes.func.isRequired,
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
  hideInViewMode: PropTypes.bool,
};

export default SeatingGrid; 