
# Classroom Management Platform User Journey

This document outlines the user journey for K-12 teachers through the modernized Plone-based Classroom Management Platform. It segments the journey into daily classroom management tasks, showing how our 7 features work together to streamline teaching operations. The features create a cohesive classroom command center (e.g., Seating Chart feeds Random Picker, Hall Pass tracking appears on Dashboard, Timer coordinates with activities). The journey leverages Plone's robust backend while adding modern interactive tools for real-time classroom management.

## 1. Morning Setup and Authentication
- **Entry Point**: Teacher arrives at school, opens platform on tablet or desktop.
- **Incorporated Features**:
  - Feature 1: Google SSO for instant secure login
- **Synergies**: Single sign-on enables quick access to all classroom tools before students arrive.
- **Journey Steps**: Teacher logs in with school Google account; system recognizes teacher role and classroom assignments.
- **Next Segment**: Proceeds to dashboard for daily overview.

## 2. Daily Command Center Overview
- **Entry Point**: Post-login, teacher views classroom dashboard.
- **Incorporated Features**:
  - Feature 7: Teacher's Daily Command Center Dashboard (showing current class status, alerts, quick actions)
  - Feature 2: Seating Chart preview (mini-view of current arrangement)
- **Synergies**: Dashboard aggregates all classroom data - active hall passes, current timer, participation stats, seating arrangement - in one view.
- **Journey Steps**: Review any overnight substitute folder requests; check for long-duration hall passes from previous day; view participation balance from yesterday.
- **Next Segment**: Prepare classroom setup before students arrive.

## 3. Pre-Class Preparation
- **Entry Point**: Teacher prepares physical and digital classroom.
- **Incorporated Features**:
  - Feature 2: Seating Chart Generator (update for new students or behavioral adjustments)
  - Feature 4: Substitute Folder Generator (if anticipating absence)
- **Synergies**: Seating chart updates automatically sync to Random Picker; substitute folder aggregates current seating charts, today's materials, and emergency info.
- **Journey Steps**: Drag student to new seat if needed; generate substitute folder if feeling unwell; print updated seating chart.
- **Next Segment**: Begin active classroom management.

## 4. Active Class Management
- **Entry Point**: Students enter classroom, instruction begins.
- **Incorporated Features**:
  - Feature 3: Random Student Picker (fair participation selection)
  - Feature 5: Lesson Timer Widget (activity time management)
  - Feature 6: Digital Hall Pass (bathroom/office permissions)
- **Synergies**: Random picker pulls from seating chart data; timer provides audio cues for transitions; hall passes tracked in real-time on dashboard.
- **Journey Steps**: 
  - Start warm-up timer (5 minutes)
  - Use random picker for discussion participation
  - Issue digital hall pass with QR code when student needs restroom
  - Monitor pass duration on dashboard
- **Next Segment**: Track and analyze classroom flow.

## 5. Real-time Monitoring and Alerts
- **Entry Point**: During instruction, teacher monitors classroom status.
- **Incorporated Features**:
  - Feature 7: Dashboard real-time updates
  - Feature 6: Hall pass tracking and alerts
- **Synergies**: Dashboard shows live data - who's out, for how long, participation equity, timer status - enabling informed decisions.
- **Journey Steps**: 
  - Receive alert when student out >10 minutes
  - Check participation stats to ensure equity
  - View remaining time on current activity
- **Next Segment**: Transition between activities or classes.

## 6. Class Transitions
- **Entry Point**: End of period approaching or activity change.
- **Incorporated Features**:
  - Feature 5: Timer with warning alerts
  - Feature 3: Random picker for cleanup duties
  - Feature 6: Ensure all passes returned
- **Synergies**: Timer warns at 2 minutes; random picker selects cleanup crew; dashboard confirms all students returned.
- **Journey Steps**: 
  - Timer gives 2-minute warning
  - Select students for board cleaning via picker
  - Verify all hall passes marked returned
  - Reset for next class
- **Next Segment**: Repeat for next period or end of day.

## 7. End-of-Day Workflow
- **Entry Point**: Final class dismissed, teacher wraps up.
- **Incorporated Features**:
  - Feature 7: Dashboard summary view
  - Feature 4: Generate tomorrow's substitute folder (if needed)
- **Synergies**: Dashboard provides participation summary, flag any concerning patterns (frequent/long hall passes), prompt for substitute prep.
- **Journey Steps**: 
  - Review participation equity across all classes
  - Note any students with excessive hall pass use
  - Generate substitute folder for tomorrow if needed
  - Log out securely
- **Next Segment**: Platform preserves all data for next day.

## 8. Special Scenarios

### Substitute Teacher Flow
- **Entry Point**: Substitute arrives, logs in with temporary credentials.
- **Features Used**: Pre-generated substitute folder with all needed materials.
- **Journey**: Access folder → View seating charts → Read lesson plans → Use timer for activities → Track hall passes.

### Emergency Situations
- **Entry Point**: Fire drill or lockdown initiated.
- **Features Used**: Dashboard shows who's out of room (hall passes), seating chart for attendance.
- **Journey**: Quick glance at dashboard → Account for students → Use mobile device to track.

### Parent Conference Preparation
- **Entry Point**: Preparing for parent meeting.
- **Features Used**: Dashboard analytics, participation history, seating arrangements.
- **Journey**: Pull participation data → Show seating considerations → Demonstrate engagement tracking.

## Journey Characteristics

### Cyclical Daily Pattern
- Morning: Setup and preparation
- Active hours: Real-time management
- Transitions: Coordinated handoffs
- Evening: Analysis and next-day prep

### Feature Interconnections
- Seating Chart → Random Picker (student list)
- Hall Pass → Dashboard (real-time tracking)
- Timer → All activities (pacing)
- All features → Dashboard (central command)

### Mobile-First Design
- Works on classroom tablet during instruction
- Desktop for detailed setup/configuration
- Phone for emergency access
- All devices sync in real-time

This journey is built around the daily rhythms of classroom management. Features interconnect to create a comprehensive command center that helps teachers maintain organized, fair, and efficient classrooms while reducing administrative burden. 