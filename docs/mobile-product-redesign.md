# Mobile product redesign — audit before implementation

Date: 15 September 2026. Evidence: the 28 English screen/state captures in `output/mobile-ux-review`, both contact sheets in `tmp/qa/mobile-redesign`, and live reproduction of the landing → editor → sample → forms → preview → actual PDF download journey. The landing hero has since been redesigned and is preserved.

Priorities: P0 = data loss / blocked completion; P1 = structural or high-frequency friction; P2 = contextual friction; P3 = polish. No P0 data-loss defect was established by this audit; the existing storage and rendering services are retained.

| Screen/state | Current problem | Why it hurts | New mobile pattern | Priority |
|---|---|---|---|---|
| Landing | Strong visual identity leads into dense editor chrome | The first tap feels like entering a different, more difficult product | Preserve landing; lightweight Start with local-draft reassurance | P1 |
| Gender & language | Header language, section dropdown, ordinal, section fraction, meter and readiness compete above two choice groups | Navigation mechanics precede the user's first decision | Compact Start; person and language choices, no persistent progress until continuing | P1 |
| Style preference | 19 fictional previews precede entering any useful details | High-effort decision is repeated at the end | Remove early design stage from mobile sequence; deep links map to the final gallery | P1 |
| Scrolled style gallery | Sticky selector plus filters consume viewing area | Detailed 150px thumbnails become harder to evaluate | One sticky filter row below compact header; horizontal large-card gallery | P1 |
| Empty personal form | Full schema, visibility actions and repeated headings precede input | Empty fields imply requirements; destructive choices interrupt entry | Name, age, height, city; Add detail sheet | P1 |
| Personal/contact filled | Each label has Remove, even for name | Creation and export visibility are mixed | Uncluttered labels; optional field menu; visibility only in Review | P1 |
| Personal fully expanded | All optional groups form one long page | Users must search through fields unrelated to them | Materialize selected fields only; phone/email in Add detail | P1 |
| Education & career | Long open entry forms and repeated record actions | Reviewing existing records requires scrolling through inputs | Summary cards; dedicated full-screen entry editing; one record at a time | P1 |
| Family | Three generic inputs with hide/remove controls | No distinction between a family member and text field | Parent/sibling cards, meaningful empty add actions; dedicated editor preserves legacy text | P1 |
| Culture & birth | All sensitive fields appear as empty inputs | Optionality copy competes with a required-looking schema | Two optional groups; add only chosen details | P1 |
| About/interests | Generic form heading stack, hide/remove actions | Personal expression feels administrative | One introduction, writing prompts, five-choice chips and custom interest | P2 |
| Custom About section | Nested schema and repeated label/value/remove rows | Advanced flexibility dominates ordinary writing | Custom-section summary cards; focused custom editor | P2 |
| Field removed | Dashed input still occupies space; Add back beside label | Users must understand retained-but-excluded state while typing | Review inclusion checklist; preserve values without displaying a destructive control per field | P1 |
| Section hidden | Entire editable form remains under a hide checkbox | Unclear whether information has been deleted, hidden or saved | Review inclusion surface with explicit Included/Not included status | P1 |
| Photos empty | Large upload card sits under duplicated progress | First meaningful action arrives late | Clear portrait placeholder and Choose photo action | P2 |
| Photos filled | Adjust, Replace and Remove are permanently scattered under thumbnail | Weak hierarchy; accidental destructive action risk | Dominant portrait, Edit and Replace; removal in photo options sheet | P1 |
| Photo crop | Floating dialog, three sliders and constrained portrait | A complex precision task is trapped in a small surface | Full-screen crop with Cancel/Done, accessible sliders, rotation | P1 |
| Design & preview | Two narrow columns, another progress hierarchy and optional Spotlight | Selecting one design requires understanding multiple modes | One mobile gallery, ~1.2 large cards visible, selected state and contextual footer | P1 |
| Spotlight | Parallel gallery mode with tiny filmstrip | Adds a mode without clarifying the user's task | Retire mobile Spotlight; retain desktop version | P1 |
| Full preview | Inset desktop modal consumes space around the A4 page | Content is small despite a dedicated viewing task | Full-screen preview, fit-width/zoom, actual page count and navigation | P1 |
| Review/download | Same form chrome; success is far below the first viewport | Completion looks like more work | Ready state with actual page image, compact edit list and inclusion control | P1 |
| Download formats | Consent and format explanations add a long inline subsection | User must find the action after reviewing | Short format sheet; explicit consent; button loading and retry state | P1 |
| Download success | Page remains at the same form heading, with success deep below | No clear endpoint or next sharing action | Dedicated completion state with file name, size, page count, Share and Download again | P1 |
| Share help | Instructions appended under a long export screen | Fallback is detached from the action | Contextual sharing sheet following completed download | P2 |
| Draft menu | Small anchored dropdown, technical backup labels | Hard to tap and decode on phones | Draft options sheet; Save a backup / Restore from backup / Language / Privacy / Delete | P2 |
| Privacy | Dense paragraphs in centered floating dialog | Important answers require reading technical prose | Question-led bottom sheet: creating versus sharing; honest local-storage limitations | P2 |
| Sample confirmation | Centered desktop dialog amid dense Start | The example action competes with starting a real draft | Secondary draft-menu action with clear replace/cancel confirmation | P2 |
| Delete confirmation | Equal-width floating actions and tiny dismissal | Destructive action needs stronger consequence hierarchy | Mobile confirmation sheet, prominent Cancel and separated red Delete | P2 |

