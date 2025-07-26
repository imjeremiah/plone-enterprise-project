/**
 * Workflow Status Component - ADDITIVE ENHANCEMENT
 *
 * Shows workflow state without breaking existing functionality
 */

import React from 'react';
import { Label, Icon } from 'semantic-ui-react';

const WorkflowStatus = ({ workflowState, duration }) => {
  const getStatusConfig = (state, duration) => {
    switch (state) {
      case 'draft':
        return { color: 'grey', icon: 'edit', text: 'Draft' };
      case 'issued':
        if (duration > 15)
          return { color: 'red', icon: 'warning', text: 'Critical' };
        if (duration > 10)
          return { color: 'yellow', icon: 'clock', text: 'Warning' };
        return { color: 'green', icon: 'checkmark', text: 'Active' };
      case 'returned':
        return { color: 'blue', icon: 'home', text: 'Returned' };
      case 'expired':
        return { color: 'red', icon: 'ban', text: 'Expired' };
      default:
        return { color: 'grey', icon: 'question', text: 'Unknown' };
    }
  };

  const config = getStatusConfig(workflowState, duration);

  return (
    <Label color={config.color} size="small">
      <Icon name={config.icon} />
      {config.text}
    </Label>
  );
};

export default WorkflowStatus;
