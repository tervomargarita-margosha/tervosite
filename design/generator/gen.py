#!/usr/bin/env python3
"""Генератор артбордов холста «Сайт — дизайн главной»."""
import json, re, os, sys, datetime

ROOT = sys.argv[1]
os.makedirs(f"{ROOT}/project", exist_ok=True)

PAL = {
    "A": dict(name="тёмно-синий, кремовый, бронза", dark="#1A2A44", dark_hi="#24375A", dark_lo="#15223A",
              cream="#F9F6F0", cream2="#F1EADF", line="#B58B5C", accl="#7E5D3A", accd="#D9B98C",
              text="#2C2C2C", muted="#58534C", rgb_dark="26,42,68", rgb_line="181,139,92", rgb_cream="249,246,240"),
    "B": dict(name="тёмная олива, кремовый, золото", dark="#3E432F", dark_hi="#4A5038", dark_lo="#32362A",
              cream="#F7F3EA", cream2="#EEE8DA", line="#B5A05A", accl="#6B5C24", accd="#D0BD76",
              text="#2B2B24", muted="#57554B", rgb_dark="62,67,47", rgb_line="181,160,90", rgb_cream="247,243,234"),
}

SHORT = r"(в|и|с|на|не|по|для|к|о|у|а|от|до|из|за|со|или|но|что|как|я|вы|мы|без|при|об|ни|под|над|про|во|ко|их|его|её|это|все|всё|уже|так|чем|где|то)"
WS = r"(?:\s|&nbsp;)"
def nb(t):
    t = t.replace("—", "–")
    for _ in range(2):
        t = re.sub(r"(^|[\s(«;])" + SHORT + r" ", lambda m: m.group(1) + m.group(2) + "&nbsp;", t, flags=re.I)
    t = re.sub(r" (бы|ли|же)(?=[\s,.!?:;]|$)", r"&nbsp;\1", t)
    t = t.replace(" – ", "&nbsp;– ").replace(" ₽", "&nbsp;₽")
    t = re.sub(r"(\d) (?=[А-Яа-яЁё₽%])", r"\1&nbsp;", t)
    return t

def _textnode(s):
    if not s.strip():
        return s
    s = nb(s)
    # слова через дефис и диапазоны цифр не переносим
    s = re.sub(r"(?<![\w\-])((?:[А-Яа-яЁёA-Za-z0-9]+-)+[А-Яа-яЁёA-Za-z0-9]+)",
               r'<span style="white-space: nowrap">\1</span>', s)
    s = re.sub(r"(\d[\d:]*–\d[\d:]*)", r'<span style="white-space: nowrap">\1</span>', s)
    # последнее слово абзаца не остаётся одно на строке
    words = s.rstrip().split(" ")
    if len(words) >= 4 and len(re.sub(r"<[^>]+>|&nbsp;", "", words[-1])) <= 12:
        idx = s.rstrip().rfind(" ")
        s = s[:idx] + "&nbsp;" + s[idx + 1:]
    return s

def typo(html):
    a, b = html.index("<x-dc>"), html.index("</x-dc>")
    body = html[a:b]
    parts = re.split(r"(<style>.*?</style>|<svg.*?</svg>)", body, flags=re.S)
    out = []
    for part in parts:
        if part.startswith("<style>") or part.startswith("<svg"):
            out.append(part)
        else:
            out.append(re.sub(r">([^<>]+)<", lambda m: ">" + _textnode(m.group(1)) + "<", part))
    return html[:a] + "".join(out) + html[b:]

PHOTOS = {}  # слот → url загруженного фото
if os.path.exists(os.path.join(os.path.dirname(__file__), "photos.json")):
    PHOTOS = json.load(open(os.path.join(os.path.dirname(__file__), "photos.json")))

UID = [0]
def uid(p="u"):
    UID[0] += 1
    return f"{p}{UID[0]}"

SERIF = "'Cormorant Garamond', Georgia, serif"
SANS = "Inter, 'Helvetica Neue', Arial, sans-serif"

# ---------- icons ----------
ICONS = {
    "lock": '<rect x="5" y="11" width="14" height="10" rx="2"></rect><path d="M8 11V8a4 4 0 0 1 8 0v3"></path>',
    "doc": '<path d="M7 3h7l4 4v14H7z"></path><path d="M14 3v4h4"></path><path d="M10 13l2 2 4-4"></path>',
    "heart": '<path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"></path>',
    "meet": '<circle cx="9" cy="12" r="5.5"></circle><circle cx="15" cy="12" r="5.5"></circle>',
    "x": '<circle cx="12" cy="12" r="9"></circle><path d="M9 9l6 6M15 9l-6 6"></path>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"></path>',
    "down": '<path d="M12 5v14M6 13l6 6 6-6"></path>',
    "chev": '<path d="M6 9l6 6 6-6"></path>',
    "copy": '<rect x="8" y="8" width="12" height="12" rx="2"></rect><path d="M16 8V5a1 1 0 0 0-1-1H5a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h3"></path>',
    "send": '<path d="M21 3L3 10.5l7 2.5 2.5 7z"></path><path d="M21 3L10 13"></path>',
    "msg": '<path d="M4 5h16v11H9l-5 4z"></path>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"></path>',
    "camera": '<path d="M4 8h3l2-3h6l2 3h3v11H4z"></path><circle cx="12" cy="13" r="3.5"></circle>',
    "pin": '<path d="M12 21s-6-5.5-6-11a6 6 0 0 1 12 0c0 5.5-6 11-6 11z"></path><circle cx="12" cy="10" r="2.2"></circle>',
    "clock": '<circle cx="12" cy="12" r="9"></circle><path d="M12 7v5l3 2"></path>',
    "play": '<path d="M9 6l10 6-10 6z"></path>',
    "file": '<path d="M7 3h7l4 4v14H7z"></path><path d="M14 3v4h4"></path><path d="M10 12h5M10 15h5M10 18h3"></path>',
    "book": '<path d="M4 5c3-1 6-1 8 1 2-2 5-2 8-1v14c-3-1-6-1-8 1-2-2-5-2-8-1z"></path><path d="M12 6v14"></path>',
}
def icon(n, size=22, color="currentColor", sw=1.5):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{sw}" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" style="flex: none">{ICONS[n]}</svg>')

# ---------- motifs (atmosphere graphics) ----------
def m_meet(P, s=160, dark=False):
    c = P["accd"] if dark else P["line"]
    i = uid("cl")
    return (f'<svg width="{s}" height="{s}" viewBox="0 0 200 200" aria-hidden="true" style="flex: none; display: block">'
            f'<defs><clipPath id="{i}"><circle cx="78" cy="100" r="58"></circle></clipPath></defs>'
            f'<circle cx="122" cy="100" r="58" fill="{c}" opacity="0.22" clip-path="url(#{i})"></circle>'
            f'<circle cx="78" cy="100" r="58" fill="none" stroke="{c}" stroke-width="1.4"></circle>'
            f'<circle cx="122" cy="100" r="58" fill="none" stroke="{c}" stroke-width="1.4"></circle>'
            f'<circle cx="78" cy="100" r="72" fill="none" stroke="{c}" stroke-width="0.8" opacity="0.4"></circle>'
            f'<circle cx="122" cy="100" r="72" fill="none" stroke="{c}" stroke-width="0.8" opacity="0.4"></circle></svg>')

def m_depth(P, s=160, dark=False):
    c = P["accd"] if dark else P["line"]
    rings = "".join(f'<circle cx="100" cy="100" r="{r}" fill="none" stroke="{c}" stroke-width="1.2" opacity="{op}"></circle>'
                    for r, op in [(16, 1), (32, .8), (48, .62), (64, .46), (80, .32), (96, .2)])
    return (f'<svg width="{s}" height="{s}" viewBox="0 0 200 200" aria-hidden="true" style="flex: none; display: block">'
            f'{rings}<circle cx="100" cy="100" r="5" fill="{c}"></circle></svg>')

def m_path(P, s=160, dark=False):
    c = P["accd"] if dark else P["line"]
    return (f'<svg width="{s}" height="{s}" viewBox="0 0 200 200" aria-hidden="true" style="flex: none; display: block">'
            f'<path d="M18 168 C 60 160, 40 110, 82 102 S 120 140, 140 96 S 120 46, 150 40" fill="none" stroke="{c}" '
            f'stroke-width="3" stroke-linecap="round" stroke-dasharray="0 9"></path>'
            f'<circle cx="160" cy="36" r="20" fill="none" stroke="{c}" stroke-width="1.4"></circle>'
            f'<circle cx="160" cy="36" r="30" fill="none" stroke="{c}" stroke-width="0.8" opacity="0.45"></circle>'
            f'<circle cx="18" cy="168" r="4" fill="{c}"></circle></svg>')

MOTIFS = [m_meet, m_depth, m_path]

def texture(op=0.16):
    i = uid("pa")
    return (f'<svg aria-hidden="true" style="position: absolute; left: 0; top: 0; width: 100%; height: 100%; opacity: {op}; '
            f'mix-blend-mode: multiply; pointer-events: none"><filter id="{i}"><feTurbulence type="fractalNoise" baseFrequency="0.9" '
            f'numOctaves="3" stitchTiles="stitch"></feTurbulence><feColorMatrix type="saturate" values="0"></feColorMatrix></filter>'
            f'<rect width="100%" height="100%" filter="url(#{i})"></rect></svg>')

# ---------- layout primitives ----------
class Ctx:
    def __init__(self, P, m):
        self.P, self.m = P, m
        self.py = 72 if m else 120
        self.h2 = 38 if m else 58
        self.k = 22 if m else 26
        self.body = 17 if m else 19
        self.small = 14 if m else 15

def container(c, inner, maxw=1200):
    if c.m:
        return f'<div style="position: relative; padding: 0 22px">{inner}</div>'
    return f'<div style="position: relative; max-width: {maxw}px; margin: 0 auto; padding: 0 60px">{inner}</div>'

def bgart(slot, css, op=0.3):
    if not PHOTOS.get(slot):
        return ""
    return (f'<img src="{PHOTOS[slot]}" alt="" aria-hidden="true" style="position: absolute; {css}; height: auto; opacity: {op}; '
            f'mix-blend-mode: screen; pointer-events: none; -webkit-mask-image: radial-gradient(closest-side, #000 35%, transparent 100%); '
            f'mask-image: radial-gradient(closest-side, #000 35%, transparent 100%)">')


def section(c, bg, inner, sid="", tex=False, dark=False, last=False, extra="", art=""):
    P = c.P
    if bg == "dark":
        bgcss = f"radial-gradient(circle at 25% 15%, {P['dark_hi']} 0%, {P['dark']} 55%, {P['dark_lo']} 100%)"
    else:
        bgcss = P[bg]
    grow = "flex: 1 0 auto; " if last else ""
    idattr = f' id="{sid}"' if sid else ""
    return (f'<section{idattr} style="{grow}position: relative; overflow: hidden; background: {bgcss}; padding: {c.py}px 0; {extra}">'
            f'{texture() if tex else ""}{art}{container(c, inner)}</section>')

def kicker(c, t, dark=False):
    col = c.P["accd"] if dark else c.P["accl"]
    return (f'<p style="margin: 0 0 8px; font-family: {SERIF}; font-style: italic; font-weight: 600; font-size: {c.k}px; '
            f'line-height: 1.2; color: {col}">{t}</p>')

def h2(c, t, dark=False, mb=None):
    col = c.P["cream"] if dark else c.P["dark"]
    mb = (28 if c.m else 40) if mb is None else mb
    return (f'<h2 style="margin: 0 0 {mb}px; font-family: {SERIF}; font-weight: 700; font-size: {c.h2}px; line-height: 1.05; '
            f'letter-spacing: -0.01em; text-wrap: balance; color: {col}">{nb(t)}</h2>')

