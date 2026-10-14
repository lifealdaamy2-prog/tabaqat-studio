#!/usr/bin/env python3
"""Render a news card on the platform template.
usage: card.py --title T --body B --photo P --out O [--fx 0.5 --fy 0.4 --zoom 1]
fx/fy: focus point of the photo (0..1) kept in view when cropping.
"""
import argparse, re
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path

HERE = Path(__file__).parent
TPL = HERE / "template.png"
FONT = HERE / "NotoKufiArabic.ttf"
W, H = 1080, 1350
BOX = (108, 184, 865, 124)
BODY = dict(x=108, w=865, top=330, bottom=525)
PHOTO = (0, 586, 1080, 629)
TASHKEEL = re.compile(r"[ً-ْٰـ]")

def clean(s): return re.sub(r"\s+", " ", TASHKEEL.sub("", s)).strip()

def font(size, wght):
    f = ImageFont.truetype(str(FONT), size, layout_engine=ImageFont.Layout.RAQM)
    try: f.set_variation_by_axes([wght])
    except Exception: pass
    return f

def width(d, t, f): return d.textlength(t, font=f, direction="rtl", language="ar")

def wrap(d, text, f, maxw):
    lines, cur = [], ""
    for w in text.split(" "):
        t = f"{cur} {w}" if cur else w
        if width(d, t, f) <= maxw or not cur: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def render(title, body, photo, out, fx=0.5, fy=0.4, zoom=1.0):
    card = Image.open(TPL).convert("RGB")
    # photo: cover-crop around focus point
    px, py, pw, ph = PHOTO
    im = Image.open(photo).convert("RGB")
    s = max(pw / im.width, ph / im.height) * zoom
    rw, rh = round(im.width * s), round(im.height * s)
    im = im.resize((rw, rh), Image.LANCZOS)
    left = min(max(0, round(fx * rw - pw / 2)), rw - pw)
    top = min(max(0, round(fy * rh - ph / 2)), rh - ph)
    card.paste(im.crop((left, top, left + pw, top + ph)), (px, py))

    d = ImageDraw.Draw(card)
    # title: single line, shrink to fit
    t = clean(title); size = 76
    while size > 34 and width(d, t, font(size, 800)) > BOX[2] - 56: size -= 2
    f = font(size, 800)
    d.text((BOX[0] + BOX[2] / 2, BOX[1] + BOX[3] / 2), t, font=f, fill="#111111",
           anchor="mm", direction="rtl", language="ar")

    # body: up to 2 lines, white with soft shadow, right-aligned
    b = clean(body); size = 48
    lines = wrap(d, b, font(size, 700), BODY["w"])
    while size > 28 and len(lines) > 2:
        size -= 2; lines = wrap(d, b, font(size, 700), BODY["w"])
    f = font(size, 700); lh = size * 1.48
    cy = (BODY["top"] + BODY["bottom"]) / 2; y0 = cy - (len(lines) - 1) * lh / 2
    xr = BODY["x"] + BODY["w"]
    shadow = Image.new("L", card.size, 0); sd = ImageDraw.Draw(shadow)
    for i, l in enumerate(lines):
        sd.text((xr, y0 + i * lh + 3), l, font=f, fill=150, anchor="rm", direction="rtl", language="ar")
    shadow = shadow.filter(ImageFilter.GaussianBlur(5))
    card.paste(Image.new("RGB", card.size, (0, 0, 0)), (0, 0), shadow)
    d = ImageDraw.Draw(card)
    for i, l in enumerate(lines):
        d.text((xr, y0 + i * lh), l, font=f, fill="#ffffff", anchor="rm", direction="rtl", language="ar")

    card.save(out, quality=95)
    return len(lines)

if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--title", required=True); a.add_argument("--body", required=True)
    a.add_argument("--photo", required=True); a.add_argument("--out", required=True)
    a.add_argument("--fx", type=float, default=0.5); a.add_argument("--fy", type=float, default=0.4)
    a.add_argument("--zoom", type=float, default=1.0)
    o = a.parse_args()
    n = render(o.title, o.body, o.photo, o.out, o.fx, o.fy, o.zoom)
    print(f"saved {o.out} ({n} body lines)")
