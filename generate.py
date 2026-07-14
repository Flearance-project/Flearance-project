#!/usr/bin/env python3
"""Генерация feed.xml и sitemap.xml из CATALOG в Flrnce.html"""
import re, os, html
from datetime import datetime, timezone

SITE = "https://flearance.github.io"
DIR = os.path.dirname(os.path.abspath(__file__))

# --- Читаем CATALOG из Flrnce.html ---
with open(os.path.join(DIR, "Flrnce.html"), encoding="utf-8") as f:
    src = f.read()

m = re.search(r'var CATALOG = \[(.*?)\];', src, re.DOTALL)
if not m:
    raise SystemExit("CATALOG not found")

raw = m.group(1)

# Парсим каждый объект {cat:"...",title:"...",desc:"...",...}
items = []
for block in re.finditer(r'\{([^}]+(?:\{[^}]*\}[^}]*)*)\}', raw):
    b = block.group(1)
    def grab(key):
        s = re.search(r'' + key + r':"((?:[^"\\]|\\.)*)"', b)
        return html.unescape(s.group(1).replace('\\"', '"').replace("\\'", "'")) if s else ""
    title = grab("title")
    desc = grab("desc")
    cat = grab("cat")
    date = grab("date")
    addr = grab("addr")
    if title:
        items.append({"title": title, "desc": desc, "cat": cat, "date": date, "addr": addr})

# Сортируем по дате (новые первые)
items.sort(key=lambda x: x["date"] or "0000", reverse=True)

CAT_LABELS = {
    "git": "Git / Open-Source", "ai": "AI-Agent", "edu": "Обучение",
    "hosting": "Хостинг", "tools": "Сервисы", "access": "Доступ",
    "sec": "Безопасность", "bypass": "Обходы", "fun": "Моды и игры"
}

# --- feed.xml ---
now_rfc = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
rss_items = ""
for it in items[:15]:
    d = it["date"]
    if d:
        try:
            dt = datetime.strptime(d, "%Y-%m-%d")
            pub = dt.strftime("%a, %d %b %Y 12:00:00 +0300")
        except:
            pub = now_rfc
    else:
        pub = now_rfc
    cat_label = CAT_LABELS.get(it["cat"], it["cat"])
    rss_items += f"""
    <item>
      <title>{html.escape(it['title'])}</title>
      <description>{html.escape(it['desc'])}</description>
      <link>{SITE}#catalog</link>
      <pubDate>{pub}</pubDate>
      <category>{html.escape(cat_label)}</category>
    </item>"""

feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>FLEARANCE — арсенал инструментов</title>
    <description>Каталог инструментов: open-source софт, AI-агенты, приватность, обход блокировок, обучение. Без регистрации, без логов.</description>
    <link>{SITE}</link>
    <atom:link href="{SITE}/feed.xml" rel="self" type="application/rss+xml"/>
    <language>ru</language>
    <lastBuildDate>{now_rfc}</lastBuildDate>{rss_items}
  </channel>
</rss>
"""
with open(os.path.join(DIR, "feed.xml"), "w", encoding="utf-8") as f:
    f.write(feed)
print(f"feed.xml: {len(items[:15])} items")

# --- sitemap.xml ---
today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
urls = ""
for it in items:
    d = it["date"] or today
    urls += f"""
  <url>
    <loc>{SITE}#{html.escape(it['title'].lower().replace(' ', '-'))}</loc>
    <lastmod>{d}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>"""

# Статические страницы
static_pages = [
    ("", "1.0", "weekly"),
    ("#catalog", "0.9", "weekly"),
    ("#howto", "0.7", "monthly"),
    ("#policy", "0.5", "monthly"),
    ("#support", "0.5", "monthly"),
]
static_xml = ""
for path, pri, freq in static_pages:
    static_xml += f"""
  <url>
    <loc>{SITE}{path}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{pri}</priority>
  </url>"""

sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{static_xml}{urls}
</urlset>
"""
with open(os.path.join(DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
    f.write(sitemap)
print(f"sitemap.xml: {len(static_pages) + len(items)} urls")
print("Done.")
