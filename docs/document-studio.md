# Design & Preview: browser document studio

## Rendering contract

`Profile.parse` → normalized, disclosure-filtered `document()` → escaped Jinja
`repaired-document.html` + trusted template CSS → browser A4 pagination.

`POST /api/preview/html` returns markup and an accessible text representation.
It never invokes Playwright, PDFium, or a renderer subprocess. Fonts use cacheable
same-origin static URLs; normalized photos and template artwork are embedded.
The browser waits for fonts and photos, then runs the same
`repaired-paginator.js` used by PDF exports against a hidden measurement frame.
Individual paginated sheets are shown in fixed-ratio, scaled A4 frames.

All frames are sandboxed with only `allow-same-origin`: scripts, forms and popup
navigation are disabled. The parent runs the trusted paginator; no script from
preview markup executes. Text alternatives live outside the frames. Zoom and
page controls remain normal keyboard-accessible controls.

Downloads explicitly call the existing isolated server renderer. They share the
same semantic builder, fonts, CSS and pagination algorithm, but are not cached
preview bytes. Browser font metrics may produce small pagination differences.
The legacy `/api/preview` endpoint remains available for existing integrations.

## Interaction and layout

Gallery cards initially show fictional sample WebPs. Selecting a design renders
current included details in its thumbnail, the side pane, Spotlight and the
mobile modal. Other cards clearly retain sample labels. The gallery makes no
background server screenshot requests for unselected designs.

Desktop Spotlight shows two pages when space permits, with designs in the side
rail. Compact layouts show one page and use the existing full-preview modal.
Page navigation, zoom, mobile download review and the text alternative all use
the same current result. Selecting a new template returns to page one; edits
preserve the page where possible. No form or draft data is changed by selection.

## Privacy, caching and failure behavior

Included details are temporarily processed by Flask to build preview markup.
Hidden fields, sections and photos are removed before requests and server
normalization checks them again. Requests require CSRF and are rate limited.
Responses are `no-store, private`. No public profile, preview URL, server cache,
or saved preview file is created. Draft autosave remains in IndexedDB.

Typing debounces previews independently of immediate draft saving. A new draft
revision or selection aborts the previous request; generation guards prevent
stale responses from overwriting current details. The tab retains at most three
paginated HTML results in memory. Clearing a draft clears this cache. Detached
measurement frames and thumbnail resize observers are cleaned up.

Loading, empty and retry states retain the A4 footprint. Requests time out after
30 seconds. Offline editing works; an uncached preview still needs Flask, but
never needs server Chromium. Downloads continue to depend on server Chromium.

## Verification

Run `RUN_EXPORT_TESTS=1 python -m pytest -q` for backend and real export coverage.
`tests/test_html_preview.py` forbids renderer subprocess creation while verifying
the new route, escaping, hidden data, validation, private caching and CSRF.

Browser QA uses a separate local app configured with a nonexistent Chromium
executable. Checks cover immediate detail updates, template changes, two-page
Spotlight, mobile full preview/page navigation and download review. Historical
studio scripts that assert raster images or reuse of preview PDF bytes describe
the previous implementation and must not be used as this version's contract.
