import html, json, os, re
import markdown

SITE = "https://drkaium.com"
NAME = "Dr. Monirujjaman Kaium"
NOTE = "Medical information here is general education and is not a substitute for care from your own doctor."

def page(title, desc, path, body, extra=""):
    url = SITE + path
    t, d = html.escape(title), html.escape(desc, quote=True)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t} | {NAME}</title>
<meta name="description" content="{d}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{url}">
<meta property="og:type" content="article">
<link rel="stylesheet" href="/blog/style.css">
{extra}</head>
<body>
<div class="wrap">
{body}
  <p class="note">{NOTE}</p>
</div>
</body>
</html>
"""

def nice(date):
    y, m, d = date.split("-")
    months = ["January","February","March","April","May","June","July","August","September","October","November","December"]
    return f"{int(d)} {months[int(m)-1]} {y}"

with open("blog/posts.json", encoding="utf-8") as f:
    posts = json.load(f)
posts.sort(key=lambda p: p["date"], reverse=True)

built, items = [], []
for p in posts:
    slug = p["slug"]
    src = f"blog/posts/{slug}.md"
    if not re.fullmatch(r"[a-z0-9-]+", slug) or not os.path.exists(src):
        print("Skipping", slug)
        continue
    with open(src, encoding="utf-8") as f:
        text = markdown.markdown(f.read(), extensions=["extra", "sane_lists"])
    title, summary = p["title"], p.get("summary", "")
    ld = json.dumps({"@context": "https://schema.org", "@type": "BlogPosting",
        "headline": title, "description": summary, "datePublished": p["date"],
        "mainEntityOfPage": f"{SITE}/blog/{slug}/",
        "author": {"@type": "Person", "name": NAME}}, ensure_ascii=False)
    body = f"""  <div class="top"><a href="/blog/">← All posts</a><a href="/">Home</a></div>
  <article class="post"><h1>{html.escape(title)}</h1><div class="date">{nice(p["date"])}</div>
{text}
  </article>"""
    os.makedirs(f"blog/{slug}", exist_ok=True)
    with open(f"blog/{slug}/index.html", "w", encoding="utf-8") as f:
        f.write(page(title, summary, f"/blog/{slug}/", body, f'<script type="application/ld+json">{ld}</script>\n'))
    built.append(slug)
    items.append(f"""  <div class="item"><h2><a href="/blog/{slug}/">{html.escape(title)}</a></h2>
  <div class="date">{nice(p["date"])}</div><p>{html.escape(summary)}</p></div>""")

body = """  <div class="top"><a href="/">← Home</a><span>Dr. M. Kaium</span></div>
  <h1>Blog</h1>
""" + "\n".join(items)
with open("blog/index.html", "w", encoding="utf-8") as f:
    f.write(page("Blog", "Healthcare tips and medical education by " + NAME + ".", "/blog/", body).replace('og:type" content="article"', 'og:type" content="website"'))

pages = [d for d in sorted(os.listdir(".")) if os.path.isdir(d) and not d.startswith(".") and d != "blog" and os.path.exists(f"{d}/index.html")]
urls = [SITE + "/", SITE + "/blog/"] + [f"{SITE}/blog/{s}/" for s in built] + [f"{SITE}/{d}/" for d in pages]
with open("sitemap.xml", "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(f"  <url><loc>{u}</loc></url>" for u in urls) + "\n</urlset>\n")
print("Built:", ", ".join(built))
