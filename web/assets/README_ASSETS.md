# Web Assets Guide

To achieve a 1:1 visual match with your reference, place image assets here and we will switch the CSS to use them.

Suggested assets (PNG/SVG):
- plaque-frame.png — gold decorative frame for temple plaques
- plaque-bg.png — inner maroon background texture
- button-gold.png — gold beveled button background
- temple-*.png — temple icons per source

How to wire:
1) Place files into this folder.
2) In styles.css, replace the CSS gradient-based backgrounds with `background-image: url('assets/plaque-bg.png')` or frame overlays using pseudo elements.
3) For per-temple icons, update `renderTemples()` in `web/index.html` to use `<img>` tags instead of emoji:
   ```
   const iconSrc = s.type === 'Tarot' ? 'assets/temple-tarot.png' : 'assets/temple-sensi.png';
   <img class="temple-img" src="${iconSrc}" alt="">
   ```

If you share exact assets, I can wire and fine-tune spacing, radii, and shadows for a pixel-perfect match.