# Parichay

A Flask marriage biodata editor for India. Guest creation, locally saved drafts, English/Hindi, 47 available document designs, and real PDF/JPG/PNG export. No signup, public profile URLs, profile database or analytics trackers.

## Run locally

Clone the repository with `git clone https://github.com/priyankjam/Parichay.git`, then `cd Parichay`.

Python 3.10+ and Chromium are required. Python 3.12 is used in development.

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
cp .env.example .env
python run.py
```

Open http://127.0.0.1:5000. Set `PORT=5050` if port 5000 is used by macOS AirPlay. On Linux, install Chromium's system dependencies with `python -m playwright install --with-deps chromium` during environment setup.

Alternatively set `CHROMIUM_EXECUTABLE` to an existing Chromium/Google Chrome executable. This workspace's ignored `.env` uses `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` and port **5050**. The application does not use your normal browser profile or cookies for rendering.

The development secret is randomly generated on process start. For a stable session across restarts, set `SECRET_KEY` using `python -c "import secrets; print(secrets.token_hex(32))"`. Production refuses to start without a configured secret.

The repository includes the application, prepared artwork and fonts, generation masters, tests and design documentation. Local `.env` files, virtual environments, caches, generated review/export files and the original reference documents are ignored. No local reference folder is required to run the app. Review outputs can be regenerated using the scripts described below.

## What works

The product UI uses **Paper & Plum**: warm paper surfaces, plum actions, editorial marketing type and a neutral document studio. The audit, tokens, component boundaries and visual QA are documented in [the design system](docs/paper-plum-design-system.md). Document themes retain their own palettes.


- A dedicated English/Hindi landing page leads into ten guided steps, starting with gender and language together, with a shortcut to personal details. Browser Back/Forward tracks sections; drafts keep their content independently.
- Mobile/tablet form-first layout through 1024 px, persistent Preview/Continue actions and a zoomable popup. Desktop keeps the header, steps and document overview stationary while the form scrolls. Short windows fall back to the form-first layout.
- Optional contact, culture, astrology, income and partner groups open on demand. Personal details use meaningful groups; About focuses on your introduction. Custom sections live in Design.
- Collapsible education/career entries have named summaries and move controls. Removing filled entries, photos or custom content asks for confirmation. Reordering preserves hidden-field flags.
- Inline validation links export errors back to the relevant field. Export review lists included sections, design, language and photos; PDF is the primary format. Progress counts sections containing details, not mandatory completion.
- Forty-seven selectable designs across the original, illustrated, contemporary, regional and cultural collections; two retired designs remain compatible with saved drafts. Shared category filters and full-bleed thumbnails in both design steps, gender-aware sample portraits, and instant template switching. Template selection never sets cultural information.
- Repeatable education and career entries; three consistent optional family inputs for father, mother and siblings; expanded optional culture/astrology sections and optional contact/partner information. Interests offer translated choices and up to five selections.
- Per-field inclusion and section hiding; custom sections and custom fields.
- Five photos, local crop/zoom/position/rotation, primary-photo selection, image validation and compression. No appearance manipulation.
- Immediate asynchronous IndexedDB writes on edits (preview rendering alone is debounced), with visible failures, return-session recovery, editable JSON backup/restore and local deletion. Corrupt/incompatible stored drafts are not silently overwritten.
- Locally served English and Hindi font resources. Interface and document labels switch language; personal writing is not automatically translated.
- A4 PDF with embedded fonts/selectable text and real browser pagination. JPG/PNG are rendered from those PDF pages. Multipage images download as a ZIP, preserving page order.
- Web Share file flow where the browser supports it; download/manual WhatsApp attachment fallback elsewhere. This does not claim to send a message or confirm delivery.
- Fictional sample biodata from `app/models/catalog.py`, available through “Try it with a sample biodata.” An empty draft previews a clearly labeled sample but never exports the sample implicitly.

## Architecture

```text
app/
  __init__.py             Flask factory, CSRF, limits, security/error responses
  config.py               Environment settings
  models/catalog.py       Canonical field and template registry + sample profile
  models/profile.py       Versioned normalized Profile and disclosure filtering
  routes/editor.py        Editor and health routes
  routes/exports.py       Validated export/image endpoints
  services/images.py      Strict decode/re-encode and metadata removal
  services/rendering.py   Bounded renderer orchestration and PDF-page images
  services/render_worker.py  Isolated Chromium subprocess
  templates/              Jinja app shell and document markup
  static/js/              Vanilla JS editor, reusable controls, IndexedDB
  static/css/             Separate product and document design tokens
  static/fonts/           Self-hosted OFL fonts and licenses
  biodata_templates/      Template contract and extension instructions
  utils/                  Reserved for small shared utilities
