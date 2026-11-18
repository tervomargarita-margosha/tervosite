#!/usr/bin/env python3
"""Вставляет общие части (head, шапка, подвал) во все страницы prototype/.

На каждой странице есть пары меток:
    <!-- @head -->…<!-- /@head -->
    <!-- @header -->…<!-- /@header -->
    <!-- @footer -->…<!-- /@footer -->
Скрипт заменяет содержимое между ними на scripts/partials/<имя>.html,
подставляя относительные пути ({{root}}, {{home}}) и отметку текущего раздела ({{cur:путь/}}).
Ссылки относительные, поэтому сайт работает и в подпапке GitHub Pages (…/tervosite/).

Запуск из корня репозитория (после него – типограф):
    python3 scripts/sync-partials.py && python3 scripts/typograph.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "prototype"
PARTS = Path(__file__).resolve().parent / "partials"


def render(name, page):
    rel = page.relative_to(SITE)
    depth = len(rel.parts) - 1
    root = "../" * depth
    home = root or "./"
    key = rel.as_posix()
    html = (PARTS / f"{name}.html").read_text(encoding="utf-8").rstrip("\n")
    html = re.sub(r"\{\{cur:([^}]+)\}\}",
                  lambda m: ' aria-current="page"' if key.startswith(m.group(1)) else "", html)
    return html.replace("{{root}}", root).replace("{{home}}", home)


def main():
    pages = sorted(SITE.rglob("*.html"))
    for page in pages:
        src = page.read_text(encoding="utf-8")
        dst = src
        for name in ("head", "header", "footer"):
            pat = re.compile(r"(<!-- @%s -->)(.*?)(<!-- /@%s -->)" % (name, name), re.S)
            dst = pat.sub(lambda m: m.group(1) + "\n" + render(name, page) + "\n" + m.group(3), dst)
        if dst != src:
            page.write_text(dst, encoding="utf-8")
    print(f"Общие части: {len(pages)} страниц")


if __name__ == "__main__":
    main()
