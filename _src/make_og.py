#!/usr/bin/env python3
"""Render media/og-card.png (1200x630), the link-preview image. Run manually: python3 _src/make_og.py"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1200, 630
BG, FG, MUTED, ACCENT = (18, 19, 21), (232, 232, 230), (154, 157, 163), (122, 176, 255)
FONT = next(p for p in ("/System/Library/Fonts/Helvetica.ttc", "/Library/Fonts/Arial.ttf") if os.path.exists(p))


def font(size, bold=False):
    try:
        return ImageFont.truetype(FONT, size, index=1 if bold else 0)
    except Exception:
        return ImageFont.truetype(FONT, size)


img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)
d.rectangle([0, 0, 10, H], fill=ACCENT)

# headshot, circular
S = 300
hs = Image.open(os.path.join(ROOT, "media/headshot.jpg")).convert("RGB")
side = min(hs.size)
top = int(hs.size[1] * 0.04)
hs = hs.crop((0, top, side, top + side)).resize((S, S), Image.LANCZOS)
mask = Image.new("L", (S * 4, S * 4), 0)
ImageDraw.Draw(mask).ellipse([0, 0, S * 4 - 1, S * 4 - 1], fill=255)
mask = mask.resize((S, S), Image.LANCZOS)
img.paste(hs, (90, (H - S) // 2), mask)

x = 450
d.text((x, 150), "Benjamin Fuller", font=font(78, True), fill=FG)
d.text((x, 258), "Engineering Leader · Founder-CTO", font=font(34), fill=MUTED)
d.text((x, 306), "AI-Native Builder", font=font(34), fill=MUTED)
line = "Building production AI and the teams that ship it."
d.text((x, 392), line, font=font(31), fill=FG)
d.text((x, 520), "benfuller.me", font=font(30, True), fill=ACCENT)
img.save(os.path.join(ROOT, "media/og-card.png"), optimize=True)
print("wrote media/og-card.png", img.size)
