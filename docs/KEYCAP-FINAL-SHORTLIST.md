# Rev B — final keycap procurement research and decision gate

**Research date: 2026-10-21. CAD rest height selected: 4mm. Keycaps NOT selected/ordered yet.**
User independently pulled `3b3c7f0` and ran the three-height CAD Python suite on Windows 11: **20 discovered, 18 passed, 2 skipped** (CadQuery/Shapely not installed). All three report-only geometry folders were generated. User explicitly preferred **4mm keycaps**. The previously exported 4mm single-solid R5 STEP shell and illustrative cap/switch/knob assembly remain the active geometry direction; do NOT overwrite or delete the 2/6mm variants.

## Required purchase specification

- **Exactly three identical-profile 1U caps** with *black body, opaque white icons* in order **previous ⏮ / play-pause ⏯ / next ⏭**, no RGB shine-through requirement; MX-style cross stem; preferably PBT plastic, not low-profile Choc-specific.
- These three media SVG masters already exist: [previous](../mechanical/revB/keycaps/previous_white_legend.svg), [play/pause](../mechanical/revB/keycaps/play_pause_white_legend.svg), [next](../mechanical/revB/keycaps/next_white_legend.svg). The design references illustrate the desired icons, not an approved supplier print template.
- **4mm above case face at rest** is an aesthetic/mechanical CAD datum, NOT the actual keycap height or switch travel. Current 4mm case presumes an **18.0mm square external cap**, **8.0mm nominal cap skirt depth**, **19.2mm square well** (0.6mm clearance per side), **1.5mm MX retaining plate with top 9.5mm inward**, **4mm switch travel**, **1.5mm nominal full-press skirt-to-plate margin**. Verify geometry; 1U denotes *keyboard spacing*, not a guaranteed 18mm external footprint or cap height.
- All three should be from **the same vendor/profile/row**; Cherry profiles are row-sculpted. Choose a consistent row after getting vendor dimensions. Unmatched OEM/Cherry/DSA profiles can produce varying cap tops and skirt interference.

## Verified retailer pages (listed UK prices, not checkout guarantees)

