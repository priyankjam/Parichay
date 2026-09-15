# Parichay hero — contemporary Indian paper craft

Scope: landing-page hero only. Navigation, routes, editor, and every section after the hero retain their existing implementation.

## Art direction

Inspected the three supplied saved Pinterest HTML files and their embedded primary images. All three saved pages contain the same primary green botanical reference; it informed the muted palette, organic stems and generous negative space. No reference illustration was copied into the application.

Original SVG systems: the architectural arch in `landing.html`, the branching botanical in `hero_botanical.svg`, and the woven arch tile in `hero-craft-textile.svg`. Comparison states use the hero's `data-art-variant` attribute. The architectural version won: its structure reads clearly while leaving space around the message. The larger botanical and textile variations are retained for reproducible comparison, not exposed as product settings.

The restraint comparison removed the third detail card and reduced the size and prominence of the foreground stem. Final composition: warm paper, a pale sage arch, two A4 sheets, a faint cropped background branch and one small rust botanical accent. No continuous floating, particles, trails or new image-generation assets.

## Behavior

- Existing create and explore links retain their destinations.
- Minimal, Floral and Classic deliberately switch the primary sample, preserving Aarav's profile. Secondary sample remains Ananya.
- High-resolution static sample images are loaded on demand; no live PDF endpoint is called by the hero.
- The classic public artwork uses compact print spacing to fit the complete fictional sample onto one page. User documents and export styles are untouched.
- Fine mouse pointer: 7px wine dot, 30px ring, expanded ring on controls and a contextual label on documents.
- Pointer depth is bounded to 2–8px. Animation frames stop once the cursor settles, and all effects reset on exit, scrolling, loss of focus or keyboard navigation.
- Touch uses native behavior without cursor/parallax. Reduced motion disables entrance movement, line drawing, parallax and cursor interpolation.
- Style changes are keyboard-accessible buttons with visible focus and announced status. Image load failures preserve the current style and allow retry.

## Validation

`scripts/hero_craft_check.py` captures and checks 320×568, 360×800, 390×844, 430×932, 768×1024, 1024×1366, 1280×800, 1440×900 and 1920×1080.

Checks include horizontal overflow, A4 image proportions, loaded images, document/control separation, mouse hover lift, contextual cursor, keyboard activation and focus, touch emulation, wheel events representing scroll/trackpad behavior, reduced-motion emulation and selected-design routing. Browser emulation does not replace testing on physical phones or trackpads.

Comparison and interaction screenshots plus the machine-readable result are saved under `tmp/qa/hero-craft/`. Reference extracts and the previous hero implementation are also retained there for local comparison; they are not public application assets.
