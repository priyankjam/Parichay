# Parichay: UX audit and redesign specification

Date: 14 September 2026. Written before implementation of this redesign.

## Method and limits

Inspected routes, normalized schema/migrations, templates, styles, JS event flow, IndexedDB, validation, image processing, private export and tests. Ran the existing desktop/mobile creation journey and edge-flow checks successfully. Captured 98 screen/step combinations across 320, 360, 375, 390, 412, 430, 768, 820, 1024, 1280, 1440, 1600 and 1920 px, plus 844×390 landscape. Raw baseline: `tmp/qa/audit/baseline.json`; screenshots: `before-*.png`. These are expert observations and Chromium emulation, not interviews or measured user success rates. Physical keyboards, Android/iOS keyboards, VoiceOver/TalkBack and native Hindi editorial review remain release checks.

Baseline has no horizontal page overflow in these measurements. Working features include local recovery, photo crop, multiple education entries, hidden-field redaction, template switching, Hindi labels, PDF download, backup/restore, failed export retry and denied-storage messaging. Preserve these rather than replacing the product wholesale. The existing full-bleed PDF pagination and stationary desktop chrome are user-requested constraints.

## Core journey and root causes

Landing → who → style → language → personal → education/career → family → culture/astrology → about/partner/contact/custom → photos → design/custom → export. Three setup decisions precede meaningful personal content. The data registry is correctly independent of presentation, but one flat field renderer also determines the form layout. This exposes all optional controls equally. The single JS module rerenders entire steps, so focus and entry context can be lost. Responsive CSS has accumulated overlapping patches and treats tablet as a narrow desktop. Navigation measures visits and position rather than useful content.

At 320×568, personal is 1,703 px tall, culture 2,216 px and About 2,176 px. Culture exposes eleven sensitive inputs; About includes seven inputs across unrelated subjects before custom fields. Continue is below the viewport in 72 of 98 captured cases (including hidden Continue on the export screen; this is a layout measurement, not a failure rate). The floating Preview button competes with form content. Browser Back from Style returns to the landing page instead of the previous editor step.

## Issue register

