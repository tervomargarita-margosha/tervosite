#!/usr/bin/env python3
"""Экспорт макетов главной в самостоятельные HTML-файлы (без холста Design).
Запуск: python3 export.py <папка design/mockups>"""
import sys, os, re

OUT = sys.argv[1]
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "gen.py")).read()
src = src[:src.index("# ---------- write ----------")]
ns = {"__file__": os.path.abspath(__file__), "__name__": "gen"}
sys.argv = [sys.argv[0], "/tmp/_unused"]
exec(compile(src, "gen.py", "exec"), ns)

ns["PHOTOS"].clear()
ns["PHOTOS"].update({
    "hero": "assets/hero-cutout.png", "work": "assets/portrait.jpg", "atmo": "assets/kollazh-doroga.png",
    "start": "assets/kollazh-nachalo-raboty.png", "office": "assets/kabinet.jpg",
    "cozy1": "assets/uyutnaya-1.jpg", "cozy2": "assets/uyutnaya-2.jpg",
})
ORDER = [1, 3, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
NAMES = {1: "Первый экран", 3: "Обратиться за помощью", 2: "Видео-визитка", 4: "С чем можно прийти", 5: "Квалификация",
         6: "Я работаю не одна", 7: "Ценности", 8: "Гештальт простыми словами", 9: "На сессиях я", 10: "Начало работы",
         11: "Условия работы", 12: "Запись", 13: "Частые вопросы", 14: "Информация и инструменты для самопомощи", 15: "Подвал"}

HEAD = """<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>{title}</title>
<!-- Только для просмотра макета. На сайте шрифты храним у себя (без Google Fonts, 23-ФЗ о локализации). -->
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,600&amp;family=Inter:wght@300;400;500&amp;display=swap">
<style>
body{{margin:0;background:#E9E5DE}}
a{{color:inherit}}a:hover{{opacity:0.85}}
summary::-webkit-details-marker{{display:none}}
details[open] summary span[aria-hidden]{{transform:rotate(180deg)}}
.frame{{margin:0 auto;box-shadow:0 0 0 1px rgba(0,0,0,0.06),0 20px 60px rgba(0,0,0,0.12)}}
</style>
</head>
<body>
"""

def page(m):
    P = ns["PAL"]["A"]
    c = ns["Ctx"](P, m)
    parts = []
    for i, n in enumerate(ORDER):
        parts.append(f"<!-- ===== {i + 1}. {NAMES[n]} ===== -->")
        if n == 1:
            parts.append(ns["b_header"](c))
            parts.append(ns["b_hero"](c, ns["ROOT_BG"][ORDER[i + 1]]))
        elif n == 15:
            parts.append(ns["b_footer"](c, last=False))
        else:
            parts.append(ns["BLOCKS"][n][1](c))
    w = 390 if m else 1440
    root = (f"width: {w}px; background: {P['cream']}; font-family: {ns['SANS']}; font-weight: 300; color: {P['text']}; "
            f"text-wrap: pretty; -webkit-font-smoothing: antialiased")
    title = f"Главная · макет · {'телефон 390 px' if m else 'компьютер 1440 px'}"
    html = HEAD.format(title=title) + f'<x-dc><div class="frame" style="{root}">\n' + "\n".join(parts) + "\n</div></x-dc>\n</body>\n</html>\n"
    html = ns["typo"](html).replace("<x-dc>", "").replace("</x-dc>", "")
    html = re.sub(r'href="Home-A-[md]3\.dc\.html"', 'href="#start"', html)
    return html

def board():
    html = ns["style_board"]()
    body = html[html.index('<div style="width: 1440px'):html.index("</x-dc>")]
    return (HEAD.format(title="Основа дизайна сайта") + '<div class="frame" style="width:1440px">' + body + "</div>\n</body>\n</html>\n")

os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, "home-mobile.html"), "w").write(page(True))
open(os.path.join(OUT, "home-desktop.html"), "w").write(page(False))
open(os.path.join(OUT, "style-board.html"), "w").write(board())
print("ok")