def p(c, t, dark=False, size=None, mb=16, muted=False, maxw=None, extra=""):
    P = c.P
    if dark:
        col = f"rgba({P['rgb_cream']},0.82)" if muted else P["cream"]
    else:
        col = P["muted"] if muted else P["text"]
    size = size or c.body
    mw = f"max-width: {maxw}px; " if maxw else ""
    return f'<p style="margin: 0 0 {mb}px; {mw}font-size: {size}px; line-height: 1.62; color: {col}; {extra}">{nb(t)}</p>'

def stub(c, t, dark=False, mb=16):
    P = c.P
    bg = f"rgba({P['rgb_cream']},0.08)" if dark else f"rgba({P['rgb_line']},0.13)"
    col = f"rgba({P['rgb_cream']},0.8)" if dark else P["muted"]
    return (f'<div style="margin: 0 0 {mb}px; padding: 16px 20px; border-radius: 18px; background: {bg}">'
            f'<p style="margin: 0; font-size: {c.small}px; line-height: 1.55; color: {col}">'
            f'<span style="font-weight: 500; letter-spacing: 0.06em; text-transform: uppercase; font-size: 12px">Заглушка · </span>{nb(t)}</p></div>')

def link(c, t, href="#", dark=False, mt=8):
    col = c.P["accd"] if dark else c.P["accl"]
    return (f'<a href="{href}" style="display: inline-flex; align-items: center; gap: 10px; margin-top: {mt}px; min-height: 44px; '
            f'font-size: {c.small + 1}px; font-weight: 500; color: {col}; text-decoration: none">{nb(t)}{icon("arrow", 18)}</a>')

def btn(c, t, kind="primary", ic=None, href="#"):
    P = c.P
    if kind == "primary":
        st = f"background: {P['accd']}; color: {P['dark']}; box-shadow: 0 10px 24px rgba(0,0,0,0.22)"
    elif kind == "ghost":
        st = f"background: rgba({P['rgb_cream']},0.1); color: {P['cream']}"
    elif kind == "darkbtn":
        st = f"background: {P['dark']}; color: {P['cream']}; box-shadow: 0 10px 24px rgba({P['rgb_dark']},0.25)"
    i = icon(ic, 19) if ic else ""
    return (f'<a href="{href}" style="display: inline-flex; align-items: center; justify-content: center; gap: 10px; min-height: 52px; '
            f'padding: 0 28px; border-radius: 999px; font-size: 16px; font-weight: 500; text-decoration: none; {st}">{i}{t}</a>')

def card(c, inner, pad=None, extra=""):
    pad = pad or (22 if c.m else 32)
    return (f'<div style="background: #FFFFFF; border-radius: 28px; padding: {pad}px; '
            f'box-shadow: 0 14px 34px rgba({c.P["rgb_dark"]},0.08); {extra}">{inner}</div>')

def darkplate(c, inner, pad=None, extra=""):
    P = c.P
    pad = pad or (24 if c.m else 44)
    return (f'<div style="position: relative; overflow: hidden; border-radius: 28px; padding: {pad}px; '
            f'background: radial-gradient(circle at 20% 10%, {P["dark_hi"]} 0%, {P["dark"]} 60%, {P["dark_lo"]} 100%); '
            f'box-shadow: 0 18px 40px rgba({P["rgb_dark"]},0.22); {extra}">{inner}</div>')

def ringcircle(c, inner, s=52, dark=False):
    P = c.P
    col = P["accd"] if dark else P["line"]
    bg = f"rgba({P['rgb_cream']},0.06)" if dark else "#FFFFFF"
    return (f'<div style="flex: none; width: {s}px; height: {s}px; border-radius: 50%; background: {bg}; '
            f'box-shadow: 0 0 0 1.5px {col}, 0 0 0 6px rgba({P["rgb_line"]},0.12); display: flex; align-items: center; justify-content: center; '
            f'color: {P["accd"] if dark else P["accl"]}">{inner}</div>')

def photo(c, caption, ratio="4 / 3", dark=False, extra="", slot=None):
    P = c.P
    if slot and PHOTOS.get(slot) and slot == "atmo":  # коллаж без фона – свободно, без рамки
        return f'<img src="{PHOTOS[slot]}" alt="" style="display: block; width: 100%; max-width: {300 if c.m else 360}px; height: auto; margin: 0 auto">'
    if slot and PHOTOS.get(slot) and slot == "online":  # ноутбук без фона – на кремовой плашке
        return (f'<figure style="margin: 0; position: relative; overflow: hidden; border-radius: 28px; aspect-ratio: {ratio}; background: {P["cream"]}; '
                f'box-shadow: 0 14px 34px rgba({P["rgb_dark"]},0.08); display: flex; align-items: center; justify-content: center; {extra}">'
                f'<img src="{PHOTOS[slot]}" alt="{caption}" style="display: block; width: 84%; height: auto"></figure>')
    if slot and PHOTOS.get(slot):
        return (f'<figure style="margin: 0; position: relative; overflow: hidden; border-radius: 28px; aspect-ratio: {ratio}; '
                f'box-shadow: 0 14px 34px rgba({P["rgb_dark"]},0.12); {extra}">'
                f'<img src="{PHOTOS[slot]}" alt="{caption}" style="display: block; width: 100%; height: 100%; object-fit: cover; object-position: {"50% 30%" if slot == "work" else "50% 50%"}"></figure>')
    if dark:
        bg = (f"radial-gradient(circle at 72% 28%, rgba({P['rgb_cream']},0.16) 0%, rgba({P['rgb_cream']},0) 55%), "
              f"linear-gradient(160deg, {P['dark_hi']}, {P['dark_lo']})")
        col = f"rgba({P['rgb_cream']},0.82)"
    else:
        bg = (f"radial-gradient(circle at 75% 22%, rgba(255,255,255,0.75) 0%, rgba(255,255,255,0) 55%), "
              f"linear-gradient(160deg, {P['cream2']}, rgba({P['rgb_line']},0.38))")
        col = P["muted"]
    return (f'<figure style="margin: 0; position: relative; overflow: hidden; border-radius: 28px; aspect-ratio: {ratio}; '
            f'background: {bg}; {extra}">'
            f'<figcaption style="position: absolute; left: 18px; right: 18px; bottom: 16px; display: flex; gap: 10px; align-items: flex-start; '
            f'font-size: 13px; line-height: 1.45; color: {col}">{icon("camera", 18)}<span>{nb(caption)}</span></figcaption></figure>')

def portrait(c, s, caption, dark=True, slot="hero"):
    """Портрет «выглядывает» из круга: голова выше круга, низ обрезан по дуге."""
    P = c.P
    h = int(s * 1.25)
    ring = s + 36
    sil = f"rgba({P['rgb_dark']},0.22)"
    if PHOTOS.get(slot):
        img = (f'<img src="{PHOTOS[slot]}" alt="Маргарита Терво" style="position: absolute; left: 0; top: 0; width: 100%; height: auto">')
        if slot != "hero":  # обычное фото с фоном — просто в круге
            return (f'<div style="position: relative; width: {ring}px; max-width: 100%; margin: 0 auto">'
                    f'<div style="position: relative; width: {ring}px; height: {ring}px; border-radius: 50%; box-shadow: inset 0 0 0 1.5px rgba({P["rgb_line"]},0.85)">'
                    f'<div style="position: absolute; left: 18px; top: 18px; width: {s}px; height: {s}px; border-radius: 50%; overflow: hidden">'
                    f'<img src="{PHOTOS[slot]}" alt="Маргарита Терво" style="width: 100%; height: 100%; object-fit: cover; object-position: 50% 28%"></div></div></div>')
    return (f'<div style="position: relative; width: {ring}px; max-width: 100%; margin: 0 auto">'
            f'<div style="position: relative; width: {ring}px; height: {h + 18}px">'
            f'<div style="position: absolute; left: 0; top: {h - s - 18 + 18}px; width: {ring}px; height: {ring}px; border-radius: 50%; '
            f'box-shadow: inset 0 0 0 1.5px rgba({P["rgb_line"]},0.85)"></div>'
            f'<div style="position: absolute; left: 18px; top: 18px; width: {s}px; height: {h}px; overflow: hidden; border-radius: 0 0 {s // 2}px {s // 2}px">'
            f'<div style="position: absolute; left: 0; top: {h - s}px; width: {s}px; height: {s}px; border-radius: 50%; '
            f'background: radial-gradient(circle at 40% 30%, #FFFFFF 0%, {P["cream"]} 55%, {P["cream2"]} 100%)"></div>'
            + (img if PHOTOS.get(slot) else
               f'<svg viewBox="0 0 400 500" width="{s}" height="{h}" aria-hidden="true" style="position: absolute; left: 0; top: 0">'
               f'<ellipse cx="200" cy="150" rx="68" ry="80" fill="{sil}"></ellipse>'
               f'<path d="M50 500 C55 350, 120 270, 200 270 C280 270, 345 350, 350 500 Z" fill="{sil}"></path></svg>')
            + f'</div></div>'
            + ("" if PHOTOS.get(slot) else
               f'<p style="margin: 14px 0 0; text-align: center; font-size: 13px; line-height: 1.45; color: '
               f'{"rgba(" + P["rgb_cream"] + ",0.75)" if dark else P["muted"]}">{icon("camera", 16)} {nb(caption)}</p>')
            + '</div>')

def diag(c, nextcol):
    P = c.P
    if c.m:
        vb, poly, ln = "0 0 390 60", "0,60 390,22 390,60", ("0", "50", "390", "12")
        hgt = 60
    else:
        vb, poly, ln = "0 0 1440 100", "0,100 1440,30 1440,100", ("0", "84", "1440", "14")
        hgt = 100
    return (f'<svg viewBox="{vb}" preserveAspectRatio="none" aria-hidden="true" style="position: absolute; left: 0; bottom: -1px; '
            f'width: 100%; height: {hgt}px"><polygon points="{poly}" fill="{nextcol}"></polygon>'
            f'<line x1="{ln[0]}" y1="{ln[1]}" x2="{ln[2]}" y2="{ln[3]}" stroke="{P["line"]}" stroke-width="1.3" opacity="0.75" '
            f'vector-effect="non-scaling-stroke"></line></svg>')

def divider(c, dark=False):
    col = c.P["accd"] if dark else c.P["line"]
    return (f'<div aria-hidden="true" style="display: flex; align-items: center; gap: 12px; margin: 0 0 24px; max-width: 220px">'
            f'<div style="flex: 1; height: 1px; background: {col}"></div>'
            f'<div style="width: 9px; height: 9px; transform: rotate(45deg); background: {col}"></div>'
            f'<div style="flex: 1; height: 1px; background: {col}"></div></div>')

def grid(c, cols_d, inner, gap=None, cols_m=1, extra=""):
    cols = cols_m if c.m else cols_d
    gap = gap if gap is not None else (14 if c.m else 24)
    return (f'<div style="display: grid; grid-template-columns: repeat({cols}, minmax(0, 1fr)); gap: {gap}px; {extra}">{inner}</div>')

def two(c, a, b, ratio="1fr 1fr", gap=72, align="center", m_rev=False):
    if c.m:
        first, second = (b, a) if m_rev else (a, b)
        return f'<div style="display: flex; flex-direction: column; gap: 36px">{first}{second}</div>'
    return (f'<div style="display: grid; grid-template-columns: {ratio}; gap: {gap}px; align-items: {align}">'
            f'<div style="min-width: 0">{a}</div><div style="min-width: 0">{b}</div></div>')

