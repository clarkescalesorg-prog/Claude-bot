# OG Car World — Ad Creatives

Eight print/social-ready ad creatives for **ogcarworld.co.uk**.

## Contents

| File | Size | Format | Headline car |
|---|---|---|---|
| `01-lamborghini.html` | 1080×1080 | IG / FB feed | Lamborghini Huracán |
| `02-ferrari.html` | 1080×1080 | IG / FB feed | Ferrari 488 GTB |
| `03-bmw-m4.html` | 1200×628 | FB / LinkedIn | BMW M4 Competition |
| `04-mercedes-amg.html` | 1080×1080 | IG / FB feed | Mercedes-AMG GT 63 S |
| `05-fleet.html` | 1080×1080 | IG / FB feed | Full fleet showcase |
| `06-weekend-special.html` | 1200×628 | FB / LinkedIn | Weekend package |
| `07-wedding-prom.html` | 1080×1080 | IG / FB feed | Weddings & prom |
| `08-instagram-story.html` | 1080×1920 | IG / TikTok story | Vertical hero |

Open `index.html` to browse them all.

## Design notes

- **Bubble writing**: location + price use a chunky cursive
  (`Sigmar One` / `Luckiest Guy`) with a thick black stroke and stacked
  drop shadow for a headline/graffiti bubble effect.
- **Cars**: stylised SVG silhouettes in `cars/`. They're recognisable
  shapes (wedge/supercar/coupe/GT) but intentionally not brand-accurate
  — safer for paid ads than real marque logos.
- **Palette**: gold (`#d4af37`), Ferrari red (`#e10600`), BMW blue
  (`#0066b1`), AMG silver (`#c8ccce`). All live in `styles.css` under
  `:root`.

## Exporting as images

The ad canvases are fixed-size (e.g. 1080×1080) so you can screenshot
or export them pixel-perfect:

```bash
# using a headless browser, e.g. Chrome or chromium
chromium --headless --disable-gpu \
  --screenshot=out/01-lamborghini.png \
  --window-size=1080,1080 \
  file://$(pwd)/ads/01-lamborghini.html
```

Or open each file in a browser, set zoom to 100%, and screenshot the
card.

## Editing

All copy lives inline in each HTML file. The bits you'll most likely
want to change:

- **Location name**: the `.bubble xxl` element in each
  `.headline-stack` (e.g. `London`, `Manchester`, `Birmingham`,
  `Leeds`).
- **Price**: the `.pricetag .amt` element (e.g. `£499`, `£599`).
- **Specs / BHP / 0–60**: the `.spec` chips.
- **CTA**: the `.cta` button text.

Rebrand globally by editing the `:root` variables in `styles.css`.

## Caveat

`ogcarworld.co.uk` was unreachable at build time (HTTP 403 on fetch),
so brand specifics (exact locations, pricing tiers, slogan) are
placeholders modelled on typical UK luxury-hire positioning. Swap
values before running paid spend.
