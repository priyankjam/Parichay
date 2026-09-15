# Design & Preview: document studio

The studio has one design-selection surface: category pills and personalized A4 thumbnails in the gallery. The right pane contains only the chosen document, its actual page count, page navigation and Full preview. On compact screens, the persistent Preview action opens the same pane in a large modal. The ordinary desktop header, steps and preview remain stationary while the gallery scrolls.

## Rendering contract

`Profile.parse` → normalized `document()` → Jinja `biodata.html` + trusted template styles → isolated Chromium A4 PDF → PDFium page images.

`POST /api/preview` calls the existing `export_document` service. Full responses contain the PDF and 1200px WebP page images; thumbnail responses contain only a 300px first sheet and the true page count. There is no second client-side document layout. The JavaScript `buildDocument` helper now supplies only the review list, inclusion checks and export filename; it does not render a visual biodata.

The pane and Full preview display the same page image at a proportional scale. Page boundaries cannot stretch with content. PDF download reuses the exact previewed PDF when the included data and template match; otherwise it uses the same server renderer. JPG/PNG continue to use that renderer. A text alternative, derived from the normalized included fields in section order, accompanies raster previews for assistive technology. Downloaded PDFs retain selectable text and tags.

The renderer preserves whole sections where possible. A section taller than one usable sheet starts on a fresh page and continues without shrinking its type. Each page repeats the full-bleed background with internal text insets. Floral designs with intrusive corner art have explicit `printSafePadding` metadata so continuation text clears the artwork. Original source padding and artwork are retained separately.

## Interaction and layout

- Five filters: All, Minimal, Modern, Classic & floral, Traditional. They remain on one horizontally scrollable row; the selected filter remains visible after resizing.
- Cards contain a first-page thumbnail, name, category and explicit check + Selected state. Clicking changes selection and save state immediately; the document area shows a stable loading sheet until accurate pages arrive.
- No template dropdown, generic swatches, duplicated preview button, design-step Skip action, editor tagline or duplicate language indicator.
- Header is 60px with compact branding, Guest, language and draft options.
- Every sidebar row keeps its sequence number. A separate check means the step has been visited/reviewed and is no longer current; it does not imply optional personal information is required. The current row remains numbered and highlighted.
- Custom fields/sections remain available under About you, outside the final design task.
- At widths ≥1280px and heights ≥700px, three fixed columns are used. Smaller or enlarged-text layouts use the existing section selector and preview modal. Desktop gallery uses three columns when its inner container can support them, otherwise two. No three-column UI is squeezed into phones.
- Preview uses one sheet at a time with Page X of Y, Previous/Next, Fit page and 100% in the full viewer. Edits preserve the current page, clamping it only if the updated document has fewer pages; selecting another template starts at page one. Escape, browser Back and the visible return control preserve the underlying editor step.

## Privacy, caching and failure behavior

Included information is sent temporarily to the server for the visible live preview, when opening a full preview, entering the design library or reviewing a download. Every information step refreshes the selected preview automatically after a 500ms typing pause, with a maximum 1500ms wait during continuous typing. Saving to IndexedDB starts immediately. Compact layouts also render the latest selected document while editing, so opening the viewer does not initiate the first refresh. Rendering no longer depends on the current step or pane visibility. Hidden fields, hidden sections and hidden photos are removed before requests. The server validates again, requires CSRF, limits requests and renderer concurrency, blocks external renderer traffic and returns no-store/private responses. No public preview URL or server profile/cache is created.

This changes the former export-only processing boundary. The editor, photo helper, privacy explanation and homepage now disclose temporary processing for **previews and downloads**. Drafts remain in IndexedDB; rendered preview copies stay only in the current tab's memory. Clearing a draft also invalidates the in-memory preview cache.

A single client request queue prioritizes the selected full preview. IntersectionObserver requests only gallery cards approaching the viewport. Results are reused for unchanged included data; at most three full PDFs are retained, with first-sheet thumbnails retained for the other designs. Editing included data invalidates the generation, and older responses cannot replace newer data. Leaving/filtering the library drops unneeded queued thumbnail jobs. The implementation does not start nineteen full-resolution jobs concurrently.

