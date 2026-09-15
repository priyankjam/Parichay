# Biodata template contract

## New collection: shared layouts and artwork packs

The twenty `craft-*` designs use `collection.json`, `layouts.json` and `artwork-packs.json`. Extend these registries instead of adding a separate Jinja document for each design. `app/services/collection.py` arranges normalized semantic sections; `collection-document.html`, `collection-document.css` and `collection-paginator.js` render all collection designs through the existing isolated export pipeline.

Start with a spec and protected art/body/photo zones. Reuse a layout preset, define section priorities and a compatible sacred-art whitelist, then supply inspected, optimized artwork. Never derive a design choice from personal identity fields. Keep None supported. Embedded font paths and artwork paths come from trusted metadata only.

Generation masters live outside static serving. Versioned artwork and gallery paths receive immutable caching: introduce a new directory version when publishing changed assets, and update `document-studio.js` to that gallery version. Regenerate thumbnails using `scripts/build_collection_gallery.py`; no separately mocked preview layouts.

See `docs/template-collection/architecture.md`, the twenty specs and `qa-report.md` for the complete extension and validation contract.

## Original collection

Five original themes are declared in `models/catalog.py`; fourteen illustrated designs are declared in `figma.json` and appended to the same catalog. Original styles live in `static/css/document.css`; illustrated themes use `static/css/figma-document.css` plus generated `figma-designs.css`. `templates/biodata.html` is the generic Jinja document; the client builds matching semantic markup in `static/js/editor.js`. Layouts never contain personal field names: they receive normalized groups of labeled rows and prose.

To add a design:

1. Add an ID/name/colors to `TEMPLATES`.
2. Add a `.theme-ID` rule family to the document stylesheet, using document tokens.
3. Keep all content dynamically sized. Do not fix section heights or use overflow clipping.
4. Keep whole sections together when they fit on a page. The renderer marks sections longer than the printable content area to start fresh and flow across pages. Keep headers with following text; never shrink fonts or clip arbitrary content.
   PDF uses zero page margins, a repeated full-bleed page background, and an internal text inset. Add any new theme background to the export body mapping as well as its screen tokens.
5. Test no photo, five photos, repeated education/career, long values, custom fields, Hindi and missing sections with real PDF/image rendering.
6. Inspect exported pages, extracted text, fonts and page boundaries. The app and PDF use the same fonts and document CSS.

Product UI styles belong in `app.css`. Avoid leaking them into document exports.

For illustrated themes, edit trusted `figma.json` metadata, regenerate styles with `models.designs.write_browser_styles()`, and provide a self-hosted WebP browser background and JPEG print background. Never accept arbitrary CSS, font paths or background URLs from profile input. See `docs/figma-templates.md` for source assets and rebuild order.