| ID / priority | Screen or flow | Evidence and user impact | Recommendation / heuristic |
|---|---|---|---|
| U01 P1 | Mobile navigation/actions | Continue follows the full form; floating preview overlays content. Small phone needs several screens of scrolling to skip optional culture. | Persistent, shared action dock with Preview/Continue; Back/Skip remain clear. User control, efficiency. |
| U02 P1 | Optional content | Eleven culture/astrology fields expanded by default, income equally prominent, partner and custom details exposed early. Optional labels do not reduce perceived work. | Native disclosure groups; saved content opens automatically; disclosure never changes inclusion. Minimalism, error prevention. |
| U03 P1 | About/contact IA | About owns contact, preferences and custom sections. A person seeking a phone number must remember this unexpected location. | Personal & contact; About + optional partner preferences; custom content in Design. Real-world match, recognition. |
| U04 P1 | Tablet | 768 px split gives only ~324 px form content beside a tiny document; long About is 1,865 px. | Form-first through 1024 px with popup preview; persistent three-column workspace only when width supports it. Flexibility. |
| U05 P1 | Browser history | Native Back from Style exits editor to landing. In-app Back and browser Back disagree. | Section-only URL fragments and history state, no personal values in URLs. Preserve local save on transitions. Consistency/control. |
| U06 P1 | Remove/reorder entries | Remove immediately discards typed entry/photo/custom content; no undo. Lists lack ordering and meaningful entry summaries. | Confirm removal of filled content; collapsible named entries with move up/down preserving hidden-field indices. Error prevention. |
| U07 P1 | Validation/recovery | Continue checks current native input validity only. Jumping can defer errors until export; server error does not link to a field. | Inline associated errors on blur/Continue and pre-export check linking back to offending section. Recovery/help. |
| U08 P1 | Export context | Three equal formats and disclosure dominate; no included-section summary or direct final-preview action. Blank export reaches server for an avoidable error. | Show current design/language, included sections with edit actions and Preview; PDF primary, images secondary; local empty-state prevention. Clarity/error prevention. |
| U09 P2 | Progress | Visited styling looks like completion even when skipped; step position bar reaches 100% on an empty profile. | Say “sections with details”; label empty sections as optional and mark content presence, never claim complete. System status. |
| U10 P2 | Field controls | Every field has a second checkbox, doubling visible decisions. Short checkbox-label rows and icon controls fall below a 44 px comfort target. | One section-level “Choose what to show” toggle; preserve and visibly indicate exclusions; enlarge targets. Minimalism/accessibility. |
| U11 P2 | Keyboard/focus | Whole-step rerender after selecting style/adding entries drops focus. Programmatic step focus outlines a huge container (baseline screenshots). | Restore initiating control or focus the new entry; focus heading with intentional styling; native details/dialog keyboard behavior. Accessibility. |
| U12 P2 | Storage status | Save failure is small text pointing to a backup action hidden in a menu. Privacy link is absent when sidebar hides. | Persistent actionable failure banner and menu privacy action at every width; retain original corrupt data. Recovery/help. |
| U13 P2 | Type/contrast | Secondary UI uses 9–12 px text; status #8c9389 on white is below 4.5:1; muted preview text also fails normal-text contrast. | Semantic foreground tokens, 13–16 px supporting text, strong focus; assess selected/disabled/error states. Accessibility. |
| U14 P2 | Setup | Style and language are separate early steps; style is asked again later. | Preserve familiar 11-step indexing/drafts, add direct “Start with my details” shortcut using editable defaults; final Design remains authoritative. Efficiency. |
| U15 P2 | Template cards | Decorative line thumbnails show color more clearly than actual content composition; selected state exists. | Keep five designs; add a labeled “Preview this design” action and concrete bilingual descriptions of layout differences. Recognition. |
| U16 P2 | Photos | Crop works, source limits enforced, main-photo action works. Decode errors can expose technical English; no reading state; removal is immediate. | Localized actionable file errors, loading feedback, confirm removal; preserve crop and size limits. Status/recovery. |
| U17 P2 | Long preview | Fit-to-panel scales long content into unreadable text, necessary for non-scrolling side panel. Expand icon is small and unclear. | Explicit “Read preview” label, popup fit/full-size modes; explain final page breaks happen at export. Keep side panel stationary. Clarity. |
| U18 P3 | Visual architecture | app.css is largely a single long rule line plus competing breakpoint overrides. | Separate base tokens/components from one authoritative workspace layout; reusable disclosure, entry, review and action components. Consistency. |
| U19 P3 | Help/copy | Privacy copy mentions Flask/rendering internals. Add-entry labels do not identify education/career. | Plain-language processing description, specific add labels and culturally neutral field hints. Real-world match. |

P0: none reproduced. Core creation/export works. P1 means serious friction or recoverable data-loss risk; this audit does not call every issue critical.

## Heuristic and accessibility evaluation

System status: saves/exports announced, but failed-save recovery and meaningful progress need improvement (U09/U12). Real-world match: contact grouping and technical privacy text fail (U03/U19). Control: template switching and hide controls work; Back/removal need fixing (U05/U06). Consistency: adaptive layouts and focus differ unpredictably (U04/U11/U18). Error prevention: secure uploads and redaction strong, destructive editing weak (U06/U07/U08). Recognition: list labels and document designs need context (U06/U15). Efficiency: mobile actions/setup need shortcuts (U01/U14). Minimalism: flattened optional content is the root problem (U02/U10). Recovery: backups and retries exist but lack discoverable action (U07/U12). Help: consent is present; contextual microcopy needs tightening (U19).

Accessibility target: WCAG AA, without claiming certification. Use real headings/labels, details/summary, button aria-expanded/pressed, labeled dialogs, visible keyboard focus, inline errors via aria-describedby/aria-invalid and alert summary. Keep labels at 14 px+, editable text at 16 px, control targets at least 44 px where practical. Use dark secondary text, 3 px focus ring, reduced-motion handling, wrapping Hindi labels, one-column small-phone fields. Keep programmatic headings focusable without drawing a page-sized border. Review browser accessibility tree and keyboard behavior; no automated scanner can establish full screen-reader usability.