Loading, empty and failure states preserve the A4 footprint. Failed selected previews show a localized explanation and Try again. Switching to a failed thumbnail also exposes that retry path. Offline editing remains available; an uncached accurate preview needs the server. Already cached PDFs can be downloaded without regenerating them. Production still needs representative server-capacity and network measurements.

## Verification

Current repeatable checks:

```sh
RUN_EXPORT_TESTS=1 python -m pytest -q
python scripts/studio_render_check.py
python scripts/studio_browser_check.py
python scripts/studio_state_check.py
python scripts/live_preview_check.py
```

The render matrix uses five fixtures across all nineteen templates: short, medium, long with repeated education/career and photos, Hindi, and long names/institutions/companies. Every returned sheet is compared with an independent rasterization of its accompanying PDF; page count and A4 geometry are checked, and glyph bounds are scanned for clipping outside the page. For each template, a separately generated thumbnail is compared with the PDF's first sheet at thumbnail resolution. Contact sheets and representative continuation pages are inspected visually; this caught floral artwork overlapping continuation text and led to the safe-inset correction.

The browser checks use a newly entered name in the thumbnails, pane and PDF, verify automatic information-step updates and hidden-field changes without opening Full preview, exercise all seven requested viewports (360×800, 390×844, 768×1024, 1024×1366, 1280×800, 1440×900, 1920×1080), page navigation and full-size zoom, and compare downloaded bytes with the actual preview response. Recovery checks exercise server failure/retry, hidden fields before transmission, stale response protection under network latency, Hindi controls, keyboard selection, reduced motion and 200% text.

Evidence is under `tmp/qa/studio/`; render records are in `render/results.json`, browser results in `browser.json`, and recovery results in `state.json`. Earlier UI QA scripts that target the removed continuous preview are historical evidence for previous iterations; the studio scripts replace those selectors and assumptions.

## Spotlight mode

Design & preview has an optional Spotlight mode. It moves the shared preview pane into the center of the workspace and turns the same nineteen template cards into a horizontally scrolling bottom strip. All templates remain available regardless of the gallery's category filter. Selection, PDF pages, thumbnails and cache are shared with the gallery; changing modes does not alter profile data. The selected card is outlined and checked. Arrow keys, Home and End move focus through the strip; Enter/Space select a template.

Wide preview areas display the current and following PDF page side by side when available. Compact areas display one A4 page. Existing page controls and Full preview remain available, and closing Full preview returns the pane to its current mode. Leaving Design & preview restores the ordinary editor layout. `python scripts/spotlight_check.py` verifies selection, pagination, keyboard access, modal return and responsive layouts.

Category pills stay pinned while scrolling either gallery. On desktop they pin to the form's scroll area; on compact layouts they sit below the app header and section selector. A ResizeObserver measures the selector so the offset also follows wrapped labels and text enlargement. `scripts/sticky_filters_check.py` checks both steps on desktop and mobile, including selection while pinned.

### Immediate gallery thumbnails

Both galleries display versioned, public WebP samples before personalized renders
finish. `scripts/build_gallery_samples.py` builds all 76 template/gender/language
variants from fictional data through the PDF pipeline (about 1 MB total). Rebuild
and bump `gallery-v1` in the generator and client when sample layouts change.
Sample-only galleries do not request thumbnail PDFs. For a personal draft, a
visible “Sample · adding your details…” label distinguishes the initial image
until its actual first PDF page replaces it. Personal images are never published
or persisted in a shared cache. A full-preview lane and a thumbnail lane permit
at most two simultaneous requests, so queued thumbnails do not block selection.

Run `scripts/gallery_speed_check.py` to verify desktop/mobile images load even
when the rendering endpoint is unavailable; the normal studio browser check
covers personalized replacement and live-preview behavior.
