# Static Pages architecture

## Context and decision

The supplied brief describes a production commerce system. The user's latest instruction explicitly requires GitHub Pages. This delivery implements the design and safe demonstrative interactions as a static concept. It supersedes the earlier production architecture proposal only for this Pages package.

There is no Django, Next.js runtime, database, authentication or payment endpoint. No credentials are required. The website does not create orders or claim payment success.

```text
GitHub main
  -> Actions: file checks, Node unit tests, static packaging
  -> Pages artifact: HTML + CSS + JavaScript + local media
  -> Browser
       -> KYMA_DATA: illustrative catalog
       -> KYMA_DOMAIN: pure filtering, variant and cents calculations
       -> KYMA app: rendering, dialogs, local interactions
       -> localStorage: favorites, variants, quantities, demo coupon
```

## Entry points and paths

Each page is a real `.html` file. Product and catalog state use query parameters. Links and assets are relative, allowing both an account Pages site and a repository Pages site without editing a base URL. Deep routes and server rewrites are not required.

`404.html` provides a conventional static not-found page. Relative assets are suitable for root-level unknown files; arbitrary nested unknown paths are not a supported routing scheme.

## State and calculations

Browser persistence uses the `kyma-preview-v1` namespace. Loaded state is sanitized against the current catalog. Unknown products and variants are removed; quantities are merged and capped at ten per variant. Totals are integer cents and read prices from the concept data rather than saved bag entries. This improves demo consistency; it does not establish a secure commercial source of truth. A visitor can still modify all client-side data.

Favorites and bags are specific to a browser/origin, not synced accounts. When storage is unavailable, interactions continue in memory with feedback. The footer provides an option to clear locally saved choices.

## Media and motion

Local compressed hero posters load early. The home has one editorial video in WebM with MP4 fallback, desktop/mobile sizes, no audio, and idle initialization. Motion pauses when offscreen, when the tab is hidden or when paused by the visitor. Reduced-motion preferences and data-saving/slow-network hints avoid loading the clip. Network Information API hints are only available in supporting browsers.

Fonts are local WOFF2 subsets. Native scroll snapping, CSS transitions, IntersectionObserver and native dialogs avoid a third-party animation dependency. There are no remote fonts, photo hotlinks, trackers or newsletter integrations.

## Deployment

Checks run on `main` pushes and pull requests. Only a successful non-PR check job can deploy the static artifact. PRs do not deploy previews. The built-in `GITHUB_TOKEN` and Pages OIDC identity are used; no manual secrets are needed. Enable GitHub Actions as the repository Pages source before the first successful deployment. Required status checks before merging need owner-configured branch protection; a workflow alone does not enforce merge rules.

The build publishes `site/` only. Generated reports and scripts remain in the source repository. `.nojekyll` supports the optional branch-root publication mode; Actions publication already serves the uploaded static artifact directly.

## Limits and transition to real commerce

No true stock, reservations, payment processing, order history, email, account verification, staff administration, customer-data collection or analytics is present. No external checkout link is included. Prices and shipping are fictional. The account page explains the limitation instead of exposing a fake login form. Privacy and terms pages describe this demo only, not production store policies.

For real commerce, move to an eligible commercial host and introduce trusted catalog/stock APIs, atomic reservations, payment verification, order persistence, transactional email, appropriate policies and monitoring. Do not simply remove the demo notices or attach secret keys to these files.

GitHub hosting rules checked on 2026-10-05: [Pages limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits). GitHub workflow structure: [custom workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).
