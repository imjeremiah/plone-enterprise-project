/**
 * Timer Widget for Dashboard Integration
 * 
 * A compact version of the lesson timer that can be embedded
 * within other views like the teacher dashboard.
 */

import React from 'react';
import PropTypes from 'prop-types';
import LessonTimer from './LessonTimer';

const TimerWidget = ({ 
  contentUrl,
  title = "Quick Timer",
  showTitle = true
}) => {
  return (
    <div className="timer-widget">
      {showTitle && (
        <h4 style={{ marginBottom: '15px', textAlign: 'center' }}>
          {title}
        </h4>
      )}
      <LessonTimer 
        contentUrl={contentUrl}
        compact={true}
      />
    </div>
  );
};

TimerWidget.propTypes = {
  contentUrl: PropTypes.string,
  title: PropTypes.string,
  showTitle: PropTypes.bool
};

export default TimerWidget; 