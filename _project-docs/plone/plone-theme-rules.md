
# Theme Rules for K-12 Educational Platform (Volto Frontend)

This document defines the visual design system for our K-12 Educational Content Platform built on Plone 6.1.2 with Volto React frontend. The theme emphasizes **clarity**, **approachability**, and **professionalism** for teachers in under-resourced schools, while ensuring **accessibility** and **mobile responsiveness**.

## Design Philosophy

Our theme balances professional educational aesthetics with warmth and approachability, avoiding both corporate sterility and childish design. It should feel like a trusted colleague's well-organized classroom.

## Color Palette

### Primary Colors
- **Primary Blue**: #2563eb (Professional trust, main CTAs)
  - Use for: Primary buttons, key navigation, active states
  - Lighter: #3b82f6 (hover states)
  - Darker: #1d4ed8 (pressed states)

- **Educational Green**: #059669 (Success, growth, learning)
  - Use for: Success messages, completed lessons, achievements
  - Lighter: #10b981 (positive feedback)
  - Darker: #047857 (emphasis)

### Secondary Colors
- **Warm Orange**: #f59e0b (Energy, creativity, attention)
  - Use for: Highlights, notifications, draft states
  - Lighter: #fbbf24 (warnings)
  - Darker: #d97706 (urgent items)

- **Supportive Purple**: #7c3aed (Innovation, special features)
  - Use for: Premium features, AI suggestions, special content
  - Lighter: #8b5cf6 (accents)
  - Darker: #6d28d9 (emphasis)

### Functional Colors
- **Error Red**: #dc2626 (Errors, critical alerts)
- **Info Blue**: #0891b2 (Information, tips)
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
- **Display**: 3rem (48px) - Landing pages only
- **H1**: 2.25rem (36px) - Page titles
- **H2**: 1.875rem (30px) - Section headers
- **H3**: 1.5rem (24px) - Subsections
- **H4**: 1.25rem (20px) - Card titles
- **Body**: 1rem (16px) - Standard text
- **Small**: 0.875rem (14px) - Metadata, captions
- **Tiny**: 0.75rem (12px) - Timestamps, legal

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

/* Educational CTAs */
.button-create-lesson {
  background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
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

### Educational-Specific Components

#### Lesson Plan Cards
```css
.lesson-card {
  border-left: 4px solid [subject-color];
  padding: 1.5rem;
  background: white;
  transition: transform 0.2s, box-shadow 0.2s;
}

.lesson-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}
```

#### Standards Tags
```css
.standards-tag {
  background: #ede9fe;
  color: #6d28d9;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 500;
}
```

#### Grade Level Indicators
- K-2: Soft green (#10b981)
- 3-5: Warm blue (#3b82f6)
- 6-8: Purple (#8b5cf6)
- 9-12: Deep orange (#f59e0b)

## Responsive Design

### Breakpoints
- Mobile: < 640px
- Tablet: 640px - 1024px
- Desktop: > 1024px
- Wide: > 1280px

### Mobile Adaptations
- Increase touch targets to 48px minimum
- Stack navigation vertically
- Simplify dashboard to single column
- Use bottom sheet pattern for actions

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
    └── educational.less
```

### Custom Properties
Use CSS-in-JS with theme provider:
```javascript
const educationalTheme = {
  colors: {
    primary: '#2563eb',
    educational: '#059669',
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
4. **Print Styles**: Ensure lesson plans print cleanly
5. **Loading States**: Use skeleton screens for better perceived performance

## Common Pitfalls to Avoid

1. Using pure black (#000000) - use #111827 instead
2. Forgetting hover/focus states for interactive elements
3. Inconsistent spacing between similar components
4. Low contrast text on colored backgrounds
5. Fixed pixel values that break responsive design

This theme system creates a professional yet approachable educational platform that teachers will find both functional and delightful to use daily. 