## Prioritized implementation

P0: preserve a working runnable app, draft schema v2, hidden-value semantics, local image processing and private export.

P1: U01–U08: structural mobile/tablet shell, optional field grouping, contact relocation, section history, safe repeatable-entry interactions, linked validation, export review.

P2: U09–U17/U19: content progress, inclusion controls, focus, actionable save failure, contrast/type, setup shortcut, template preview, photo feedback and clear read-preview action.

P3: U18: consolidate responsive CSS as part of changing the shell; defer a broad framework rewrite and cosmetic animation. No extra dependencies or new signup/sharing services.

## Responsive strategy

| Range | Form and navigation | Preview | Actions and components |
|---|---|---|---|
| 320–375 | One column, 16 px gutters, compact heading; sticky top navigation and section selector; meaningful saved/progress text. | Popup over current form, large close/read-size controls, scrolling inside popup only. | Bottom Preview/Continue dock with safe-area spacing; Back/Skip on form. Input focus keeps keyboard area free. Entries collapse with named summaries. |
| 390–430 | Same structure, 20–24 px gutters; no two-column text fields merely because space exists. | Same popup, retain template switching without data reset. | 44–48 px controls; no floating button over fields. |
| 768–1024 | Centered form up to 720 px; two-column short fields where useful; direct section selector. | Explicit preview popup, avoiding a squeezed default split. | Same action dock; contact/culture are disclosures. |
| 1280+ | Stationary header, left section navigation, center form scroller, stationary right document overview. Readable bounded form width. | Full document fitted to fixed panel; labeled Read preview opens scrollable popup. | Form footer actions; left steps fit available height; short landscape falls back to selector/form-first. |

Rotation uses available height, not a phone identity. Narrow/short viewports fall back to form-first. Dialogs have bounded dynamic-viewport height. Do not lock body scroll on phone; do not allow desktop side panels to scroll, per user request.

## Design direction and system

Retain warm ivory, deep green, DM Sans for UI and DM Serif Display for editorial headings; Devanagari fallback stays local. The document remains the strongest visual object. Use one green primary action, dark muted text, restrained dividers, no ornamental graphics. Spacing scale 4/8/12/16/24/32/48 px; 8/12/16 px radii; border and shadow tokens; 14/16 px UI, 28–38 px step heading. Use natural language headings with concise instructions. Disclosures reduce decisions without hiding saved data. No pseudo-percentage completeness or culturally prescriptive required fields.

## Implementation map

- `app/static/js/editor.js`: integrate semantic form groups, entry controls, navigation/history, inline errors, save recovery and review; keep profile/document separation.
- New `app/static/js/editor-ui.js`: reusable disclosure markup, presentation group metadata, validation helpers and index-safe entry ordering. No persistence dependency.
- `app/static/js/locales.js`: English/Hindi strings for all new controls, errors and states.
- `app/templates/editor.html`: status recovery banner, mobile action dock, privacy menu and accessible labels.
- `app/static/css/app.css`: retain component foundation; remove competing workspace/media patches. New `workspace.css` owns adaptive shell and redesign components; tokens live in shared foundation and landing benefits from contrast refinements.
- Existing normalized model, routes/export and PDF design stay compatible. No schema change required.
- `scripts/ux_redesign_check.py`: full breakpoint matrix, repeated/hidden data ordering, history, inline errors, deletion, keyboard, restoration and actual export. Update prior scripts for intentional disclosure/IA changes.

## Validation contract

Re-run baseline widths and all eleven screens in both languages; check overflow, action reachability, stationary desktop chrome, no field occlusion, popup close/zoom/theme/keyboard behavior. Test new/incomplete/long profiles; repeated education/career; no astrology/family; multiple photos and invalid/large image errors; failed export retry; PDF/JPG/PNG backend; refresh and browser Back; denied storage and hidden-data migration. Record outcomes separately after implementation; retain baseline evidence.