## Architecture and screen jobs

Mobile below 768px: Start → Basics → Education & work → Family → About you → Optional details → Photos → Design → Review. Desktop/tablet step order and presentation remain unchanged. One mobile renderer consumes the shared normalized profile, validation, autosave, thumbnail/PDF service and export actions. Mobile UI metadata (chosen empty optional fields, height unit and explicitly completed/skipped stages) stays in the local draft envelope, never in exported profile data.

Entry editing is a full-screen sub-flow. Section navigation, add detail, format selection, options and privacy use short sheets. Preview and crop use full-screen surfaces. Native dialogs provide focus containment; history entries make browser Back dismiss a surface before leaving a stage. Inputs remain single-column and retain draft values when navigating or cancelling an editor.

Review is where users control what appears in the document. Skipping an empty optional section does not invent content; skipping a populated section retains its data, with inclusion controlled explicitly in Review.

## Evaluation plan

Automated browser checks plus heuristic persona walkthroughs, not a claim of moderated research with actual participants. A: professional, basic modern flow. B: parent, family/culture/photo and share. C: low-confidence creator, skip optional, correct an error, reopen section, refresh and download. Check 320/360/375/390/412/430 widths with short/tall heights, tablet and desktop regression captures, keyboard focus, touch emulation, history, refresh, offline/renderer failure, upload/crop, actual PDF and native-share fallback. Physical screen-reader/phone validation remains a separate device check.


## Implemented presentation

The mobile shell, renderer and state surfaces are in `app/static/js/mobile-product.js` and `app/static/css/mobile-product.css`. `editor.js` supplies the existing profile, storage, validation, media and document services. Desktop keeps its original renderer. No dependency or persistence service was added.

- Nine stages replace the earlier ten-stage sequence; legacy style deep links open the final mobile design gallery.
- The Start screen has no progress chrome. Editing has one ordinal/progress indicator, one save status and an accessible section navigator. Review and success have completion-specific layouts.
- Personal details start with four inputs. Optional fields are added from a sheet; height converts between centimetres and feet/inches. Education, work, family and custom sections use summary cards and focused editing.
- About includes prompts and up to five standard/custom interests. Culture and birth are optional, initially empty groups. The cropper and paginated preview use the full viewport, with keyboard-operable sliders/zoom/navigation.
- The gallery uses one horizontal row of large A4 thumbnails and sticky category filters. There is no separate mobile Spotlight stage. Loading personal pages use a skeleton instead of another person's profile.
- Review shows the actual exported page, compact edit links and inclusion choices. Hidden values remain in the local draft and are stripped before transmission. A profile with all details excluded cannot download an empty file.
- Format selection, explicit processing consent, generation feedback, retry, successful file download and sharing are separate states. Share invokes the native file-sharing API when supported, with contextual WhatsApp instructions otherwise.
- Browser history handles sheets, entry editing, full preview and crop. Deletion reindexes visibility and optional-field metadata. Legacy sibling text with blank lines retains the original row indices when a card is edited. A cancelled photo replacement retains the original image.
- The optional `parichay:analytics` event hook covers the mobile funnel. It has no transport or tracking identifiers and allows only event, surface, stage number and template ID. No entered values are logged. An analytics consumer must be configured separately if actual reporting is wanted.

