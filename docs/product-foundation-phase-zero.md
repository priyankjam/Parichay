# Parichay — Product Foundation / Phase Zero

14 September 2026 · v0.1 · Decision proposal, not validated strategy

“Parichay” is a working name taken from this workspace. Naming, trademark and domain availability have not been checked.

## Decision in brief

Build toward **the easiest way to create a marriage introduction you and your family feel comfortable sharing**. Start with people actively preparing a biodata, including parents helping an adult child, in an English/Hindi pilot. Deliver a good document without requiring an account. Treat accurate content, appropriate disclosure, recovery and dependable exports as the core product.

Do not commit to a national platform, ten templates, hosted profiles or AI before observing users. The first investment should be four weeks of discovery and prototype evaluation. Authorize MVP implementation only when users can complete the core task, understand disclosure, and prefer the output to their current alternative.

The strongest current hypothesis is not “more beautiful templates.” It is **less uncertainty between being asked for a biodata and feeling ready to send it**. That uncertainty includes what to say, what to omit, whether family members agree, whether the file looks right, and whether private information will travel farther than intended.

### Evidence and limits

- **Observed:** facts about publicly accessible pages, with sources beside the claims. A published product promise is evidence of positioning, not proof of implementation quality.
- **Assumption:** a planning input that has not been established, such as team size or launch language.
- **Hypothesis:** a claim to test with behavior, artifacts or transactions.
- **Recommendation:** a proposed decision and its rationale.

This document includes current desk research. No interviews, usability sessions, purchases, mobile audits, network inspections or exported-file comparisons have been performed. Competitor traffic, revenues, customer counts and claimed privacy guarantees are unverified. No market-size estimate is presented as fact. Cultural examples below are research prompts, not findings about populations.

## 1. Precise problem definition

When someone is asked to send a marriage biodata, they must turn personal and family information into a socially appropriate introduction that recipients can easily open, understand and forward. The creator may lack writing or design confidence, may be working on a phone, and may need another person's agreement. Existing documents can be difficult to update and impossible to recall once distributed.

The problem has four layers:

| Layer | User's uncertainty | Desired outcome |
|---|---|---|
| Functional | What should I include, and how do I format it? | Accurate, readable document without layout work |
| Emotional | Does this represent me without sounding boastful or impersonal? | Confidence and dignity |
| Social | Will my family and the receiving family understand it? | A useful introduction acceptable to the people involved |
| Disclosure | Who will receive these details after forwarding? | Deliberate sharing with understood limits |

**Hypothesis:** resolving these layers together produces more value than accelerating data entry alone. Test their relative importance; do not assume privacy or personality is everyone's leading concern.

Our unit of success is a usable introduction, not a complete database record or a marriage outcome. A sparse biodata can be complete for its intended purpose. We should not claim that better design improves match prospects without evidence.

## 2. Jobs-to-be-done

| Trigger | Job | Evidence to seek |
|---|---|---|
| “Send your biodata” arrives | Help me create something presentable quickly | Last creation timeline, tools and interruptions |
| Parent prepares an adult child's introduction | Help me include what matters without needing technical help | Actual helper involvement and correction cycles |
| Creator dislikes a conventional format | Help me sound like myself while remaining appropriate | Edits made to an existing document |
| Family disagrees about details | Help us choose what appears without redoing the document | A real disagreement and its resolution |
| Different recipients need different detail | Help me make a shorter or more private version | Files with different contacts, income or birth details |
| Job or location changes | Help me update once and regenerate accurately | Number of old copies and rework performed |
| Recipient gets a file | Help me read, save and forward it easily | Opening behavior on a real phone |
| Someone wants to stop circulating | Help me stop future access where possible | Expectations about recall, expiry and deletion |

**Recommendation:** prototype creation, correction and recipient reading together. A fast editor fails if the recipient receives an unreadable image or a document the subject does not endorse.

## 3. User segments and initial focus

Segment primarily by role, urgency, device, language and assistance needs. Age, region and religion do not reliably determine desired style.

| Segment | Initial role | Product implication |
|---|---|---|
| Adult making their own biodata | Primary pilot participant | Writing guidance, control over sections, good mobile output |
| Parent helping an adult child | Co-primary pilot participant | Plain language, large controls, clear save/recovery and review |
| Sibling/cousin helping | Secondary creator | Easy corrections and safe handoff; no assumption of ownership |
| Recipient, including older relatives | Essential test participant | Readability, familiar file formats, no forced signup |
| Low typing confidence or constrained device | Cross-cutting test group | Low input burden, forgiving interaction and recovery |
| Broker or bureau | Research-only commercial segment initially | Learn frequency and approval needs without building a CRM |

**Recommendation:** recruit English/Hindi users first because a focused bilingual pilot is more testable than twelve simultaneous language launches. This is an operational assumption, not a judgment of market size. If recruitment access and paid demand favor another language, change the pilot pair before implementation.

Include self-employed people, people outside salaried careers, remarriage situations, varied family structures and users who omit cultural fields. Do not make metro professionals the aesthetic default for everyone.

## 4. Core user journeys