# ---------- blocks ----------
def b_header(c):
    P = c.P
    strip = (f'<div style="background: {P["dark_lo"]}; padding: 8px {22 if c.m else 60}px; display: flex; '
             f'justify-content: {"center" if c.m else "flex-end"}">'
             f'<a href="#" style="display: inline-flex; align-items: center; gap: 8px; min-height: 28px; font-size: 13px; '
             f'color: {P["accd"]}; text-decoration: none">Если вам сейчас очень тяжело {icon("arrow", 15)}</a></div>')
    brand = (f'<a href="#" style="display: flex; flex-direction: column; gap: 3px; text-decoration: none">'
             f'<span style="font-family: {SERIF}; font-weight: 700; font-size: {24 if c.m else 27}px; line-height: 1; color: {P["cream"]}">Маргарита Терво</span>'
             f'<span style="font-size: 11px; letter-spacing: 0.16em; text-transform: uppercase; color: {P["accd"]}">психолог, гештальт-подход</span></a>')
    if c.m:
        right = (f'<button type="button" aria-label="Открыть меню" style="width: 46px; height: 46px; border: 0; border-radius: 50%; '
                 f'background: rgba({P["rgb_cream"]},0.1); color: {P["cream"]}; display: flex; align-items: center; justify-content: center">'
                 f'{icon("menu", 22)}</button>')
        pad = "14px 22px"
    else:
        items = ["Обо мне", "С чем прийти", "Как я работаю", "Стоимость", "Статьи", "Материалы"]
        nav = "".join(f'<a href="#" style="font-size: 15px; color: rgba({P["rgb_cream"]},0.86); text-decoration: none">{t}</a>' for t in items)
        right = (f'<div style="display: flex; align-items: center; gap: 40px"><nav aria-label="Разделы" style="display: flex; gap: 28px">{nav}</nav>'
                 f'{btn(c, "Записаться")}</div>')
        pad = "20px 60px"
    hdr = (f'<header style="background: {P["dark"]}; padding: {pad}; display: flex; align-items: center; justify-content: space-between; '
           f'border-bottom: 1px solid rgba({P["rgb_line"]},0.25)">{brand}{right}</header>')
    return strip + hdr

def b_hero(c, nextbg):
    P = c.P
    pills = "".join(f'<span style="padding: {"7px 16px" if c.m else "9px 22px"}; border-radius: 999px; background: rgba({P["rgb_cream"]},0.1); '
                    f'font-family: {SERIF}; font-weight: 700; font-size: {20 if c.m else 25}px; line-height: 1.15; color: {P["cream"]}">{t}</span>'
                    for t in ["Тревога", "Стыд", "Контроль", "Отношения", "Внутренние конфликты"])
    info = (f'<div style="align-self: flex-start; display: flex; flex-direction: column; gap: 6px; padding: {"16px 22px" if c.m else "18px 30px"}; '
            f'border-radius: 26px; background: {P["cream"]}; box-shadow: 0 14px 30px rgba(0,0,0,0.25)">'
            f'<span style="display: flex; align-items: center; gap: 8px; font-size: {15 if c.m else 16}px; color: {P["text"]}">'
            f'<span style="color: {P["accl"]}; display: flex">{icon("pin", 18)}</span>Онлайн и&nbsp;очно, м.&nbsp;Невский проспект</span>'
            f'<span style="font-family: {SERIF}; font-weight: 700; font-size: {27 if c.m else 33}px; line-height: 1.05; color: {P["dark"]}">'
            f'Первая встреча <span style="color: {P["accl"]}">1000&nbsp;₽</span>'
            f'<span style="font-family: {SANS}; font-weight: inherit; font-size: 14px; color: {P["muted"]}"> · 55&nbsp;минут</span></span></div>')
    actions = (f'<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 12px 26px; margin-top: 8px">{btn(c, "Записаться", ic="msg")}'
               f'<a href="Home-A-{"m" if c.m else "d"}3.dc.html" style="display: inline-flex; align-items: center; gap: 8px; min-height: 44px; font-size: 15px; color: {P["accd"]}; '
               f'text-decoration: none">Как начинается работа {icon("down", 17)}</a></div>')
    text = (f'<div style="display: flex; flex-direction: column; gap: {16 if c.m else 20}px">'
            f'<p style="margin: 0; font-family: {SERIF}; font-style: italic; font-weight: 600; font-size: {22 if c.m else 28}px; color: {P["accd"]}">психолог, гештальт-подход</p>'
            f'<h1 style="margin: -6px 0 0; font-family: {SERIF}; font-weight: 700; font-size: {50 if c.m else 92}px; line-height: 0.98; '
            f'letter-spacing: -0.015em; color: {P["cream"]}">Маргарита Терво</h1>'
            f'<p style="margin: 0; font-family: {SERIF}; font-weight: 600; font-size: {26 if c.m else 34}px; line-height: 1.15; color: {P["cream"]}">'
            f'Психолог для взрослых и&nbsp;подростков</p>'
            f'<div style="display: flex; flex-wrap: wrap; gap: {8 if c.m else 12}px">{pills}</div>{info}{actions}</div>')
    light = (f'<div aria-hidden="true" style="position: absolute; right: -10%; top: -20%; width: 70%; height: 120%; '
             f'background: radial-gradient(circle, rgba({P["rgb_cream"]},0.07) 0%, rgba({P["rgb_cream"]},0) 60%)"></div>')
    bg = f"radial-gradient(circle at 30% 20%, {P['dark_hi']} 0%, {P['dark']} 55%, {P['dark_lo']} 100%)"
    if c.m:
        pic = portrait(c, 250, "Портрет без фона – после фотосессии")
        inner = f'<div style="display: flex; flex-direction: column; gap: 28px">{pic}{text}</div>'
        return (f'<section style="position: relative; overflow: hidden; background: {bg}; padding: 36px 0 96px">{light}'
                f'{container(c, inner)}{diag(c, P[nextbg])}</section>')
    # компьютер: фото без фона почти во всю высоту, по центру между текстом и правым краем
    if PHOTOS.get("hero"):
        fig = (f'<img src="{PHOTOS["hero"]}" alt="Маргарита Терво" style="position: absolute; left: 0; bottom: 0; width: 100%; height: 100%; '
               f'object-fit: contain; object-position: 50% 100%; filter: drop-shadow(0 24px 40px rgba(0,0,0,0.35))">')
    else:
        sil = f"rgba({P['rgb_cream']},0.13)"
        fig = (f'<svg viewBox="0 0 400 640" preserveAspectRatio="xMidYMax meet" aria-hidden="true" style="position: absolute; left: 0; bottom: 0; width: 100%; height: 100%">'
               f'<ellipse cx="200" cy="150" rx="74" ry="90" fill="{sil}"></ellipse>'
               f'<path d="M20 640 C 24 420, 100 300, 200 300 C 300 300, 376 420, 380 640 Z" fill="{sil}"></path></svg>'
               f'<p style="position: absolute; left: 50%; bottom: 150px; transform: translateX(-50%); width: 240px; margin: 0; text-align: center; '
               f'font-size: 13px; line-height: 1.45; color: rgba({P["rgb_cream"]},0.75)">Ваше фото без фона, в&nbsp;полный рост до&nbsp;пояса</p>')
    glow = (f'<div aria-hidden="true" style="position: absolute; left: calc(50% + 120px); bottom: 40px; width: 520px; height: 520px; border-radius: 50%; '
            f'background: radial-gradient(circle, rgba({P["rgb_line"]},0.28) 0%, rgba({P["rgb_line"]},0) 65%)"></div>')
    figure = (f'<div style="position: absolute; left: calc(50% + 120px); bottom: 0; width: 540px; height: 92%; z-index: 2">{fig}</div>')
    inner = f'<div style="max-width: 620px">{text}</div>'
    return (f'<section style="position: relative; overflow: hidden; background: {bg}; padding: 72px 0 170px; min-height: 760px; box-sizing: border-box">'
            f'{light}{glow}{container(c, inner)}{diag(c, P[nextbg])}{figure}</section>')

def b_video(c, **kw):
    """Вертикальное видео: рамка 9:16 не на всю ширину, вокруг – кольца."""
    P = c.P
    fw = 236 if c.m else 330
    cover = (f'<img src="{PHOTOS["video"]}" alt="" style="position: absolute; left: 0; top: 0; width: 100%; height: 100%; object-fit: cover">'
             if PHOTOS.get("video") else
             f'<div aria-hidden="true" style="position: absolute; left: -30%; top: 8%; opacity: 0.4">{m_depth(P, int(fw * 1.6), dark=True)}</div>')
    frame = (f'<div style="position: relative; z-index: 1; width: {fw}px; aspect-ratio: 9 / 16; overflow: hidden; border-radius: {26 if c.m else 32}px; '
             f'background: radial-gradient(circle at 30% 25%, {P["dark_hi"]} 0%, {P["dark"]} 60%, {P["dark_lo"]} 100%); '
             f'box-shadow: 0 0 0 1px rgba({P["rgb_line"]},0.5), 0 30px 60px rgba({P["rgb_dark"]},0.3); display: flex; align-items: center; justify-content: center">'
             f'{cover}'
             f'<button type="button" aria-label="Смотреть видео-знакомство" style="position: relative; width: {68 if c.m else 84}px; height: {68 if c.m else 84}px; '
             f'border: 0; border-radius: 50%; background: {P["cream"]}; color: {P["dark"]}; box-shadow: 0 0 0 10px rgba({P["rgb_line"]},0.25), 0 14px 30px rgba(0,0,0,0.35); '
             f'display: flex; align-items: center; justify-content: center">{icon("play", 28 if c.m else 34)}</button>'
             f'<p style="position: absolute; left: 18px; right: 18px; bottom: 16px; margin: 0; font-size: 12px; line-height: 1.4; color: rgba({P["rgb_cream"]},0.8)">Обложка – кадр из&nbsp;видео</p></div>')
    rings = (f'<div aria-hidden="true" style="position: absolute; left: 50%; top: 50%; width: {int(fw * 2.1)}px; height: {int(fw * 2.1)}px; '
             f'transform: translate(-50%, -50%); border-radius: 50%; box-shadow: inset 0 0 0 1px rgba({P["rgb_line"]},0.45)"></div>'
             f'<div aria-hidden="true" style="position: absolute; left: 50%; top: 50%; width: {int(fw * 1.55)}px; height: {int(fw * 1.55)}px; '
             f'transform: translate(-50%, -50%); border-radius: 50%; background: radial-gradient(circle, rgba({P["rgb_line"]},0.22) 0%, rgba({P["rgb_line"]},0) 70%)"></div>')
    stage = (f'<div style="position: relative; display: flex; justify-content: center; padding: {28 if c.m else 40}px 0">{rings}{frame}</div>')
    note = stub(c, "видео-визитка, размещаем через VK Видео или Rutube, не YouTube", mb=0)
    if c.m:
        inner = kicker(c, "о работе со мной в двух словах") + stage + note
    else:
        left = (kicker(c, "о работе со мной в двух словах", ) +
                p(c, "Пара минут, чтобы услышать мой голос и увидеть, как я говорю о работе.", maxw=440, mb=24) + note +
                f'<div aria-hidden="true" style="margin-top: 40px">{m_meet(P, 150)}</div>')
        inner = (f'<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 40px; align-items: center">'
                 f'<div style="min-width: 0">{left}</div><div style="min-width: 0">{stage}</div></div>')
    return section(c, "cream2", inner, tex=True, **kw)

def b_hard(c, **kw):
    P = c.P
    text = (h2(c, "Обратиться за помощью – важный, но часто сложный шаг", mb=24) +
            stub(c, "абзац для контакта: что чувствует человек, когда начинает искать психолога, и что ему сложно, страшно, тяжело. Пишем после интервью (вопросы 1–4)") +
            p(c, "Здесь можно спокойно понять, подхожу ли я вам, и найти что-то полезное уже сейчас.", mb=20) +
            f'<div style="display: flex; flex-wrap: wrap; gap: 12px">'
            f'<a href="#" style="display: inline-flex; align-items: center; gap: 10px; min-height: 48px; padding: 0 22px; border-radius: 999px; background: #FFFFFF; '
            f'box-shadow: 0 10px 24px rgba({P["rgb_dark"]},0.08); font-size: 15px; font-weight: 500; color: {P["dark"]}; text-decoration: none">{icon("book", 18)}Статьи</a>'
            f'<a href="#" style="display: inline-flex; align-items: center; gap: 10px; min-height: 48px; padding: 0 22px; border-radius: 999px; background: #FFFFFF; '
            f'box-shadow: 0 10px 24px rgba({P["rgb_dark"]},0.08); font-size: 15px; font-weight: 500; color: {P["dark"]}; text-decoration: none">{icon("file", 18)}Материалы</a></div>')
    pic = photo(c, "Атмосферный кадр без лица: кресло, свет из окна, чашка, ткань", "4 / 3" if c.m else "5 / 4", slot="atmo")
    return section(c, "cream", two(c, pic, text, "1fr 1fr", 72), tex=True, **kw)

