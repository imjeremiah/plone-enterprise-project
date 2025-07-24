
# Theme Rules for K-12 Classroom Management Platform (Volto Frontend)

This document defines the visual design system for our K-12 Classroom Management Platform built on Plone 6.1.2 with Volto React frontend. The theme emphasizes **clarity**, **efficiency**, and **real-time feedback** for teachers managing their classrooms, while ensuring **accessibility** and **mobile responsiveness**.

## Design Philosophy

Our theme balances professional classroom management aesthetics with intuitive controls and real-time information display. It should feel like a modern classroom command center that's both powerful and approachable.

## Color Palette

### Primary Colors
- **Primary Blue**: #2563eb (Professional trust, main CTAs)
  - Use for: Primary buttons, key navigation, active states
  - Lighter: #3b82f6 (hover states)
  - Darker: #1d4ed8 (pressed states)

- **Educational Green**: #059669 (Success, active, all-clear)
  - Use for: Active timers, available students, success states
  - Lighter: #10b981 (positive feedback)
  - Darker: #047857 (emphasis)

### Secondary Colors
- **Warm Orange**: #f59e0b (Attention, warnings, alerts)
  - Use for: Timer warnings, long hall passes, attention needed
  - Lighter: #fbbf24 (warnings)
  - Darker: #d97706 (urgent items)

- **Supportive Purple**: #7c3aed (Special features, analytics)
  - Use for: Random picker, special tools, data insights
  - Lighter: #8b5cf6 (accents)
  - Darker: #6d28d9 (emphasis)

### Functional Colors
- **Error Red**: #dc2626 (Errors, critical alerts, timer end)
- **Info Blue**: #0891b2 (Information, active passes)
- **Neutral Grays**: 
  - Text: #111827 (primary), #4b5563 (secondary), #9ca3af (muted)
  - Backgrounds: #ffffff (primary), #f9fafb (secondary), #f3f4f6 (tertiary)
  - Borders: #e5e7eb (standard), #d1d5db (emphasis)

### Accessibility Requirements
- All text colors must meet WCAG AA standards (4.5:1 for normal text, 3:1 for large text)
- Interactive elements require 3:1 contrast ratio
- Provide color-blind safe alternatives (use icons + color)

## Typography

### Font Stack
```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
```
- Primary: Inter (modern, highly readable, free)
- Fallbacks: System fonts for performance

### Type Scale
- **Display**: 3rem (48px) - Dashboard headers only
- **H1**: 2.25rem (36px) - Page titles
- **H2**: 1.875rem (30px) - Section headers
- **H3**: 1.5rem (24px) - Widget titles
- **H4**: 1.25rem (20px) - Card titles
- **Body**: 1rem (16px) - Standard text
- **Small**: 0.875rem (14px) - Metadata, labels
- **Tiny**: 0.75rem (12px) - Timestamps, fine print

### Type Styles
- **Line Heights**: 1.5 for body, 1.2 for headings
- **Font Weights**: 400 (regular), 500 (medium), 600 (semibold), 700 (bold)
- **Letter Spacing**: Normal, except -0.025em for display text

## Spacing System

Based on 8px grid for consistency:
- **Micro**: 0.25rem (4px)
- **Tiny**: 0.5rem (8px)
- **Small**: 0.75rem (12px)
- **Base**: 1rem (16px)
- **Medium**: 1.5rem (24px)
- **Large**: 2rem (32px)
- **XL**: 3rem (48px)
- **XXL**: 4rem (64px)

## Component Styles

### Buttons
```css
/* Primary Button */
.button-primary {
  background: #2563eb;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 500;
  transition: all 0.2s;
}

/* Timer Controls */
.button-timer-start {
  background: linear-gradient(135deg, #059669 0%, #10b981 100%);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}
```

