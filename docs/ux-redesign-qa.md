# UX redesign: implementation and second-pass QA

14 September 2026. Read `ux-audit-redesign.md` for the audit and implementation priorities written before changes. Baseline evidence remains under `tmp/qa/audit/`.

## What changed and why

- **U01/U04 — action reachability and tablet layout:** one Preview/Continue dock for phone and tablet; form-first layout through 1024 px and in short landscape windows. At 1100 px+ with at least 700 px height, header/steps/document remain stationary while the center form scrolls. No competing floating preview button. Form field scroll margins reserve space for navigation/actions.
- **U02/U03/U10 — cognitive load and grouping:** optional culture, astrology, contact, extra personal details, income and partner content use native disclosures. Populated optional groups open on initial render. Closing a group never hides or deletes values. Contact moved to Personal & contact; custom sections moved to Design. Inclusion controls are available under “Choose what to show”; excluded fields remain marked and recoverable.
- **U05/U09/U14 — orientation:** browser history tracks section fragments without personal data. Back/Forward, reload and explicit step jumps work together. Progress reports how many of six information steps contain data; it does not claim completion or imply fields are mandatory. Start offers a shortcut to personal details with editable defaults.
- **U06/U11 — repeated entries and focus:** named collapsible education/career entries, explicit move up/down controls, focus on newly added fields, and confirmation before removing filled content. Moving a row also moves its hidden-field flags. Keyboard focus returns after selection and dialogs; the preview includes a keyboard-focusable scroll region and explicit Tab/Shift+Tab cycling.
- **U07/U08 — errors and export:** inline age/email/birth-date errors use associated messages and invalid states. Pre-export validation returns to the relevant field even if its disclosure was closed. Review lists included sections, name/photos where relevant, design/language and edit links. PDF is the primary format; JPG/PNG remain available in a disclosure. Empty exports are stopped locally.
- **U12/U16/U19 — recovery and copy:** a failed-save banner has a direct backup action; privacy and keyboard-accessible restore are in the global menu. Photo opening has feedback and localized size/decode errors. Privacy text no longer exposes Flask implementation details. Existing local draft recovery, consent, redaction and upload processing remain intact.
- **U13/U15/U17/U18 — presentation:** reusable presentation helpers and validation/ordering logic in `editor-ui.js`; shared design tokens; readable field/support text; consistent focus and target sizing. Removed prior workspace layout declarations and established `workspace.css` as the responsive shell. Template cards have concrete English/Hindi descriptions and an actual-document preview action. The non-scrolling document overview has a labeled Read preview control.

No profile schema, export route, font dependency or PDF template changes were required. Version 1 family migration and version 2 drafts remain compatible. Existing PDF full-bleed backgrounds and whole-section pagination are preserved.

## Verified results

- **40 backend tests pass**, including all five PDF themes, long Hindi pagination, hidden-data exclusion, embedded fonts, full-bleed corner checks, whole-section movement and PNG/JPG exports.
- **308 screen checks pass:** all eleven steps in English and Hindi across 14 viewports: 320×568, 360×800, 375×812, 390×844, 412×915, 430×932, 768×1024, 820×1180, 1024×1366, 1280×800, 1440×900, 1600×900, 1920×1080, 844×390. No page horizontal overflow. The mobile primary action stays in view; desktop chrome stays stationary and every step remains accessible.
- `ux_redesign_check.py` passes browser Back/Forward, age and email recovery, order/hidden-flag preservation, cancellation and confirmation of removal, saved-draft reload, custom fields, template changes, popup zoom and a real PDF download. No JavaScript errors.
- Existing `browser_check.py`, `check_edge_flows.py` and `revision_check.py` pass after updating selectors for the intentional disclosure/grouping changes. They cover photo cropping, transmitted hidden-income exclusion, offline editing, backup/restore, error retry, deletion, denied storage, legacy hidden family data and Hindi labels.
- `ux_content_check.py` passes 50 content-heavy screen checks across ten viewports, plus Hindi landing checks. Fixtures include four education entries, four career entries, long Hindi prose, no family/astrology, and three photos uploaded from a 14.4-megapixel source. Files over 8 MB, unsupported types and a 25-megapixel image are rejected. Popup keyboard cycling, 44 px control target heights and direct backup recovery pass with no JavaScript errors.
- Python compilation passes. No new runtime dependencies or external UI services.

## Findings corrected during second pass

1. Tightened small-phone section controls so the first personal input appears on a 320×568 screen while Continue remains visible.
2. Corrected section fragments after draft deletion/sample/restore so reloading does not jump to stale navigation state.
3. Kept preview keyboard focus within its controls and scrollable document region. Native Escape and backdrop dismissal remain.
4. Enlarged the tablet language selector and desktop privacy control to a 44 px minimum target height.
5. Kept the preview caption tied to draft content so opening the popup does not restore sample-only copy.
6. Preserved focus after adding custom fields and after destructive confirmation; synchronized menu expanded state after Escape/outside click.

## Evidence and reproducibility

- `scripts/audit_capture.py`: baseline measurement workflow. Run again only when intentionally taking a new baseline; original `tmp/qa/audit/baseline.json` predates this redesign.
- `scripts/ux_redesign_check.py`: bilingual responsive matrix and end-to-end interaction checks.
- `scripts/ux_content_check.py`: long Hindi/repeated entries, multiple large photos, upload failures, keyboard traversal, recovery and target sizing.
- Screenshots, matrix JSON and downloaded PDF: `tmp/qa/redesign/`. These are ignored QA artifacts containing fictional data. Use the README commands with the app running locally.

## Practical limits and follow-up

These results are Chromium emulation on macOS, not measured task success with Indian users. Physical low-cost Android/iPhone devices, software keyboard behavior, Safari, VoiceOver/TalkBack, native Hindi copy review and a full WCAG conformance assessment still need human testing. The redesigned UI targets AA; this report does not claim certification.

Template cards retain schematic thumbnails; the labeled popup renders actual data/designs for comparison. Long documents intentionally shrink in the fixed overview; use Read preview and 100% for reading. Final page boundaries remain determined by the actual export. Eleven steps are preserved for continuity, with a shortcut to reduce setup friction. Cloud accounts, public share links and guarantees of WhatsApp delivery remain outside scope.