def b_requests(c, **kw):
    P = c.P
    items = ["Переживания в отношениях: романтических, дружеских, семейных, рабочих", "Тревога, страхи, беспокойство",
             "Стыд, вина, самокритика", "Ощущение потери контроля", "Тревожно отделяться от родителей или близких",
             "«Хочу, но не могу»: одна часть хочет одного, другая другого", "Трудно принять решение: учеба, переезд, расставание, увольнение",
             "Не получается проявлять эмоции или справляться с ними", "Сложности адаптации: в новом коллективе, городе, профессии",
             "«Не понимаю что, но что-то не так»"]
    cells = "".join(
        f'<div style="display: flex; gap: 14px; align-items: flex-start; background: #FFFFFF; border-radius: 22px; padding: {"16px 18px" if c.m else "20px 24px"}; '
        f'box-shadow: 0 10px 26px rgba({P["rgb_dark"]},0.07)">'
        f'<span aria-hidden="true" style="flex: none; width: 12px; height: 12px; margin-top: 7px; border-radius: 50%; box-shadow: 0 0 0 1.5px {P["line"]}, 0 0 0 5px rgba({P["rgb_line"]},0.14)"></span>'
        f'<span style="font-size: {c.body}px; line-height: 1.5; color: {P["text"]}">{nb(t)}</span></div>' for t in items)
    lim = ["дети и подростки младше 15 лет", "наркотические и алкогольные зависимости в активной фазе употребления",
           "острые кризисные состояния", "шизофрения и расстройства этого спектра", "сексуальные дисфункции",
           "работа с парой или семьей целиком"]
    def lcell(t):
        return (f'<div style="display: flex; gap: 12px; align-items: flex-start; color: {P["accd"]}">{icon("x", 22)}'
                f'<span style="font-size: {c.body}px; line-height: 1.5; color: {P["cream"]}">{nb(t)}'
                + (f'<br><a href="#" style="display: inline-flex; align-items: center; gap: 6px; margin-top: 4px; min-height: 32px; font-size: 14px; color: {P["accd"]}; text-decoration: none">'
                   f'Если вам сейчас очень тяжело {icon("arrow", 15)}</a>' if "кризис" in t else "") + '</span></div>')
    gap = 18 if c.m else 22
    col = lambda items: f'<div style="display: flex; flex-direction: column; gap: {gap}px; min-width: 0">{"".join(lcell(t) for t in items)}</div>'
    if c.m:
        lgrid = col(lim)
    else:
        # две независимые колонки: расстояния между строками в каждой одинаковые
        lgrid = (f'<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 22px 40px; align-items: start">'
                 f'{col([lim[0], lim[2], lim[4]])}{col([lim[1], lim[3], lim[5]])}</div>')
    limits = darkplate(c,
        kicker(c, "мои границы", dark=True) +
        f'<h3 style="margin: 0 0 14px; font-family: {SERIF}; font-weight: 700; font-size: {32 if c.m else 44}px; line-height: 1.05; color: {P["cream"]}">С&nbsp;чем я&nbsp;не&nbsp;работаю</h3>' +
        p(c, "Честно говорю об этом заранее, чтобы вы не тратили время и деньги:", dark=True, muted=True, mb=24) + lgrid)
    inner = (kicker(c, "ваш запрос") + h2(c, "С чем можно прийти") + grid(c, 2, cells, gap=12 if c.m else 16) +
             f'<div style="margin: {28 if c.m else 36}px 0 {36 if c.m else 56}px">' +
             p(c, "Работаю со взрослыми и подростками от 15 лет.", mb=16, extra="font-weight: 500") +
             stub(c, "своя фраза о том, что можно прийти без готовой цели, и о том, что цель работы — качество жизни, а не «избавиться любой ценой». После интервью (вопросы 5–6)", mb=0) +
             '</div>' + limits)
    return section(c, "cream", inner, sid="requests", tex=True, **kw)

def b_qual(c, **kw):
    P = c.P
    edu = [("Факультет психологии СПбГУ", "2026, красный диплом"),
           ("Московский гештальт институт, базовый курс", "1 ступень, в процессе"),
           ("Основы психологической работы с детьми и подростками", "«Архитектура будущего», 2024"),
           ("Профессионально-личностное консультирование", "Центр при психологической клинике СПбГУ, 2025")]
    rows = "".join(
        f'<div style="display: flex; gap: 16px; align-items: flex-start; padding: {"14px 0" if c.m else "16px 0"}; border-top: 1px solid rgba({P["rgb_line"]},0.3)">'
        f'<span aria-hidden="true" style="flex: none; width: 9px; height: 9px; margin-top: 11px; transform: rotate(45deg); background: {P["line"]}"></span>'
        f'<div><p style="margin: 0; font-family: {SERIF}; font-weight: 700; font-size: {22 if c.m else 25}px; line-height: 1.2; color: {P["dark"]}">{nb(a)}</p>'
        f'<p style="margin: 4px 0 0; font-size: {c.small}px; line-height: 1.5; color: {P["muted"]}">{nb(b)}</p></div></div>' for a, b in edu)
    left = (kicker(c, "образование") + h2(c, "Квалификация", mb=20) + rows +
            f'<div style="margin-top: {24 if c.m else 32}px; padding-top: 22px; border-top: 1px solid rgba({P["rgb_line"]},0.3)">' +
            p(c, "Если вам так же важно знать что-то обо мне как о человеке, можете заглянуть на отдельную страницу.", mb=4) +
            link(c, "Обо мне", mt=0) + '</div>')
    docs = "".join(
        f'<div style="display: flex; flex-direction: column; gap: 10px">'
        f'<div style="aspect-ratio: {r}; border-radius: 14px; background: #FFFFFF; box-shadow: 0 10px 24px rgba({P["rgb_dark"]},0.1); '
        f'padding: 10px; display: flex"><div style="flex: 1; border-radius: 6px; background: linear-gradient(180deg, {P["cream"]}, {P["cream2"]}); '
        f'display: flex; align-items: center; justify-content: center; color: {P["line"]}">{icon("doc", 26)}</div></div>'
        f'<span style="font-size: 12px; line-height: 1.4; color: {P["muted"]}">{nb(t)}</span></div>'
        for t, r in [("Диплом СПбГУ", "3 / 4"), ("Сертификат «Архитектура будущего»", "3 / 4"), ("Сертификат клиники СПбГУ", "3 / 4")])
    right = (photo(c, "Марго за работой: записи, книги, ноутбук", "4 / 3" if c.m else "1 / 1", slot="work") +
             f'<div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; margin-top: 22px">{docs}</div>'
             '')
    return section(c, "cream2", two(c, left, right, "1fr 0.9fr", 80, "start"), tex=True, **kw)

def b_values(c, **kw):
    P = c.P
    vals = [("lock", "Конфиденциальность", p(c, "Всё, что вы рассказываете, остаётся между нами. Исключения: угроза жизни и здоровью и случаи, предусмотренные законом.", mb=10) +
             p(c, "Работаю в соответствии с этическим кодексом Московского гештальт института.", size=c.small, muted=True, mb=0)),
            ("doc", "Договорённости", stub(c, "как ценность проявляется на сессии — после интервью (вопрос 7)", mb=0)),
            ("heart", "Искренность", stub(c, "после интервью (вопрос 7)", mb=0)),
            ("meet", "Контакт и Встреча", stub(c, "что для меня Контакт и Встреча — после интервью (вопрос 8)", mb=0))]
    cells = "".join(card(c,
        f'<div style="display: flex; flex-direction: column; gap: 18px">{ringcircle(c, icon(i, 24), 54)}'
        f'<h3 style="margin: 0; font-family: {SERIF}; font-weight: 700; font-size: {26 if c.m else 30}px; line-height: 1.1; color: {P["dark"]}">{nb(t)}</h3>'
        f'<div>{body}</div></div>') for i, t, body in vals)
    inner = (kicker(c, "как я работаю") + h2(c, "Ценности в работе") + grid(c, 2, cells, gap=16 if c.m else 24))
    return section(c, "cream", inner, tex=True, **kw)

def b_gestalt(c, **kw):
    P = c.P
    cols = "".join(
        f'<div style="display: flex; flex-direction: column; gap: 16px; align-items: flex-start">{f(P, 120 if c.m else 150)}'
        f'<h3 style="margin: 0; font-family: {SERIF}; font-weight: 700; font-size: {25 if c.m else 28}px; color: {P["dark"]}">Идея {n}</h3>'
        f'{stub(c, "одна из трёх идей гештальта, самых важных для клиентов — после интервью (вопросы 9–10)", mb=0)}</div>'
        for n, f in zip([1, 2, 3], MOTIFS))
    inner = (kicker(c, "как я работаю") + h2(c, "Гештальт простыми словами", mb=22) +
             p(c, "Гештальт помогает расширить контакт — с миром, с другими людьми и со своими переживаниями. Когда контакт с чувствами становится лучше, "
                  "проще заметить свои потребности и найти разные, в том числе творческие, способы их удовлетворить.", maxw=760, mb=40 if c.m else 56) +
             grid(c, 3, cols, gap=36 if c.m else 48) + f'<div style="margin-top: 28px">{link(c, "Статья «Гештальт простыми словами»", mt=0)}</div>')
    return section(c, "cream2", inner, tex=True, **kw)

