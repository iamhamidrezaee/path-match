# PathMatch Frontend

Modern, elegant landing page for the PathMatch mentorship platform with Cornell CIS-inspired design.

## Features

- **Modern Typography**: Large, bold headings with elegant font sizing and spacing
- **Left-Aligned Layout**: Professional, editorial-style content presentation
- **Animated Backgrounds**: Subtle Cornell red dot patterns that gently animate
- **Cornell Design Language**: Inspired by Cornell Bowers CIS aesthetic
- **Responsive Layout**: Optimized for all device sizes
- **Minimal & Elegant**: Clean design that doesn't overwhelm

## Getting Started

### Development

Simply open `index.html` in your browser to view the landing page.

For a local development server:

```bash
# Using Python
python -m http.server 8000

# Using Node.js (if you have http-server installed)
npx http-server -p 8000
```

Then navigate to `http://localhost:8000`

## Design System

### Colors

- **Cornell Red**: `#B31B1B` - Primary brand color
- **Dark Red**: `#8B0000` - Hover states
- **Light Background**: `#FAFAFA` - Section backgrounds
- **Text Primary**: `#111111` - Main text
- **Text Secondary**: `#5F5F5F` - Subtle text

### Typography

The design uses Inter with system font fallbacks:
- **Font Family**: Inter, SF Pro Display, Segoe UI, system defaults
- **Headings**: Bold (700 weight), tight letter-spacing (-0.03em)
- **Hero Title**: 5.5rem (clamps responsively)
- **Section Titles**: 3.75rem (clamps responsively)
- **Body Text**: 1.0625rem with 1.7 line-height

### Layout

- **Max content width**: 1200px
- **Alignment**: Left-aligned for editorial feel
- **Responsive breakpoint**: 768px
- **Spacing**: Generous padding for breathing room
- **Grid layouts**: 3-column on desktop, single column on mobile

### Animated Backgrounds

Three canvas-based dot pattern animations:
- **Hero Section**: Right-aligned, subtle animation
- **Problem Section**: Left-aligned, denser pattern
- **CTA Section**: White dots on Cornell red background

## Future Enhancements

This is a static landing page. Future development will include:
- React/Vue.js integration for dynamic features
- Survey interface for mentors and mentees
- Profile management dashboard
- Matching results display
- Calendly integration
- User authentication UI

## File Structure

```
frontend/
├── index.html     # Main landing page structure
├── styles.css     # All styling and responsive design
├── base.js        # Navigation + animated dot patterns
└── README.md      # This file
```

## Design Inspiration

The design takes inspiration from Cornell Bowers College of Computing and Information Science's visual identity:
- Animated dot patterns inspired by Cornell's signature design elements
- Cornell red color palette
- Bold, editorial typography
- Clean, professional aesthetic
- Left-aligned layouts for academic sophistication

## Current State
The frontend has been developed into a homepage with a linked signup page that prompts users to answer relevant questions. From this are the following pages:
- Mentor-specific survey page for collecting mentor bio, skillset, Information Science concentration
- Mentee-specific survey page for collecting mentee bio, topics for discussion with mentors, Information Science concentration/planned concentration
- Results page for displaying a mentee's algorithmic mentor pairings post-survey completion

## Final Steps
To finalize the frontend development, the surveys must be linked to the backend algorithm as to supply it with the relevant information necessary for mentor-mentee pairing. With this integration completed, the site will be useable by our desired population.