#!/usr/bin/env python3
"""Типограф для прототипа tervopsy.ru – правила Марго (паспорт, раздел 6; design/README.md).

Что делает в текстах страниц (только в видимом тексте внутри <body>):
  • «—» → «–»;
  • неразрывный пробел после предлогов, союзов и коротких слов (в, и, с, на, не, по, для…);
  • частицы «бы», «ли», «же» привязаны к предыдущему слову;
  • « – » привязано к предыдущему слову, число – к следующему слову или «₽»;
  • слова через дефис («гештальт-подход») и диапазоны цифр («11:00–20:00») – в <span class="nw">
    (white-space: nowrap);
  • последнее короткое слово абзаца не остаётся одно на строке.

Не трогает <head>, <script>, <style>, <svg>, <code>, <pre>, <textarea>, комментарии и атрибуты.
Повторный запуск ничего не ломает (идемпотентен).

Запуск из корня репозитория:
    python3 scripts/typograph.py            # все *.html в prototype/
    python3 scripts/typograph.py файл.html  # отдельные файлы
Логика перенесена из design/generator/gen.py (nb, _textnode, typo).
"""
import re
import sys
from pathlib import Path

SHORT = (r"(в|и|с|на|не|по|для|к|о|у|а|от|до|из|за|со|или|но|что|как|я|вы|мы|без|при|об|ни|под|над|про|"
         r"во|ко|их|его|её|это|все|всё|уже|так|чем|где|то|ваш|ваши|вам|вас|мой|мои|мне|меня|наша|наш|если|когда|чтобы|м\.|ул\.)")
SKIP = {"head", "script", "style", "svg", "code", "pre", "textarea", "title"}
# после текста идёт закрывающий тег блока → можно привязывать последнее слово
BLOCK_END = re.compile(r"</(p|li|h[1-6]|dd|dt|figcaption|blockquote|td|th|summary|button|label)>", re.I)
TOKEN = re.compile(r"(<!--.*?-->|<[^>]+>)", re.S)
TAGNAME = re.compile(r"<\s*(/?)\s*([a-zA-Z0-9]+)")


def nb(t: str) -> str:
    t = t.replace("—", "–")
    for _ in range(2):
        t = re.sub(r"(^|[\s(«;]|&nbsp;)" + SHORT + r" ", lambda m: m.group(1) + m.group(2) + "&nbsp;", t, flags=re.I)
    t = re.sub(r" (бы|ли|же)(?=[\s,.!?:;]|$)", r"&nbsp;\1", t)
    t = t.replace(" – ", "&nbsp;– ").replace(" ₽", "&nbsp;₽")
    t = re.sub(r"(\d) (?=[А-Яа-яЁё₽%])", r"\1&nbsp;", t)
    return t


def nowrap(s: str) -> str:
    s = re.sub(r"(?<![\w\-])((?:[А-Яа-яЁёA-Za-z0-9]+-)+[А-Яа-яЁёA-Za-z0-9]+)(?![\w\-])",
               r'<span class="nw">\1</span>', s)
    s = re.sub(r"(?<![\w>])(\d[\d:]*–\d[\d:]*)", r'<span class="nw">\1</span>', s)
    return s


def orphan(s: str) -> str:
    body = s.rstrip()
    tail = s[len(body):]
    if re.search(r"&nbsp;[^\s]*$", body):  # уже привязано
        return s
    idx = body.rfind(" ")
    if idx <= 0:
        return s
    last = re.sub(r"<[^>]+>|&nbsp;", "", body[idx + 1:])
    if len(body.split(" ")) >= 4 and len(last) <= 12:
        body = body[:idx] + "&nbsp;" + body[idx + 1:]
    return body + tail


def process(html: str) -> str:
    m = re.search(r"<body[^>]*>", html, re.I)
    if not m:
        return html
    head, rest = html[: m.end()], html[m.end():]
    parts = TOKEN.split(rest)
    stack = []          # открытые теги из SKIP
    in_nw = False       # внутри <span class="nw">
    out = []
    for i, part in enumerate(parts):
        if i % 2 == 1:  # тег или комментарий
            tm = TAGNAME.match(part)
            if tm:
                closing, name = tm.group(1) == "/", tm.group(2).lower()
                if name in SKIP and not part.endswith("/>"):
                    if closing:
                        if stack and stack[-1] == name:
                            stack.pop()
                    else:
                        stack.append(name)
                if name == "span":
                    in_nw = (not closing) and 'class="nw"' in part
            out.append(part)
            continue
        if stack or not part.strip():
            out.append(part)
            continue
        s = part if in_nw else nowrap(nb(part))
        nxt = parts[i + 1] if i + 1 < len(parts) else ""
        if not in_nw and BLOCK_END.match(nxt):
            s = orphan(s)
        out.append(s)
    return head + "".join(out)


def main(argv):
    root = Path(__file__).resolve().parent.parent / "prototype"
    files = [Path(a) for a in argv] if argv else sorted(root.rglob("*.html"))
    changed = 0
    for f in files:
        src = f.read_text(encoding="utf-8")
        dst = process(src)
        if dst != src:
            f.write_text(dst, encoding="utf-8")
            changed += 1
    print(f"Типограф: обработано {len(files)}, изменено {changed}")


if __name__ == "__main__":
    main(sys.argv[1:])