| Journey | Main path | Alternatives and recovery | Privacy and measurement |
|---|---|---|---|
| First creation | See sample and price → choose language → add basic details → choose optional sections → review → export | Skip sections; enter approximate age instead of birth date; proceed without photo; exit to saved draft | No profile values in analytics; measure start, review, export and time |
| Parent/helper creation | Identify helper role → enter adult subject's information → show subject a review → correct → export | Subject disagrees; remove fields; switch contact person; continue without account | Helper role is not proof of subject consent; measure correction burden in research |
| Disclosure review | See exactly what export includes → remove sensitive details → inspect result → confirm | Back to editing without losing changes; remove an entire section | Hidden values must be absent from exported content, not merely invisible |
| Change design/update | Reopen draft → change job or design → inspect pages → export new file | Missing local draft → import an editable backup; incompatible template → offer supported layout | Preserve data independently of design; show export date if user chooses |
| Share/receive | Export PDF or images → system share sheet or download → recipient opens | Sharing unsupported/cancelled → save file and explain manual attachment; retry export | A share-sheet launch is not proof of delivery; downloaded files can be forwarded |
| Recover/delete | Reopen saved draft or retry after failure → verify recovered content | Storage unavailable → explicit warning and backup option; delete draft with clear scope | Explain deletion affects this browser, not files already sent |

**Recommendation:** start with a useful document skeleton and a default design. Defer the full template gallery until users have content. This reduces early decisions; test against template-first onboarding rather than treating it as settled.

On mobile, use a clearly labeled form/preview switch rather than a tiny persistent split view. Desktop can show both. Progress should describe the next useful action, never penalize omitted optional fields.

## 5. India-specific cultural complexity map

The product needs flexible representation, not a rules engine that decides what a community should disclose.

| Research lens | Possible variations to investigate | Architectural response |
|---|---|---|
| North India | Hindi, Punjabi, Urdu and other languages; family contact conventions; optional lineage/birth information | Independent language, contact and optional cultural modules |
| South India | Tamil, Telugu, Kannada and Malayalam; initials and naming order; different astrology labels and calendars | Full display-name control, extensible labels, script-aware wrapping |
| West India | Marathi/Gujarati terminology; native place, family business or family deity details where requested | User-added fields and sections; no compulsory cultural preset |
| East India | Bengali/Odia and other languages; education descriptions, household introductions and birth information | Flexible narratives, regional editorial review and font testing |
| Northeast India | Many distinct linguistic, ethnic and religious contexts; local scripts and English usage | Recruit separately across contexts; never use a single “Northeast” template as coverage |
| Migration and diaspora | Different hometown/current city, currencies, education systems, time zones | Separate residence and origin; currency/unit-aware values |

These examples deliberately do not establish prevalence. Region cannot stand in for language, religion, economic circumstances or personal preference.

For religious and non-religious coverage, ask participants what they actually used:

| Participant context | Optional topics to investigate, never infer |
|---|---|
| Hindu | Whether any gotra, deity, birth-chart or observance details matter |
| Muslim | Whether denomination, practice, language or family introduction is relevant |
| Sikh | Whether religious practice or any community detail is wanted |
| Christian | Whether denomination, parish/church or practice should appear |
| Jain | Whether sect, dietary practice or community detail is wanted |
| Buddhist | Whether any religious affiliation or practice should appear |
| Interfaith | How to describe more than one tradition without forcing a single choice |
| Non-religious | How to omit these sections completely while keeping a polished document |

**Recommendation:** language and design choice must never activate sensitive fields automatically. Offer an optional “Culture and traditions” section with examples and editable labels. Avoid fixed father/mother assumptions, compulsory gender categories, complexion fields, caste ranking or “desirability” scores. Support family descriptions without requiring disclosure of bereavement, estrangement or other private circumstances.

## 6. Competitive landscape

Snapshot researched on 14 September 2026. Prices below are advertised offers, not completed Indian checkouts or guarantees of final tax-inclusive charges. Similar brand names are not evidence of affiliation.

