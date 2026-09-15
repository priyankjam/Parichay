# Paper & Plum

## Audit before implementation — 14 September 2026

The running app was inspected across the landing page, all eleven editor steps, preview popup, draft menu, privacy dialog and error page. Baseline captures and the complete selector/color/value inventory are in `tmp/qa/paper-plum/before/`.

The three product stylesheets contained 594 rules across roughly 42 KB. `app.css` and `workspace.css` overlapped on headings, fields, buttons, navigation, photos, dialogs and responsive behavior, including 20 `!important` declarations. Late accessibility overrides corrected some earlier pale colors but left both systems active. Spacing, radii, shadow and type values were scattered rather than expressed through semantic roles.

The green shell lacked a distinctive identity. Serif editor headings competed with the documents. Functional controls mixed chess/clover/diamond characters with arrows and plus signs. Section hints were boxed as cards; repetitive education rows had nested borders; inactive and disabled treatments were too similar. The homepage used a single clipped live specimen with oversized text and a small template gallery. The error page had a different wordmark. Save/loading states were mostly plain text. There is no Bootstrap dependency, pricing, payment or dashboard to redesign.

## Implementation direction

Warm paper surfaces, restrained plum interactions, ink typography and sage status feedback. DM Sans is the interface family; DM Serif Display is reserved for the wordmark and marketing display moments. The app and biodata retain separate tokens and stylesheet boundaries. Existing flow, optional fields, draft privacy, template data and export behavior remain intact.

`tokens.css` owns colors, type, spacing, radii, shadows, motion, dimensions and stacking order. `app.css` owns shared foundations/components. `workspace.css` owns editor layout and preview. `landing.css` owns marketing composition. Shared icons use one local 24-unit, 1.75-stroke outlined SVG set. No icon network dependency or emoji controls.

Layout breakpoints remain 600 px for compact controls and 1100 px with at least 700 px height for the stationary three-column editor. These values are documented as tokens but written literally in media queries because native CSS custom properties cannot be used in media conditions. The gallery adds a third column only when the form column is wide enough for readable thumbnails. The mobile preview remains a native dialog and supports full-size reading.

The UI remains available in English and Hindi. Logical CSS properties and locale direction metadata prepare the shell for RTL; naming a font fallback does not supply translations or font files for another language. Existing Devanagari fonts are self-hosted separately from Latin fonts. Additional scripts require their appropriate fonts and reviewed translations before being advertised as supported.

## Component contract

Use `primary`, `secondary`, `quiet`/`text-button`, and `destructive` for actions. Targets are 48 px by default; compact sidebar and filter controls have a 44 px minimum. Inputs are 52 px, use visible labels, and retain native keyboard behavior. Checkbox labels enlarge the clickable area. Focus uses plum and an explicit ring; invalid fields and destructive confirmations use the independent danger color. Button foreground/background changes are immediate so disabled-to-enabled transitions do not briefly create low-contrast text.

Forms use headings, whitespace and dividers. Repeatable education/career and custom sections have separators instead of nested rounded cards. Actual choice objects, photos and template thumbnails retain restrained borders and radius. Template selection marks sit alongside the name rather than covering a portrait in the artwork.

Use `components.html` for server-rendered brand/icons and `editor-ui.js` for the same client-rendered icon set. Keep SVG geometry in `static/icons.svg`. The monogram represents a folded sheet of paper; religious artwork remains inside explicitly selectable document templates.

The homepage uses locally generated sample documents, not a clipped interactive document. `build_template_previews.py` regenerates both gallery thumbnails and the two higher-resolution hero images from fictional data. Supplied dummy photography is retained inside these document samples. The homepage no longer loads document layout styles or embeds a base64 sample portrait into its HTML.

## Status and motion

Saved state combines a checkmark, text and sage. Offline and storage failure states explain recovery; storage failure exposes the backup action. Export shows an indeterminate status while the real request runs, without pretending to know server-side stages. A failed export removes stale success feedback, brings the error into view and offers a working retry button. Draft data is unchanged by retries.

Motion is limited to short state changes, dialog entry, accordion indicators and progress. Native dialogs use the browser top layer and focus behavior; the preview retains its keyboard focus trap and return focus. Reduced-motion preferences remove animations and transitions. Shadows are limited to paper, menus, overlays and dialogs.

## Accessibility and visual QA

Representative token contrast ratios:

| Foreground / background | Ratio |
|---|---:|
| Plum primary / white | 11.59:1 |
| Secondary ink / paper | 5.97:1 |
| Secondary ink / preview surface | 5.29:1 |
| Sage / paper | 5.45:1 |
| Danger / danger surface | 6.23:1 |
| Warning / warning surface | 6.44:1 |
| Info / info surface | 6.87:1 |
| Input boundary / white | 3.48:1 |

Normal functional text uses at least 4.5:1; non-text input boundaries use at least 3:1. Tertiary ink, terracotta and brass are not used for small functional text. The browser QA checks computed foreground/background contrast for visible product text, excluding document artwork and disabled controls. This is a targeted check, not a complete assistive-technology certification.

Verification completed on the local Chrome environment:

- 59 automated tests passed, including all 19 real PDF themes and PNG/JPG exports.
- 308 English/Hindi editor screen checks passed, covering all eleven steps, history, validation, entry reordering/removal, draft recovery, stationary desktop panels, mobile popup and PDF download.
- 24 homepage checks passed at 320, 360, 375, 390, 430, 768, 820, 1024, 1280, 1440, 1600 and 1920 px in both English and Hindi.
- All-template switching with a photo, disclosure privacy, Hindi reload and export passed.
- No contrast failures or JavaScript errors in the visual-state run. Export success/failure/retry, photo cropping/removal, menus, privacy, offline state, storage exhaustion/recovery, keyboard focus and reduced motion were exercised.
- Long-script heading samples were rendered for Marathi, Gujarati, Punjabi, Bengali, Odia, Tamil, Telugu, Kannada, Malayalam and Urdu; Urdu also exercised RTL geometry. These are layout/fallback checks on this host, not additional translated interfaces or physical Android-device tests.

Screenshots are in `tmp/qa/paper-plum/after/`; JSON evidence is in `results.json` and `style-inventory.json`. The major landing, form, gallery, preview, crop and recovery screenshots were visually inspected. Product rules were consolidated from 594 to 467, plus seven font/token blocks. `!important` use fell from 20 declarations to four, restricted to the hidden utility and reduced-motion accessibility reset. Product component styles contain no scattered hex colors.

Re-run `python scripts/paper_plum_check.py` for marketing widths, contrast, visual states and RTL/script checks, and `python scripts/ux_redesign_check.py` for the full editor matrix. `visual_audit.py` captures a baseline; its existing `before` folder should be archived before capturing a new baseline.