### Cards & Containers
- **Background**: White with subtle shadow
- **Border Radius**: 0.75rem (12px) for cards, 0.5rem (8px) for inputs
- **Shadow Scale**:
  - Small: `0 1px 3px rgba(0, 0, 0, 0.1)`
  - Medium: `0 4px 6px -1px rgba(0, 0, 0, 0.1)`
  - Large: `0 10px 15px -3px rgba(0, 0, 0, 0.1)`

### Forms
- **Input Height**: 2.75rem (44px) - touch-friendly
- **Label Style**: Font-weight 500, margin-bottom 0.5rem
- **Focus State**: 2px solid #2563eb with 4px light blue glow
- **Error State**: Border #dc2626, background #fef2f2

### Classroom-Specific Components

#### Seating Chart Grid
```css
.seating-grid {
  display: grid;
  gap: 0.5rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 0.75rem;
}

.student-seat {
  background: white;
  border: 2px solid #e5e7eb;
  padding: 0.75rem;
  cursor: move;
  transition: all 0.2s;
}

.student-seat:hover {
  border-color: #2563eb;
  transform: scale(1.02);
}
```

#### Timer Display
```css
.timer-display {
  font-size: 4rem;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.025em;
}

.timer-warning {
  color: #f59e0b;
  animation: pulse 2s infinite;
}

.timer-critical {
  color: #dc2626;
  animation: pulse 1s infinite;
}
```

#### Hall Pass Status
```css
.hall-pass-active {
  background: #dbeafe;
  border-left: 4px solid #0891b2;
  padding: 1rem;
  margin-bottom: 0.5rem;
}

.hall-pass-warning {
  background: #fef3c7;
  border-left-color: #f59e0b;
}

.hall-pass-alert {
  background: #fee2e2;
  border-left-color: #dc2626;
}
```

#### Random Picker Wheel
```css
.picker-wheel {
  position: relative;
  width: 300px;
  height: 300px;
  border-radius: 50%;
  background: linear-gradient(135deg, #7c3aed 0%, #8b5cf6 100%);
  animation: spin var(--spin-duration) ease-out;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(var(--spin-amount)); }
}
```

## Responsive Design

### Breakpoints
- Mobile: < 640px
- Tablet: 640px - 1024px
- Desktop: > 1024px
- Wide: > 1280px

### Mobile Adaptations
- Increase touch targets to 48px minimum
- Stack dashboard widgets vertically
- Simplify seating chart to list view
- Full-screen timer mode

## Dark Mode (Future Enhancement)

When implemented, use CSS custom properties:
```css
:root {
  --bg-primary: #ffffff;
  --text-primary: #111827;
}

[data-theme="dark"] {
  --bg-primary: #111827;
  --text-primary: #f9fafb;
}
```

## Implementation in Volto

### Theme Structure
```
packages/volto-project-title/src/theme/
├── globals/
│   ├── site.overrides
│   └── site.variables
├── components/
│   └── [component].overrides
└── extras/
    └── classroom.less
```

### Custom Properties
Use CSS-in-JS with theme provider:
```javascript
const classroomTheme = {
  colors: {
    primary: '#2563eb',
    success: '#059669',
    warning: '#f59e0b',
    alert: '#dc2626',
    // ...
  },
  spacing: {
    unit: 8,
    // ...
  }
};
```

## Best Practices

1. **Consistency**: Use design tokens for all values
2. **Performance**: Prefer CSS transforms over layout changes
3. **Accessibility**: Test with screen readers and keyboard navigation
4. **Print Styles**: Ensure seating charts and passes print cleanly
5. **Loading States**: Use skeleton screens for dashboard updates

## Common Pitfalls to Avoid

1. Using pure black (#000000) - use #111827 instead
2. Forgetting hover/focus states for interactive elements
3. Inconsistent spacing between similar components
4. Low contrast text on colored backgrounds
5. Fixed pixel values that break responsive design

This theme system creates a professional classroom management interface that teachers will find both functional and efficient for daily use. 