## Verification results

- `scripts/mobile_product_check.py`: complete fresh-draft journey, height conversion, optional contact, refresh, education/family/custom entries, five interests, actual photo upload/crop, template switching, real preview, hidden contact exclusion, PDF download and share fallback. Passed without browser errors.
- `scripts/mobile_product_regression.py`: all nine stages at 320×568, 360×800, 375×667, 390×844, 412×915 and 430×740. Additional chrome/reflow checks covered all six widths with heights 568, 667, 740, 800, 844 and 915. Visible enabled mobile action targets meet the practical 44px target. Sheet focus containment, names, Back/Forward, immediate reload, offline save, entry deletion, crop cancellation and invalid-photo handling passed.
- The same regression compared original and current desktop/tablet rendering at 768×1024, 1024×1366 and 1440×900 for Personal, Family and Design. Eight captures had zero changed pixels; one had two rasterisation pixels of difference. Desktop controls and layout remained unchanged.
- `scripts/mobile_product_recovery.py`: simulated local-write failure and recovery; renderer failure/retry; excluded sensitive content absent from preview requests; real three-page PDF and multi-page JPG archive; failed image export and successful retry; native-share handoff (API simulated, no message/file sent); backup, confirmed deletion and restore. Passed without browser errors.
- `scripts/mobile_product_review.py`: a parent creating a daughter's biodata through family, education, work, a photo, optional-section skip, design, review, PDF and sharing. Captures 33 English screens/states, including the preserved landing hero, and verifies the all-excluded empty-export guard.
- `python -m pytest -q`: 38 passed; 26 opt-in rendering cases skipped. The browser journeys above independently exercised the live renderer. No backend changes required rerunning the entire opt-in rendering matrix.
- The live landing CTA handoff to Start and its privacy-safe funnel event were verified separately.
- Mobile text colours and input boundaries were checked numerically. Low-contrast empty-state/file metadata and input outlines were strengthened; the input outline now exceeds 3:1 against its white field. Existing focus outlines were retained. This is a targeted contrast/semantics check, not a claim of a complete WCAG certification.

Viewport tests use a fixed real-PDF fixture to keep geometry comparisons deterministic; the separate creation/recovery/review journeys use the production preview/export endpoints. Motion is suppressed for screenshots, and reduced-motion rules were exercised. The shortened on-screen keyboard viewport and native sharing were simulated. Physical Android/iOS keyboards, TalkBack/VoiceOver speech output, system share sheets and real participant usability sessions were not available in this environment.

## Persona walkthroughs

These are expert walkthroughs backed by browser interactions, not recruited-participant findings.

| Persona | Tasks examined | Result and remaining validation |
|---|---|---|
| A — 28-year-old professional | Start with own details, convert height, add education/work, write an introduction, pick interests/design, preview and download | The complete route passes. Early design selection and repeated visibility decisions have been removed. Real-user completion time has not been measured. |
| B — 58-year-old parent | Choose daughter, enter family/education/work, add a portrait, skip optional culture, review and share | The parent route passes. Family cards and full-screen crop controls have 44px-or-larger practical targets. Confidence and readability on a physical budget Android device still need participant/device validation. |
| C — lower digital confidence | Skip empty sections, correct invalid age, jump back to edit, refresh, recover a failed save/download and restore a backup | Values are retained and each failure has a local explanation and next action. Browser Back dismisses the current surface before leaving creation. Comprehension of local backup/privacy copy still needs real-user testing. |

Final screenshots: `output/mobile-product-review/index.html`. Captures use fictional information and isolated browser storage; the user's own draft was not read or changed.
