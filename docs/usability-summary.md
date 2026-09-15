# Usability evaluation — final summary

**Implemented and retested on the running app.** Six independent simulated journeys covered the three personas on their primary and secondary devices. All completed creation, photo crop, preview, work-city correction, PDF download and draft recovery. These are expert simulations, not interviews or evidence of human completion time.

## Biggest problems and changes

| Before | After | Why it helps |
|---|---|---|
| Latest typing disappeared on immediate refresh in 5/5 attempts. | IndexedDB writes start immediately; 5/5 refreshes and a tab-close test retain the latest edit. | Saving is independent of delayed preview rendering. |
| Browser Back changed the form behind an open preview. | Back dismisses preview; Forward and visible return work predictably. | The screen and browser history now agree. |
| Enlarged text clipped desktop navigation; pinch zoom hid mobile actions. | Enlarged text uses the existing compact navigation; zoom no longer masquerades as a keyboard. | Users retain access to every section and action. |
| Successful download left sharing offscreen; fallback downloaded another identical file. | Visible success, identifiable filename, native file-sharing hand-off or persistent WhatsApp instructions. | The user can find and attach the intended file. |
| Photo errors appeared below the viewport; small-photo warnings vanished. | Focused recovery messages, persistent crop-quality warning and safe Replace. | Users can recover without deleting a good photo first. |
| Nineteen designs appeared before any personal details. | Three starting designs, with the full catalogue later. | Fewer early decisions, with safe experimentation retained. |
| Parent choice did not change “your details” instructions. | Subject-specific personal headings and clearer family/education wording. | Reduces uncertainty about whose information to enter. |
| Units, privacy, birth details and preview controls required inference. | Persistent height examples, explicit income guidance, birth-date shortcut, Next/Done behavior and labeled zoom/return. | Actions and inputs better match the task. |

All six original severity 3/4 findings are resolved within the tested browser conditions. The full findings table, root causes, inferred think-aloud notes and individual statuses are in [the detailed report](usability-personas.md).

## Persona and device outcomes

- **Young professional, 390px/desktop:** modern design, optional culture skipped, personality and interests included; editing and template changes preserve data.
- **Parent, Hindi 360px/tablet:** daughter-specific guidance, family and birth/community fields, traditional design, named PDF and WhatsApp fallback.
- **Lower-confidence user, Hindi 320px/412px:** complete basic flow with photo, visible recovery and labeled preview controls; less initial design choice.

Small and large mobiles retain direct section navigation and a preview popup. Tablets use the compact flow. Normal desktop keeps stationary header, steps and preview while the form scrolls. At 200% text, compact navigation replaces the clipped sidebar.

## Verification

- **59 tests passed**, including real PDF/image exports, all 19 themes, Hindi pagination, privacy filtering, validation and security.
- **Six final persona journeys** produced real PDFs with no JavaScript errors. Native sharing payloads were inspected; unsupported sharing displayed instructions.
- **308 standard editor checks**, **220 section checks at 200% text**, all-template switching, **24 landing checks**, zero failures in the product UI contrast scan.
- Safe five-photo replacement, immediate tab close, Back/Forward, long Hindi, storage exhaustion, offline editing and failed-export retry passed.

## Remaining risks

Cold landing-to-form time under 400kbps/300ms latency and 4× CPU throttling fell from 17.38s to 15.53s in single runs; it remains slow and needs production/device measurement. This is a partial performance improvement, not a benchmark.

Recruit real users to validate comprehension, hesitation, assistance needs and the ten-minute target. Physical Android keyboards, camera/gallery selection, TalkBack/VoiceOver, native Hindi wording, iOS Safari and actual WhatsApp sending/receipt still require hands-on testing. Local drafts remain vulnerable to browser-data clearing/eviction and simultaneous editing tabs. Horoscope document attachments remain outside the current product scope.
