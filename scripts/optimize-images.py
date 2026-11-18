#!/usr/bin/env python3
"""Готовит картинки для прототипа: WebP в нескольких ширинах для srcset.

Запуск из корня репозитория:
    python3 scripts/optimize-images.py

Берёт файлы из design/mockups/assets/, кладёт в prototype/assets/img/:
    имя-400.webp, имя-800.webp, … (ширины не больше исходной)
WebP понимают все актуальные браузеры, поэтому запасные JPG/PNG не делаем:
так репозиторий и страницы остаются лёгкими.
Печатает размеры, чтобы вписать width/height в <img>.
Нужен Pillow: pip install pillow
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "design" / "mockups" / "assets"
OUT = ROOT / "prototype" / "assets" / "img"

# ширины для srcset; исходная ширина добавляется, если она меньше последней
WIDTHS = {
    "hero-cutout": [360, 540, 690],
    "portrait": [480, 800, 1200],
    "kabinet": [480, 800, 1000],
    "kollazh-doroga": [360, 540, 759],
    "kollazh-nachalo-raboty": [320, 480, 640],
    "uyutnaya-1": [400, 700],
    "uyutnaya-2": [360, 640],
}


def resize(im, w):
    if im.width <= w:
        return im
    h = round(im.height * w / im.width)
    return im.resize((w, h), Image.LANCZOS)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for src in sorted(SRC.iterdir()):
        if src.suffix.lower() not in (".jpg", ".jpeg", ".png"):
            continue
        name = src.stem
        im = Image.open(src)
        alpha = im.mode in ("RGBA", "LA", "P")
        im = im.convert("RGBA" if alpha else "RGB")
        widths = sorted({min(w, im.width) for w in WIDTHS.get(name, [400, 800, 1200])})
        for w in widths:
            r = resize(im, w)
            r.save(OUT / f"{name}-{w}.webp", "WEBP", quality=80, method=6)
            print(f"{name}-{w}.webp  {r.width}×{r.height}")


if __name__ == "__main__":
    main()
