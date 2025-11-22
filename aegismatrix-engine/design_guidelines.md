# Tradyxa AegisMatrix Design Guidelines

## Design Approach
**Specialized Financial Dashboard** - A data-dense, utility-focused interface for NIFTY options intelligence. Design priority is clarity, readability, and quick data scanning rather than marketing appeal.

## Layout System

### Global Structure
- **Header**: Product name + subtitle, 3-tab navigation (Direction | Option Sellers | Option Buyers), theme toggle, hard refresh button
- **Background**: Animated concentric "radar" rings with subtle rotation (AegisMatrix visual motif)
- **Content Area**: 3×4 tile grid per tab (12 tiles total per view)
- **Bottom**: Collapsible "How to Use This Dashboard" section
- **Footer**: Comprehensive legal text, links, and attribution

### Spacing Framework
Use Tailwind spacing: **p-4, p-6, p-8** for tile padding; **gap-4, gap-6** for grid gaps; **py-12, py-16** for section spacing

## Typography

### Font Strategy
- **Primary**: Inter or DM Sans (Google Fonts)
- **Monospace**: JetBrains Mono or Roboto Mono for numerical data
- **Hierarchy**:
  - Dashboard title: text-2xl/3xl font-bold
  - Tab labels: text-base font-medium
  - Tile headers: text-sm font-semibold uppercase tracking-wide
  - Data values: text-3xl/4xl font-bold (monospace)
  - Descriptions: text-xs/sm font-normal

## Color System

### Dark Mode (Primary)
- **Background**: #081015
- **Tiles**: #0E141C
- **Grid/Borders**: #172029
- **Text Primary**: #E8EDF2
- **Text Secondary**: #9BA3B5

### Light Mode
- **Background**: #F7FBFE
- **Tiles**: #FFFFFF
- **Grid/Borders**: #D7DFE8
- **Text Primary**: #0A1628
- **Text Secondary**: #6B7280

### Semantic Colors (Consistent Across Themes)
- **Direction Tab**:
  - Bullish/Up: #00EA99 (dark), #1FA378 (light)
  - Bearish/Down: #FF4E68 (dark), #D62839 (light)
  - Neutral: #9BA3B5 / #6B7280

- **Sellers Tab** (Safety Focus):
  - Safe: #00EA99 / #1FA378
  - Danger: #FF4E68 / #D62839
  - Neutral: #6B7280

- **Buyers Tab** (Spike/Edge Focus):
  - Opportunity/Spike: #2BDFFF (dark), #0894C9 (light)
  - Green/Red for directional bias

### Background Animation
- Concentric rings: rgba(43, 223, 255, 0.05) and rgba(0, 234, 153, 0.05) in dark; rgba(8, 148, 201, 0.05) in light
- Subtle rotation animation (slow, 120s+ duration)

## Component Library

### Tile Components (36 Total Across 3 Tabs)

**Core Tile Structure**:
- Rounded corners (rounded-lg)
- Border: 1px solid (theme-appropriate)
- Padding: p-6
- Shadow: subtle drop shadow in light mode
- Click-to-help: Question mark icon → themed popup modal

**Visualization Types**:
1. **Half-Circle Gauges**: Direction indicators with arrows (SVG-based)
2. **Circular Dials**: Risk scores, stress meters (0-100 scale)
3. **Horizontal Bars**: Range bands, theta-edge scores
4. **Vertical Bars**: Skew comparison (calls vs puts), 5-day breakout map
5. **Mini Line Charts**: Chart.js for horizons, historical trends, breach curves
6. **Sparklines**: Micro-trends for spot price changes
7. **Numeric Displays**: Large monospace numbers with delta indicators (△/▽)
8. **Regime Pills**: Rounded badges with icons (Bull/Bear/Neutral, Calm/Cautious/Hostile)
9. **Time-Strip Heat Maps**: Gamma burst windows (intraday 30-min blocks)
10. **Split Bars**: Spike direction bias (up% vs down%)

### Navigation
- **Tab Bar**: Horizontal, centered, with active state indicator (underline or background)
- **Active State**: Accent color + bold
- **Inactive State**: Muted text

### Modals/Popups

**Tile Help Modal**:
- Overlay: rgba(0,0,0,0.6) backdrop blur
- Card: Centered, max-w-lg, matching theme
- Header: Tile name
- Content: Plain-language explanation of interpretation
- Close Button: Top-right X icon

**Disclaimer Modal** (Every 2 Days):
- No close button
- "I Understand" primary button (required to proceed)
- Legal text about educational use
- Theme-matched styling

**Cookie & Ad Consent**:
- Granular controls: "Allow Analytics & Advertising", "Accept All", "Reject All", "Save Choices"
- Links: Privacy, Cookies, Terms
- Persists choice in localStorage

### Footer
- **Content**: Multi-line text block with data sources, analytics attribution, NSE disclaimer, Zeta Aztra Technologies copyright, contact email, jurisdiction, version
- **Links**: Privacy Policy | Cookie Preferences | Terms of Use | Disclaimer | About (empty placeholder pages)
- Typography: text-xs, muted color
- Layout: Centered, max-w-5xl

### Collapsible Section
- "How to Use This Dashboard" at bottom
- Expand/collapse icon
- When expanded: Grid of tile descriptions or step-by-step guide

## Tile Grid Layouts

### All Tabs: 3×4 Grid
- Desktop: `grid-cols-3 gap-6`
- Tablet: `grid-cols-2 gap-4`
- Mobile: `grid-cols-1 gap-4`

### Specific Tile Placements
Each tab follows Row 1-4 structure with specific tiles per the specification document.

## Animations
- **Background Rings**: Slow rotation (CSS transform rotate)
- **Tile Hover**: Subtle scale(1.02) + shadow increase
- **Tab Transitions**: Fade in/out (200ms)
- **Chart Updates**: Smooth data transitions (Chart.js animations)
- **NO DISTRACTING ANIMATIONS**: Keep motion minimal and purposeful

## Interactions

### Hard Refresh Button
- Icon: Circular arrow (Heroicons or Font Awesome)
- Action: `window.location.reload()`
- Visual feedback: Spin animation on click

### Theme Toggle
- Icon: Sun/Moon switch
- Smooth color transitions (transition-colors duration-200)
- Persist in localStorage

### Data Loading States
- Skeleton loaders for tiles (shimmer effect)
- Error states: Red border + "Data Unavailable" message

## Accessibility
- ARIA labels for gauges and charts
- Keyboard navigation for tabs and modals
- Focus states: 2px outline with accent color offset
- Contrast ratios: WCAG AA compliant

## No Images Strategy
This is a data-centric dashboard. **No hero images or decorative photos**. All visuals are functional (charts, gauges, indicators).

---

**Key Principle**: This is a professional financial tool, not a marketing page. Prioritize data density, readability, and instant comprehension over visual flair. Every pixel serves information delivery.