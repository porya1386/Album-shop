"""Make sharp background images for phones, tablets and desktops from ONE big original.

Why: a 1080 px wide picture looks blurry when a phone is turned sideways (the screen is
2340 px wide) and when it is stretched over a whole page. We need
    NAME-land.webp   wide picture (2560 px)  -> landscape phones, tablets, laptops
    NAME-port.webp   tall picture (1200x2600) -> phones held upright (a crop of the painting)

Usage (PowerShell, inside the project, venv active):
    pip install pillow
    python make_backgrounds.py originals/starry-night.jpg  starry-night
    python make_backgrounds.py originals/great-wave.jpg    great-wave   --focus-x 0.6
    python make_backgrounds.py originals/water-lilies.jpg  water-lilies
    python make_backgrounds.py originals/poppy-field.jpg   poppy-field
    python make_backgrounds.py originals/forest.jpg        forest

    --focus-x  0 = crop the left part, 0.5 = the middle (default), 1 = the right part
    --out      folder for the result (default: static/images/themes)

Use ORIGINALS that are at least 2560 px wide (download the biggest file from Wikimedia Commons or a
museum's open-access page). A small original cannot get sharper, the script only warns you.
"""
import argparse
import sys
from pathlib import Path

from PIL import Image, ImageOps

LAND_WIDTH = 2560
PORT_SIZE = (1200, 2600)      # 9 : 19.5, like modern phones
QUALITY = 78


def save(img, path):
    img.save(path, "WEBP", quality=QUALITY, method=6)
    print(f"  {path.name:28s} {img.width}x{img.height}  {path.stat().st_size // 1024} KB")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source")
    ap.add_argument("name")
    ap.add_argument("--focus-x", type=float, default=0.5)
    ap.add_argument("--out", default="static/images/themes")
    args = ap.parse_args()

    src = Path(args.source)
    if not src.is_file():
        sys.exit(f"File not found: {src}")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    img = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
    w, h = img.size
    print(f"{src.name}: {w}x{h}")
    if w < LAND_WIDTH:
        print(f"  WARNING: the original is only {w}px wide. Phones on their side need about {LAND_WIDTH}px "
              f"for a sharp picture. Download a bigger original if you can.")

    # wide picture: only shrink, never enlarge
    land = img if w <= LAND_WIDTH else img.resize((LAND_WIDTH, round(h * LAND_WIDTH / w)), Image.LANCZOS)
    save(land, out / f"{args.name}-land.webp")

    # tall picture: crop the part you want, then shrink
    target_ratio = PORT_SIZE[0] / PORT_SIZE[1]
    crop_w = min(w, round(h * target_ratio))
    crop_h = round(crop_w / target_ratio)
    left = round((w - crop_w) * min(max(args.focus_x, 0), 1))
    top = (h - crop_h) // 2
    if crop_h < 2300:
        print(f"  WARNING: for phones held upright the original should be at least 2340px TALL "
              f"(yours is {h}px). The upright picture will be a little soft.")
    port = img.crop((left, top, left + crop_w, top + crop_h))
    if port.width > PORT_SIZE[0]:
        port = port.resize(PORT_SIZE, Image.LANCZOS)
    save(port, out / f"{args.name}-port.webp")


if __name__ == "__main__":
    main()