/**
 * Standards Widget for Educational Content
 * 
 * A teacher-friendly widget for selecting educational standards.
 * Features search, filtering by subject/grade, and intuitive selection.
 * Designed specifically for K-12 educators' workflow.
 */

import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { 
  FormField, 
  Grid, 
  Dropdown, 
  Input, 
  Label, 
  Button, 
  Segment,
  Header,
  Icon,
  Message
} from 'semantic-ui-react';
import { defineMessages, useIntl } from 'react-intl';
import { SelectWidget } from '@plone/volto/components';

const messages = defineMessages({
  standardsAlignment: {
    id: 'Standards Alignment',
    defaultMessage: 'Standards Alignment',
  },
  searchStandards: {
    id: 'Search standards...',
    defaultMessage: 'Search standards (e.g., "3rd grade math" or "CCSS.MATH.3.OA")',
  },
  filterBySubject: {
    id: 'Filter by Subject',
    defaultMessage: 'Filter by Subject',
  },
  filterByGrade: {
    id: 'Filter by Grade',
    defaultMessage: 'Filter by Grade',
  },
  selectedStandards: {
    id: 'Selected Standards',
    defaultMessage: 'Selected Standards',
  },
  noStandardsSelected: {
    id: 'No standards selected',
    defaultMessage: 'No standards selected yet. Search and select standards that align with your content.',
  },
  clearAll: {
    id: 'Clear All',
    defaultMessage: 'Clear All',
  },
  helpText: {
    id: 'Standards help text',
    defaultMessage: 'Select educational standards that your content addresses. This helps with lesson planning, reporting, and finding related materials.',
  },
});

const SUBJECT_FILTERS = [
  { key: 'all', value: 'all', text: 'All Subjects' },
  { key: 'math', value: 'CCSS.MATH', text: 'Mathematics' },
  { key: 'ela', value: 'CCSS.ELA', text: 'English Language Arts' },
  { key: 'science', value: 'NGSS', text: 'Science (NGSS)' },
  { key: 'social', value: 'NCSS', text: 'Social Studies' },
];

const GRADE_FILTERS = [
  { key: 'all', value: 'all', text: 'All Grades' },
  { key: 'elementary', value: 'K,1,2,3,4,5', text: 'Elementary (K-5)' },
  { key: 'middle', value: '6,7,8', text: 'Middle School (6-8)' },
  { key: 'high', value: '9,10,11,12', text: 'High School (9-12)' },
  { key: 'k', value: 'K', text: 'Kindergarten' },
  { key: '1', value: '1', text: '1st Grade' },
  { key: '2', value: '2', text: '2nd Grade' },
  { key: '3', value: '3', text: '3rd Grade' },
  { key: '4', value: '4', text: '4th Grade' },
  { key: '5', value: '5', text: '5th Grade' },
  { key: '6', value: '6', text: '6th Grade' },
  { key: '7', value: '7', text: '7th Grade' },
  { key: '8', value: '8', text: '8th Grade' },
];

