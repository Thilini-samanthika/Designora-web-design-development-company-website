# Designora - Web Design & Development Company

## Project Overview
A premium, fully responsive website for "Designora", a web design and website development company. Built with a dark modern UI style with neon gradient accents.

## Tech Stack
- **Frontend**: HTML, CSS, JavaScript (no frameworks)
- **Backend**: Python Flask
- **Fonts**: Google Fonts (Inter)
- **Icons**: Font Awesome 6.5.1

## Project Structure
```
/static
  style.css        - All CSS styles (dark theme, glassmorphism, responsive)
  script.js        - Navbar toggle, smooth scrolling, contact form, animations
/templates
  index.html       - Single-page website with all sections
app.py             - Flask backend (serves site, handles contact form POST)
requirements.txt   - Python dependencies (flask, gunicorn)
```

## Brand Colors
- Primary Blue: #1DA1F2
- Secondary Purple: #7B3FF2
- Accent Pink: #FF3EA5
- Dark Background: #0B0B0F
- Section Background: #14141A

## Website Sections
1. Sticky Navbar with mobile hamburger menu
2. Hero Section with animated gradient text
3. About Section with company stats (counter animation)
4. Services Section (6 service cards with hover effects)
5. Portfolio Section (6 project cards with overlay)
6. Process Section (4 steps: Research, Design, Development, Launch)
7. Testimonials Section (3 client testimonials)
8. CTA Section
9. Contact Section with working form (POST to /contact endpoint)
10. Footer with links, social icons, and contact info

## Running the Project
- Command: `python app.py`
- Port: 5000
- The Flask backend serves the HTML template and handles contact form submissions via POST /contact