| Candidate | Listed price | Confirmed from product page | Unresolved blocker |
|---|---:|---|---|
| [Tech Toppers 4-key custom WASD set](https://www.techtoppers.co.uk/products/wasd-custom-keycaps-editor) | **£14.95 + £3.95 Royal Mail standard delivery ≈£18.90** | Exactly four customisable MX-compatible PBT caps. Seller allows upload of artwork per key; described printing is dye sublimation; seller states usual custom processing 8–10 business days. Three required + one spare. | Supplier must **confirm a genuine black-cap/white-icon result**, whether reverse dye-sub black background on white PBT is available, all four share a consistent height/row, exact outer underside dimensions (max skirt X/Y, total depth, stem-socket height). Conventional dye sublimation cannot print opaque white ink on a black base. |
| [Mechbox 4 blank WASD keycaps](https://mechbox.co.uk/products/blank-wasd-keys) | **£1.56 + shipping** | Four 1U, MX-compatible PBT, OEM-profile caps; black colour listed. | Completely blank; would require separate white durable artwork/decal or laser/UV print. No guarantee of cap skirts/dimensions and no confirmed cheap symbol-adding service. Best fit-test sample or DIY fallback, not yet a finished ⏮/⏯/⏭ set. |
| [Krome custom Cherry 1U cap](https://www.kromekeycaps.com/products/create-your-own-custom-cherry-keycap) | **£8 each ×3 = £24 + shipping** | 1U, MX-compatible PBT Cherry-profile, UV printed from SVG, separately selectable R1–R4; no backlight. Single-item order. | Verify stock **black plastic/opaque white UV print**, row R choice and exact outside size before paying. Reasonable image-print fallback if Tech Toppers can't reproduce white-on-black; not mandatory. |
| [Tech Toppers custom single](https://www.techtoppers.co.uk/products/single-keycap-editor) | **£6.95 on product page for currently shown variant + shipping** | MX-compatible custom PBT with 1U available, dye sub; alternatives shown in site collection may have different prices. | Three singles at shown £6.95 would exceed price of four-key bundle, and same black-on-white problem. No benefit over four-key set. |
| [Krome custom Cherry text](https://www.kromekeycaps.com/products/create-your-own-custom-cherry-text-keycap) | **£3 shown on product page** (site collection may show different figure) | UV text cap with Cherry profile, MX stem. | Only use if seller confirms Unicode media symbols print as intended, including distinct ⏮/⏯/⏭ and white on black; not verified as equivalent to uploaded icon SVG or correct fixed checkout price. |

**Ready-made media legend search:** UK direct suppliers, media-keycap marketplaces and broad shopping listings reviewed. No *specific in-stock, matching three-cap 1U/MX black+white prior/play-pause/next trio with validated profile, dimensions, seller URL and delivered price* was found. This is a limit of what was verified, **not evidence no ready-made sets exist anywhere**. Do not purchase unrelated full keyboard sets merely to extract media legends.

## Tech Toppers chatbot response received — 2026-10-21

The user asked the Tech Toppers storefront chatbot about four custom WASD keycaps appearing **black (#000000) with white (#FFFFFF) previous / play-pause / next / play symbols** in the preview.

**Chatbot claims, not written production confirmation:**
- Printing method: **dye sublimation**; minor colour and design-clarity differences are possible, and the supplier may correct colours or layers.
- It **did not confirm** that the finished result will have white artwork on genuinely black material or an equivalent sharp **white-on-black appearance**. Instead, it urged the buyer to notify the supplier **in writing before production** with exact colour requirements.
- It states **Cherry profile** and **Cherry MX-style cross-stem compatibility**. Four WASD positions are **normally 1U**, but even the chatbot recommended directly confirming individual sizes.
- It supplied **no measured cap outer width, underside/skirt size, height, stem socket depth or row/profile equality**. The conventional WASD grouping may have **mixed sculpted Cherry rows**; three side-by-side controls in Spotify Desk require identical physical row and top slope.
- These statements are from a generic chatbot, **not a named human order/production guarantee**. The configuration screenshot and ability to add to cart are NOT proof of feasible white printing.

**Next action before checkout:** request a human/support team response in writing explaining whether they print dark dye *around white negative-space symbols* on light material or have another actual technique for high-contrast white on black; request a finished example/photograph if possible, confirm identical 1U profile row for the three main keys (ideally all four), and request maximal cap skirt dimensions/overall depth/underside MX socket drawing. Verify saved artwork and total delivered price. If they cannot confirm appearance or row consistency, consider Krome UV printed alternatives instead. User has **not stated they have paid for or received** these caps.

## Provisional recommendation and next supplier confirmation

**Primary procurement candidate:** **Tech Toppers 4-key WASD custom set**, not three £8 Krome singles. It has a verifiable 4-key MX PBT listing, allows 3 independent media SVG designs and is about **£18.90 delivered** at the listed UK standard rate. **However, do NOT mark this as the chosen keycap model until the vendor confirms the actual black-white process and underside dimensions.** White lettering cannot be directly dye-sub printed onto black PBT by a conventional coloured dye process; an inverted design on light PBT may be possible, but must be vendor confirmed for colour/quality.

**Budget fit-test candidate:** Mechbox 4 blank **black OEM** MX-compatible caps for £1.56 + shipping if a cheap physical test matters more than printed symbols, but their OEM silhouette is not interchangeable with every Cherry-profile cap. If 4mm CAD is refined with Mechbox OEM, switching later to Tech Toppers Cherry-shaped caps may demand new clearance calculations.

**Fallback for print fidelity:** Krome UV-image-print at £24 + postage if Tech Toppers cannot give adequate contrast. Also check whether their cheaper **text** product supports accurate monochrome vector-style symbols before paying for image uploads; this is unconfirmed.

**Supplier verification requirements, before ordering anything:**
1. Supply three matching 1U **black with true white** ⏮/⏯/⏭ symbols, with the fourth WASD cap as a spare? Is reverse dye-sub or another suitable printing method used?
2. Are all four caps the **same height, profile/row and top slope** when fitted side by side on an independent desk controller?
3. Measure or provide **maximum cap X/Y including the lower skirt**, cap total physical height/depth, top-surface dimensions and **inside MX stem socket engagement**, ideally 3D CAD/technical drawing. Ask whether any underside/support ribs protrude.
4. Confirm standard **MX cross-stem** fit for three full-height plate-mounted mechanical switches, not Kailh Choc or membrane scissor.
5. Check final price incl. delivery, custom print artwork review, lead time and return/cancellation policy.

## Design implementation status

No hardware purchases or physical switch/cap fit tests. The **4mm R5 STEP variant is the selected DESIGN direction**, not fabrication-ready. Next CAD revision should use **one exact keycap product, chosen row/profile and measured silhouette**; evaluate 19.2mm opening, MX skirt collision at full stroke, stem socket seating, printer wall strength and plate support. Retain reversible 2/6mm reference designs and the user-approved USB-left rounded aesthetic. Do not commit any revised cap clearance based on a seller's *approximate 1U* alone.
