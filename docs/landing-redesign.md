# Landing page redesign

Preserve: Paper & Plum, local fonts, fictional examples, real A4 template renders,
English/Hindi, honest privacy explanation and guest creation.
Improve: direct marriage-biodata proposition, product visibility, mobile document
size, header hierarchy, interaction, contrast and visual rhythm.
Remove/consolidate: overlapping sheets, six-card inventory, repeated benefits,
abstract CTA copy, repeated large serif headings.

Narrative: clear hero with editable sample → compact reassurance → visual three
step journey → same-profile design switcher → personality and bilingual example
→ plum privacy controls → finished-document outcome and creation CTA.

All demonstrations use fictional data. Hero edits are ephemeral, never submitted
or saved. Gallery uses public prebuilt samples; no PDF renders on landing.
Only English and Hindi are represented. Privacy copy distinguishes local drafts
from temporary server processing. No fabricated claims, reviews or dead legal links.

## Validation

- English and Hindi: editable sample, template selection and creation link,
  privacy toggles, language switch and reduced-motion mode.
- Full-page screenshots inspected at desktop, tablet and mobile; automated
  overflow/image checks at 1440, 1024, 768, 430, 390, 360 and 320px.
- Corrected a min-content grid overflow at 320px and a tablet heading line break.
- Text contrast checks meet AA thresholds; labelled inputs, named buttons,
  keyboard activation and visible focus verified. This is a focused check,
  not a formal accessibility certification.
- No landing-page API/PDF jobs. Lower images lazy-load; JS uses native DOM only.
- Python suite: 38 passed; 26 optional export integration tests skipped.

QA scripts: `scripts/landing_redesign_check.py` and
`scripts/landing_accessibility_check.py`. Screenshots: `tmp/qa/landing-redesign/`.

## Editorial hero refinement

The hero now returns to a brochure composition at the user's request: “Your
story. A beautiful beginning.”, clear marriage-biodata copy, one primary CTA,
and two softly layered real document samples. The ephemeral form and color
controls were removed. English uses existing 650px WebP artwork (56 KB combined);
Hindi uses the corresponding Hindi samples. Other product demonstrations remain.
Responsive QA passes in both languages at all seven widths; 38 Python tests pass.

## Premium sample refinement

Rear sample now uses Warm Indian with an arched female portrait. Sheets are
staggered with a gap between their headers, replacing the overlap that covered
the rear portrait. The dense botanical asset was replaced with sparse generated
plum/champagne linework (`hero-couture-linework.webp`). Source PNG is retained.
`hero_portrait_check.py` checks five points across each portrait against browser
hit-testing at 1440, 768, 390 and 320px. All pass; both language layouts also pass
seven-width QA. Caption clearance increased for larger document displays.

## Modern Indian Wedding Editorial hero

Hero-only art direction: “Your story, beautifully introduced.”, deeper plum type,
restrained CTA treatment, a small vector thread motif (under 1 KB), softer paper
shadows and a larger primary Peach Floral sample beside Blossom. Both selected
backgrounds and portraits remain intact. Sample education/institution and career/
company content was restored using the compact public-hero presentation; normal
user exports are unchanged. Tablet uses a dedicated 45/55 composition.

Validation: English/Hindi, seven widths (320–1440), keyboard controls, text
contrast, reduced motion, loaded assets, no overflow or landing PDF requests.
Portrait-area hit-testing confirms both faces stay unobstructed at four widths.
Lower landing sections and navigation are preserved.

## Final materiality and mobile pass

The repeated hero brief prompted a focused refinement: dominant primary paper
(56% desktop / 59% mobile), smaller secondary, unobstructed portraits, subtle
paper-edge layers and low-opacity grain. The same thread motif and chosen floral
templates remain. Hero rules are now consolidated in `static/css/hero.css`; old
editorial override blocks were removed from `landing.css`.

Both language variants pass seven-width visual/interaction checks, contrast and
keyboard checks, reduced motion, and portrait-area tests. No render API requests
are made by the landing page. Header and lower sections were not redesigned.

Fuller brochure samples: restored native place, mother tongue, education year,
work location, About Me and partner preferences in both fictional profiles.
Increased body/heading sizes and moved content higher into the clear center of
the supplied floral backgrounds. All four English/Hindi renders remain one A4
page; exported images were visually checked for floral/text clearance.
