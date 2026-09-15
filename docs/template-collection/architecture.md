# Template collection architecture — plan before implementation

Inspected 15 September 2026: normalized Profile/field registry, visibility filtering, all template metadata, Jinja document markup, Chromium pagination, PDF-to-preview/image rasterization, canonical thumbnail generator, embedded fonts, image normalization/crop and static assets.

## Reuse

Keep the version-2 normalized profile, optional/hidden section semantics, guest drafts, upload validation, CSRF-protected endpoints, isolated Chromium worker, PDFium preview/image pipeline and desktop/mobile editor. Existing 19 designs remain available. A single complete fictional sample drives all new thumbnails through the actual document engine.

## Refactor

Add a collection registry built from independent layout presets, artwork packs and optional cultural headers. Eleven reusable layout families provide real information-architecture variation; their typography, ordering, photo mode and safe zones are metadata. One section renderer consumes the normalized document, not hard-coded profile fields. Existing designs retain their original rendering branch.

New collection documents use an explicit measured A4 paginator. Page one has its chosen header/decoration; later pages have only a compact continuation header and rule. Whole sections move together; a section larger than a page splits at semantic boundaries, then at measured text boundaries if necessary. Type has a readable floor and does not shrink to meet an arbitrary page count.

## Artwork

Generate only named decorative and portrait assets after the specs exist. Master PNGs stay in the project; PDF and preview WebPs are optimized derivatives. Artwork occupies defined header/edge/footer zones and never a body-text background. Optional sacred headers are separate assets; no generated lettering is used. Verified Ik Onkar/Khanda/cross/Dhamma-wheel Unicode symbols use proper fonts. Jain Ahimsa uses non-symbolic architecture/lotus rather than an unverified sacred emblem.

## Explicit user choice

A presentation object stores the header-art choice and document direction, independent of profile sections. Each design allows only its supported header choices. The named devotional designs may show their named art as their own design default after explicit selection; Sikh/Christian/Buddhist symbols require a separate opt-in. Selecting None removes the header asset and reclaims its space. No surname, religion, caste, city, gender or language is used for design selection or filtering.

## Language and photos

Keep English/Hindi UI; add script-aware embedded Noto fonts for the requested Indic scripts and Urdu. Use auto-direction on values and explicit RTL document support. No fixed-height heading boxes. Preserve the user's approved photo crop and use contain-fit within decorative frames, with optional native face-detection assistance when available.

## Batches and acceptance

Batch 1: five contemporary designs; stabilize layout/pagination and review all five. Batch 2: six creative/regional designs. Batch 3: nine cultural designs, with individual visual review of every generated sacred portrait. Each design gets short/medium/long, no-photo, missing-section, Unicode and A4/thumbnail tests. Check colour/grayscale output, page-two restraint, readable type and exact preview/PDF correspondence. Emulated mobile/desktop browsing covers selection and header changes. Physical print and community-member review cannot be claimed from automated checks.

Reference sources are documented separately. Specs precede implementation and prompts precede image generation.

## Preview capacity recovery

The existing two-slot renderer remains bounded. A temporary busy preview response includes Retry-After; the client retries at most three times with backoff and an overall timeout. A changed draft cancels obsolete retries, and a failed thumbnail cannot overwrite a complete full preview. Other renderer or validation failures remain explicit errors.
