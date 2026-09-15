# Standalone template versions — 15 September 2026

The personalization panel and reading-direction selector have been removed from both design steps. Every previously configurable artwork/heading combination is now a separately selectable card. Documents use left-to-right page layout; Unicode content remains supported.

There are 49 selectable designs: 19 original designs plus 30 collection versions. Ten lightweight definitions in `app/biodata_templates/variants.json` inherit their base layout, styling and artwork pack:

- Braj Lotus (without the Krishna figure)
- Ivory & Saffron (without Ganesha)
- Heritage Parchment (without Rama)
- Phulkari · Ik Onkar
- Phulkari · Khanda
- Cathedral · Cross
- Dhamma · Wheel
- Equality Blue (without the Ambedkar portrait)
- Ambedkarite Blue · Jai Bhim
- Equality Blue · Jai Bhim

Existing draft and backup choices are migrated to the equivalent card before the obsolete options are reset. This migration is idempotent and implemented in both browser restore and server validation. Selecting a card always renders that card's fixed version; a previous design's artwork cannot change it.

## Validation

- Full test suite with actual Chromium exports: **109 passed**.
- Desktop and mobile: all 49 cards present, no personalization controls in either design step, selection survives reload.
- Existing no-art, Khanda and Jai Bhim drafts restored to their equivalent new IDs in the browser.
- All 49 designs rendered with complete fictional male and female English sample profiles; every resulting page was captured. Name, education, custom details and contact text were checked in the PDFs.
- 49 distinct first-page image hashes confirm that each design has its own visual output.
- 120 optimized gallery thumbnails generated for the 30 collection versions, covering both sample people and both interface languages, under the new immutable `collection-gallery-v2` path.

## Screenshot folder

`output/unique-template-samples/` contains:

- 49 numbered design folders.
- **226 full-page PNG screenshots**, 1200 pixels wide, including continuation pages.
- **98 complete PDFs**, one male and one female sample per design.
- `index.html`, with sample-person switching and links to every page.
- `all-designs.jpg`, showing all 49 designs at a glance.
- `manifest.json`, listing every generated file.

Run `python scripts/capture_unique_template_samples.py` to reproduce the folder. It uses the same pagination functions as the application export worker. Generated review files stay local under the ignored `output/` directory; no personal draft data is used.

The original specification and QA documents record the earlier configurable collection. This note supersedes their personalization and RTL product behavior.