def b_support(c, **kw):
    P = c.P
    sup = ["Личная терапия", "Индивидуальная супервизия в гештальт-подходе", "Групповая супервизия в гештальт-подходе",
           "Групповая супервизия с коллегами разных подходов", "Интервизии с коллегами разных подходов"]
    rme = 25 if c.m else 66
    me = (f'<div style="flex: none; width: {rme * 2}px; height: {rme * 2}px; border-radius: 50%; '
          f'background: radial-gradient(circle at 40% 30%, #FFFFFF 0%, {P["cream"]} 60%, {P["cream2"]} 100%); '
          f'outline: 1px solid {P["line"]}; outline-offset: {4 if c.m else 7}px; box-shadow: 0 10px 24px rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; '
          f'font-family: {SERIF}; font-weight: 700; font-size: {24 if c.m else 54}px; color: {P["dark"]}">Я</div>')
    session = (f'<div style="display: flex; align-items: center; justify-content: center; text-align: center; min-height: 58px; padding: 12px 26px; '
               f'border-radius: 999px; background: {P["accd"]}; font-family: {SERIF}; font-weight: 700; font-size: {22 if c.m else 26}px; color: {P["dark"]}">'
               f'Наша с&nbsp;вами сессия</div>')
    mk = uid("ar")
    marker = (f'<defs><marker id="{mk}" viewBox="0 0 12 12" refX="9" refY="6" markerWidth="11" markerHeight="11" orient="auto" markerUnits="userSpaceOnUse">'
              f'<path d="M1 1 L11 6 L1 11 Z" fill="{P["accd"]}"></path></marker></defs>')
    dash = f'fill="none" stroke="{P["accd"]}" stroke-width="3" stroke-linecap="round" stroke-dasharray="0.1 9" marker-end="url(#{mk})"'
    if c.m:
        # пять опор в кругах вокруг «Я», от каждого – стрелка к «Я»
        # опоры полукругом над «Я»: слева, слева-сверху, сверху, справа-сверху, справа
        W, R = 346, 54
        cs = [(173, 68), (83, 157), (263, 157), (56, 296), (290, 296)]
        mex, mey = 173, 318
        H = 500
        arrows = ""
        for (x, y) in cs:
            dx, dy = mex - x, mey - y
            d = (dx * dx + dy * dy) ** 0.5
            ux, uy = dx / d, dy / d
            x1, y1 = x + ux * (R + 5), y + uy * (R + 5)
            x2, y2 = mex - ux * (rme + 10), mey - uy * (rme + 10)
            arrows += f'<path d="M{x1:.0f} {y1:.0f} L{x2:.0f} {y2:.0f}" {dash}></path>'
        arrows += f'<path d="M{mex} {mey + rme + 12} L{mex} {H - 76}" {dash}></path>'
        svg = f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" aria-hidden="true" style="position: absolute; left: 0; top: 0">{marker}{arrows}</svg>'
        circles = "".join(
            f'<div style="position: absolute; left: {x - R}px; top: {y - R}px; width: {R * 2}px; height: {R * 2}px; border-radius: 50%; box-sizing: border-box; '
            f'padding: 0; background: rgba({P["rgb_cream"]},0.1); outline: 1px solid rgba({P["rgb_line"]},0.7); outline-offset: 3px; '
            f'display: flex; align-items: center; justify-content: center; text-align: center">'
            f'<span style="display: block; max-width: 94px; font-family: {SERIF}; font-weight: 700; font-size: 12px; line-height: 1.08; '
            f'color: {P["cream"]}">{nb(t)}</span></div>' for (x, y), t in zip(cs, sup))
        mepos = f'<div style="position: absolute; left: {mex - rme}px; top: {mey - rme}px">{me}</div>'
        sespos = f'<div style="position: absolute; left: 38px; right: 38px; top: {H - 62}px">{session}</div>'
        schema = f'<div style="position: relative; width: {W}px; height: {H}px; margin: 0 auto">{svg}{circles}{mepos}{sespos}</div>'
    else:
        pill = lambda t: (f'<div style="display: flex; align-items: center; min-height: 64px; box-sizing: border-box; padding: 10px 24px; border-radius: 999px; '
                          f'background: rgba({P["rgb_cream"]},0.09); font-size: 16px; line-height: 1.35; color: {P["cream"]}">{nb(t)}</div>')
        H = 5 * 64 + 4 * 14
        ys = [32 + i * 78 for i in range(5)]
        SW = 190
        lines = "".join(f'<path d="M8 {y} C 70 {y}, 110 {H // 2 + (i - 2) * 30}, {SW - 14} {H // 2 + (i - 2) * 30}" {dash}></path>'
                        for i, y in enumerate(ys))
        conv = f'<svg width="{SW}" height="{H}" viewBox="0 0 {SW} {H}" aria-hidden="true" style="flex: none">{marker}{lines}</svg>'
        harrow = (f'<svg width="110" height="20" viewBox="0 0 110 20" aria-hidden="true" style="flex: none; margin-left: 10px">{marker.replace(mk, mk + "h")}'
                  f'<path d="M14 10 L98 10" {dash.replace(mk, mk + "h")}></path></svg>')
        schema = (f'<div style="display: flex; align-items: center">'
                  f'<div style="flex: 1 1 0; min-width: 0; display: flex; flex-direction: column; gap: 14px">{"".join(pill(t) for t in sup)}</div>'
                  f'{conv}{me}{harrow}<div style="flex: 0 0 230px">{session}</div></div>')
    defs = (f'<div style="display: grid; grid-template-columns: {"1fr" if c.m else "1fr 1fr"}; gap: {16 if c.m else 28}px; margin-top: {36 if c.m else 56}px">'
            f'<div style="border-radius: 24px; padding: 22px 24px; background: rgba({P["rgb_cream"]},0.06)">'
            f'<p style="margin: 0; font-size: {c.body}px; line-height: 1.6; color: {P["cream"]}"><span style="font-family: {SERIF}; font-weight: 700; font-size: 1.25em; color: {P["accd"]}">Супервизия</span> – '
            f'{nb("разбор сложных моментов работы с более опытным специалистом, один на один или в группе.")}</p></div>'
            f'<div style="border-radius: 24px; padding: 22px 24px; background: rgba({P["rgb_cream"]},0.06)">'
            f'<p style="margin: 0; font-size: {c.body}px; line-height: 1.6; color: {P["cream"]}"><span style="font-family: {SERIF}; font-weight: 700; font-size: 1.25em; color: {P["accd"]}">Интервизия</span> – '
            f'{nb("такой же разбор с коллегами на равных. Всегда без имён и деталей, по которым вас можно узнать.")}</p></div></div>'
            + p(c, "За нашей работой стоит не только мой опыт, но и опыт моих коллег и наставников.", dark=True, mb=0,
                extra=f"margin-top: 28px; font-family: {SERIF}; font-style: italic; font-weight: 600; font-size: {22 if c.m else 27}px; line-height: 1.3; color: {P['accd']}"))
    inner = (kicker(c, "опора в работе", dark=True) +
             f'<h2 style="margin: 0 0 20px; font-family: {SERIF}; font-weight: 700; font-size: {c.h2}px; line-height: 1.05; color: {P["cream"]}">'
             f'Я&nbsp;работаю <em style="font-style: italic; font-weight: 600; color: {P["accd"]}">не&nbsp;одна</em></h2>' +
             p(c, "Я человек, а у всех людей есть свои ограничения, и я отношусь к этому ответственно. Поэтому у меня выстроена система опор – вот как она устроена:",
               dark=True, muted=True, mb=36 if c.m else 52, maxw=760) + schema + defs)
    art = (bgart("cozy1", "right: -70px; top: -10px; width: 330px", 0.32) if c.m else
           bgart("cozy1", "right: -40px; top: -60px; width: 640px", 0.34))
    return section(c, "dark", inner, art=art, **kw)


def b_sessions(c, **kw):
    P = c.P
    rows = [("Не командую вами, не «тяну» в ту или иную сторону, не давлю",
             "Способствую тому, чтобы вы могли говорить о том и так, как хочется вам. Если мне кажется, что мы далеко ушли от темы запроса, могу мягко это обозначить и поинтересоваться, хотелось бы ли вам вернуться к изначальной теме. Если у меня есть какое-то предположение, открыто выношу его на обсуждение."),
            ("Не оцениваю", "Обращаюсь к вашим чувствам или говорю, что чувствую относительно ваших слов."),
            ("Не даю советов и, соответственно, не агитирую в сторону их выполнения",
             "Даю рекомендации в рамках моей компетенции: техники, упражнения, обращение к смежным специалистам."),
            ("Не перевожу внимание на свою жизнь и свои переживания",
             "И ваше, и свое внимание направляю на вас. Этот час для того, чтобы своими мыслями, чувствами и происшествиями могли поделиться вы. Я говорю о своих чувствах или опыте только относительно ваших слов и процесса работы, и только если вижу это полезным и уместным.")]
    if c.m:
        # «не делаю» выше и левее, стрелка к «делаю» ниже и правее; пары чуть смещены, чтобы композиция дышала
        offs = [(0, 54, 78), (22, 34, 74), (6, 60, 80), (28, 40, 72)]
        out = ""
        for n, ((a, b), (x1, x2, wa)) in enumerate(zip(rows, offs)):
            mk = uid("sa")
            arrow = (f'<svg width="120" height="52" viewBox="0 0 120 52" aria-hidden="true" style="display: block; margin: 10px 0 10px {x1 + 18}px">'
                     f'<defs><marker id="{mk}" viewBox="0 0 12 12" refX="9" refY="6" markerWidth="10" markerHeight="10" orient="auto" markerUnits="userSpaceOnUse">'
                     f'<path d="M1 1 L11 6 L1 11 Z" fill="{P["accd"]}"></path></marker></defs>'
                     f'<path d="M6 4 C 8 34, 40 44, {x2 - x1 + 30} 46" fill="none" stroke="{P["accd"]}" stroke-width="3" stroke-linecap="round" '
                     f'stroke-dasharray="0.1 8" marker-end="url(#{mk})"></path></svg>')
            deco = ""
            if n % 2 == 0:
                deco = (f'<div aria-hidden="true" style="position: absolute; right: {-30 + n * 6}px; top: -14px; width: 74px; height: 74px; border-radius: 50%; '
                        f'box-shadow: inset 0 0 0 1px rgba({P["rgb_line"]},0.4)"></div>')
            else:
                deco = (f'<div aria-hidden="true" style="position: absolute; left: -36px; bottom: 6px; width: 52px; height: 52px; border-radius: 50%; '
                        f'background: radial-gradient(circle, rgba({P["rgb_line"]},0.3) 0%, rgba({P["rgb_line"]},0) 70%)"></div>')
            out += (f'<div style="position: relative; margin: 0 0 {44 if n < 3 else 28}px">{deco}'
                    f'<p style="position: relative; margin: 0; margin-left: {x1}px; width: {wa}%; font-family: {SERIF}; font-weight: 700; font-size: 24px; line-height: 1.15; '
                    f'text-wrap: balance; color: {P["cream"]}">{nb(a)}</p>{arrow}'
                    f'<div style="position: relative; margin-left: {x2}px; padding: 16px 18px; border-radius: 22px; background: rgba({P["rgb_cream"]},0.08)">'
                    f'<p style="margin: 0; font-size: 16px; line-height: 1.58; color: rgba({P["rgb_cream"]},0.86)">{nb(b)}</p></div></div>')
        inner = (kicker(c, "как я работаю", dark=True) + h2(c, "На сессиях я", dark=True, mb=36) + out +
                 link(c, "Подробнее обо мне", dark=True, mt=0))
        return section(c, "dark", inner, art=bgart("cozy2", "right: -80px; top: -20px; width: 320px", 0.26), **kw)
    out = ""
    for a, b in rows:
        left = (f'<p style="margin: 0; font-family: {SERIF}; font-weight: 700; font-size: 30px; line-height: 1.18; color: {P["cream"]}">{nb(a)}</p>')
        right = p(c, b, dark=True, muted=True, mb=0)
        lay = (f'<div style="display: grid; grid-template-columns: 0.9fr 1.1fr; gap: 56px; align-items: start">{left}{right}</div>')
        out += f'<div style="padding: 32px 0; border-top: 1px solid rgba({P["rgb_line"]},0.35)">{lay}</div>'
    inner = (kicker(c, "как я работаю", dark=True) + h2(c, "На сессиях я", dark=True, mb=24) + out +
             f'<div style="border-top: 1px solid rgba({P["rgb_line"]},0.35); padding-top: 16px">{link(c, "Подробнее обо мне", dark=True, mt=0)}</div>')
    return section(c, "dark", inner, art=bgart("cozy2", "right: -60px; top: -80px; width: 600px", 0.28), **kw)


def start_pic(P, w):
    if PHOTOS.get("start"):
        return f'<img src="{PHOTOS["start"]}" alt="" style="display: block; width: {w}px; max-width: 100%; height: auto">'
    return start_graphic(P, w)


def start_graphic(P, w):
    """Своя графика «путь»: круги вглубь, по ним пунктирная тропа через четыре шага."""
    h = int(w * 1.2)
    rings = "".join(f'<circle cx="230" cy="250" r="{r}" fill="none" stroke="{P["line"]}" stroke-width="{sw}" opacity="{op}"></circle>'
                    for r, sw, op in [(210, 1, .25), (172, 1, .35), (134, 1.2, .5), (96, 1.2, .65)])
    pts = [(78, 470), (150, 330), (300, 300), (330, 140)]
    path = (f'<path d="M30 540 C 60 520, 70 495, 78 470 S 110 360, 150 330 S 250 330, 300 300 S 360 200, 330 140 S 300 70, 360 40" fill="none" '
            f'stroke="{P["line"]}" stroke-width="3.2" stroke-linecap="round" stroke-dasharray="0.1 11"></path>')
    nodes = ""
    for n, (x, y) in enumerate(pts, 1):
        nodes += (f'<circle cx="{x}" cy="{y}" r="34" fill="#FFFFFF"></circle>'
                  f'<circle cx="{x}" cy="{y}" r="34" fill="none" stroke="{P["line"]}" stroke-width="1.4"></circle>'
                  f'<circle cx="{x}" cy="{y}" r="44" fill="none" stroke="{P["line"]}" stroke-width="0.8" opacity="0.45"></circle>'
                  f'<text x="{x}" y="{y + 11}" text-anchor="middle" font-family="Cormorant Garamond, Georgia, serif" font-weight="700" font-size="32" fill="{P["accl"]}">{n}</text>')
    glow = (f'<defs><radialGradient id="sg{w}" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="{P["line"]}" stop-opacity="0.32"></stop>'
            f'<stop offset="1" stop-color="{P["line"]}" stop-opacity="0"></stop></radialGradient></defs>'
            f'<circle cx="230" cy="250" r="230" fill="url(#sg{w})"></circle>')
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 460 552" aria-hidden="true" style="display: block; max-width: 100%">'
            f'{glow}{rings}{path}{nodes}<circle cx="360" cy="40" r="6" fill="{P["line"]}"></circle></svg>')