```

There is deliberately **no SQLAlchemy/SQLite profile table** in this guest release: persistence is on the device, and exports are ephemeral. Adding a database just to retain sensitive profiles would be unnecessary. `Profile` is a normalized, versioned domain schema independent of persistence. If account-based saving is added, use a SQLAlchemy repository with JSON profile payloads, explicit owner authorization, migrations and a configurable database URL (SQLite locally, PostgreSQL in production). Do not add a public profile endpoint or cloud persistence implicitly.

### Data contract

`schemaVersion: 2`, `forWhom`, `gender`, `language`, `template`, `presentation`, `sections`, `hiddenSections`, `hiddenFields`, `customSections`, `photos`. The section registry declares each field's label, type, limit and sensitivity. Unknown properties are discarded on server normalization. Text stays plain text and is escaped at rendering boundaries rather than attempting unsafe HTML sanitization.

Repeatable lists support 12 entries each. Custom sections: eight; fields per custom section: twelve. Five photos, each source up to 8 MB/24 megapixels; accepted formats JPEG/PNG/WebP. Text total: 40,000 characters. Exports are limited to 20 pages. These limits bound computation rather than silently truncate user data. Age or birth date, if supplied, must represent an adult; no exact date of birth is required.

The design studio renders the actual PDF into fixed-ratio A4 sheets. Thumbnail, selected-page preview and full preview come from the same Chromium/Jinja export engine, and PDF download reuses the exact previewed bytes when the data matches. All 49 saved template IDs now use the shared semantic builder in `services/repaired_documents.py`, explicit compositions in `biodata_templates/repair.json`, and `repaired-paginator.js`. The field registry still owns profile labels and values. Short education/career/family records stay together; oversized content continues at measured record, row and Unicode grapheme boundaries. There is no independent client-side print layout or text autoscaling. Page backgrounds are full bleed with readable internal text insets.

### Routes

| Route | Behavior |
|---|---|
| `GET /` | English/Hindi landing page with Get started |
| `GET /create` | Guest editor; embeds schema/config and CSRF token |
| `GET /health` | Process health only; does not launch the renderer |
| `POST /api/export/pdf` | Profile JSON → PDF attachment |
| `POST /api/export/jpg` | Profile JSON → JPG or multipage ZIP |
| `POST /api/export/png` | Profile JSON → PNG or multipage ZIP |
| `POST /api/images/validate` | Multipart `photo` → normalized JPEG data URL; no disk upload |

POSTs require the session-bound `X-CSRFToken` header. The normal photo workflow decodes/crops in the browser; the optional image-validation endpoint supports clients needing server normalization. Exports revalidate all images regardless of origin.

## Privacy and security boundaries

Drafts and photos remain in IndexedDB while editing. IndexedDB is **not encrypted storage or access control**: someone using the same browser can access the draft. Browser eviction or clearing data can remove it. Download a backup to retain an editable copy. Offline editing works in an already loaded tab; a full offline reload is not guaranteed (no service worker/PWA cache yet).

The export review requires explicit confirmation of temporary processing. The browser removes hidden values before sending a profile. The server independently removes hidden fields/sections before building the rendered document. Do not put sensitive values into URLs, logs, telemetry or a future session replay tool.

Each export runs in a fresh browser context with JavaScript disabled and external network requests blocked. Fonts and validated images are embedded as data URLs. Renderer calls are time-bounded, capacity-limited and disposed after the job. Browser temporary files are transient, not saved profiles. On timeout, the process group is terminated on POSIX systems; abrupt process/host failures may leave temporary browser files, so deployment must use an ephemeral private temporary directory with cleanup. Do not promise that data never touches disk.

Uploads are decoded by Pillow, bounded, resized, re-encoded and stripped of EXIF/comments. Original filenames never become filesystem paths. Remote image URLs and SVG are rejected. Jinja autoescapes content; client markup escapes strings. Static scripts/fonts are local, CSP prohibits external scripts, responses have `nosniff`, no-referrer, anti-framing and no-store for application/export routes. No public profile or enumeration endpoints exist.

Files already sent cannot be revoked. Link sharing, PIN controls and public hosting are intentionally not simulated. Downloading a PDF is not proof of delivery through WhatsApp. Language selection changes labels, not names or personal prose. Hindi copy should receive native-speaker editorial review before a national release.

## Production deployment

For PythonAnywhere WSGI setup, domain configuration, and Chromium compatibility,
see [the PythonAnywhere guide](docs/pythonanywhere.md).

Use Linux, a non-root process, Chromium's sandbox, a reverse proxy with HTTPS, and a persistent high-entropy `SECRET_KEY`. Set `APP_ENV=production` and `TRUSTED_HOSTS` to the real hostname(s). Never expose Flask's development server to the internet.

```sh
APP_ENV=production gunicorn --bind 127.0.0.1:8000 --workers 1 --threads 4 --timeout 75 run:app
```

Start with one worker and measure peak memory. Each process admits at most two simultaneous renderer jobs; a six-per-minute per-IP export limit and default request limit are also applied. The default limiter backend is in-memory: for multiple workers or instances, install a supported shared-store adapter (for example `Flask-Limiter[redis]`) and set `RATELIMIT_STORAGE_URI`. Keep edge limits as well. Do not trust arbitrary `X-Forwarded-For`: configure a precisely bounded trusted proxy chain before using forwarded client IPs.

Ensure the host supports Chromium sandboxing as the non-root runtime user. Do not “fix” deployment by adding `--no-sandbox`. Use isolated compute, constrained CPU/memory, a private ephemeral temp volume, outbound network restrictions for the renderer and observability that logs error categories only. Browser installation happens at build/setup, not on a user's request. With HTTPS, secure session cookies and HSTS are enabled.

At the reverse proxy, set body size to the app's 18 MB maximum, bounded request/response timeouts and no body/access payload logging. Do not cache editor pages or exports. Use `/health` for liveness and a separate synthetic export probe with fictional data for readiness. There are no database migrations, paid services or third-party API secrets needed for this release.

Before broad launch: validate on real budget Android and iOS devices, native Hindi review, load/abuse tests under deployment limits, accessibility assistive-technology review, privacy/consent/legal review, and restore/temporary-storage operational checks. Local automated tests are not a security audit, nationwide language certification or a production SLA.

## Tests and QA

```sh
pip install -r requirements-dev.txt
python -m pytest -q
RUN_EXPORT_TESTS=1 python -m pytest -q
# With the local app running:
python scripts/studio_browser_check.py
python scripts/studio_state_check.py
# All nineteen designs × five content fixtures, using the same local renderer:
python scripts/studio_render_check.py
```

The exact tested application/test environment is recorded in `requirements-lock.txt`. Optional font rebuilding uses `scripts/compress_fonts.py` with the development-only `fonttools` and `brotli` packages; the app ships prebuilt WOFF2 assets and does not need those tools at runtime.

Browser/renderer tests use `CHROMIUM_EXECUTABLE` when supplied; on this Mac they use the existing Chrome installation. On other machines, set a binary path or use Playwright's installed Chromium (scripts automatically use its default when no system Chrome exists).

Tests cover normalization, hidden data, invalid input, age/birth date, custom/Hindi fields, CSRF, no public profiles, escaped HTML, malicious/oversized uploads, metadata removal, actual PDF text/fonts/A4 dimensions, all thirty-nine themes, long Hindi pagination and image archives. Browser QA covers the ten-step path, adding entries/custom fields, template preservation, crop, download, reload recovery, offline editing, Hindi, mobile overflow, backup/restore and browser errors. Synthetic exports/screenshots are written under ignored `tmp/qa/`.

## Known scope and maintenance notes

- No accounts, cloud drafts, SQL database, hosted links, payments, runtime AI generation, voice, collaborations or matrimony matching. Decorative AI artwork is pre-generated and reviewed.
- IndexedDB last-write behavior between separate tabs needs care; use one editing tab for a draft. Export/delete actions apply only to this local draft and files subsequently generated.
- Version 1 drafts/backups migrate to version 2 on both client and server. Legacy family rows become father/mother/siblings; unrecognized relationships and individually hidden legacy fields are preserved in custom sections with their disclosure settings. Unsupported future versions are rejected; failed recovery preserves the stored original.
- Renderer fonts are self-hosted DM Sans, DM Serif Display, Noto Sans Devanagari, Inria Sans, Figtree, Poppins, Tiro Devanagari Sanskrit and Merriweather under the included SIL Open Font License files. The new collection also embeds Noto families for Marathi/Devanagari, Gujarati, Gurmukhi, Bengali, Tamil, Telugu, Kannada, Malayalam and Urdu, plus verified optional cultural symbols. English/Hindi remain the interface languages.
- Update Chromium/Playwright and Pillow regularly, rerunning artifact QA. Do not upgrade the renderer without comparing long-content exports.

The pre-implementation audit, priorities, responsive strategy and design direction are in `docs/ux-audit-redesign.md`. Second-pass results are in `docs/ux-redesign-qa.md`. Reusable form presentation helpers live in `app/static/js/editor-ui.js`; `tokens.css` owns product design tokens, `app.css` owns shared components, `workspace.css` owns the adaptive editor/preview layout, and `landing.css` owns marketing composition. A local SVG icon set is shared by Jinja and JavaScript.

The earlier product discovery document is retained in `docs/product-foundation-phase-zero.md`; this implementation follows the later Flask build brief.

The imported design catalog, supplied asset mapping, preview regeneration and image-edit provenance are documented in `docs/figma-templates.md`.

The three-persona usability evaluation, pre-change findings, root causes, implementation and retest evidence are in `docs/usability-personas.md`. Six fresh-context journeys cover English/Hindi mobile, tablet and desktop. Focused checks cover immediate reload/tab close, history-aware preview, safe photo replacement, WhatsApp fallback instructions and 200% text. These are expert simulations, not participant research or actual WhatsApp delivery tests.

The current Design & Preview architecture, privacy boundary, cache limits and verification are documented in `docs/document-studio.md`. Previewing and comparing designs temporarily processes included details on the server; hidden details are removed before transmission. There are no public preview links or server-side preview caches. Earlier browser scripts are retained as historical QA for the previous continuous-preview interface.

The gender, gallery, family and hobby refinements, generated portrait prompt and QA flow are documented in [editor refinements](docs/editor-refinements.md).


### Mobile product experience

Below 768px the editor uses a separate nine-stage mobile presentation over the same normalized profile and autosave/rendering services. Optional details, record editing, the design gallery, full-screen crop/preview, review, download and sharing have dedicated mobile patterns. Tablet and desktop retain the existing layout; the landing hero is unchanged.

The audit, implementation decisions, test boundaries and persona walkthroughs are in `docs/mobile-product-redesign.md`. The English review gallery is `output/mobile-product-review/index.html`.

Current mobile browser checks (start the app on port 5050 first):

```sh
python scripts/mobile_product_check.py
python scripts/mobile_product_regression.py
python scripts/mobile_product_recovery.py
python scripts/mobile_product_review.py
```

Run the creation check before regression: the latter reuses its actual PDF as a deterministic viewport fixture. Review captures use fictional data in disposable browser contexts. The privacy-safe `parichay:analytics` DOM event is an integration hook only; no analytics data is transmitted unless a consumer is explicitly added.


### Curated document collection

The twenty new templates are available first in the design gallery under Contemporary, Regional, and Traditional & cultural. The original nineteen remain available. New editor drafts start with Editorial Ivory; existing drafts retain their chosen design. Template selection never reads identity fields. “Personalize this design” exposes only compatible cultural artwork/symbols and document direction. Choosing None is preserved when switching designs. The optional जय भीम heading is real Devanagari text.

- Architecture: `docs/template-collection/architecture.md`.
- Template registry: `app/biodata_templates/collection.json`; reusable layouts and artwork packs live beside it.
- Twenty design specifications: `docs/template-collection/specs/`.
- Original prompts, asset decisions, provenance, font sources and test fixtures: `docs/template-collection/`.
- Generated masters: `artwork-masters/collection-v1/` (not served). Optimized print/preview/thumbnail artwork: `app/static/artwork/collection-v1/`.
- One hundred and twenty complete fictional browsing samples for the new collection: `app/static/artwork/collection-gallery-v2/`. They are rendered by the actual document engine. No user's data is cached publicly.
- Review gallery and A4/color/grayscale proofs: `output/template-collection/index.html`.

```sh
python scripts/check_collection.py --batch 1
python scripts/check_collection.py --batch 2
python scripts/check_collection.py --batch 3
python scripts/check_collection_edges.py
python scripts/check_collection_browser.py
python scripts/check_collection_final.py
python scripts/check_collection_choices.py
python scripts/check_collection_retry.py
python scripts/build_collection_gallery.py
python scripts/package_collection_review.py
python scripts/capture_unique_template_samples.py
```

Artwork and gallery paths are versioned and immutable-cacheable. Bump their version when publishing changed assets. Fonts and all art are local; no image-generation API is called at runtime. Approved photo crops are contained within frames; optional browser-native face detection assists manual cropping when available, with no network request.

The current paginator keeps fitting sections whole, splits oversized text at semantic boundaries and measured Unicode grapheme boundaries, and uses compact continuation headers. It rejects unresolved overflow rather than clipping. Body text is at least 11pt (11.5pt on the dark designs); labels are 9.5pt and footers 9pt. Color/grayscale checks are digital proofs, not physical printer or community-member certification.

### Standalone designs and full-page sample screenshots

The design picker contains no personalization panel or reading-direction selector. Each artwork/symbol/heading combination is a separate card, including the plain versions and both Jai Bhim variations. All documents use left-to-right page layout; existing drafts with old artwork preferences migrate to the equivalent card without changing profile content.

The twenty base concepts remain in `collection.json`; ten alternate-version definitions live in `variants.json`. The 49-template print revision defines their final compositions in `repair.json`. A version owns its header art and salutation, so its thumbnail, live preview and PDF remain consistent. Gallery subtitles identify variant families and distinguish Ganesha Ivory — Illustrated from Ganesha Ivory — Gold linework.

Run `python scripts/capture_unique_template_samples.py` to create `output/unique-template-samples/`. It contains all 47 available designs with filled fictional English male/female profiles, every full A4 page as a 1200-pixel-wide PNG, complete PDFs, an overview image and a browsable `index.html`. Generated screenshots stay local and are excluded from Git.

### 49-template audit revision

The exact audit fixture is `scripts/review_fixture.py`. The review pack lives in `output/template-repair/index.html`; its before PDFs are frozen inputs and must not be overwritten. Once that local pack exists, double-click `Open Template Review.html` to review it offline without a running server. Generated review files are not included in a fresh clone. `docs/template-repair/completion-checklist.md` contains the 49-row implementation checklist, and `asset-manifest.json` records artwork replacements and unverified provenance. All 47 active revised sample exports use two pages, with every source value retained. No source profile strings were shortened. Nikah Nocturne and Christian Cathedral Ivory are retired from new selection; all 49 original IDs still restore existing private drafts without changing their selected design.

```sh
python scripts/export_repaired_review.py
python scripts/check_repaired_documents.py
python scripts/measure_repaired_print.py
python scripts/build_repaired_gallery.py
python scripts/build_template_review_pack.py
RUN_EXPORT_TESTS=1 python -m pytest -q
```

The gallery uses `artwork/repair-gallery-v2/` (188 active male/female English/Hindi samples, plus 8 compatibility samples). Template 48 supports an explicitly selected `?paper=light` export treatment; this does not change the saved design. The final review documents distinguish completed engineering checks from pending independent iconography, language and artwork-rights review.
