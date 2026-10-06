# KYMA — GitHub Pages presentation

A complete static fashion concept based on the supplied KYMA brief, adapted to the user's explicit GitHub Pages requirement. The UI is in Brazilian Portuguese. Owner setup instructions are in [COMECE-AQUI.md](COMECE-AQUI.md).

This is a presentation and interaction demo. It does not sell goods, accept payments, create orders, authenticate users, or collect contact information. Products, prices, shipping and coupon calculations are illustrative. Photos are editorial references; repeated photos do not represent separate real inventory items.

## Included

- 13 HTML entry points, 32 concept products, eight categories and eight collections.
- Responsive home, accessible menus, search, URL-based catalog filters and sorting.
- Size/color selection, gallery zoom, local favorites and variant-based bag.
- Demonstrative coupon `KYMA10`, shipping by Brazilian state and an explicitly simulated checkout.
- Original SVG wordmark, generated hero image, licensed editorial references, compressed local WebM/MP4 video and self-hosted fonts.
- Reduced-motion/data-saving fallbacks, keyboard focus states and native dialogs.
- GitHub Actions checks and Pages deployment on pushes to `main`; pull requests run checks only.

## Local development

Node.js 22 or newer is only needed for local tools and CI. The published site is plain HTML, CSS and JavaScript. No package installation, database, credentials or server runtime is needed.

```sh
npm run dev
npm run check
npm test
npm run build
```

Open `http://127.0.0.1:4321/`. Test project-site paths at `http://127.0.0.1:4321/kyma-test/`. `npm run build` copies the public files to `site/`. It does not include source scripts, reports or documentation in the deployed artifact.

## Editing

| Content | File |
| --- | --- |
| Concept products, prices, categories, collections and copy | `assets/js/data.js` |
| Page templates and interactions | `assets/js/app.js` |
| Local bag normalization, filtering and money calculations | `assets/js/domain.js` |
| Responsive styles and motion | `assets/css/styles.css` |
| Replaceable original wordmark | `assets/brand/kyma-logo.svg` |
| Local photos and hero posters | `assets/images/` |
| Video sources | `assets/video/` |
| CI and deployment | `.github/workflows/pages.yml` |

Use relative URLs. Do not change them to `/assets/...`, because project Pages sites are served under the repository name. Product links use `produto.html?id=...`, so direct links do not require routing rewrites.

See [architecture and limits](docs/ARCHITECTURE.md), [validation results](docs/QA.md), [media credits](docs/MEDIA-CREDITS.md) and [change log](CHANGELOG.md).

## Hosting scope

GitHub Pages is a static host. Its rules also restrict commercial stores and sensitive transactions. This package deliberately remains a labeled concept demonstration. A real KYMA store requires a separate commerce host and trusted services for inventory, payments, orders and customer information.

Sources checked on 2026-10-05: [Pages limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits), [custom workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).