def b_start(c, **kw):
    P = c.P
    steps = [("Переписка", "Можно в нескольких предложениях описать, что вас беспокоит, и задать вопросы, которые важны вам перед началом работы. Если сложно сформулировать, хватит и пары слов, даже «не понимаю, что со мной, но что-то не так». Если запрос не в моих компетенциях, я скажу об этом сразу и подскажу, к какому специалисту обратиться. Затем договариваемся о времени и формате первой встречи.",
              "Если вам менее 18 лет, до начала работы нужно, чтобы родители подписали согласие на нее."),
             ("Первичная консультация: 55 минут, 1000 ₽", "Говорим о том, что вас беспокоит: как давно, в каких ситуациях, как это сказывается на вашей жизни. Можно говорить в своем темпе и не отвечать на то, о чем пока не хочется. Вместе формулируем, к чему вы хотели бы прийти, и обсуждаем, что работа может дать, а что нет. После встречи вы спокойно решаете, продолжать ли. Первая встреча ни к чему не обязывает.", None),
             ("Психологический контракт", "Договариваемся о том, какой вклад в работу будет внесен с вашей и с моей стороны, какие условия нам необходимо соблюсти для успешной работы.", None),
             ("Дальнейшая работа", "Встречаемся регулярно и движемся к цели, которую сформулировали вместе. Цель может меняться, и это нормально. Время от времени сверяемся, что происходит и подходит ли вам работа.", None)]
    items = ""
    for n, (t, body, note) in enumerate(steps, 1):
        num = ringcircle(c, f'<span style="font-family: {SERIF}; font-weight: 700; font-size: 24px; color: {P["accl"]}">{n}</span>', 46)
        notehtml = (f'<p style="margin: 12px 0 0; padding: 12px 16px; border-radius: 16px; background: rgba({P["rgb_line"]},0.13); font-size: {c.small}px; '
                    f'line-height: 1.5; color: {P["text"]}">{nb(note)}</p>' if note else "")
        items += (f'<details style="background: #FFFFFF; border-radius: 24px; box-shadow: 0 10px 26px rgba({P["rgb_dark"]},0.07)">'
                  f'<summary style="list-style: none; cursor: pointer; display: flex; align-items: center; gap: 16px; min-height: 72px; '
                  f'padding: {"12px 16px" if c.m else "14px 22px"}">{num}'
                  f'<span style="flex: 1; font-family: {SERIF}; font-weight: 700; font-size: {22 if c.m else 26}px; line-height: 1.15; color: {P["dark"]}">{nb(t)}</span>'
                  f'<span aria-hidden="true" style="flex: none; width: 36px; height: 36px; border-radius: 50%; box-shadow: 0 0 0 1.5px {P["line"]}; '
                  f'display: flex; align-items: center; justify-content: center; color: {P["accl"]}">{icon("chev", 18)}</span></summary>'
                  f'<div style="padding: 0 {18 if c.m else 26}px {20 if c.m else 24}px {18 if c.m else 84}px">{p(c, body, mb=0)}{notehtml}</div></details>')
        if n < len(steps):
            items += (f'<div aria-hidden="true" style="height: 18px; width: 3px; margin-left: {39 if c.m else 45}px; '
                      f'background-image: radial-gradient(circle, {P["line"]} 1.4px, transparent 1.6px); background-size: 3px 8px; background-repeat: repeat-y"></div>')
    prepay = darkplate(c, f'<p style="margin: 0; font-family: {SERIF}; font-weight: 700; font-size: {23 if c.m else 27}px; line-height: 1.2; color: {P["cream"]}">'
                          f'Запись утверждается по&nbsp;стопроцентной предоплате</p>', pad=22 if c.m else 28)
    steps_col = (f'<div style="display: flex; flex-direction: column">{items}</div>'
                 f'<div style="margin-top: {20 if c.m else 28}px">{prepay}</div>'
                 '')
    if c.m:
        inner = (kicker(c, "шаг за шагом") + h2(c, "Начало работы", mb=22) +
                 f'<div style="display: flex; justify-content: center; margin: 0 0 22px">{start_pic(P, 300)}</div>' + steps_col)
    else:
        left = (kicker(c, "шаг за шагом") + h2(c, "Начало работы", mb=24) +
                f'<div style="margin-top: 8px">{start_pic(P, 440)}</div>')
        inner = (f'<div style="display: grid; grid-template-columns: 460px 1fr; gap: 64px; align-items: start; max-width: 1140px">'
                 f'<div style="min-width: 0">{left}</div><div style="min-width: 0; max-width: 600px; padding-top: 12px">{steps_col}</div></div>')
    return section(c, "cream", inner, sid="start", tex=True, **kw)


def b_terms(c, **kw):
    P = c.P
    prices = [("Первичная консультация", "вне зависимости от формата", "1000 ₽", True),
              ("Онлайн", "в Яндекс Телемосте", "2700 ₽", False),
              ("Очно", "Санкт-Петербург, Думская ул., 5/22, м. Невский проспект и Гостиный двор", "3200 ₽", False),
              ("Для студентов", "вне зависимости от формата", "2000 ₽", False),
              ("Для получающих государственную социальную помощь", "вне зависимости от формата", "1500 ₽", False)]
    cells = ""
    for t, sub, price, feat in prices:
        tc, sc, pc = (P["cream"], f"rgba({P['rgb_cream']},0.78)", P["accd"]) if feat else (P["dark"], P["muted"], P["accl"])
        inner = (f'<div style="display: flex; flex-direction: column; height: 100%; gap: 8px">'
                 f'<h3 style="margin: 0; font-family: {SERIF}; font-weight: 700; font-size: {24 if c.m else 27}px; line-height: 1.12; color: {tc}">{nb(t)}</h3>'
                 f'<p style="margin: 0; font-size: {c.small}px; line-height: 1.5; color: {sc}">{nb(sub)}</p>'
                 f'<p style="margin: auto 0 0; padding-top: 14px; font-family: {SERIF}; font-weight: 700; font-size: {40 if c.m else 48}px; line-height: 1; color: {pc}">{nb(price)}</p></div>')
        cells += darkplate(c, inner, pad=24 if c.m else 30) if feat else card(c, inner, pad=24 if c.m else 30)
    cells += card(c, f'<div style="display: flex; flex-direction: column; gap: 14px">{ringcircle(c, icon("clock", 24), 54)}'
                     f'<p style="margin: 0; font-family: {SERIF}; font-weight: 700; font-size: {24 if c.m else 27}px; line-height: 1.15; color: {P["dark"]}">Будни, 11:00–20:00 по&nbsp;Москве</p>'
                     f'<p style="margin: 0; font-size: {c.small}px; color: {P["muted"]}">Сессия длится 55&nbsp;минут</p></div>', pad=24 if c.m else 30)
    rules = (f'<div style="display: grid; grid-template-columns: {"1fr" if c.m else "0.8fr 1.2fr"}; gap: {16 if c.m else 32}px; align-items: center; margin-top: {24 if c.m else 32}px">'
             + darkplate(c, f'<p style="margin: 0; font-family: {SERIF}; font-weight: 700; font-size: {23 if c.m else 27}px; line-height: 1.2; color: {P["cream"]}">'
                            f'Перенос и&nbsp;отмена не&nbsp;позже чем за&nbsp;24&nbsp;часа</p>', pad=24 if c.m else 30)
             + p(c, "Онлайн-встречи проходят с включенными камерой и микрофоном у обоих, клиенту необходимо организовать себе уединенное пространство на время встречи.", mb=0)
             + '</div>')
    mapbox = (f'<a href="#" aria-label="Открыть кабинет на Яндекс Картах" style="position: relative; display: block; overflow: hidden; border-radius: {20 if c.m else 28}px; aspect-ratio: 4 / 3; '
              f'background: {P["cream"]}; text-decoration: none; box-shadow: 0 14px 34px rgba({P["rgb_dark"]},0.08)">'
              f'<svg viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" aria-hidden="true" style="position: absolute; left: 0; top: 0; width: 100%; height: 100%">'
              f'<g stroke="rgba({P["rgb_line"]},0.45)" stroke-width="10" fill="none" stroke-linecap="round"><path d="M-20 90 L420 60"></path><path d="M-20 210 L420 190"></path>'
              f'<path d="M120 -20 L150 320"></path><path d="M290 -20 L270 320"></path></g>'
              f'<path d="M-20 140 C 100 130, 220 160, 420 120" stroke="rgba({P["rgb_dark"]},0.18)" stroke-width="16" fill="none"></path></svg>'
              f'<div style="position: absolute; left: 50%; top: 42%; transform: translate(-50%, -50%); width: {36 if c.m else 52}px; height: {36 if c.m else 52}px; border-radius: 50%; background: {P["dark"]}; '
              f'color: {P["accd"]}; display: flex; align-items: center; justify-content: center; box-shadow: 0 10px 22px rgba(0,0,0,0.3)">{icon("pin", 24)}</div>'
              f'<p style="position: absolute; left: {8 if c.m else 18}px; right: {8 if c.m else 18}px; bottom: {8 if c.m else 14}px; margin: 0; padding: {"6px 8px" if c.m else "10px 14px"}; border-radius: {10 if c.m else 14}px; background: rgba(255,255,255,0.92); '
              f'font-size: {11 if c.m else 13}px; line-height: 1.35; color: {P["text"]}">Думская ул., 5/22 · карта картинкой, по&nbsp;нажатию — Яндекс Карты</p></a>')
    photos = grid(c, 2, photo(c, "Кабинет на Думской: общий вид и место клиента", slot="office", extra="border-radius: 20px" if c.m else "") + mapbox,
                  gap=10 if c.m else 24, cols_m=2, extra=f"margin-top: {36 if c.m else 56}px")
    inner = (kicker(c, "стоимость и формат") + h2(c, "Условия работы") + grid(c, 3, cells, gap=14 if c.m else 24) + rules + photos)
    return section(c, "cream2", inner, sid="terms", tex=True, **kw)

def b_contact(c, **kw):
    P = c.P
    example = (f'<div style="margin-top: 28px; border-radius: 24px; padding: {"18px 20px" if c.m else "22px 26px"}; background: rgba({P["rgb_cream"]},0.07)">'
               f'<p style="margin: 0 0 10px; font-family: {SERIF}; font-style: italic; font-weight: 600; font-size: 21px; color: {P["accd"]}">можно начать с такого сообщения</p>'
               f'{stub(c, "пример первого сообщения — напишем на этапе деталей", dark=True, mb=14)}'
               f'<button type="button" style="display: inline-flex; align-items: center; gap: 8px; min-height: 44px; padding: 0 18px; border: 0; border-radius: 999px; '
               f'background: rgba({P["rgb_cream"]},0.12); color: {P["cream"]}; font-family: inherit; font-size: 14px">{icon("copy", 17)}Скопировать</button></div>')
    text = (kicker(c, "давайте знакомиться", dark=True) + h2(c, "Запись", dark=True, mb=20) +
            p(c, "Записаться и задать вопросы можно в личных сообщениях. Также буду рада ответить на оставшиеся вопросы.", dark=True, muted=True, mb=28) +
            f'<div style="display: flex; flex-wrap: wrap; gap: 12px">{btn(c, "Написать в&nbsp;Telegram", ic="send")}{btn(c, "Написать во&nbsp;ВКонтакте", "ghost", ic="msg")}</div>' +
            example)
    return section(c, "dark", text if c.m else f'<div style="max-width: 760px">{text}</div>', sid="contact", **kw)

