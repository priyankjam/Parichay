# Editor refinements

The first step combines optional gender selection and English/Hindi language selection. The editor now has ten visible steps. Stable internal section IDs preserve saved progress and existing links; the former Language step redirects to the combined first page. Gender controls sample portraits. It does not print gender on the biodata. Older backups without this preference remain valid. Known demo-photo bytes can be replaced when switching gender; uploaded or cropped images are preserved.

Style preference and Design & preview share all nineteen templates, category filters and edge-to-edge document cards. When a draft is empty, these galleries use a clearly labelled, gender-aware sample that is never written into the user's draft. Once details are entered, previews use the included user data. The explicit sample-biodata action still imports sample details and a portrait into the draft.

Family uses the same labelled input grid as other details: father, mother and siblings. Existing multiline or long family text continues to use a textarea without losing content. Culture and birth details remain expanded and optional, with their existing visibility controls.

Interests use keyboard-accessible toggle buttons, a five-selection limit and a custom-interest input. Known options translate between English and Hindi. The existing plain-text data field and older custom interests remain compatible; older drafts with more than five interests retain their data and allow removing choices before adding more.

## Generated portrait

Built-in image generation was used. App asset: `app/static/artwork/demo-portrait-female.jpg` (600 × 750, optimized JPEG). Original: `app/static/artwork/demo-portrait-female-original.png`.

Exact prompt:

> Generate a photorealistic natural editorial portrait for a fictional sample profile in an Indian marriage biodata maker. One adult Indian woman aged about 28, warm medium brown skin, natural dark hair, gentle confident smile, looking at camera. Elegant understated ivory Indian kurta with subtle embroidery, small tasteful earrings. Head and upper torso, centered composition, generous room above head, vertical 4:5 portrait crop. Soft daylight, warm neutral softly blurred indoor background, realistic skin texture, polished professional portrait photography. No text, no watermark, no bridal veil, no wedding props, no excessive jewelry. This is a fictional demo portrait, not a real person. Save a usable image for the app.

## Verification

`python scripts/editor_refinements_check.py` covers gender persistence, sample-only gallery rendering, identical gallery inventories, full-bleed cards, family editing, expanded culture fields, five-interest selection, custom interests, Hindi, mobile widths, and preserving uploaded pictures when switching gender. `python scripts/live_preview_check.py` retains the automatic-update regression checks.
