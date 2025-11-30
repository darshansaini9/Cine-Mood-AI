# Movie Recommendation Application Design Guidelines

## Design Approach
**Reference-Based Design** inspired by modern streaming platforms (Netflix, IMDb, Disney+) with emphasis on visual storytelling through movie posters and imagery. Clean, content-first layout that prioritizes movie discovery through rich visuals.

## Core Design Principles
- **Visual-First**: Large, high-quality movie posters drive the experience
- **Discoverable**: Clear navigation between search, featured content, and recommendations
- **Cinematic**: Dark, immersive backgrounds that make movie posters pop
- **Minimal Friction**: Instant results, smooth scrolling, no unnecessary clicks

---

## Layout System

### Spacing Scale
Use Tailwind spacing units: **2, 4, 6, 8, 12, 16, 24** for consistent rhythm
- Component padding: `p-6` to `p-8`
- Section spacing: `py-12` (mobile), `py-16` to `py-24` (desktop)
- Card gaps: `gap-6` (mobile), `gap-8` (desktop)

### Container Strategy
- Full-width sections with inner `max-w-7xl` containers
- Hero: Full viewport width with centered content overlay
- Content sections: `max-w-7xl mx-auto px-4 sm:px-6 lg:px-8`

---

## Typography

### Font Families
- **Primary**: Inter or DM Sans (headings, UI elements)
- **Secondary**: System font stack for body text (optimal readability)

### Type Scale
- **Hero Title**: `text-5xl lg:text-7xl font-bold`
- **Section Headings**: `text-3xl lg:text-4xl font-semibold`
- **Movie Titles**: `text-lg font-medium`
- **Body/Metadata**: `text-sm` to `text-base`
- **Search Input**: `text-base`

---

## Component Library

### 1. Hero Banner Section
- **Layout**: Full viewport height (`min-h-screen`) with featured movie backdrop
- **Structure**: 
  - Background: Large movie poster with dark gradient overlay (bottom to top, opacity 0.9 to 0.3)
  - Content: Centered vertically, left-aligned on desktop
  - Elements: Movie title, genre tags, brief overview, "Watch Now" and "More Info" buttons
- **Buttons**: Blurred background (`backdrop-blur-md bg-white/20`), white text, rounded corners

### 2. Search Bar
- **Placement**: Below hero, sticky at top on scroll
- **Design**: Large, prominent search input with icon
- **Specs**: 
  - Full-width on mobile, `max-w-2xl` centered on desktop
  - Height: `h-14`
  - Rounded: `rounded-full`
  - Icon: Search icon (left), clear button (right when active)
  - Dropdown: Results appear below as user types, with movie poster thumbnails + title

### 3. Featured Today - Horizontal Scroll
- **Layout**: Full-width scrollable container
- **Card Design**:
  - Aspect ratio: 2:3 (movie poster proportion)
  - Width: `w-48` (mobile), `w-56` (desktop)
  - Hover: Subtle scale (`hover:scale-105 transition-transform`)
  - Shadow: `shadow-lg hover:shadow-2xl`
- **Scrolling**: Horizontal overflow with hidden scrollbar (custom CSS), smooth scroll behavior

### 4. Recommendation Sections
- **Genre Recommendations**: 
  - Grid layout: 2 columns (mobile), 4-5 columns (desktop)
  - Section header with genre name
  - Same card design as Featured section
- **Mood-Based Recommendations**:
  - Similar grid layout
  - Header indicates mood (e.g., "Feeling Adventurous?", "Need a Laugh?")

### 5. Movie Cards
- **Structure**:
  - Poster image (full card)
  - Overlay gradient on hover revealing title + rating
  - Rating badge (top-right corner)
- **Specs**:
  - Rounded: `rounded-lg overflow-hidden`
  - Transition: `transition-all duration-300`

### 6. Navigation
- **Header**: Fixed top navigation with logo (left), search icon toggle (right)
- **Design**: Semi-transparent background (`bg-black/80 backdrop-blur-sm`)
- **Links**: Home, Browse by Genre, My List (if applicable)

---

## Images

### Hero Section
- **Large Hero Image**: Featured movie backdrop (high-resolution, 1920x1080+)
- **Placement**: Full viewport background with dark overlay gradient
- **Source**: OMDb API poster_path for featured movie

### Movie Posters
- **Throughout**: All movie cards display poster images from OMDb API
- **Dimensions**: 2:3 aspect ratio, minimum 300x450px
- **Loading**: Lazy load with skeleton placeholder

### Fallback
- For missing posters: Gradient placeholder with movie title

---

## Interaction Patterns

### Hover States
- Movie cards: Scale up slightly, show title/rating overlay
- Buttons: Brightness increase, no color change
- Search results: Background highlight

### Scrolling
- Horizontal scroll: Mouse drag enabled on desktop, touch swipe on mobile
- Smooth scroll behavior throughout
- "See All" buttons for each recommendation section

### Loading States
- Movie cards: Skeleton loaders with pulsing animation
- Search: Inline spinner while fetching results

---

## Accessibility
- All interactive elements have focus states (`focus:ring-2 focus:ring-offset-2`)
- Poster images include alt text with movie title
- Keyboard navigation for search and movie selection
- Sufficient contrast for all text overlays

---

## Responsive Behavior
- **Mobile**: Single column layouts, full-width search, stacked sections
- **Tablet**: 2-3 column grids, larger touch targets
- **Desktop**: Multi-column grids (4-5), hover interactions, sticky navigation

---

This design creates a visually immersive, Netflix-inspired movie discovery experience that balances rich imagery with clean, intuitive navigation.