def b_faq(c, **kw):
    P = c.P
    rows = ""
    for i in range(1, 8):
        op = " open" if i == 1 else ""
        ans = (f'<div style="padding: 0 {20 if c.m else 28}px {20 if c.m else 24}px">'
               f'{stub(c, "ответ — Марго пишет на этапе деталей", mb=0)}</div>' if i == 1 else
               f'<div style="padding: 0 {20 if c.m else 28}px {20 if c.m else 24}px">{stub(c, "ответ на этапе деталей", mb=0)}</div>')
        rows += (f'<details{op} style="background: #FFFFFF; border-radius: 22px; box-shadow: 0 10px 26px rgba({P["rgb_dark"]},0.07)">'
                 f'<summary style="list-style: none; cursor: pointer; display: flex; align-items: center; justify-content: space-between; gap: 16px; '
                 f'min-height: 64px; padding: {"12px 20px" if c.m else "14px 28px"}">'
                 f'<span style="font-family: {SERIF}; font-weight: 700; font-size: {21 if c.m else 25}px; line-height: 1.2; color: {P["dark"]}">Частый вопрос №&nbsp;{i}</span>'
                 f'<span aria-hidden="true" style="flex: none; width: 36px; height: 36px; border-radius: 50%; box-shadow: 0 0 0 1.5px {P["line"]}; '
                 f'display: flex; align-items: center; justify-content: center; color: {P["accl"]}">{icon("chev", 18)}</span></summary>{ans}</details>')
    inner = (kicker(c, "частые вопросы") + h2(c, "Частые вопросы") +
             f'<div style="display: flex; flex-direction: column; gap: 12px; max-width: 900px">{rows}</div>')
    return section(c, "cream", inner, tex=True, **kw)

def b_read(c, **kw):
    P = c.P
    arts = ["Чем отличается психолог от психотерапевта и психиатра", "Как выбрать психолога", "Как проходит первая консультация"]
    cells = ""
    for n, t in enumerate(arts):
        dark = n % 2 == 0
        bg = (f"radial-gradient(circle at 30% 20%, {P['dark_hi']} 0%, {P['dark']} 60%, {P['dark_lo']} 100%)" if dark else P["cream"])
        cells += (f'<a href="#" style="display: flex; flex-direction: column; overflow: hidden; border-radius: 28px; background: #FFFFFF; text-decoration: none; '
                  f'box-shadow: 0 14px 34px rgba({P["rgb_dark"]},0.08)">'
                  f'<div style="aspect-ratio: 16 / 10; background: {bg}; display: flex; align-items: center; justify-content: center">{MOTIFS[n](P, 130 if c.m else 150, dark=dark)}</div>'
                  f'<div style="padding: {"20px 22px 24px" if c.m else "24px 28px 30px"}; display: flex; flex-direction: column; gap: 10px">'
                  f'<span style="align-self: flex-start; padding: 5px 14px; border-radius: 999px; background: rgba({P["rgb_line"]},0.15); font-size: 13px; color: {P["accl"]}">О&nbsp;терапии</span>'
                  f'<h3 style="margin: 0; font-family: {SERIF}; font-weight: 700; font-size: {24 if c.m else 27}px; line-height: 1.15; color: {P["dark"]}">{nb(t)}</h3>'
                  f'<p style="margin: 0; font-size: 13px; color: {P["muted"]}">Статья-заглушка · время чтения</p></div></a>')
    mats = "".join(
        f'<a href="#" style="display: flex; align-items: center; gap: 18px; padding: {"18px 20px" if c.m else "22px 26px"}; border-radius: 24px; background: #FFFFFF; '
        f'text-decoration: none; box-shadow: 0 10px 26px rgba({P["rgb_dark"]},0.07)">{ringcircle(c, icon("file", 22), 50)}'
        f'<span style="display: flex; flex-direction: column; gap: 4px"><span style="font-family: {SERIF}; font-weight: 700; font-size: {21 if c.m else 24}px; line-height: 1.15; color: {P["dark"]}">{nb(t)}</span>'
        f'<span style="font-size: 13px; color: {P["muted"]}">Материал-заглушка · PDF, без почты и&nbsp;телефона</span></span></a>'
        for t in ["Упражнение на телесные импульсы", "Арт-терапевтическая техника"])
    inner = (kicker(c, "полезное") + h2(c, "Информация и инструменты для самопомощи") + grid(c, 3, cells, gap=16 if c.m else 24) +
             grid(c, 2, mats, gap=12 if c.m else 24, extra=f"margin-top: {16 if c.m else 24}px") +
             f'<div style="display: flex; flex-wrap: wrap; gap: 8px 32px; margin-top: 20px">{link(c, "Все статьи", mt=0)}{link(c, "Все материалы", mt=0)}</div>')
    return section(c, "cream2", inner, tex=True, **kw)

def b_footer(c, last=True):
    P = c.P
    head = lambda t: f'<p style="margin: 0 0 12px; font-size: 12px; letter-spacing: 0.14em; text-transform: uppercase; color: {P["accd"]}">{t}</p>'
    a = lambda t: f'<a href="#" style="display: block; padding: 5px 0; font-size: 15px; color: rgba({P["rgb_cream"]},0.86); text-decoration: none">{t}</a>'
    t = lambda s: f'<p style="margin: 0; padding: 5px 0; font-size: 15px; line-height: 1.5; color: rgba({P["rgb_cream"]},0.86)">{nb(s)}</p>'
    col1 = (f'<div><p style="margin: 0; font-family: {SERIF}; font-weight: 700; font-size: 28px; color: {P["cream"]}">Маргарита Терво</p>'
            f'<p style="margin: 4px 0 0; font-size: 11px; letter-spacing: 0.16em; text-transform: uppercase; color: {P["accd"]}">психолог, гештальт-подход</p>'
            f'</div>')
    col2 = "<div>" + head("Разделы") + "".join(a(x) for x in ["Обо мне", "С чем прийти", "Как я работаю", "Стоимость", "Статьи", "Материалы", "Частые вопросы"]) + "</div>"
    col3 = "<div>" + head("Запись") + a("Telegram") + a("ВКонтакте") + t("Кабинет: Думская ул., 5/22") + t("Будни 11:00–20:00 по Москве") + "</div>"
    col4 = "<div>" + head("Читать") + a("ВКонтакте") + a("b17") + "</div>"
    cols = grid(c, 4, col1 + col2 + col3 + col4, gap=28 if c.m else 40, cols_m=1)
    crisis = (f'<a href="#" style="display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-top: 40px; padding: 18px 24px; border-radius: 22px; '
              f'background: rgba({P["rgb_cream"]},0.07); text-decoration: none; color: {P["accd"]}">'
              f'<span style="font-family: {SERIF}; font-weight: 700; font-size: {21 if c.m else 25}px; line-height: 1.2">Если вам сейчас очень тяжело — телефоны доверия</span>{icon("arrow", 20)}</a>')
    bottom = (f'<div style="display: flex; flex-wrap: wrap; justify-content: space-between; gap: 10px 24px; margin-top: 32px; padding-top: 20px; '
              f'border-top: 1px solid rgba({P["rgb_line"]},0.3); font-size: 13px; color: rgba({P["rgb_cream"]},0.7)">'
              f'<span>Маргарита Терво · самозанятая · ИНН [ИНН]</span>'
              f'<a href="#" style="color: rgba({P["rgb_cream"]},0.86)">Политика обработки персональных данных</a></div>')
    grow = "flex: 1 0 auto; " if last else ""
    return (f'<footer style="{grow}background: {P["dark_lo"]}; padding: {"48px 0 32px" if c.m else "72px 0 40px"}">'
            f'{container(c, cols + crisis + bottom)}</footer>')

BLOCKS = {
    1: ("Первый экран", None), 2: ("Видео-визитка", b_video), 3: ("Вам сейчас непросто", b_hard), 4: ("С чем можно прийти", b_requests),
    5: ("Квалификация", b_qual), 6: ("Я работаю не одна", b_support), 7: ("Ценности", b_values), 8: ("Гештальт простыми словами", b_gestalt),
    9: ("На сессиях я", b_sessions), 10: ("Начало работы", b_start), 11: ("Условия", b_terms), 12: ("Запись", b_contact),
    13: ("Частые вопросы", b_faq), 14: ("Почитать и попробовать", b_read), 15: ("Подвал", None),
}
ROOT_BG = {2: "cream2", 3: "cream", 4: "cream", 5: "cream2", 6: "dark", 7: "cream", 8: "cream2", 9: "dark",
           10: "cream", 11: "cream2", 12: "dark", 13: "cream", 14: "cream2", 15: "dark_lo"}

def doc(title, body, w, h, root_style):
    props = f'{{"$preview":{{"width":{w},"height":{h}}}}}'
    html = f'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>{title}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,600&amp;family=Inter:wght@300;400;500&amp;display=swap">
