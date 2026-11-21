# Mobile experience update

## What changed
- Added a thumb-friendly five-item bottom navigation (Home, Care, Explore, Studio, Book) on phones only.
- Added a mobile-only three-question Smile Minute dental-care quiz to the home page, with instant explanations, score, replay, and English/Hindi labels.
- Added phone-specific spacing, touch target, form, grid, typography, and safe-area adjustments.
- Repositioned Nandi, the Nandi chat panel, and utility controls above the mobile navigation so they do not overlap.
- Kept the existing desktop layout unchanged: the mobile navigation and Smile Minute quiz are hidden above 760px, and responsive overrides only apply at 760px and below.
- Added reduced-motion support and kept the quiz educational rather than diagnostic.

## Files added
- `public_html/assets/mobile-experience.css`
- `public_html/assets/mobile-experience.js`

## Files updated
- `public_html/index.html`
- `public_html/treatments.html`
- `public_html/studio.html`
- `public_html/explore.html`

## Checks
- Mobile JavaScript syntax: passed.
- Existing Nandi JavaScript syntax: passed.
- PHP voice endpoint syntax: passed.
- Existing voice security/static checks: 30 passed.
- Full Playwright browser test: could not run because the Chromium browser binary is not installed in this environment. Test on a real phone and desktop browser before publishing.
