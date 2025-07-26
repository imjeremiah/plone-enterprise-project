/**
 * Substitute Folder Generator Component for Classroom Management
 *
 * Provides interface for teachers to generate organized folders containing
 * all necessary materials for substitute teachers including schedules,
 * seating charts, lesson plans, and emergency information.
 */

import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import {
  Button,
  Form,
  Message,
  Segment,
  Header,
  Icon,
  Grid,
  List,
  Loader,
  Label,
  Divider,
} from 'semantic-ui-react';
import './SubstituteGenerator.css';

const SubstituteGenerator = ({ contentUrl }) => {
  const [generating, setGenerating] = useState(false);
  const [loading, setLoading] = useState(true);
  const [generationResult, setGenerationResult] = useState(null);
  const [customNotes, setCustomNotes] = useState('');
  const [availableMaterials, setAvailableMaterials] = useState(null);
  const [error, setError] = useState(null);

  /**
   * Load available materials information on component mount
   */
  useEffect(() => {
    loadAvailableMaterials();
  }, [contentUrl]);

  /**
   * Fetch information about available classroom materials
   */
  const loadAvailableMaterials = async () => {
    if (!contentUrl) {
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(`${contentUrl}/@@substitute-folder-info`, {
        method: 'GET',
        credentials: 'include',
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setAvailableMaterials(data);
        }
      }
    } catch (error) {
      console.warn('Failed to load substitute folder info:', error);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Generate the substitute folder with custom notes
   */
  const generateFolder = async () => {
    setGenerating(true);
    setError(null);

    try {
      const response = await fetch(`${contentUrl}/@@substitute-folder-info`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          generate: true,
          notes: customNotes.trim(),
        }),
      });

      const data = await response.json();

      if (data.success) {
        setGenerationResult(data);
        // Clear form after successful generation
        setCustomNotes('');
      } else {
        setError(data.error || 'Failed to generate substitute folder');
      }
    } catch (error) {
      console.error('Error generating substitute folder:', error);
      setError('Network error occurred while generating folder');
    } finally {
      setGenerating(false);
    }
  };

  /**
   * Copy access code to clipboard
   */
  const copyAccessCode = async (code) => {
    try {
      await navigator.clipboard.writeText(code);
      // You could add a toast notification here
    } catch (error) {
      console.warn('Failed to copy access code to clipboard:', error);
    }
  };

  /**
   * Reset the form and results
   */
  const resetForm = () => {
    setGenerationResult(null);
    setError(null);
    setCustomNotes('');
  };

  if (loading) {
    return (
      <Segment>
        <Loader active inline="centered">
          Loading substitute folder information...
        </Loader>
      </Segment>
    );
  }

  return (
    <div className="substitute-generator">
      <Segment>
        {/* Available Materials Summary */}
        {availableMaterials && (
          <Message info>
            <Message.Header>Available Materials</Message.Header>
            <Grid columns={3} divided>
              <Grid.Column>
                <Label color="blue">
                  <Icon name="users" />
                  {availableMaterials.available_materials.seating_charts}{' '}
                  Seating Charts
                </Label>
              </Grid.Column>
              <Grid.Column>
                <Label color="green">
                  <Icon name="file text" />
                  {availableMaterials.available_materials.documents} Documents
                </Label>
              </Grid.Column>
              <Grid.Column>
                <Label color="orange">
                  <Icon name="id card" />
                  {availableMaterials.available_materials.hall_passes} Hall
                  Passes
                </Label>
              </Grid.Column>
            </Grid>
          </Message>
        )}

        {/* Generation Form */}
        {!generationResult && (
          <Form>
            <Form.TextArea
              label="Additional Notes for Substitute"
              placeholder="Include any special instructions, behavior notes, student accommodations, or important reminders for the substitute teacher..."
              value={customNotes}
              onChange={(e, { value }) => setCustomNotes(value)}
              rows={6}
              style={{ minHeight: '120px' }}
            />

            <Form.Field>
              <Button
                primary
                size="large"
                fluid
                loading={generating}
                disabled={generating}
                onClick={generateFolder}
                icon
                labelPosition="left"
              >
                <Icon name="magic" />
                Generate Substitute Folder
              </Button>
            </Form.Field>
          </Form>
        )}

        {/* Error Message */}
        {error && (
          <Message negative>
            <Message.Header>Generation Failed</Message.Header>
            <p>{error}</p>
            <Button onClick={resetForm} size="small">
              Try Again
            </Button>
          </Message>
        )}

        {/* Success Result */}
        {generationResult && (
          <>
            <Message positive>
              <Message.Header>
                <Icon name="check circle" />
                Substitute Materials Generated Successfully!
              </Message.Header>

              <Grid columns={2} divided>
                <Grid.Column>
                  <Header as="h4">Access Information</Header>
                  <List>
                    <List.Item>
                      <List.Icon name="key" />
                      <List.Content>
                        <strong>Access Code:</strong>
                        <Label
                          color="green"
                          style={{ marginLeft: '10px', cursor: 'pointer' }}
                          onClick={() =>
                            copyAccessCode(generationResult.access_code)
                          }
                          title="Click to copy"
                        >
                          {generationResult.access_code}
                          <Icon name="copy" style={{ marginLeft: '5px' }} />
                        </Label>
                      </List.Content>
                    </List.Item>
                    <List.Item>
                      <List.Icon name="clock" />
                      <List.Content>
                        <strong>Generated:</strong>{' '}
                        {generationResult.generated_date}
                      </List.Content>
                    </List.Item>
                    <List.Item>
                      <List.Icon name="clock" />
                      <List.Content>
                        <strong>Expires:</strong>{' '}
                        {new Date(
                          generationResult.expiry_time,
                        ).toLocaleString()}
                      </List.Content>
                    </List.Item>
                  </List>
                </Grid.Column>

                <Grid.Column>
                  <Header as="h4">Materials Included</Header>
                  <List>
                    {generationResult.sections_created.map((section, index) => (
                      <List.Item key={index}>
                        <List.Icon name="checkmark" color="green" />
                        <List.Content>{section}</List.Content>
                      </List.Item>
                    ))}
                  </List>
                </Grid.Column>
              </Grid>

              <Divider />

              <Grid columns={2}>
                <Grid.Column>
                  <Button
                    color="blue"
                    icon
                    labelPosition="left"
                    onClick={() => window.print()}
                  >
                    <Icon name="print" />
                    Print Materials
                  </Button>
                </Grid.Column>
                <Grid.Column textAlign="right">
                  <Button onClick={resetForm} icon labelPosition="left">
                    <Icon name="plus" />
                    Generate New Materials
                  </Button>
                </Grid.Column>
              </Grid>
            </Message>

            {/* Display the actual substitute materials */}
            <Segment style={{ marginTop: '20px' }}>
              <Header as="h3">
                <Icon name="folder open" />
                {generationResult.document_title}
              </Header>

              <div
                style={{
                  background: '#f8f9fa',
                  padding: '15px',
                  borderRadius: '5px',
                  marginBottom: '20px',
                  textAlign: 'center',
                }}
              >
                <strong>Access Code for Substitute Teacher: </strong>
                <span
                  style={{
                    background: '#007bff',
                    color: 'white',
                    padding: '8px 15px',
                    borderRadius: '20px',
                    fontSize: '1.2em',
                    fontWeight: 'bold',
                  }}
                >
                  {generationResult.access_code}
                </span>
              </div>

              {generationResult.sections_data &&
                Object.entries(generationResult.sections_data).map(
                  ([sectionTitle, sectionContent], index) => (
                    <div key={index} style={{ marginBottom: '30px' }}>
                      <Divider horizontal>
                        <Header as="h4">{sectionTitle}</Header>
                      </Divider>
                      <div
                        style={{
                          padding: '15px',
                          background: 'white',
                          border: '1px solid #ddd',
                          borderRadius: '5px',
                        }}
                        dangerouslySetInnerHTML={{ __html: sectionContent }}
                      />
                    </div>
                  ),
                )}
            </Segment>
          </>
        )}

        {/* What's Included Information */}
        <Segment>
          <Header as="h3">
            <Icon name="list" />
            What's Included in the Substitute Folder
          </Header>

          <Grid columns={2} divided>
            <Grid.Column>
              <List bulleted>
                <List.Item>
                  <Icon name="calendar" color="blue" />
                  <List.Content>
                    <strong>Daily Schedule</strong>
                    <List.Description>
                      Complete class periods with times and locations
                    </List.Description>
                  </List.Content>
                </List.Item>
                <List.Item>
                  <Icon name="users" color="green" />
                  <List.Content>
                    <strong>Current Seating Charts</strong>
                    <List.Description>
                      Up-to-date seating arrangements for all classes
                    </List.Description>
                  </List.Content>
                </List.Item>
                <List.Item>
                  <Icon name="book" color="orange" />
                  <List.Content>
                    <strong>Today's Lesson Plans</strong>
                    <List.Description>
                      Available materials and backup activities
                    </List.Description>
                  </List.Content>
                </List.Item>
              </List>
            </Grid.Column>

            <Grid.Column>
              <List bulleted>
                <List.Item>
                  <Icon name="warning sign" color="red" />
                  <List.Content>
                    <strong>Emergency Procedures</strong>
                    <List.Description>
                      Fire drill, lockdown, and medical emergency protocols
                    </List.Description>
                  </List.Content>
                </List.Item>
                <List.Item>
                  <Icon name="phone" color="purple" />
                  <List.Content>
                    <strong>Important Contacts</strong>
                    <List.Description>
                      Administration, support staff, and key personnel
                    </List.Description>
                  </List.Content>
                </List.Item>
                <List.Item>
                  <Icon name="student" color="teal" />
                  <List.Content>
                    <strong>Student Information</strong>
                    <List.Description>
                      Special accommodations and classroom management notes
                    </List.Description>
                  </List.Content>
                </List.Item>
              </List>
            </Grid.Column>
          </Grid>

          <Message info>
            <Message.Header>
              <Icon name="lightbulb" />
              Pro Tip
            </Message.Header>
            <p>
              Generate the substitute folder the night before or early in the
              morning when you're feeling unwell. The access code is valid for
              24 hours and includes all current classroom materials.
            </p>
          </Message>
        </Segment>
      </Segment>
    </div>
  );
};

SubstituteGenerator.propTypes = {
  contentUrl: PropTypes.string,
};

SubstituteGenerator.defaultProps = {
  contentUrl: '',
};

export default SubstituteGenerator;
