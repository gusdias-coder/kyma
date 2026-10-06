# Validation — 2026-10-05

## Results

| Check | Result |
| --- | --- |
| Static source validation | Passed: 13 pages, 80 initial references, JS syntax, font signatures and hero poster budget |
| Domain tests | Six passed |
| Browser scenarios | 12 passed; no captured JavaScript errors or failed asset responses |
| Responsive pages | 11 key pages at 320, 390, 768 and 1440 CSS pixels; no horizontal document overflow |
| axe-core automated WCAG checks | Zero reported violations on 11 key pages at 390 pixels |
| Lighthouse home, mobile simulation | Performance 97, Accessibility 100, Best Practices 100, SEO 100 |
| Lighthouse metrics | LCP 2.6 seconds, CLS 0, total blocking time 30 milliseconds |

Environment: Windows, headless installed Google Chrome, local HTTP server with a repository-like `/kyma-test/` path. Lighthouse used simulated mobile throttling. Node tests and static checks require only Node.js 22+. These measurements apply to the local static package, not a verified remote deployment or every visitor's device.

## Browser coverage

Search from the project subdirectory; filter persistence in the URL; required size selection; variant-based bag; dialog Escape and focus restoration; favorites persistence; coupon and quantity persistence; explicit checkout simulation; unknown product handling; escaped search text; responsive image/layout checks; reduced-motion video avoidance; real video playback and pause control.

Unit tests cover unique catalog IDs and category/collection coverage, corrupt local-state rejection, variant merging and limits, integer-cent totals, accent-insensitive filtering and all 27 Brazilian UFs.

## Fixes applied from QA

- Changed mobile bag grid tracks to `minmax(0, 1fr)` and allowed the summary to shrink, removing overflow at 320 pixels.
- Added meaningful roles and accessible names to illustrative color swatches.
- Included the changing bag count in the header button's accessible name.
- Restored focus after quantity, favorites and coupon view updates.
- Preloaded the responsive hero posters to improve image discovery.
- Added a valid robots file and appropriate local text/video content types.

## Evidence and limits

- [Browser results](browser-check-results.json)
- [Automated accessibility results](accessibility-results.json)
- [Full Lighthouse report](lighthouse-home.json)
- [Desktop preview](preview-desktop.png)
- [Mobile preview](preview-mobile.png)

Automated accessibility tools do not establish complete WCAG conformance. axe flagged some image/background combinations for manual contrast review. Visible headline overlays, button contrast, focus rings and minimum text sizes were visually checked; a full assistive-technology audit remains outside this concept delivery. Lighthouse scores vary between runs.

No live GitHub deployment, real checkout, payment webhook, concurrent inventory reservation, staff authentication, transactional email or real order flow was tested, because those services are absent. The Pages workflow is prepared and follows the official Actions structure, but needs to run in the owner's repository before remote deployment can be confirmed.
