# Imported biodata designs

The app now has 19 selectable designs: five existing themes and fourteen distinct designs from Figma file `ZdHTDaQEF4JXKcir1B7xsj`. The two identical Blossom frames are one selectable design. Background-only frames and unrelated reference screenshots are not additional templates.

| App design | Figma node | Current background source |
|---|---|---|
| Peach Floral | 1:2 | Supplied Basic flower 4 clean PNG |
| Lavender Floral | 1:85 | Supplied Basic flower 3 clean PNG |
| Blue Botanical | 1:168 | Supplied Basic flower 6 clean PNG |
| Amber Botanical | 1:254 | Same clean blue artwork, alternate typography and accent |
| Slate Classic | 1:339 | Original Figma composition |
| Blue Frame | 1:425 | Original Figma composition |
| Floral Wreath | 1:508 | Supplied Basic 1 clean PNG |
| Garden Corners | 1:591 | Supplied Basic 2 clean PNG |
| Blossom | 1:676, duplicate 1:756 | Original Figma composition |
| Blossom Serif | 1:837 | Original Figma composition |
| Ganesha Ivory | 1:965 | Supplied Hindu Traditional 2 clean PNG |
| Ganesha Rose | 1:1048 | Supplied Hindu Traditional 3 clean PNG |
| Ganesha Maroon | 1:1137 | Original Figma composition, clean texture over fixed portrait frame |
| Ganesha Festive | 1:1217 | Supplied Hindu Traditional 1, frame removed as described below |

The user's `biodata template/` folder is retained unchanged. Reference images with embedded names, details or portraits are layout references only. In particular, the nominally blank Basic 3, Basic 4 and Basic flower 5 images still contain the reference portrait; they are not served as backgrounds. Exact file paths and SHA-256 hashes for imported clean images are recorded in `app/static/artwork/local-provenance.json`. Original Figma source hashes are in `app/static/artwork/provenance.json`.

## Content and privacy

Layouts receive the same normalized sections, labeled rows and prose as the original themes. A selected illustration cannot populate religion, caste, family details or other profile fields. Hidden fields are removed independently on the client and server before export. No source reference person's details are imported into demo data.

All 19 gallery thumbnails render fictional Aarav Mehta data with `Reference/Dummy photo.png`. A compressed copy is `app/static/artwork/demo-portrait.jpg`. The clearly labeled empty-state preview and explicit sample action also use this portrait. `empty_profile()` always has an empty photo list. Once a user enters their own details, the illustrative sample disappears; exporting never implicitly substitutes sample content or a sample photo.

## Layout adaptations

Original colors, artwork and English font families are retained. Fixed-position Figma text becomes flowing content, so optional fields, multiple entries, long prose and custom sections work. Photos are separate images, with the primary portrait beside the first visible section and extra photos in a gallery. A section that fits on a page stays together; oversized sections can continue across pages. PDF uses A4, a full-bleed repeating background and internal text insets to protect decorative edges. The screen preview remains a continuous document; export calculates pagination.

English fonts are self-hosted Inria Sans, Figtree, Poppins, Tiro Devanagari Sanskrit and Merriweather, with their included OFL licenses. Hindi uses the existing Noto Devanagari face first to preserve shaping and reliable PDF text extraction. Browser WOFF2 and export TTF files are local. The PDF embeds only the selected design's additional fonts and JPEG background; JPEG avoids Chromium converting textured WebP artwork into excessively large lossless PDF images.

## Rebuilding assets

Generated assets ship with the app; production startup requires no Figma connection or asset generation.

```sh
# Only needed when reconstructing the original Figma layer composition:
python scripts/build_figma_backgrounds.py
# Apply reviewed local clean sources after the Figma base:
python scripts/import_local_template_assets.py
# Generate all public gallery thumbnails with the supplied dummy portrait:
python scripts/build_template_previews.py
# Verify English and long Hindi output separately; never overwrites thumbnails:
python scripts/check_figma_templates.py
```

`figma.json` owns presentation metadata; `models/designs.py` owns CSS/font mapping. After changing presentation tokens, run `write_browser_styles()` from that module. Font-fetch scripts are maintenance tools, not runtime dependencies. Expiring Figma download URLs are not part of the shipped code or asset manifests.

## Festive background edit provenance

Tool: built-in image generation/editing tool. Source: `biodata template/Boi data templates/Hindu tradition/Hindu traditional 1/Hindu Traditional 1-1.png`. Saved edited source: `app/static/artwork/sources/festive-frame-free.png`. The supplied original is unchanged. The frame-free result was visually checked and converted to the browser/print formats by the import script.

Final prompt:

> Use case: precise-object-edit. Edit the provided marriage biodata background. Remove ONLY the rectangular gold portrait frame in the upper right, including its glow, and seamlessly fill its former area with the same surrounding maroon textured paper. Preserve everything else exactly: canvas aspect ratio, outer ornamental corners, hanging bells, maroon texture, bottom flowers and diya, central Ganesha icon, Sanskrit text 'श्री गणेशाय नमः', and ornamental rule below it. Do not add any text, portrait, symbols, border or objects. This must be a clean printable background for dynamically overlaid biodata text. Keep all original composition and colors. Return a single full-page portrait image.

## Validation

`test_figma_templates.py` checks catalog/disclosure independence, oversized opening sections with three photos, and real PNG/JPG backgrounds. The existing real-PDF test parametrizes all 19 themes. `check_figma_templates.py` exports all 14 additions with both English and long Hindi fixtures, checking final entries and hidden-data exclusion. `build_template_previews.py` requires every gallery preview to fit on one page. `check_figma_browser.py` covers all-template switching with a photo, sample-photo isolation, category filters, six viewport widths, Hindi draft reload and actual PDF download.

Verified locally on 2026-09-14: all 59 tests passed with real Chromium exports enabled. All 28 English/Hindi fixtures passed (PDF sizes 123–600 KB, one to five pages depending on content). All 19 gallery previews fit one page. Browser checks passed at widths 320, 390, 768, 1024, 1440 and 1920 with no JavaScript errors; the landing/mobile-family/popup/export/legacy-draft regression also passed. Screenshots of supplied-background previews and the mobile/desktop gallery were visually inspected. Results describe this local Chrome environment, not testing on physical Android devices.