<style>
body{{margin:0}}
a{{color:inherit}}a:hover{{opacity:0.85}}
summary::-webkit-details-marker{{display:none}}
details[open] summary span[aria-hidden]{{transform:rotate(180deg)}}
</style>
</helmet>
<div style="{root_style}">
{body}
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{props}'>
class Component extends DCLogic {{
renderVals() {{
return {{}};
}}
}}
</script>
</body>
</html>
'''
    return typo(html)

def home_part(v, m, blocks, w, h):
    P = PAL[v]
    c = Ctx(P, m)
    parts = []
    for i, n in enumerate(blocks):
        last = i == len(blocks) - 1
        if n == 1:
            parts.append(b_header(c))
            parts.append(b_hero(c, ROOT_BG[blocks[i + 1]] if i + 1 < len(blocks) else "cream"))
        elif n == 15:
            parts.append(b_footer(c, last=last))
        else:
            parts.append(BLOCKS[n][1](c, last=last))
    bgk = ROOT_BG.get(blocks[-1], "cream")
    rootbg = P["dark"] if bgk == "dark" else P[bgk]
    root_style = (f"width: {w}px; min-height: 100vh; display: flex; flex-direction: column; background: {rootbg}; "
                  f"font-family: {SANS}; font-weight: 300; color: {P['text']}; text-wrap: pretty; -webkit-font-smoothing: antialiased")
    dev = "телефон" if m else "компьютер"
    title = f"Главная · {dev} · часть {PARTS.index(blocks) + 1}"
    html = doc(title, "\n".join(parts), w, h, root_style)
    return title, html

# ---------- style board (Main) ----------
def style_board():
    W = 1440
    A, B = PAL["A"], PAL["B"]
    def sw(col, name, hexv, light_text=False):
        tc = "#FFFFFF" if light_text else "#2C2C2C"
        return (f'<div style="display: flex; flex-direction: column; gap: 8px">'
                f'<div style="height: 84px; border-radius: 20px; background: {col}; box-shadow: 0 8px 20px rgba(0,0,0,0.08)"></div>'
                f'<span style="font-size: 13px; line-height: 1.35; color: #2C2C2C">{name}<br><span style="color: #6A655E">{hexv}</span></span></div>')
    def palette(P, label):
        dark = f"radial-gradient(circle at 25% 15%, {P['dark_hi']} 0%, {P['dark']} 55%, {P['dark_lo']} 100%)"
        hero = (f'<div style="position: relative; overflow: hidden; height: 230px; border-radius: 28px; background: {dark}; padding: 34px 38px; box-sizing: border-box">'
                f'<p style="margin: 0; font-family: {SERIF}; font-style: italic; font-weight: 600; font-size: 24px; color: {P["accd"]}">психолог, гештальт-подход</p>'
                f'<p style="margin: 4px 0 0; font-family: {SERIF}; font-weight: 700; font-size: 58px; line-height: 1; color: {P["cream"]}">Маргарита Терво</p>'
                f'<span style="display: inline-flex; align-items: center; margin-top: 22px; min-height: 46px; padding: 0 24px; border-radius: 999px; background: {P["accd"]}; '
                f'color: {P["dark"]}; font-size: 15px; font-weight: 500">Записаться</span>'
                f'<div aria-hidden="true" style="position: absolute; right: -40px; top: -30px; opacity: 0.55">{m_depth(P, 280, dark=True)}</div></div>')
        sws = (f'<div style="display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 14px; margin-top: 22px">'
               + sw(P["dark"], "Основной тёмный", P["dark"], True) + sw(P["cream"], "Кремовый фон", P["cream"]) + sw(P["cream2"], "Кремовый глубже", P["cream2"])
               + sw(P["line"], "Линии, кольца", P["line"]) + sw(P["accd"], "Акцент на тёмном", P["accd"]) + '</div>')
        return (f'<div style="flex: 1 1 0; min-width: 0; padding: 34px; border-radius: 32px; background: #FFFFFF; box-shadow: 0 14px 34px rgba(0,0,0,0.06)">'
                f'<p style="margin: 0 0 18px; font-family: {SERIF}; font-weight: 700; font-size: 34px; color: #1E1E1E">{label}</p>{hero}{sws}</div>')
    txt = "Говорим о том, что вас беспокоит: как давно, в каких ситуациях, как это сказывается на вашей жизни. Можно говорить в своем темпе и не отвечать на то, о чем пока не хочется."
    def tsample(weight, dark):
        P = A
        bg = (f"radial-gradient(circle at 25% 15%, {P['dark_hi']} 0%, {P['dark']} 55%, {P['dark_lo']} 100%)" if dark else P["cream"])
        col = P["cream"] if dark else P["text"]
        return (f'<div style="padding: 28px 30px; border-radius: 24px; background: {bg}">'
                f'<p style="margin: 0 0 10px; font-size: 12px; letter-spacing: 0.14em; text-transform: uppercase; color: {P["accd"] if dark else P["accl"]}">Inter {weight} · 18 px</p>'
                f'<p style="margin: 0; font-family: {SANS}; font-weight: {weight}; font-size: 18px; line-height: 1.62; color: {col}">{nb(txt)}</p></div>')
    typo = (f'<div style="display: grid; grid-template-columns: 1fr 1.4fr; gap: 40px; align-items: start">'
            f'<div style="display: flex; flex-direction: column; gap: 14px">'
            f'<p style="margin: 0; font-family: {SERIF}; font-style: italic; font-weight: 600; font-size: 28px; color: {A["accl"]}">подпись над заголовком · Cormorant 600 курсив</p>'
            f'<p style="margin: 0; font-family: {SERIF}; font-weight: 700; font-size: 64px; line-height: 1; color: {A["dark"]}">Заголовок раздела</p>'
            f'<p style="margin: 0; font-family: {SERIF}; font-weight: 700; font-size: 30px; line-height: 1.15; color: {A["dark"]}">Подзаголовок, Cormorant 700</p>'
            f'<p style="margin: 8px 0 0; font-size: 14px; line-height: 1.55; color: #6A655E">{nb("Шрифты на сайте храним на своём сервере, без Google Fonts. На холсте они подгружаются только для показа.")}</p></div>'
            f'<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px">{tsample(300, False)}{tsample(300, True)}</div></div>')
    P = A
    el = lambda inner, cap: (f'<div style="display: flex; flex-direction: column; align-items: center; justify-content: flex-end; gap: 14px; min-height: 150px">'
                             f'{inner}<span style="font-size: 13px; color: #6A655E; text-align: center">{cap}</span></div>')
    cctx = Ctx(A, False)
    elements = (f'<div style="display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); gap: 24px; align-items: end">'
                + el(f'<span style="padding: 9px 22px; border-radius: 999px; background: {P["dark"]}; font-family: {SERIF}; font-weight: 700; font-size: 22px; color: {P["cream"]}">Тревога</span>', "Таблетка, без обводки")
                + el(f'<div style="width: 130px; height: 74px; border-radius: 24px; background: #FFFFFF; box-shadow: 0 12px 28px rgba({P["rgb_dark"]},0.12)"></div>', "Белая плашка с мягкой тенью")
                + el(ringcircle(cctx, icon("lock", 24), 58), "Иконка в круге с кольцом")
                + el(ringcircle(cctx, f'<span style="font-family: {SERIF}; font-weight: 700; font-size: 26px; color: {P["accl"]}">2</span>', 54), "Номер шага")
                + el(f'<svg width="120" height="20" viewBox="0 0 120 20" aria-hidden="true"><line x1="6" y1="10" x2="102" y2="10" stroke="{P["line"]}" stroke-width="3" stroke-linecap="round" stroke-dasharray="0 9"></line>'
                     f'<path d="M102 3 L114 10 L102 17 Z" fill="{P["line"]}"></path></svg>', "Пунктирная стрелка")
                + el(f'<div style="width: 140px">{divider(cctx)}</div>', "Разделитель с ромбом")
                + el(f'<div style="display: flex; gap: 12px; color: {P["accl"]}">{icon("x", 26)}{icon("clock", 26)}{icon("pin", 26)}</div>', "Тонкие линейные иконки")
                + '</div>')
    def atm_col(title, sub, body):
        return (f'<div style="display: flex; flex-direction: column; gap: 14px; padding: 28px; border-radius: 28px; background: #FFFFFF; box-shadow: 0 14px 34px rgba(0,0,0,0.06)">'
                f'<p style="margin: 0; font-family: {SERIF}; font-weight: 700; font-size: 28px; line-height: 1.1; color: #1E1E1E">{title}</p>'
                f'<p style="margin: 0 0 6px; font-size: 14px; line-height: 1.5; color: #6A655E">{nb(sub)}</p>{body}</div>')
    c_ph = Ctx(A, False)
    atm1 = atm_col("1. Свои фото", "Атмосферные кадры без лица со съёмки: свет из окна, ткань, кресло, чашка, книги. Самый живой вариант.",
                   f'<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px">{photo(c_ph, "Свет из окна на ткани", "1 / 1")}{photo(c_ph, "Кресло и плед", "1 / 1")}'
                   f'{photo(c_ph, "Чашка, блокнот", "1 / 1")}{photo(c_ph, "Книги на полке", "1 / 1")}</div>')
    atm2 = atm_col("2. Графика из кругов и линий", "Своя графика в духе карточек: «Встреча» двух кругов, круги вглубь, путь к себе. Без вопросов о правах.",
                   f'<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px">'
                   f'<div style="aspect-ratio: 1 / 1; border-radius: 22px; background: {A["cream"]}; display: flex; align-items: center; justify-content: center">{m_meet(A, 150)}</div>'
                   f'<div style="aspect-ratio: 1 / 1; border-radius: 22px; background: radial-gradient(circle at 30% 20%, {A["dark_hi"]}, {A["dark"]} 60%, {A["dark_lo"]}); display: flex; align-items: center; justify-content: center">{m_depth(A, 150, True)}</div>'
                   f'<div style="aspect-ratio: 1 / 1; border-radius: 22px; background: radial-gradient(circle at 30% 20%, {B["dark_hi"]}, {B["dark"]} 60%, {B["dark_lo"]}); display: flex; align-items: center; justify-content: center">{m_meet(B, 150, True)}</div>'
                   f'<div style="aspect-ratio: 1 / 1; border-radius: 22px; background: {B["cream2"]}; display: flex; align-items: center; justify-content: center">{m_path(B, 150)}</div></div>')
    atm3 = atm_col("3. Фактура и свет", "Бумажная фактура на кремовых фонах и мягкое «окно света» на тёмных. Работает фоном под всем остальным.",
                   f'<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px">'
                   f'<div style="position: relative; overflow: hidden; aspect-ratio: 1 / 1; border-radius: 22px; background: {A["cream"]}">{texture(0.35)}</div>'
                   f'<div style="position: relative; overflow: hidden; aspect-ratio: 1 / 1; border-radius: 22px; background: {A["dark"]}">'
                   f'<div style="position: absolute; left: -20%; top: -30%; width: 140%; height: 140%; background: radial-gradient(circle at 70% 30%, rgba({A["rgb_cream"]},0.22) 0%, rgba({A["rgb_cream"]},0) 50%)"></div></div>'
                   f'<div style="position: relative; overflow: hidden; aspect-ratio: 1 / 1; border-radius: 22px; background: {B["cream"]}">{texture(0.35)}</div>'
                   f'<div style="position: relative; overflow: hidden; aspect-ratio: 1 / 1; border-radius: 22px; background: {B["dark"]}">'
                   f'<div style="position: absolute; left: -20%; top: -30%; width: 140%; height: 140%; background: radial-gradient(circle at 70% 30%, rgba({B["rgb_cream"]},0.22) 0%, rgba({B["rgb_cream"]},0) 50%)"></div></div></div>')
    sec = lambda t, inner: (f'<section style="margin-top: 64px"><h2 style="margin: 0 0 24px; font-family: {SERIF}; font-weight: 700; font-size: 44px; color: #1E1E1E">{t}</h2>{inner}</section>')
    body = (f'<h1 style="margin: 0; font-family: {SERIF}; font-weight: 700; font-size: 72px; line-height: 1; color: #1E1E1E">Основа дизайна сайта</h1>'
            f'<p style="margin: 14px 0 0; max-width: 900px; font-size: 18px; line-height: 1.6; color: #55524D">{nb("Тот же визуальный язык, что в карточках Авито: глубокие цвета, круги вместо арок, плашки без обводок, тонкий основной текст Inter 300. Справа на холсте – главная для телефона и компьютера.")}</p>'
            + sec("Палитра", f'<div style="display: flex; gap: 28px; max-width: 760px">{palette(A, "Тёмно-синий, кремовый, бронза")}</div>')
            + sec("Шрифты: Cormorant Garamond и Inter", typo)
            + sec("Элементы", f'<div style="padding: 36px; border-radius: 32px; background: {A["cream"]}">{elements}</div>')
            + sec("Атмосферные картинки: фото, графика, фактура", f'<div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 24px">{atm1}{atm2}{atm3}</div>'))
    root = f"width: {W}px; min-height: 100vh; box-sizing: border-box; padding: 72px 80px 90px; background: #F4F2EE; font-family: {SANS}; font-weight: 300; color: #2C2C2C"
    return doc("Основа дизайна сайта", body, W, 2700, root).replace('"bodyWeight":{"editor":"enum","options":["300","400"],"default":"300","section":"Шрифт основного текста"},', "")

# ---------- write ----------
PARTS = [[1, 3, 2, 4, 5], [6, 7, 8, 9], [10, 11, 12], [13, 14, 15]]
H_M = [6410, 6190, 3625, 4100]
H_D = [5215, 4190, 3020, 2850]
LABELS = ["блоки 1–5", "блоки 6–9", "блоки 10–12", "блоки 13–15"]
idx = json.load(open(sys.argv[2]))  # текущий canvas.json с холста
boards, files = idx["boards"], []

def put(name, html):
    with open(f"{ROOT}/project/{name}", "w") as f:
        f.write(html)
    files.append(name)

put("Main.dc.html", style_board())
boards["Main.dc.html"]["title"] = "Основа стиля"
for i, bl in enumerate(PARTS):
    for dev, m, w, H in [("m", True, 390, H_M), ("d", False, 1440, H_D)]:
        name = f"Home-A-{dev}{i + 1}.dc.html"
        title, html = home_part("A", m, bl, w, H[i])
        put(name, html)
        boards[name]["h"] = H[i]
        boards[name]["title"] = f"{'Телефон' if m else 'Компьютер'} · {LABELS[i]}"
for k in list(boards):
    if k.startswith("Home-B-"):
        del boards[k]
idx["order"] = [o for o in idx["order"] if not o.startswith("Home-B-")]
idx["notes"].pop("t_B", None)
if "noteOrder" in idx:
    idx["noteOrder"] = [n for n in idx["noteOrder"] if n != "t_B"]
idx["notes"]["t_A"]["text"] = "Главная: тёмно-синий, кремовый, бронза"
idx["title"] = "Сайт tervopsy.ru — дизайн главной"
with open(f"{ROOT}/project/canvas.json", "w") as f:
    json.dump(idx, f, ensure_ascii=False, indent=1)
print("\n".join(f"{n} {os.path.getsize(ROOT + '/project/' + n)}" for n in files))
