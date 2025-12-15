# DemoPage Clone - React.js Single Page Website

A pixel-perfect React.js clone of the DemoPage.io homepage, featuring modern UI/UX design with dark theme, gradient accents, smooth animations, and responsive layouts.

## Design Features

### Visual Design
- **Dark Theme**: Premium dark color palette with subtle gradients
- **Gradient Accents**: Purple-to-cyan gradient effects on CTAs and text
- **Glass Morphism**: Frosted glass effects on navigation and cards
- **Particle Effects**: Floating particles in hero section
- **Grid Patterns**: Subtle grid overlays for depth

### Typography
- **Syne**: Bold display font for headings
- **DM Sans**: Clean sans-serif for body text
- **Gradient Text**: Animated gradient text effects

### Animations (Framer Motion)
- Staggered reveal animations on scroll
- Smooth hover transitions on cards
- Floating animations on background elements
- Page load transitions
- Interactive button effects

### Sections
1. **Header**: Fixed navigation with dropdown menus, mobile hamburger menu
2. **Hero**: Animated headline, stats, CTAs, Ethereum logo visualization
3. **Partners**: Trusted by logos with hover effects
4. **Products**: Product cards for MetaMask, Linea, Infura, MetaMask Developer
5. **Protocol**: Timeline of Ethereum milestones
6. **About**: Company story with team grid and feature highlights
7. **News**: Blog/news article cards
8. **Newsletter**: Email subscription form with features
9. **Footer**: Links, social icons, legal

## Tech Stack

- **React 18**: Latest React with hooks
- **Framer Motion**: Animation library for smooth transitions
- **CSS Variables**: Theming with custom properties
- **React Intersection Observer**: Scroll-triggered animations
- **Responsive Design**: Mobile-first approach

## Getting Started

### Prerequisites
- Node.js 16+ 
- npm or yarn

### Installation

```bash
# Navigate to the project directory
cd DemoPage-clone

# Install dependencies
npm install

# Start the development server
npm start
```

The app will be available at `http://localhost:3000`

### Build for Production

```bash
npm run build
```

## Project Structure

```
DemoPage-clone/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── Header.js / Header.css
│   │   ├── Hero.js / Hero.css
│   │   ├── Partners.js / Partners.css
│   │   ├── Products.js / Products.css
│   │   ├── Protocol.js / Protocol.css
│   │   ├── About.js / About.css
│   │   ├── News.js / News.css
│   │   ├── Newsletter.js / Newsletter.css
│   │   └── Footer.js / Footer.css
│   ├── styles/
│   │   └── globals.css
│   ├── App.js
│   ├── App.css
│   └── index.js
├── package.json
└── README.md
```

## CSS Variables

The project uses CSS custom properties for easy theming:

```css
:root {
  --color-bg-primary: #0a0a0a;
  --color-accent-primary: #6366f1;
  --color-accent-secondary: #8b5cf6;
  --color-accent-tertiary: #06b6d4;
  --gradient-primary: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%);
  --font-heading: 'Syne', sans-serif;
  --font-body: 'DM Sans', sans-serif;
}
```

## Responsive Breakpoints

- **Desktop**: 1200px+
- **Tablet**: 768px - 1199px
- **Mobile**: < 768px

## Key Design Patterns

### Glassmorphism
```css
background: rgba(10, 10, 10, 0.9);
backdrop-filter: blur(20px);
border: 1px solid rgba(255, 255, 255, 0.05);
```

### Gradient Text
```css
background: var(--gradient-primary);
-webkit-background-clip: text;
-webkit-text-fill-color: transparent;
```

### Hover Card Effect
```css
transition: all 0.3s ease;
transform: translateY(-8px);
box-shadow: 0 20px 40px rgba(99, 102, 241, 0.3);
```

## Customization

### Changing Colors
Edit the CSS variables in `src/styles/globals.css` to customize the color scheme.

### Adding Sections
1. Create component file in `src/components/`
2. Create corresponding CSS file
3. Import and add to `App.js`

### Modifying Animations
Animation settings are controlled through Framer Motion props in each component.

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## License

This project is for educational purposes, demonstrating UI/UX design patterns inspired by DemoPage.io.

---

Built with ❤️ using React.js

