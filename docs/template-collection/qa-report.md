# Collection implementation and QA — 15 September 2026

## Delivered

- 20 new designs alongside the 19 existing templates, grouped as Contemporary (6), Regional (5), and Traditional & cultural (9).
- Eleven reusable layout presets, separate artwork packs, compatible optional cultural headers, and a shared semantic renderer for preview, PDF and image export.
- Twenty complete specifications, nineteen structured asset prompts, nineteen inspected source artworks, and fifty-seven optimized print/preview/thumbnail assets. No personal information or document labels are baked into artwork.
- Eighty prebuilt gallery images: twenty designs × two fictional sample people × English/Hindi, generated with the actual document engine.
- Embedded font architecture for English, Hindi, Marathi, Gujarati, Punjabi, Bengali, Tamil, Telugu, Kannada, Malayalam and Urdu. The app interface remains English/Hindi; additional-script content and explicit RTL are supported.
- Structured data, section hiding and field hiding, user-controlled cultural options, compatible backup parsing, local autosave, and accessible preview text preserved.

New drafts start with Editorial Ivory. Existing drafts retain their design. Discovery never reads caste, religion, surname, city, language or gender to recommend or filter cultural templates. An explicit None choice survives design switches and reloads; incompatible specific symbols cannot transfer to an unrelated design.

## Validation evidence

| Check | Result | Evidence |
| --- | --- | --- |
| Normal test suite | 52 passed; 46 renderer tests intentionally skipped without the opt-in flag | `python -m pytest -q` |
| Full real-export suite, before the three new recovery unit cases | 93 passed initially; two PDF-size failures corrected and both passed on targeted rerun | `tests/test_exports.py`, `tests/test_figma_templates.py`, `tests/test_collection.py` |
| Seven content scenarios per design | 140 passed | `output/template-collection/batch-{1,2,3}/report.json` |
| Long names, uninterrupted text, whole-section movement, all compatible headers | 68 passed | `output/template-collection/edge-checks/report.json` |
| Mobile preview for all designs; responsive categories; keyboard, live update and autosave | 30 checks passed, no JavaScript errors | `output/template-collection/browser/report.json` |
| Final RTL/header/image-export checks | 25 passed | `output/template-collection/final-render-checks.json` |
| Explicit None and incompatible-art persistence | Four passed | `output/template-collection/browser/choice-persistence.json` |
| Busy renderer recovery, bounded retries and stale-draft protection | Three browser cases passed; three new endpoint unit cases passed | `output/template-collection/browser/busy-recovery.json`, `tests/test_studio.py` |
| Existing mobile creation through photo crop, preview, privacy and PDF/share fallback | Passed | `scripts/mobile_product_check.py` |

Nine Chromium viewport configurations were checked: 320×568, 360×800, 390×844, 430×932, 768×1024, 1024×1366, 1280×800, 1440×900 and 1920×1080. These are emulated browser sizes and touch input, not a physical-device lab. Keyboard interaction, live auto-updates and reduced-motion behavior were exercised. Final viewport screenshots wait for the preview to be ready.

Every template was rendered with short, medium, long, no-photo, hidden-section, multilingual and RTL fixtures. Assertions check A4 dimensions, visible text, no geometry overflow, no empty hidden sections, a body minimum of 10.5 pt, and quiet continuation pages. Dedicated stress cases keep an eight-entry education section intact when it fits a page and preserve a 2,900-character uninterrupted field. Longer sections split at measured content boundaries instead of reducing type size.

Color/grayscale first pages, cultural artwork and symbols, mobile previews, multilingual glyphs and RTL first pages were visually reviewed. The collection retains cream/ivory reading areas, selectable text, thin printable rules and complete photo framing. Full source images are not served to the browser.

## Final asset and export sizes

- All scenario PDFs: maximum **1,239,996 bytes** (Gujarat Patola multilingual); medium-profile maximum **1,029,448 bytes**.
- Eighty gallery thumbnails: **1,087,006 bytes total**, median **14,116 bytes**, maximum **19,558 bytes**.
- Fifty-seven optimized artwork variants: **3,195,738 bytes total**, maximum individual asset **218,212 bytes**.
- Nineteen generation masters: **28,841,050 bytes**, stored outside the served static directory.

Live previews and exports run in the existing isolated renderer. User data is not cached in shared artwork/font caches, saved publicly or sent to an image model. Generated artwork is a build-time asset only. Image export uses the same paginated PDF; multi-page image exports retain the established archive behavior.

Repeated concurrent capture sessions exposed the two-slot renderer's temporary busy response. The preview endpoint now identifies only that condition with Retry-After. The client keeps its loading state and retries at most three times with increasing delays, within the existing overall timeout. Changed drafts abandon pending retries; renderer failures and validation failures are not retried automatically. A failed thumbnail cannot replace a successful full preview. Fault-injection checks verify recovery against the real renderer and verify the bounded error state when capacity remains unavailable.

## Review and reproduction

- Visual gallery: `output/template-collection/index.html`.
- Architecture: `docs/template-collection/architecture.md`.
- Registry: `app/biodata_templates/collection.json`; layouts and art packs sit beside it.
- Specs and prompts: `docs/template-collection/specs` and `prompts`.
- Generation provenance, review decisions and font licenses: `artwork-manifest.json`, `cultural-review.md`, `font-provenance.json` and vendored OFL files.
- Run `scripts/check_collection.py --batch 1` (then 2 and 3), `check_collection_edges.py`, `check_collection_browser.py`, `check_collection_final.py`, `check_collection_choices.py` and `check_collection_retry.py` with the configured Chromium path.
- Regenerate browsing images with `scripts/build_collection_gallery.py` and the review page with `scripts/package_collection_review.py`.

Physical printer proofs and review by members of the represented communities are not claimed. FaceDetector-assisted initial framing is available only in browsers that implement that API; complete-image framing and manual crop remain available everywhere.