const StandardsWidget = ({ 
  id, 
  title, 
  description, 
  required, 
  error, 
  value = [], 
  onChange,
  vocabulary = {},
  placeholder,
  ...props 
}) => {
  const intl = useIntl();
  const [searchTerm, setSearchTerm] = useState('');
  const [subjectFilter, setSubjectFilter] = useState('all');
  const [gradeFilter, setGradeFilter] = useState('all');
  const [filteredOptions, setFilteredOptions] = useState([]);

  // Convert vocabulary to options format
  const vocabularyOptions = React.useMemo(() => {
    if (!vocabulary?.terms) return [];
    
    return vocabulary.terms.map(term => ({
      key: term.token,
      value: term.token,
      text: term.title,
      description: term.title.includes(' - ') ? term.title.split(' - ')[1] : '',
    }));
  }, [vocabulary]);

  // Filter options based on search term, subject, and grade
  useEffect(() => {
    let filtered = vocabularyOptions;

    // Filter by subject
    if (subjectFilter !== 'all') {
      filtered = filtered.filter(option => 
        option.value.toLowerCase().includes(subjectFilter.toLowerCase())
      );
    }

    // Filter by grade (for math and ELA standards)
    if (gradeFilter !== 'all') {
      const grades = gradeFilter.split(',');
      filtered = filtered.filter(option => {
        return grades.some(grade => {
          if (grade === 'K') {
            return option.value.includes('.K.') || option.value.includes('K-');
          }
          return option.value.includes(`.${grade}.`) || option.value.includes(`${grade}-`);
        });
      });
    }

    // Filter by search term
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      filtered = filtered.filter(option => 
        option.text.toLowerCase().includes(searchLower) ||
        option.value.toLowerCase().includes(searchLower) ||
        option.description.toLowerCase().includes(searchLower)
      );
    }

    setFilteredOptions(filtered);
  }, [vocabularyOptions, searchTerm, subjectFilter, gradeFilter]);

  // Handle adding a standard
  const handleAddStandard = (standardValue) => {
    if (!value.includes(standardValue)) {
      const newValue = [...value, standardValue];
      onChange(id, newValue);
    }
  };

  // Handle removing a standard
  const handleRemoveStandard = (standardValue) => {
    const newValue = value.filter(v => v !== standardValue);
    onChange(id, newValue);
  };

  // Clear all selected standards
  const handleClearAll = () => {
    onChange(id, []);
  };

  // Get selected standard details
  const getStandardDetails = (standardValue) => {
    const option = vocabularyOptions.find(opt => opt.value === standardValue);
    return option || { text: standardValue, description: '' };
  };

  return (
    <FormField className="standards-widget" error={error ? true : false}>
      <Grid>
        <Grid.Row>
          <Grid.Column width={16}>
            <label htmlFor={`field-${id}`}>
              {title}
              {required && <span className="required">&nbsp;*</span>}
            </label>
            {description && (
              <div className="help text">{description}</div>
            )}
          </Grid.Column>
        </Grid.Row>

        {/* Search and Filter Controls */}
        <Grid.Row>
          <Grid.Column width={8}>
            <Input
              fluid
              placeholder={intl.formatMessage(messages.searchStandards)}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              icon="search"
              iconPosition="left"
            />
          </Grid.Column>
          <Grid.Column width={4}>
            <Dropdown
              fluid
              selection
              placeholder={intl.formatMessage(messages.filterBySubject)}
              options={SUBJECT_FILTERS}
              value={subjectFilter}
              onChange={(e, { value }) => setSubjectFilter(value)}
            />
          </Grid.Column>
          <Grid.Column width={4}>
            <Dropdown
              fluid
              selection
              placeholder={intl.formatMessage(messages.filterByGrade)}
              options={GRADE_FILTERS}
              value={gradeFilter}
              onChange={(e, { value }) => setGradeFilter(value)}
            />
          </Grid.Column>
        </Grid.Row>

        {/* Available Standards (Search Results) */}
        {(searchTerm || subjectFilter !== 'all' || gradeFilter !== 'all') && (
          <Grid.Row>
            <Grid.Column width={16}>
              <Segment>
                <Header as="h4">
                  <Icon name="search" />
                  Available Standards ({filteredOptions.length})
                </Header>
                <div className="standards-list" style={{ maxHeight: '300px', overflowY: 'auto' }}>
                  {filteredOptions.slice(0, 20).map(option => (
                    <div 
                      key={option.value} 
                      className="standard-option"
                      style={{ 
                        padding: '8px 12px', 
                        border: '1px solid #ddd',
                        marginBottom: '4px',
                        cursor: 'pointer',
                        backgroundColor: value.includes(option.value) ? '#e8f5e8' : '#fff'
                      }}
                      onClick={() => handleAddStandard(option.value)}
                    >
                      <strong>{option.value}</strong>
                      <br />
                      <small>{option.description || option.text}</small>
                      {value.includes(option.value) && (
                        <Icon name="checkmark" color="green" style={{ float: 'right' }} />
                      )}
                    </div>
                  ))}
                  {filteredOptions.length > 20 && (
                    <Message info>
                      Showing first 20 results. Refine your search to see more specific standards.
                    </Message>
                  )}
                  {filteredOptions.length === 0 && (
                    <Message>
                      No standards found matching your criteria. Try different search terms or filters.
                    </Message>
                  )}
                </div>
              </Segment>
            </Grid.Column>
          </Grid.Row>
        )}

        {/* Selected Standards */}
        <Grid.Row>
          <Grid.Column width={16}>
            <Segment>
              <Header as="h4">
                <Icon name="tag" />
                {intl.formatMessage(messages.selectedStandards)} ({value.length})
                {value.length > 0 && (
                  <Button 
                    size="mini" 
                    basic 
                    onClick={handleClearAll}
                    style={{ marginLeft: '10px' }}
                  >
                    {intl.formatMessage(messages.clearAll)}
                  </Button>
                )}
              </Header>
              {value.length === 0 ? (
                <Message info>
                  {intl.formatMessage(messages.noStandardsSelected)}
                </Message>
              ) : (
                <div className="selected-standards">
                  {value.map(standardValue => {
                    const details = getStandardDetails(standardValue);
                    return (
                      <Label 
                        key={standardValue}
                        size="medium"
                        style={{ margin: '2px' }}
                      >
                        <strong>{standardValue}</strong>
                        <br />
                        <small>{details.description || details.text}</small>
                        <Icon 
                          name="delete" 
                          onClick={() => handleRemoveStandard(standardValue)}
                          style={{ cursor: 'pointer', marginLeft: '8px' }}
                        />
                      </Label>
                    );
                  })}
                </div>
              )}
            </Segment>
          </Grid.Column>
        </Grid.Row>

        {/* Help Text */}
        <Grid.Row>
          <Grid.Column width={16}>
            <Message info size="small">
              <Icon name="info circle" />
              {intl.formatMessage(messages.helpText)}
            </Message>
          </Grid.Column>
        </Grid.Row>
      </Grid>

      {error && (
        <Label basic color="red" pointing>
          {error}
        </Label>
      )}
    </FormField>
  );
};

StandardsWidget.propTypes = {
  id: PropTypes.string.isRequired,
  title: PropTypes.string,
  description: PropTypes.string,
  required: PropTypes.bool,
  error: PropTypes.arrayOf(PropTypes.string),
  value: PropTypes.arrayOf(PropTypes.string),
  onChange: PropTypes.func.isRequired,
  vocabulary: PropTypes.object,
  placeholder: PropTypes.string,
};

StandardsWidget.defaultProps = {
  title: 'Standards Alignment',
  description: 'Select educational standards that align with this content',
  required: false,
  error: null,
  value: [],
  vocabulary: {},
  placeholder: 'Search for standards...',
};

export default StandardsWidget; 