| Competitor/category | Public evidence | Strategic implication |
|---|---|---|
| Canva | Dedicated Hindi marriage-biodata page, editable templates and multilingual creation guidance. [Canva](https://www.canva.com/hi_in/banaye/marriage-shadi-biodata/) | Design breadth and brand familiarity are real substitutes. We must test task completion and document adaptability against Canva, not assume generic tools fail. |
| MakeBiodata | Advertises free, watermark-free PDFs, no registration and Hindi/English AI fill. [Pricing](https://makebiodata.com/price.html) | Free, guest access and AI are already claimed in-category. Its claims do not establish output quality or privacy implementation. |
| Bio Data Bannao | Advertises ₹49–99 per download, three days of free edits, ₹499/three months for unlimited downloads and an ₹11 AI review. [Pricing](https://biodatabanno.com/pricing) | Low-price exports, bureau offers and AI review already exist. Long-term editing entitlement could matter; validate frequency. |
| Hindi Biodata | Advertises ₹50/design, watermark-free PNG and PDF. [Pricing](https://hindibiodata.com/pricing) | Hindi plus image export is not an unoccupied niche. |
| MarriageBiodataMaker.in | Hindi page advertises free watermarked output and displays ₹39 templates. [Hindi offering](https://marriagebiodatamaker.in/marriage-biodata-in-hindi) | Distinguish free creation from free usable output when benchmarking price clarity. |
| BiodataPDF.app | Search-indexed page advertises ₹19 PDFs, six templates, no signup, on-device data, autosave and Hindi/English support. Direct page retrieval failed in this research pass. [Product page](https://www.biodatapdf.app/?template=modern) | Even the combined local-first/low-cost proposition is already advertised; implementation remains unverified. |
| ShubhLekha | Advertises Hindi labels, automatic horoscope, free PNG/WhatsApp and premium PDF from ₹99. [Hindi offering](https://www.shubhlekha.in/marriage-biodata-hindi) | Distinguish translated labels from translated content. Optional astrology is a competing feature, not a reason to infer belief. |
| Android Marriage Biodata Maker, Aqua App Studio | Listing advertises ten languages and a ₹50 PDF/share unlock for 31 days; says uninstalling removes locally saved data. [Google Play listing](https://play.google.com/store/apps/details?id=com.aquaappstudio.biodatamakerglobal) | Regional language breadth and local persistence already exist as claims. Recovery expectations deserve explicit testing. |
| Shaadi.com | Official help describes structured profile search and filters. [Search help](https://support.shaadi.com/support/solutions/articles/48000953830-how-can-i-search-for-profiles-on-shaadi-com-what-are-the-search-options-available-) | Competes for profile preparation and distribution within matchmaking. A dedicated standalone export tool was not verified here. |
| BharatMatrimony | FAQ describes registration, profile creation, privacy settings and horoscope functionality. Some procedural details may be legacy. [FAQ](https://www.bharatmatrimony.com/faq.php) | Study existing profile reuse with consent; do not infer a current document-export feature from profile functionality. |
| Jeevansathi | Privacy policy describes profile information collection and visibility of some non-identifying profile details to visitors. [Privacy policy](https://www.jeevansathi.com/privacy-policy) | A private document workflow is a different distribution choice. Do not imply matrimonial platforms have no privacy controls. |
| Resume.io | Official UK builder advertises PDF/TXT downloads for free templates. India checkout pricing was not established. [Builder](https://resume.io/uk/builder) | Benchmark structured entry and preview/export fidelity; do not conflate resume.io with similarly named domains. |
| Greetings Island | Invitation example offers image/PDF/print/share and a one-time design purchase alongside subscription pricing. [Example](https://www.greetingsisland.com/preview/invitations/opulence/202-37542) | Benchmark recipient experience and purchase clarity; invitations have different layout/content demands. |
| Word, Google Docs, copied PDF, relative or local designer | Substitutes to investigate in interviews; no comparative task trial completed | “Ask someone who already knows how” may be the strongest incumbent. Test against actual behavior, not websites alone. |

**Audit still required:** for six direct tools and three substitutes, record exact entry-to-export steps, signup gates, final prices, editing entitlements, field flexibility, photos/cropping, languages versus labels, mobile behavior, privacy notices and observed requests, export fidelity/size, sharing and errors. Use the same short, long and Hindi synthetic profiles. Audit Canva, a resume builder and an invitation tool for adjacent interaction lessons. Record unknowns explicitly.

Review app-store complaints and independent discussions for recurring issues, separating publisher posts from customers, locale and product version. No systematic complaints analysis or traffic-source audit has yet been completed. Search visibility in this session is not market share.

## 7. Competitor weaknesses: evidence versus hypotheses

**Observed offer limitations:** some providers gate usable exports, restrict edit periods, or price per design. Those constraints are visible in the pricing sources above. They may be reasonable business choices; only user evidence can show whether they cause dissatisfaction.

**Hypotheses to test:** excessive formatting work in general editors; family disagreement not supported by existing workflows; difficulty understanding disclosure; preview/PDF differences; brittle long regional-language content; uncertain recovery. We have not established that every competitor—or any specific competitor—fails these tests.

**Recommendation:** build an evidence-based advantage claim: “X of Y participants completed unaided, with zero omitted/extra fields and readable exported pages.” Avoid “all competitors are outdated” and unsupported security superiority.

## 8. Market gaps and opportunity

Potential gaps, in priority order:

1. **Confidence before sharing.** A final review that makes content and disclosure understandable may reduce embarrassing mistakes. Validate whether mistakes actually delay sending.
2. **Person and family both represented appropriately.** Guidance and editable family sections may help without requiring real-time collaboration. Observe actual negotiation.
3. **Consistent output across variable content and scripts.** This could earn trust through repeated experience. Benchmark exports before calling it a gap.
4. **Dependable guest editing.** Recovery, backup and clear device boundaries may be more valuable than an account prompt. Test return visits.
5. **A paid offer proportionate to an occasional task.** Test a transparent one-time purchase with useful free output.

There is no defensible TAM from this desk research. Annual weddings are not equivalent to annual paying biodata creators: people may not use biodatas, households may create one jointly, many use free tools, and the same person can make many exports.

Build a bottom-up model: qualified annual creation occasions × reachable share × creation completion × paid conversion × net revenue per purchase. Estimate each separately using keyword-demand research, observed cohort conversion and transactions. Report ranges and overlap rather than a single impressive number.

**Recommendation:** pursue this first as a focused consumer utility. A large platform business remains an option contingent on distribution and economics; it is not an established outcome.

## 9. Strongest possible positioning

**For adults and families preparing a marriage introduction, Parichay helps you create a clear, personal biodata you feel ready to share—without struggling with formatting or including details you would rather leave out.**

Why this position: it centers the task and its emotional outcome, includes both traditional and modern users, and can be proved through completion, recipient readability and disclosure understanding.

“India's best” should be our internal quality ambition, not an unsubstantiated launch claim. “Privacy-first” must be supported by observable defaults and data handling. Neither is a moat by itself.

Potential durable advantages are a consented, synthetic rendering test corpus, editorial knowledge from diverse user research, well-tested localization, trustworthy support and accumulated distribution. Competitors can copy individual controls. We should not hoard sensitive profiles as proprietary training data.

## 10. Proposed value proposition

**A marriage biodata that feels like you. Ready to share.**

Supporting promises to validate:

- Add your details once; change the design without starting again.
- Include what matters to you. Leave out what does not.
- Create without an account; understand where your draft is saved.
- Get a readable PDF and images for sharing.

Do not promise “five minutes” publicly until measured end to end, including correction and export. Do not promise control after forwarding a file. Brand voice should be calm and practical, with human-reviewed Hindi copy. A premium feel should come from readability and care, not ornate decoration or an assumption that English signals quality.

## 11. Product principles and changes to the brief

Keep: sensitive fields optional; no forced signup before value; data separate from presentation; strong regional-language foundations; good output on modest devices; no stereotyping, identity fabrication, surveillance or matchmaking scope creep.

Change these assumptions:

| Original ambition | Recommended change | Why |
|---|---|---|
| Ten to twenty initial templates | Three excellent layout families for prototype/alpha; expand only after evidence | Template count multiplies layout and language testing before value is proven |
| Style selection before information | Default design, with an early sample and later full selection | Fewer decisions before progress; test whether it improves completion |
| Every section never breaks across pages | Keep short entries together; allow deliberate splitting of long narratives with continuation treatment | A section longer than a page cannot remain intact without clipping or unreadably small text |
| “Private link” plus “disable download” as privacy | Explain link possession/access rules and limits; never promise screenshot or forwarding prevention | Prevents false confidence |
| Personalized OpenGraph preview | Generic metadata for private links; personal previews only with explicit opt-in | Messaging previews can expose information before access checks |
| Share with three people to unlock | Remove sharing quotas | Creates pressure to distribute intimate information for a reward |
| Privacy controls as premium upsell | Basic exclusion, deletion and secure defaults free; basic access control included whenever hosting exists | Safety should not depend on willingness to pay |
| Voice/AI in core ambition | Promote only after observing typing or writing bottlenecks | Adds cost and identity-error risks before benefit is demonstrated |
| Completion as field fullness | Completion as ready for the chosen purpose | Optional fields must remain genuinely optional |
| Latest URL solves old PDFs | State it updates the hosted page only | Previously downloaded documents cannot be remotely corrected |

## 12. Master biodata information architecture

This is a conceptual model, not a frozen database schema.

| Entity | Proposed content and rules |
|---|---|
| Profile envelope | Schema version, stable local ID, revision and timestamps; distinguish subject from helper; account owner only if cloud accounts later exist |
| Personal | Display name, optional preferred name, age OR birth date, height with unit, residence, native place, languages, optional nationality/marital status |
| About | Introduction, values, lifestyle and interests; all optional and editable |
| Education[] | Stable entry ID, qualification, institution, specialization, optional year |
| Career[] | Profession/business, organization, role, location, narrative; optional income with currency and period |
| Family[] | Relationship label, optional name, occupation and narrative; support chosen family/guardian/free text |
| Culture | User-selected facts and editable labels; no auto-inferred identity |
| Astrology | Optional birth time/place and user-entered terms; reference canonical birth date rather than duplicating it |
| Contacts[] | Contact person, relationship, channel and value; distinguish subject's phone from helper's |
| Partner preferences | Optional respectful narrative and selected factual preferences; no ranking or matching engine |
| Photos[] | Local asset reference, order, crop/rotation metadata, optional caption; do not couple crop to identity data |
| Custom sections/fields | Stable IDs, user label, typed value, order and visibility; plain text initially, no executable rich content |
| Document configuration | Template/version, language(s), typography preset, section order and explicit included field IDs |
| Future share configuration | Access policy, expiry and revocation separate from document data; server enforcement |

**Recommendation:** one canonical profile feeds a filtered document model, then preview and exports. Hidden information must be removed before rendering. A later online version needs its own explicit disclosure selection; export inclusion must not imply online publication.

Use stable field keys with localized labels; preserve names as typed. Separate UI language, document-label language and user-authored content language. Do not translate a person's name without confirmation. Design for repeated entries and Urdu directionality now, but only advertise languages actually tested.

For age, accept an entered age with an “as of” date, or derive it from a supplied birth date. Do not require exact birth date to display age. Blank is not equivalent to zero or “not applicable.” Clearing a value must remove it from the output.

Custom fields are fundamental, but initial types can be text, multiline text, number and date. Add more only when real examples justify them. Templates declare supported scripts and layout capabilities; unsupported choices should offer a compatible alternative without discarding information.

## 13. MVP hypothesis

**Hypothesis:** with their information available, adults and parents can create an accurate, acceptable English or Hindi biodata on their own phone within ten minutes, without an account or design help, and successfully obtain a file they want to send.

Proposed MVP after validation:

- Guest creation, editable local drafts, honest save status, recovery and explicit deletion.
- English and human-reviewed Hindi UI/labels/content rendering; no automatic translation claim.
- Optional modular personal, education, career, family, culture, astrology, about, interests and contact sections; custom fields/sections.
- Repeatable education/career/family entries and simple move-up/down section ordering.
- Three layout families: restrained editorial, warm contemporary and opt-in traditional styling without mandatory religious imagery.
- One primary photo with local crop, rotate and compression; no-photo layouts equally polished.
- Live preview, design switching, disclosure review, A4 PDF and per-page images.
- Device sharing where supported, clear download/manual attachment fallback.
- Editable backup export/import if local persistence cannot safely satisfy return-editing needs; file clearly identified as containing private details.
- Minimal privacy-conscious operational measurement and accessible support.

Payments enter a controlled beta only after useful output and demand are demonstrated. Guest creation does not require a full account backend. Local-only profile handling is a proposed design direction until rendering feasibility is tested.

## 14. Explicit MVP exclusions

| Excluded | Reconsider when |
|---|---|
| Hosted profiles, PINs, expiry, revocation and accounts | Users repeatedly need persistent links and understand their limits; authorization/deletion design is ready |
| Family invitations and real-time collaboration | Observed correction loops cannot be served by review and local editing |
| AI writing, interview, transcription and translation | A measured bottleneck justifies consent, correction UI and inference cost |
| Twelve-language launch, bilingual layout and Urdu release | Native review, fonts and content stress tests pass per locale |
| Photo galleries, background cleanup, horoscope uploads | Actual demand justifies layout/storage/security complexity |
| Ten-plus templates, freeform canvas and template marketplace | Additional choices improve success enough to cover maintenance |
| Broker CRM, bulk creation, white labeling, public API | Consumer execution is stable and separately validated recurring demand exists |
| Viewer identities, exact locations and fingerprinting | Not planned; inconsistent with the product's trust objectives |
| Match discovery, chat, ranking and compatibility scores | Requires an explicit change of company strategy, not routine roadmap expansion |

Exclusion does not mean the schema cannot evolve. It means we do not build infrastructure solely to satisfy imagined future demand.

## 15. Major product risks

| Risk | Early signal | Response / decision owner |
|---|---|---|
| Solving aesthetics when effort lies in gathering information | Users cannot finish even with a simple prototype | Product: add useful examples/checklist; measure prepared and unprepared users separately |
| Parent and subject goals conflict | Subject rejects an otherwise completed document | Research/Product: individual interviews then consensual paired review; prioritize subject agency |
| Optionality becomes overwhelming | Repeated hesitation in section selection | Design: suggested minimal starting document and progressive disclosure |
| Premium visual taste excludes other users | Preference varies sharply across cohorts | Design: test diverse styles with equal readability, not a single “modern” ideal |
| Universal promise exceeds launch coverage | Repeated unsupported script or family-structure requests | Product: state supported scope plainly and prioritize evidence-led expansion |
| Recipients prefer existing files | Creators like preview but do not send output | Research: test the received PDF/image, not only the editor |
| Free alternatives satisfy the job | Little observable preference or payment demand | Founder: narrow differentiation or keep a lean utility; do not manufacture complexity |

## 16. Privacy risks and launch requirements

**Recommendation:** default to no public profile and the least disclosure needed for the current export. Treat photos, family facts and custom text as potentially sensitive even when not classified that way by a particular statute.

| Risk | Proposed control | Residual limitation |
|---|---|---|
| Shared-device draft exposure | Offer “remember on this device” versus session-only; visible deletion and save scope | Local storage is not protection from another device user or compromised browser |
| Helper publishes without subject agreement | Clear helper-role explanation and subject-review step; counsel reviews consent basis before cloud features | A checkbox cannot prove authorization or resolve coercion |
| Hidden fields leak in export or telemetry | Filter before rendering; inspect PDF text/metadata and requests; no form replay | Third-party scripts and diagnostic tooling require ongoing review |
| Photos expose location metadata | Remove metadata in derived exports; minimize retained originals | Visible background can still identify a place |
| Files are forwarded | Plain-language export warning, deliberate contact selection | Files and screenshots cannot be recalled |
| Future bearer link is forwarded/guessed | Random tokens, optional additional access check, rate limits, expiry and revocation | Possession is access unless another check is enforced |
| Private details leak through previews/caches | Generic link metadata, correct cache behavior, authorized asset requests | Social-platform caching requires explicit testing |
| Deletion promise exceeds actual deletion | Document draft, job, log, backup and payment retention separately | Legally retained transaction records may have different deletion rules |

Exact proposed export copy: **“This file includes the details shown in the preview. Anyone who receives it can save or forward it. Remove anything you do not want shared.”**

Exact local-save copy, only if implementation supports it: **“Saved in this browser on this device. Clearing browser data can remove your draft.”** When saving fails, say **“Your changes could not be saved. Keep this page open and download a backup.”**

**Current legal evidence:** final DPDP Rules were notified in November 2025 with staggered commencement: some immediately, Rule 4 after one year, and a further group after eighteen months. The final text—not the earlier draft—supports this distinction. [MeitY final Rules, rule 1](https://www.meity.gov.in/static/uploads/2025/11/53450e6e5dc0bfa85ebd78686cadad39.pdf)

Before launch, Indian counsel must map the applicable Act provisions and Rules to the actual launch date, processing purposes and architecture; review helper/subject consent, information about relatives, eligibility/minors, processors, cross-border processing, retention, incidents, notices and payments. Do not interpret phased commencement as an exemption from all current obligations. This document makes no legal compliance certification.

Use an adult-only product policy subject to counsel's eligibility review; do not collect identity documents just to create a draft. Complete abuse reporting and subject-removal procedures before hosted profiles. Basic deletion, field omission and access protection must not be premium-only benefits.

## 17. Technical risks and provisional architecture

Do not freeze a stack before testing document output. The highest-risk boundary is consistent PDF/image generation with Indian scripts on modest devices.

**Recommendation:** a TypeScript web application with a versioned data model and a single document-layout definition is a reasonable default. Static/cacheable acquisition pages should load independently of the editor. Use a modular monolith if a backend becomes necessary; no microservices, Redis or full account database without measured need.

| Decision | Preferred starting point | Alternative and trade-off | Gate before commitment |
|---|---|---|---|
| Guest persistence | IndexedDB for structured drafts/assets, explicit save errors | Server drafts improve device continuity but introduce accounts, consent and ongoing storage | Recovery, storage-denial, quota and browser-clear tests |
| Rendering | Time-box comparison of client-side document generation and isolated Chromium rendering | Browser generation minimizes transmission but may cost memory or sacrifice fidelity; server rendering adds per-job cost, queues and personal-data processing | Hindi shaping, embedded fonts, selectable text, pagination, photos, peak memory and latency |
| Preview | Same filtered document/layout model as export | Shared components alone do not ensure identical rendering engines | Compare actual artifacts, not architecture claims |
| Cloud if justified | PostgreSQL, private object storage and explicit authorization | Managed services lower operations effort but impose cost, processor and migration constraints | Data-flow review, deletion test and cost model |
| Localization | Locale dictionaries, native review, fonts loaded per required script | Shipping all fonts is simpler but bloats mobile transfer | Test long text and font-loading failures |
| Analytics | Allowlisted events without values or field labels entered by users | Session recording speeds debugging but exposes private details | Inspect telemetry payloads; prohibit sensitive values |

If server rendering wins, disclose the upload before export and stop claiming “never leaves your device.” Isolate rendering jobs, disallow arbitrary remote fetches, avoid logging content, and set measurable cleanup of temporary data including failure cases. If neither path meets privacy and quality requirements, revise scope before launch rather than silently rasterizing all text.

Support long sections with continuation labels and deliberate page breaks. Never shrink text indefinitely to force one page. A photograph's resolution should be assessed against its placed print size, not by a generic “HD” label.

Planning effort: reserve roughly 5–8 engineer-days for a rendering comparison after prototype validation; this is an estimate assuming an experienced engineer and synthetic content. Measure cost per successful export, including retries and compute memory. Schema migrations are manageable with explicit versions; replacing a layout engine after many templates is expensive, which is why the rendering gate comes early.

## 18. Business-model hypotheses

**Recommendation:** useful free creation/export plus an optional, clearly priced one-time design upgrade. Do not start with a consumer subscription. Frequency and willingness to pay have not been established, while advertised low-cost/free alternatives constrain the proposition.

Test ₹49, ₹99 and ₹199 as experimental offers, not settled pricing. Show the price and exact entitlement before effort is invested. An initial paid hypothesis is a premium design pack with repeat exports/edits of the same profile for a clearly specified 90-day period; test the period and avoid “one download only” frustration. Basic readability, safe omission, deletion and correction of our export failures remain available without an upgrade.

Illustrative arithmetic, not a forecast: 10,000 qualified visits × 30% starts × 60% usable-export rate × 5% purchasing among exporters × ₹99 = **₹8,910 gross revenue**. At ₹199 the same unchanged funnel would yield ₹17,910, but price may change conversion. This shows why cheap exports alone do not justify expensive acquisition or a large team.

Compute contribution after applicable taxes, payment fees, refunds, render/storage costs and support. Evaluate incremental paid acquisition against contribution per acquired visitor, not checkout price. Do not assume annual retention or subscription lifetime value for an episodic task.

If free output wins adoption but premium conversion stays weak, first evaluate whether a small sustainable business is viable. A separately validated professional offering could follow; it is not a rescue assumption. Avoid selling profile data or introducing intrusive advertising to patch poor economics.

## 19. Growth hypotheses

1. **Useful search content:** detailed examples and creation guidance for supported languages and actual questions. Test a small number of human-reviewed pages. Index public educational content only, never private profiles. Search rank and demand are unverified here.
2. **Recipient discovery:** an optional discreet product credit may introduce the tool to future creators. Compare with no credit; never require referrals or retain recipient lists.
3. **Trusted helpers:** siblings, community volunteers and local service providers may recommend a reliable tool. Test referrals without paying people to circulate somebody else's personal information.
4. **Return editing:** an accurate editable backup or later saved profile can make updates easy. Treat return editing as service value, not a reason to manufacture habitual usage.

Start with useful search content plus consensual pilot referrals. Do not spread effort across every social channel. A recipient may not need a biodata for years; forwarding is not necessarily a viral growth loop. Measure voluntary source attribution and aggregate referral conversion, without embedding unique identifiers in exported personal documents.

## 20. Research required before coding

Four-week discovery proposal; no full application implementation during it.

| Work | Output | Decision unlocked | Owner |
|---|---|---|---|
| Competitor task audit | Comparable mobile recordings, price notes and synthetic exports; unknowns explicit | Demonstrable differentiation | Product + design |
| Interviews and artifact walkthroughs | De-identified evidence tagged by role/language/device | Essential sections and first audience | Research lead/founder |
| Cultural/editorial review | User-requested field vocabulary and translation issues | Schema and launch-language scope | Research + paid language reviewers |
| Prototype sessions | Task outcomes, errors, privacy comprehension and output preferences | Whether/how to build MVP | Design + product |
| Privacy/data-flow workshop | Processing inventory, retention proposal and counsel questions | Local/server boundary and launch requirements | Engineering + privacy/legal |
| Business discovery | Actual past spending and permissioned offer test design | Free/paid entitlement hypothesis | Founder |
| Demand research | Keyword clusters, qualitative channel access and cautious bottom-up model | Acquisition priority | Growth |

**Build gate:** two prototype rounds resolve all critical disclosure/data-loss misunderstandings; at least 80% of the final round completes core tasks without facilitation; results are examined separately for parents and self-creators. A small study is directional, so do not claim population-level validation. If it fails, repeat the affected flow rather than building more features.

Keep a decision log: hypothesis, evidence, counterexamples, confidence, decision and trigger for reconsideration. A quote is evidence of one experience, not its prevalence.

## 21. User interview plan

Begin with 24 adults: eight self-creators, eight parents/helpers, four recent recipients and four brokers/local document helpers. Recruit for a real creation or receiving event in the past six months or an imminent need. Include people who abandoned a tool and people who were content with their existing approach.

Across overlapping quotas, seek at least eight Hindi-preferred participants, eight using budget/older Android devices, eight from tier-2/3 settings, and meaningful gender and family-structure variation. Recruit beyond the founder's network. Do not pretend this covers India. Expand toward 50–100 conversations across the five regional research lenses and the religious/non-religious contexts in section 5 as expansion decisions arise; disclose sampling gaps.

Run 40–50 minute sessions in the participant's preferred language. Offer a consistent research honorarium, provisionally ₹500–1,000, independent of praise or product use. For 24 sessions that is ₹12,000–24,000 before recruitment, translation and researcher time; this is a planning allowance, not a vendor quote.

Ask about actual behavior:

1. Tell me about the last time someone asked for or sent you a biodata.
2. What happened first, and what did you do next?
3. Who typed it, chose the format, checked it and paid?
4. What information was hardest to find or decide on?
5. Which details did you remove or change, and why?
6. Did anyone disagree? What happened afterward?
7. What tool or helper did you use? What did it cost in money and time?
8. If comfortable, show a redacted example of something you changed.
9. How did you send or receive it? What happened when it was opened?
10. Did you make another version or update it later? How?
11. Who did you expect could see it? Did anything surprise you?
12. What would have made you stop using that tool?

Interview parent and subject independently before an optional joint review. Do not expose one person's answers to the other without permission. Do not collect original unredacted biodatas by default; participants may describe or redact them. Get explicit recording permission and propose deleting recordings within 30 days after synthesis, retaining de-identified findings only under the agreed research policy.

Synthesize by job and observed friction: incident → consequence → workaround → frequency evidence → proposed decision. Record disconfirming cases. Ask willingness-to-pay questions only after actual spending history; stated enthusiasm is not a purchase.

## 22. Prototype testing plan

Two rounds of eight participants, approximately half parents/helpers and half self-creators, spanning English/Hindi. Prefer fresh participants for round two. Add six recipient reading sessions, including older readers. Use synthetic information; participants should not need to expose their own intimate details to test controls.

Tasks: create a basic profile; skip culture/astrology; add a family detail and custom field; change a design; remove income/contact from one export; inspect a two-page document; recover after interruption; correct a job; and explain who can see the exported file. Recipients open the PDF/image, find education/contact details and explain forwarding expectations.

Compare output against each participant's actual alternative where possible. Counterbalance task order and use equivalent content. Ask separately whether the document represents the subject appropriately and whether it is easy to read; do not equate ornamental preference with task success.

Prototype representations of save/export must be labeled as simulations. A clickable prototype cannot validate file generation, persistence or offline operation. Follow successful flow testing with a bounded technical feasibility test before MVP commitment.

Provisional pass criteria: at least 80% unaided completion in the final round, median core task under ten minutes with details provided, no unresolved critical disclosure misunderstanding, and at least six of eight willing to use the resulting design for the tested purpose. Report individual failures and cohort differences, not just a combined percentage.

## 23. Preliminary success metrics and quality gates

**North-star candidate:** weekly creators with a usable exported biodata they intend to share. Export generation is observable; actual WhatsApp delivery generally is not. Use voluntary post-task/next-day research to estimate sharing, and report that estimate separately. Do not label share-button clicks “successfully shared biodatas.”

| Metric | Definition / provisional target |
|---|---|
| Start → usable export | Export-ready sessions / sessions with a meaningful first edit; ≥60% in beta is a working threshold, not an industry benchmark |
| Time to first usable file | Median ≤10 minutes, p90 ≤15 with details available; include errors/retries; report unprepared users separately |
| Export reliability | ≥99.5% valid completed exports / export attempts in a stable beta measurement window; distinguish user cancellation and unsupported input |
| Content integrity | Zero critical omitted, clipped or unintentionally included fields in supported regression fixtures and release-blocking beta reports |
| Disclosure understanding | ≥90% in a dedicated comprehension study; any severe misunderstanding triggers design review |
| Recovery | All supported interruption fixtures preserve committed changes; explicitly surface failures to persist |
| Recipient usability | ≥90% task success locating requested details in the pilot reading study |
| Mobile performance | Working budgets: landing LCP <2.5s, INP <200ms, CLS <0.1 at p75 when enough field samples exist; also test actual budget Android hardware |
| Output weight | Provisional standard PDF budget ≤2MB for two pages/one photo; readable images; evaluate exceptions rather than silently degrading output |
| Paid conversion/economics | Purchases / users exposed to an offer; contribution per qualified visitor, refunds and support minutes |

All numeric thresholds are proposed release targets, not measured results. A few hundred users cannot substantiate a 99.5% long-run reliability claim; report counts, uncertainty and synthetic tests separately.

Allowlisted events: creation_started, section_step_completed, preview_opened, export_requested, export_ready, export_failed, share_invoked, draft_recovered and purchase_completed. Include only necessary technical dimensions such as supported locale, template ID and coarse device category. Never send names, photos, exact birth dates, income, contact values, custom labels or free text. Avoid sensitive field-level analytics; study confusion through consented research instead.

Before beta, test every supported template against short and long names, empty sections, long paragraphs, twelve education entries, many custom fields, no photo, rotated/large input photo and mixed English/Hindi. Use Tamil and Urdu as architecture probes without claiming production support. Inspect font embedding, extracted PDF text, page boundaries and actual opening on Android/iOS/Windows/macOS. Exercise storage denial, reload, network interruption, render timeout, retry, cancellation and duplicate payment callbacks if payments are present. Keyboard, screen-reader, zoom and contrast checks are release requirements, not later polish.

## 24. Recommended 12-month roadmap

Assumption: founder/product lead, one product designer/researcher, two experienced engineers and part-time language, QA/security and legal support. This is a capacity scenario; a solo build requires reduced scope or more time. Months begin at approved kickoff, not a fixed release promise.

| Window | Work and expected output | Gate / response if unmet |
|---|---|---|
| Month 1 | Interviews, artifact audit, competitor comparison, cultural map and two prototype rounds | Revise positioning/flow if completion, disclosure or preference fails |
| Month 2 | Rendering/localization feasibility, data flow, schema and three template specifications | Do not commit to renderer or privacy promises until artifacts pass |
| Months 3–4 | Guest MVP, English/Hindi, local recovery, photo crop, preview, exports; private alpha with 25–50 users | Resolve data loss, privacy and export defects before expansion |
| Months 5–6 | Beta with 200–500 users; recipient testing, accessibility/performance, transparent payment experiment and support | Expand only with usable completion, stable outputs and credible economics |
| Months 7–8 | One additional language if demand supports it; focused SEO/content; improve highest-abandonment steps | Native review and renderer tests per language; no templated national rollout |
| Months 9–10 | Choose one: hosted private links, better repeat editing, or input assistance, based on observed demand | Hosted links require authorization, retention, abuse response and legal/security gate |
| Months 11–12 | Consolidate reliability and distribution; evaluate paid bureau pilot only with independent demand | Marketplace/voice/collaboration remain options, not promised deliverables |

Each month review completion, recipient success, support load, export integrity and contribution economics. Stop adding features if output or disclosure safety degrades. If users do not meaningfully prefer the product after two focused iterations, revisit the segment/problem rather than adding AI or more templates.

## 25. Ten most important unanswered questions

| Question | Why it changes the plan | Best next evidence |
|---|---|---|
| 1. Is the dominant pain gathering information, writing, formatting or family agreement? | Determines core interaction and whether AI matters | Recent-event interviews and artifact timelines |
| 2. Who decides a document is ready: subject, parent or helper? | Determines ownership, review and consent design | Separate interviews and consensual paired review |
| 3. Does our output outperform the real alternative enough to switch? | Tests the central business premise | Counterbalanced prototype and recipient trials |
| 4. Which initial language/region is reachable and underserved? | Determines editorial investment and launch focus | Recruitment access, competitor audits and demand data |
| 5. Which information do people actually want to omit for different recipients? | Determines disclosure controls versus version complexity | Redacted real versions and observed editing tasks |
| 6. Do users understand and accept local-only draft storage? | Determines recovery, backup and account priorities | Return-session/recovery tests and comprehension checks |
| 7. Can exports meet script, pagination, memory and privacy requirements? | Determines architecture and viable promises | Measured rendering comparison on real devices |
| 8. What will people actually pay for when good free alternatives exist? | Determines whether the consumer business can sustain itself | Transparent offer tests and completed purchases |
| 9. Do recipients reliably generate new creators at low cost? | Determines whether distribution can scale | Aggregate opt-in attribution and cohort experiments |
| 10. Can we acquire and support users profitably without exploiting personal data? | Determines company scale and channel choice | Bottom-up contribution model using observed funnel/cost data |

The immediate decision is to run discovery against these questions. The next deliverable should be an evidence ledger and tested prototype brief—not a homepage, a national feature roadmap treated as a commitment, or a claim that this strategy is already validated.
