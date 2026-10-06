# KYMA concept design system

## Direction

Independent fashion with editorial contrast, inclusive visual references and bold, condensed typography. The urban hoodie hero establishes the initial mood; tailoring, shirts, denim and layered silhouettes broaden the brand beyond streetwear.

## Tokens

| Role | Value |
| --- | --- |
| Ink | `#0B0B0C` |
| Paper | `#F4F2EE` |
| White | `#FFFFFF` |
| Muted text | `#64635F` |
| Divider | `#DCDAD5` |
| Keyboard focus | `#3565E8` |
| Display | Local Oswald subset, headings mainly weight 500 |
| Body | Local Inter subset, mainly weights 400–600 |
| Body sizing | 14 px base with 1.65 line height |
| Microcopy | At least 12 px |
| Page gutter | Fluid 20–84 px; 17 px on the smallest screens |

Tokens live in the CSS `:root`. Blue is reserved for visible keyboard focus, keeping the brand surfaces predominantly monochrome.

## Components and behavior

Rectangular light/dark/outline buttons with line arrows; native selects and labeled controls; product cards with reference badges and pressed-state favorites; size and color selectors; accordions; native dialogs; status toasts; bag steppers; empty and unavailable states. Touch icon controls generally reserve a 44-pixel target. Dialog dismissal restores focus. Inline feedback explains size, quantity and simulated-checkout constraints.

## Layout and motion

The home alternates full-bleed photography with paper sections, asymmetric editorial type and a horizontally snapping collection rail. Product pages use a two-column desktop layout and a stacked mobile layout with a fixed add-to-bag control. Catalogs change from four columns to two on small screens.

The header compacts over 460 milliseconds while its original space remains reserved. Motion includes a slow camera effect on the generated backdrop, one real editorial video, card image changes, scroll reveals and native scrolling. Reduced-motion preferences disable transitions/animation and avoid inserting the clip. The visible pause button controls hero movement.

## Critique and applied corrections

| Area | Finding | Applied result |
| --- | --- | --- |
| Identity | The brief needs its own angular identity. | Created an original, swappable SVG wordmark and symbol. |
| Scope clarity | A Pages demo could be mistaken for a live store. | Kept a visible concept notice and explicit simulation language. |
| Mobile layout | The bag summary exceeded the smallest viewport. | Changed grid sizing and summary minimum width. |
| Accessibility | Color swatches had invalid ARIA labeling. | Added a valid image role and color names. |
| Keyboard interaction | View updates could discard the active button. | Restored focus after relevant bag/favorite/coupon updates. |
| Speed | The hero image was first discovered after JS rendered. | Added responsive image preloads and compact local media. |
| Product accuracy | Photos are editorial references. | Added reference notes and avoided inventory/stock claims. |

Future commercial use requires the supplied brand logo, accurate product media and approved catalog copy. The concept uses two reference views per product and one real video clip; it does not claim the larger production media set in the original brief.
