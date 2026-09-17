# Parichay template revision — review handoff

The audit covered 49 original IDs. The selectable collection now contains **47 designs**: Nikah Nocturne (`craft-nikah-nocturne`, original 21) and Christian Cathedral Ivory (`craft-christian-cathedral-ivory`, original 22) were removed at the user's subsequent request. Cathedral · Cross remains a separate available design. Retired IDs remain readable for existing private drafts, with no automatic cultural-design migration.

## What changed

- Replaced the separate legacy print paths with one semantic document renderer and explicit composition settings for every original ID. Profile fields and user values remain in the normalized schema, separate from presentation.
- Reworked portrait placement, hierarchy, section treatments, decorative lanes, columns, frames and continuation headers. Typical portrait sizes are 36 × 48 to 41 × 55 mm; Modern Mono retains 45 × 60 mm.
- Raised body type to 11 pt, or 11.5 pt on dark designs. Labels are 9.5 pt; footers are 9 pt. Names are 30–32 pt. Long prompts stack above answers when their measured label exceeds two lines.
- Paginate using loaded fonts and measured content. Short education, career and family records stay together. Oversized answers can continue without reducing type or removing values. Optional balancing falls back safely when a large additional photo needs a full page.
- Removed text-area watermarks and full-page devotional composites. Ganesha linework, invocation text and decorative frames are now separate. Added native amber foliage, an open floral crest and restrained festive drapery/still-life. Simple arches, frames, textile repeats and symbols use native geometry or embedded-font glyphs.
- Refreshed the template picker samples, added honest variant subtitles, and provided an explicit light-paper PDF option for Ganesha Maroon. This option does not alter the selected design in the draft.

## Sample and page counts

The source fixture is `scripts/review_fixture.py`: the original fictional Aarav Mehta data, including both education records, career description and income, family, birth information, narrative, preferences, contact and Everyday life. It was not shortened. Before-PDF page counts and per-page extracted content match the original review; PDF metadata can differ between reproductions.

The original 49-design review contained 112 pages. The 47 designs that remain in the collection occupied **107 before pages and now occupy 94 pages**. Every active sample is two pages. All thirteen remaining former three-page samples now fit two pages, including 38, 39, 48 and 49. Their custom-section rows are preserved. Two pages is a result for this fixture, not a general hard limit.

## Validation evidence

- The complete automated suite passed, including real Chromium PDF/JPG/PNG exports, hidden-field handling, escaping, upload security and draft compatibility. The exact test log accompanies the pack.
- `validation.json`: 245 successful cases across all 49 compatible IDs — no photo, Hindi, long content, a single populated field, and multiple photos. Long-content cases include 12 education entries, a long unbroken email, long institution/company/location, long custom prompts and multi-paragraph answers. Values are compared before and after pagination, and overlapping rows are rejected.
- `print-geometry.json`: physical portrait dimensions, body/label sizes, preservation of complete sample education/career/family records, and no intersection between sacred figures and text.
- `pdf-metrics.json`: effective PDF text sizes after transforms, self-contained fonts/glyph programs with Unicode mappings, file sizes, and contrast against the rendered paper field. Chromium can emit variable fonts as Type 3 embedded glyph programs; these are not missing fonts.
- Revised sample PDFs are approximately 198–946 KiB. The smallest effective type is 9 pt (footer); body copy remains at least 11 pt. The lowest measured essential-text contrast against the sampled final paper is 5.49:1.
- Desktop and 360/390 CSS-pixel mobile preview checks passed without horizontal UI overflow or JavaScript errors. The picker contains 47 cards, the two removed cards are absent, both Ganesha Ivory subtitles are distinct, and light-paper export remains an explicit choice. Live preview rasterizes the actual exported PDF; print remains A4.

The pack includes every active before/after page as a 1200-pixel-wide PNG, full PDFs, a same-scale color gallery and its grayscale counterpart. These are digital proofs. They do not constitute a physical printer proof or a community-member certification.

## Artwork and remaining specialist review

`asset-manifest.json` maps source assets to retained artwork, new native vectors and Unicode text. Regional names are existing product labels, not claims of authenticated regional craftsmanship. No new religious symbol or invocation is inferred from profile data.

The following independent checks remain outstanding; they are not represented as complete:

- **12, 14, 16, 27 and 29:** the existing Krishna, illustrated Ganesha, Rama and Ambedkar subjects were retained provisionally. Final-size digital inspection checks rendering, silhouette and clearance; it does not certify religious/iconographic correctness or likeness rights.
- **46–49:** the existing line-emblem silhouette was traced into separate native SVG contours, with actual Unicode invocation text. The supplied wording **श्री गणेशाय नमः** is preserved. It appears in [Sanskrit Documents' Mangalacharanam text](https://sanskritdocuments.org/doc_ganesha/mangalAcharaNam.html), but an independent language-competent reviewer has not signed off on this product treatment. The source illustration's rights are also unverified.
- **Supplied artwork provenance:** rights/source records were not available for the reused imagery listed in the manifest. Their presence in the repository is not proof of permission. Noto/DM/Tiro font license notices remain bundled. New CSS/SVG ornamental geometry is original implementation work; it makes no cultural-authenticity claim.
- Physical paper/ink reproduction and independent accessibility/native-language editorial review remain release-review tasks. Digital grayscale and contrast checks are included.

## Files and reproduction

Open `index.html` to compare designs, filter by name, switch to grayscale, and open individual PDFs or full-size pages. `49-template-checklist.csv` accounts for every original ID, including the two removals. `after.zip` contains only the 47 active sample PDFs, plus feedback instructions.

The frozen `before/` inputs must not be overwritten. Run the scripts documented in the repository README to regenerate the revised exports, regression evidence, gallery and comparison pack. Review assets contain only fictional sample data and stay in the ignored local output directory. This revision has been verified locally; it has not been deployed to PythonAnywhere by this task.
