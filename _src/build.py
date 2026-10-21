#!/usr/bin/env python3
"""Build benfuller.me (English + Spanish) from _src/content.py.

    python3 _src/build.py

Writes plain static files into the repo root. No dependencies beyond the
standard library. The `_src` folder is ignored by GitHub Pages (Jekyll skips
folders that start with an underscore).
"""
import datetime
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import content as C  # noqa: E402

LANGS = ["en", "es"]
PREFIX = {"en": "", "es": "/es"}
OTHER = {"en": "es", "es": "en"}
LOCALE = {"en": "en_US", "es": "es_ES"}
MONTHS_ES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
             "noviembre", "diciembre"]
MONTHS_EN = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
             "November", "December"]
SITE = C.SITE
URL = SITE["url"]


# ---------------------------------------------------------------- helpers

def tr(x, lang):
    return x[lang] if isinstance(x, dict) else x


def esc(s):
    return html.escape(s, quote=True)


def h(s):
    """Content strings are trusted HTML; only fix bare ampersands."""
    return re.sub(r"&(?!#?\w+;)", "&amp;", s)


def plain(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s))


def fill(s, **kw):
    for k, v in kw.items():
        s = s.replace("{" + k + "}", v)
    return s


def home(lang):
    return PREFIX[lang] + "/"


SLUGS = {"privacy": C.PRIVACY["slug"], "timeline": {"en": "timeline", "es": "cronologia"}}


def page_path(lang, key):
    slug = SLUGS[key][lang] if key in SLUGS else key
    return f"{PREFIX[lang]}/{slug}/"


def a(href, text, cls="", extra=""):
    c = f' class="{cls}"' if cls else ""
    return f'<a href="{esc(href)}"{c}{(" " + extra) if extra else ""}>{h(text)}</a>'


SK = {s[0]: {"id": s[0], "cat": s[1], "name": s[2], "aliases": s[3]} for s in C.SKILLS}
CAT = {c[0]: {"id": c[0], "name": c[1], "summary": c[2]} for c in C.CATEGORIES}
ROLE = C.ROLE_BY_ID
PROJECT_BY_ID = {p["id"]: p for p in C.PROJECTS}


def skill_name(sid, lang):
    return tr(SK[sid]["name"], lang)


def uses():
    """skill id -> (project ids, role ids)"""
    pr, ro = {}, {}
    for p in C.PROJECTS:
        for sid in p["skills"] + p["stack"]:
            pr.setdefault(sid, []).append(p["id"])
            ro.setdefault(sid, set()).add(p["role"])
    for r in C.ROLES:
        for sid in r["skills"]:
            ro.setdefault(sid, set()).add(r["id"])
    return pr, {k: sorted(v) for k, v in ro.items()}


USE_P, USE_R = uses()


def ui(key, lang, **kw):
    return fill(tr(C.UI[key], lang), **{k: str(v) for k, v in kw.items()})


def link_map(lang):
    return {
        "Inunity": a("https://www.inunity.com", "Inunity"),
        "Textedly": a("https://www.textedly.com", "Textedly"),
        "RentRange": a("https://www.rentrange.com", "RentRange"),
        "Nymblr": a(page_path(lang, "nymblr"), "Nymblr"),
        "linkedin": a(SITE["linkedin"], "LinkedIn"),
    }


def rich(text, lang, **extra):
    s = h(text)
    for k, v in {**link_map(lang), **extra}.items():
        s = s.replace("{" + k + "}", v)
    return s


def skill_link(sid, lang, cls="tag", count=False):
    n = len(USE_P.get(sid, []))
    r = len(USE_R.get(sid, []))
    badge = f'<span class="n">{n}</span>' if count and n else ""
    title = esc(ui("used_in", lang, p=n, r=r))
    if not n:
        return f'<span class="{cls} off" title="{title}">{h(skill_name(sid, lang))}</span>'
    return (f'<a class="{cls}" href="{home(lang)}?skill={sid}#projects" data-skill="{sid}" title="{title}">'
            f"{h(skill_name(sid, lang))}{badge}</a>")


def fmt_date(iso, lang):
    y, m, d = (int(x) for x in iso.split("-"))
    if lang == "es":
        return f"{d} de {MONTHS_ES[m - 1]} de {y}"
    return f"{d} {MONTHS_EN[m - 1]} {y}"


# ---------------------------------------------------------------- layout

def site_config(lang):
    U = C.UI
    consent = {k: tr(v, lang) for k, v in U["consent"].items()}
    return {
        "lang": lang,
        "home": home(lang),
        "searchIndex": f"{PREFIX[lang]}/search-index.json",
        "privacy": page_path(lang, "privacy"),
        "posthog": {"key": SITE["posthog_key"], "host": SITE["posthog_host"]},
        "ui": {
            "search": tr(U["search_ph"], lang), "empty": tr(U["search_empty"], lang), "hint": tr(U["search_hint"], lang),
            "types": {k: tr(v, lang) for k, v in U["search_types"].items()},
            "count": tr(U["filter_count"], lang), "total": tr(U["filter_total"], lang),
            "searchAria": tr(U["search_aria"], lang),
            "top": "Back to top" if lang == "en" else "Volver arriba",
            "consent": consent,
        },
    }


def head(lang, key, title, desc, alts, og_type="website", jsonld=None, image=None):
    canon = URL + alts[lang]
    tags = [
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{h(title)}</title>",
        f'<meta name="description" content="{esc(desc)}">',
        f'<link rel="canonical" href="{canon}">',
    ]
    for lg in LANGS:
        tags.append(f'<link rel="alternate" hreflang="{lg}" href="{URL + alts[lg]}">')
    tags.append(f'<link rel="alternate" hreflang="x-default" href="{URL + alts["en"]}">')
    img = image or f"{URL}/media/headshot.jpg"
    tags += [
        f'<meta property="og:title" content="{esc(title)}">',
        f'<meta property="og:description" content="{esc(desc)}">',
        f'<meta property="og:type" content="{og_type}">',
        f'<meta property="og:url" content="{canon}">',
        f'<meta property="og:image" content="{img}">',
        f'<meta property="og:locale" content="{LOCALE[lang]}">',
        f'<meta property="og:locale:alternate" content="{LOCALE[OTHER[lang]]}">',
        '<meta name="twitter:card" content="summary">',
        '<link rel="icon" href="/media/favicon.svg" type="image/svg+xml">',
        '<link rel="icon" href="/favicon.ico" sizes="48x48">',
        '<link rel="apple-touch-icon" href="/media/apple-touch-icon.png">',
        '<link rel="manifest" href="/media/site.webmanifest">',
        '<meta name="theme-color" content="#fafaf8" media="(prefers-color-scheme: light)">',
        '<meta name="theme-color" content="#121315" media="(prefers-color-scheme: dark)">',
        '<link rel="stylesheet" href="/style.css">',
    ]
    if jsonld:
        tags.append('<script type="application/ld+json">' + json.dumps(jsonld, ensure_ascii=False).replace("</", "<\\/") + "</script>")
    return "\n  ".join(tags)


SEARCH_ICON = ('<svg aria-hidden="true" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" '
               'stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>')


def header(lang, nav_items, alts):
    base = home(lang)
    nav = "\n        ".join(
        a(page_path(lang, "timeline") if k == "timeline" else f"{base}#{k}", tr(v, lang)) for k, v in nav_items)
    other = OTHER[lang]
    langs = []
    for lg in LANGS:
        label = lg.upper()
        if lg == lang:
            langs.append(f'<span class="cur" aria-current="true" lang="{lg}">{label}</span>')
        else:
            langs.append(f'<a href="{alts[lg]}" hreflang="{lg}" lang="{lg}" aria-label="{esc(ui("lang_switch_aria", lang))}">{label}</a>')
    return f'''  <a class="skip" href="#main">{"Skip to content" if lang == "en" else "Saltar al contenido"}</a>
  <header class="top">
    <div class="wrap hdr">
      <a class="brand" href="{base}">Benjamin Fuller</a>
      <div class="tools">
        <button type="button" class="search-btn" id="search-open" aria-label="{esc(ui("search_aria", lang))}" aria-keyshortcuts="Control+K Meta+K">
          {SEARCH_ICON}<span>{h(ui("search", lang))}</span><kbd>⌘K</kbd>
        </button>
        <span class="lang" role="group" aria-label="Language / Idioma">{langs[0]}<span aria-hidden="true">/</span>{langs[1]}</span>
        <button type="button" class="menu-btn" id="menu-btn" aria-expanded="false" aria-controls="site-nav" aria-label="{"Menu" if lang == "en" else "Menú"}"><span aria-hidden="true"></span></button>
      </div>
      <nav id="site-nav" aria-label="{"Primary" if lang == "en" else "Principal"}">
        {nav}
      </nav>
    </div>
  </header>'''


def footer(lang):
    return f'''  <footer>
    <div class="wrap">
      <span>&copy; {datetime.date.today().year} Benjamin Fuller</span>
      <span class="foot-links">
        {a(page_path(lang, "privacy"), ui("footer_privacy", lang))}
        <button type="button" class="linklike" data-open-cookies>{h(ui("footer_cookies", lang))}</button>
      </span>
    </div>
  </footer>'''


def layout(lang, key, title, desc, alts, body, nav_items, og_type="website", jsonld=None, image=None):
    cfg = json.dumps(site_config(lang), ensure_ascii=False).replace("</", "<\\/")
    return f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
  {head(lang, key, title, desc, alts, og_type, jsonld, image)}
</head>
<body>
{header(lang, nav_items, alts)}
  <main class="wrap" id="main">
{body}
  </main>
{footer(lang)}
  <script type="application/json" id="site-config">{cfg}</script>
  <script src="/site.js" defer></script>
  <script src="/consent.js" defer></script>
</body>
</html>
'''


def write(rel, text):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


# ---------------------------------------------------------------- timeline page

MONTHS_SHORT = {"en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
                "es": ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]}


def timeline_events():
    """Newest-first list of events. Jobs only have years, so a start sits at the
    beginning of its year and an end near the end; projects use C.AT estimates."""
    now = datetime.date.today()
    ev = []
    for i, r in enumerate(C.ROLES):
        sy, ey = r["span"]
        ev.append({"pos": sy + 0.0, "tie": i, "type": "job", "kind": "start", "role": r["id"], "year": sy})
        if ey:
            ev.append({"pos": ey + 0.95, "tie": i, "type": "job", "kind": "end", "role": r["id"], "year": ey})
        else:
            ev.append({"pos": now.year + (now.month - 1) / 12 + 0.06, "tie": i, "type": "job", "kind": "now",
                       "role": r["id"], "year": now.year})
    for i, m_ in enumerate(C.MILESTONES):
        y, m = m_["date"]
        ev.append({"pos": y + (m - 1) / 12 + 0.015, "tie": i, "type": "job", "kind": "milestone", "milestone": m_,
                   "role": m_["role"], "year": y, "month": m})
    for i, p in enumerate(C.PROJECTS):
        y, m = p["at"]
        ev.append({"pos": y + (m - 1) / 12 + 0.02, "tie": i, "type": "project", "kind": "project", "project": p,
                   "role": p["role"], "year": y})
    for i, p in enumerate(C.HOME["press"]):
        y, m = p["date"]
        ev.append({"pos": y + (m - 1) / 12 + 0.01, "tie": i, "type": "press", "kind": "press", "press": p,
                   "year": y, "month": m})
    ev.sort(key=lambda e: (-e["pos"], e["tie"]))
    return ev


def event_html(e, lang):
    base = home(lang)
    if e["type"] == "job" and e["kind"] == "milestone":
        r, m_ = ROLE[e["role"]], e["milestone"]
        when = f'{MONTHS_SHORT[lang][e["month"] - 1]} {e["year"]}'
        return (f'<li class="ev job milestone" data-type="job" data-role="{r["id"]}">'
                f'<div class="ev-meta"><span class="k">{"Milestone" if lang == "en" else "Hito"}</span><span class="d">{h(when)}</span></div>'
                f'<a class="ttl" href="{page_path(lang, r["page"])}#acquisition">{h(tr(m_["title"], lang))}</a>'
                f'<span class="sub">{h(tr(m_["sub"], lang))}</span></li>')
    if e["type"] == "job":
        r = ROLE[e["role"]]
        if e["kind"] == "now":
            k, d = ui("tl_now", lang), ui("present", lang)
        else:
            k, d = ui("tl_started" if e["kind"] == "start" else "tl_ended", lang), str(e["year"])
        title = f'{h(tr(r["title"], lang))} · {h(r["company"])}'
        if e["kind"] == "start" and r.get("start_title"):
            title = f'{h(tr(r["title"], lang))} · {h(tr(r["start_title"], lang))}'
        return (f'<li class="ev job {e["kind"]}" data-type="job" data-role="{r["id"]}">'
                f'<div class="ev-meta"><span class="k">{h(k)}</span><span class="d">{h(d)}</span></div>'
                f'<a class="ttl" href="{page_path(lang, r["page"])}">{title}</a></li>')
    if e["type"] == "project":
        p = e["project"]
        r = ROLE[p["role"]]
        return (f'<li class="ev project" data-type="project" data-role="{r["id"]}">'
                f'<div class="ev-meta"><span class="k">{h(ui("tl_kind_project", lang))}</span><span class="d">~{e["year"]}</span></div>'
                f'<a class="ttl" href="{base}?project={p["id"]}#p-{p["id"]}">{h(tr(p["title"], lang))}</a>'
                f'<span class="sub">{h(r["company"])}</span></li>')
    p = e["press"]
    when = f'{MONTHS_SHORT[lang][e["month"] - 1]} {e["year"]}'
    return (f'<li class="ev press" data-type="press">'
            f'<div class="ev-meta"><span class="k">{h(ui("tl_kind_press", lang))}</span><span class="d">{h(when)}</span></div>'
            f'<a class="ttl" href="{esc(p["url"])}" rel="noopener">{h(tr(p["title"], lang))}</a>'
            f'<span class="sub">{h(tr(p["source"], lang))}</span></li>')


def build_timeline(lang):
    items, last = [], None
    for e in timeline_events():
        y = int(e["pos"])
        if y != last:
            items.append(f'<li class="yr" aria-hidden="true"><span>{y}</span></li>')
            last = y
        items.append(event_html(e, lang))
    toggles = "".join(
        f'''<label class="tl-chip"><input type="checkbox" data-tl="{k}" checked><span>{h(ui("tl_" + k, lang))}</span></label>'''
        for k in ("job", "project", "press"))
    legend = "".join(f'<li data-role="{r["id"]}"><i></i>{h(r["company"])}</li>' for r in C.ROLES)
    base = home(lang)
    body = f'''    <p class="crumb">{a(base, "Benjamin Fuller")} / {h(ui("timeline_h", lang))}</p>
    <h1 class="page-title">{h(ui("timeline_h", lang))}</h1>
    <p class="page-sub">{h(ui("timeline_lede", lang))}</p>
    <fieldset class="tl-toggles" id="tl-toggles" hidden><legend>{h(ui("tl_show", lang))}</legend>{toggles}</fieldset>
    <ul class="legend" aria-label="{"Colors" if lang == "en" else "Colores"}">{legend}<li class="lg-press"><i></i>{h(ui("tl_press", lang))}</li></ul>
    <ol class="vt" id="vt">
{chr(10).join(items)}
    </ol>
    <p class="tl-note">{h(ui("timeline_note", lang))}</p>
    <p class="back">{a(f"{base}#experience", ui("back", lang))}</p>'''
    alts = {lg: page_path(lg, "timeline") for lg in LANGS}
    title = f'{ui("timeline_h", lang)} · Benjamin Fuller'
    out = layout(lang, "timeline", title, tr(C.UI["tl_desc"], lang), alts, body, C.UI["company_nav"])
    write(page_path(lang, "timeline").strip("/") + "/index.html", out)


# ---------------------------------------------------------------- home

def logos(role):
    out = []
    for f, alt, cls in role["logos"]:
        out.append(f'<span class="logo {cls}"><img src="/media/logos/{f}" alt="{esc(alt)} logo" loading="lazy"></span>')
    return "".join(out)


def role_heading(role, lang):
    title = h(tr(role["title"], lang))
    co = a(page_path(lang, role["page"]), role["company"])
    return f'{title} <span class="co">· {co}{h(role.get("company_suffix", ""))}</span>'


def role_meta(role, lang):
    meta = h(tr(role["meta"], lang))
    if "meta_link" in role:
        n, u = role["meta_link"]
        meta += " " + a(u, n)
    return f'{h(tr(role["when"], lang))} · {meta}'


def role_html(role, lang):
    chips = " ".join(skill_link(s, lang, "tag") for s in role["skills"])
    nproj = sum(1 for p in C.PROJECTS if p["role"] == role["id"])
    sid = f'skills-{role["id"]}'
    actions = (
        f'<button type="button" class="skills-toggle" aria-expanded="false" aria-controls="{sid}" hidden>'
        f'{h(ui("role_skills", lang))} <span class="count">{len(role["skills"])}</span><span class="chev" aria-hidden="true"></span></button>'
        f'{a(page_path(lang, role["page"]), ui("more_page", lang))}'
        f'{a(f"{home(lang)}?company={role["id"]}#projects", ui("related_projects", lang, n=nproj))}')
    bullets = "\n".join(f"          <li>{rich(tr(b, lang), lang)}</li>" for b in role["bullets"])
    return f'''      <article class="job" id="{role["id"]}">
        <div class="job-head">
          <div class="logos">{logos(role)}</div>
          <div>
            <h3>{role_heading(role, lang)}</h3>
            <div class="when">{role_meta(role, lang)}</div>
          </div>
        </div>
        <ul>
{bullets}
        </ul>
        <div class="job-actions">{actions}</div>
        <div class="tags skills-panel" id="{sid}">{chips}</div>
      </article>'''


def project_html(p, lang):
    role = ROLE[p["role"]]
    skills = " ".join(skill_link(s, lang) for s in p["skills"])
    stack = ""
    if p["stack"]:
        stack = (f'<h4>{h(ui("tech", lang))}</h4><div class="tags">'
                 + " ".join(skill_link(s, lang) for s in p["stack"]) + "</div>")
    allskills = " ".join(p["skills"] + p["stack"])
    return f'''        <article class="proj" id="p-{p["id"]}" data-company="{p["role"]}" data-skills="{allskills}">
          <div class="proj-meta"><a class="co-chip" href="{home(lang)}?company={p["role"]}#projects" data-company="{p["role"]}">{h(role["company"])}</a><span>{h(tr(p["when"], lang))}</span></div>
          <h3>{h(tr(p["title"], lang))}</h3>
          <p>{h(tr(p["summary"], lang))}</p>
          <p class="outcome"><b>{h(ui("outcome", lang))}</b> {h(tr(p["outcome"], lang))}</p>
          <div class="tags">{skills}</div>
          <details>
            <summary>{h(ui("case_study", lang))}</summary>
            <dl>
              <dt>{h(ui("problem", lang))}</dt><dd>{h(tr(p["problem"], lang))}</dd>
              <dt>{h(ui("approach", lang))}</dt><dd>{h(tr(p["approach"], lang))}</dd>
            </dl>
            {stack}
          </details>
        </article>'''


def filters_html(lang):
    cos = "".join(
        f'<button type="button" class="chip" data-kind="company" data-value="{r["id"]}" aria-pressed="false">{h(r["company"])}</button>'
        for r in C.ROLES)
    groups = []
    for cid, cname, _ in C.CATEGORIES:
        chips = "".join(
            f'<button type="button" class="chip" data-kind="skill" data-value="{s[0]}" aria-pressed="false">{h(tr(s[2], lang))}</button>'
            for s in C.SKILLS if s[1] == cid and USE_P.get(s[0]))
        if chips:
            groups.append(f'<div class="sg"><span>{h(tr(cname, lang))}</span><div>{chips}</div></div>')
    return f'''      <div class="filters" id="filters" hidden>
        <div class="filter-row"><span>{h(ui("filter_company", lang))}</span><div>{cos}</div></div>
        <details class="skillfilter" id="skillfilter">
          <summary>{h(ui("filter_skill", lang))}</summary>
          {"".join(groups)}
        </details>
        <p class="filter-status" aria-live="polite"><span id="f-count"></span> <button type="button" class="linklike" id="f-clear" hidden>{h(ui("filter_clear", lang))}</button></p>
      </div>'''


def skills_html(lang):
    out = []
    for cid, cname, csum in C.CATEGORIES:
        items = [s for s in C.SKILLS if s[1] == cid]
        chips = " ".join(skill_link(s[0], lang, "skill", count=True) for s in items)
        out.append(f'''      <details class="skillcat" id="skills-{cid}">
        <summary><strong>{h(tr(cname, lang))}</strong> <span class="count">{len(items)}</span><span class="sum">{h(tr(csum, lang))}</span></summary>
        <div class="tags">{chips}</div>
      </details>''')
    return "\n".join(out)


def jsonld_person(lang):
    return {
        "@context": "https://schema.org",
        "@type": "Person",
        "@id": URL + "/#person",
        "name": "Benjamin Fuller",
        "url": URL + home(lang),
        "image": URL + "/media/headshot.jpg",
        "jobTitle": tr(C.HOME["role"], lang),
        "description": tr(C.HOME["description"], lang),
        "sameAs": [SITE["linkedin"]],
        "knowsLanguage": ["en", "es"],
        "worksFor": {"@type": "Organization", "name": "InsidePartners.ai", "url": "https://www.insidepartners.ai"},
        "alumniOf": {"@type": "CollegeOrUniversity", "name": "University of Wisconsin-Whitewater"},
        "knowsAbout": [skill_name(s[0], "en") for s in C.SKILLS],
    }


def build_home(lang):
    H = C.HOME
    li = a(SITE["linkedin"], "LinkedIn")
    pillars = "\n".join(
        f"        <li><strong>{h(tr(t, lang))}</strong>{h(tr(d, lang))}</li>" for t, d in H["pillars"])
    strip = "\n".join(f"      <div><b>{h(tr(k, lang))}</b>{h(tr(v, lang))}</div>" for k, v in H["strip"])
    about = "\n".join(f"      <p>{h(tr(p, lang))}</p>" for p in H["about"])
    roles = "\n\n".join(role_html(r, lang) for r in C.ROLES)
    cards = "\n".join(project_html(p, lang) for p in C.PROJECTS)
    press = "\n".join(
        f'''        <li>
          {a(p["url"], tr(p["title"], lang))}
          <span class="src">{h(tr(p["source"], lang))}</span>
          {rich(tr(p["blurb"], lang), lang)}
        </li>''' for p in H["press"])
    edu_t, edu_s = H["education"]
    body = f'''    <div class="hero" id="top">
      <div class="hero-top">
        <img class="headshot" src="/media/headshot.jpg" alt="Benjamin Fuller" width="120" height="120" onerror="this.remove()">
        <div>
          <h1>Benjamin Fuller</h1>
          <p class="role">{h(tr(H["role"], lang))}</p>
        </div>
      </div>
      <p class="tagline">{h(tr(H["tagline"], lang))}</p>
      <p class="meta">{h(tr(H["location"], lang))}</p>
      <p class="domains">{h(tr(H["domains"], lang))}</p>
      <div class="links">
        {li}
        <a href="#experience">{h(ui("see_my_work", lang))}</a>
      </div>
    </div>

    <div class="strip">
{strip}
    </div>

    <section id="about">
      <h2>{h(ui("about_h", lang))}</h2>
{about}
    </section>

    <section id="what-i-do">
      <h2>{h(ui("what_h", lang))}</h2>
      <ul class="pillars">
{pillars}
      </ul>
    </section>

    <section id="experience">
      <h2>{h(ui("exp_h", lang))}</h2>

{roles}
      <p class="more">{a(page_path(lang, "timeline"), ui("timeline_link", lang))}</p>
    </section>

    <section id="projects">
      <h2>{h(ui("projects_h", lang))}</h2>
      <p class="lede">{h(ui("projects_lede", lang))}</p>
{filters_html(lang)}
      <div class="proj-list" id="proj-list">
{cards}
      </div>
    </section>

    <section id="skills">
      <h2>{h(ui("skills_h", lang))}</h2>
      <p class="lede">{h(ui("skills_lede", lang))}</p>
{skills_html(lang)}
    </section>

    <section id="press">
      <h2>{h(ui("press_h", lang))}</h2>
      <ul class="press">
{press}
      </ul>
    </section>

    <section id="education">
      <h2>{h(ui("edu_h", lang))}</h2>
      <p><strong>{h(tr(edu_t, lang))}</strong><br>{h(edu_s)}</p>
    </section>

    <section id="contact">
      <h2>{h(ui("contact_h", lang))}</h2>
      <p>{fill(h(tr(H["contact"], lang)), linkedin=li)}</p>
      <p>{h(tr(H["languages"], lang))}</p>
    </section>'''
    alts = {lg: home(lg) for lg in LANGS}
    html_out = layout(lang, "home", tr(H["title"], lang), tr(H["description"], lang), alts, body, C.UI["nav"],
                      jsonld=jsonld_person(lang))
    write("index.html" if lang == "en" else "es/index.html", html_out)


# ---------------------------------------------------------------- company pages

def figure_html(fig, lang, linkedin=None):
    link = a(fig["href"], tr(fig["link_text"], lang))
    cap = fill(h(tr(fig["caption"], lang)), link=link, linkedin=linkedin or "")
    return (f'<figure class="shot"><a href="{esc(fig["href"])}"><img src="/media/companies/{fig["img"]}" '
            f'alt="{esc(tr(fig["alt"], lang))}" width="1440" height="{fig["h"]}" loading="lazy"></a>'
            f"<figcaption>{cap}</figcaption></figure>")


def build_company(lang, key):
    P = C.COMPANY_PAGES[key]
    role = ROLE[P["role"]]
    base = home(lang)
    li_company = a(P["linkedin"], "LinkedIn") if P.get("linkedin") else ""
    facts = "".join(f"<li>{h(tr(f, lang))}</li>" for f in P["facts"])
    visit = ""
    if P.get("visit"):
        visit = f'<p class="links">{a(P["visit"], ui("visit", lang), extra="rel=\"noopener\"")}</p>'
    blocks = []
    for b in P["blocks"]:
        parts = [f'<h2>{h(tr(b["h"], lang))}</h2>']
        if b.get("figure"):
            parts.append(figure_html(b["figure"], lang, li_company))
        if b.get("p"):
            parts.append(f'<p>{rich(tr(b["p"], lang), lang)}</p>')
        if b.get("list"):
            parts.append("<ul>" + "".join(f"<li>{h(tr(i, lang))}</li>" for i in b["list"]) + "</ul>")
        sec_id = ' id="acquisition"' if "acquisition" in tr(b["h"], "en").lower() and "After" not in tr(b["h"], "en") else ""
        blocks.append(f"    <section{sec_id}>\n      " + "\n      ".join(parts) + "\n    </section>")
    bullets = "".join(f"<li>{rich(tr(b, lang), lang)}</li>" for b in role["bullets"])
    projs = [p for p in C.PROJECTS if p["role"] == role["id"]]
    plist = "".join(
        f'<li><a href="{base}?project={p["id"]}#p-{p["id"]}">{h(tr(p["title"], lang))}</a>'
        f'<span class="src">{h(tr(p["outcome"], lang))}</span></li>' for p in projs)
    chips = " ".join(skill_link(s, lang) for s in role["skills"])
    links = "".join(f'<li>{a(u, tr(lbl, lang), extra="rel=\"noopener\"")}</li>' for lbl, u in P["links"])
    press = ""
    if P["press"]:
        items = "".join(
            f'''<li>{a(p["url"], tr(p["title"], lang))}<span class="src">{h(tr(p["source"], lang))}</span>{h(tr(p["blurb"], lang))}</li>'''
            for p in P["press"])
        press = f'''
    <section>
      <h2>{h(ui("mentioned", lang))}</h2>
      <ul class="press">{items}</ul>
    </section>'''
    sub = rich(tr(P["subtitle"], lang), lang)
    body = f'''    <p class="crumb">{a(f"{base}#experience", ui("crumb", lang))} / {h(tr(P["title"], lang))}</p>
    <div class="page-head">
      <div class="logos">{logos(role)}</div>
      <h1 class="page-title">{h(tr(P["title"], lang))}</h1>
    </div>
    <p class="page-sub">{sub}</p>
    <ul class="facts">{facts}</ul>
    {visit}

{chr(10).join(blocks)}

    <section>
      <h2>{h(ui("what_i_did", lang))}</h2>
      <ul>{bullets}</ul>
    </section>

    <section>
      <h2>{h(ui("company_projects", lang))}</h2>
      <ul class="press">{plist}</ul>
      <p class="more">{a(f"{base}?company={role['id']}#projects", ui("related_projects", lang, n=len(projs)))}</p>
    </section>

    <section>
      <h2>{h(ui("company_skills", lang))}</h2>
      <div class="tags">{chips}</div>
    </section>
{press}
    <section>
      <h2>{h(ui("links_h", lang))}</h2>
      <ul class="plain">{links}</ul>
    </section>

    <p class="back">{a(f"{base}#experience", ui("back", lang))}</p>'''
    alts = {lg: page_path(lg, key) for lg in LANGS}
    first_img = next((b["figure"]["img"] for b in P["blocks"] if b.get("figure")), None)
    title = f'{tr(P["title"], lang)} · Benjamin Fuller'
    out = layout(lang, key, title, tr(P["description"], lang), alts, body, C.UI["company_nav"], og_type="article",
                 image=f"{URL}/media/companies/{first_img}" if first_img else None)
    write(page_path(lang, key).strip("/") + "/index.html", out)


# ---------------------------------------------------------------- privacy

def build_privacy(lang):
    P = C.PRIVACY
    posthog = a("https://posthog.com/privacy", tr(P["posthog_privacy_text"], lang))
    github = a("https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement",
               tr(P["github_privacy_text"], lang))
    cookies_btn = ('<button type="button" class="linklike" data-open-cookies>'
                   + ("cookie settings" if lang == "en" else "los ajustes de cookies") + "</button>")
    if SITE["contact_email"]:
        contact = fill(h(tr(P["contact_email"], lang)), email=a("mailto:" + SITE["contact_email"], SITE["contact_email"]))
    else:
        contact = fill(h(tr(P["contact_linkedin"], lang)), linkedin=a(SITE["linkedin"], "LinkedIn"))
    secs = []
    for title, paras in P["sections"]:
        ps = []
        for para in paras:
            t = fill(h(tr(para, lang)), contact=contact, posthog_privacy=posthog, github_privacy=github,
                     cookie_settings=cookies_btn, retention=h(tr(SITE["retention"], lang)))
            ps.append(f"      <p>{t}</p>")
        secs.append(f"    <section>\n      <h2>{h(tr(title, lang))}</h2>\n" + "\n".join(ps) + "\n    </section>")
    base = home(lang)
    body = f'''    <p class="crumb">{a(base, "Benjamin Fuller")} / {h(tr(P["title"], lang))}</p>
    <h1 class="page-title">{h(tr(P["title"], lang))}</h1>
    <p class="page-sub">{h(fill(tr(P["updated"], lang), date=fmt_date(SITE["policy_updated"], lang)))}</p>
{chr(10).join(secs)}
    <p class="back">{a(base, "← Back to the site" if lang == "en" else "← Volver al sitio")}</p>'''
    alts = {lg: page_path(lg, "privacy") for lg in LANGS}
    out = layout(lang, "privacy", tr(P["title"], lang) + " · Benjamin Fuller",
                 "How this site handles cookies and analytics." if lang == "en" else "Cómo gestiona este sitio las cookies y la analítica.",
                 alts, body, C.UI["company_nav"])
    write(page_path(lang, "privacy").strip("/") + "/index.html", out)


# ---------------------------------------------------------------- search index, sitemap

def build_index(lang):
    base = home(lang)
    items = []

    def add(t, n, s, u, k="", **extra):
        items.append({"t": t, "n": n, "s": s, "u": u, "k": k, **extra})

    for key, label in C.UI["nav"]:
        add("section", tr(label, lang), "", page_path(lang, "timeline") if key == "timeline" else f"{base}#{key}",
            "history chronology dates" if key == "timeline" else "")
    add("section", tr(C.UI["what_h"], lang), "", f"{base}#what-i-do")
    add("section", tr(C.UI["edu_h"], lang), "", f"{base}#education", "university wisconsin")
    for r in C.ROLES:
        k = " ".join([skill_name(s, lang) for s in r["skills"]] + [plain(tr(b, lang)) for b in r["bullets"]])
        add("role", f'{plain(tr(r["title"], lang))} · {r["company"]}', tr(r["when"], lang), f"{base}#{r['id']}", k)
        add("role", f'{r["company"]}: ' + ("company page" if lang == "en" else "página de la empresa"),
            tr(r["when"], lang), page_path(lang, r["page"]), r["company"] + " screenshots links")
    for m_ in C.MILESTONES:
        r = ROLE[m_["role"]]
        add("role", tr(m_["title"], lang), f'{MONTHS_SHORT[lang][m_["date"][1] - 1]} {m_["date"][0]}',
            f'{page_path(lang, r["page"])}#acquisition', "rentrange investability goldengator reismart acquisition altisource 2015")
    for p in C.PROJECTS:
        r = ROLE[p["role"]]
        k = " ".join([skill_name(s, lang) for s in p["skills"] + p["stack"]]
                     + [tr(p["summary"], lang), tr(p["outcome"], lang), tr(p["problem"], lang), tr(p["approach"], lang)])
        add("project", tr(p["title"], lang), f'{r["company"]} · {tr(p["when"], lang)}', f"{base}?project={p['id']}#p-{p['id']}", k)
    for s in C.SKILLS:
        sid = s[0]
        n, rr = len(USE_P.get(sid, [])), len(USE_R.get(sid, []))
        add("skill", tr(s[2], lang), f'{tr(CAT[s[1]]["name"], lang)} · ' + ui("used_in", lang, p=n, r=rr),
            f"{base}?skill={sid}#projects", " ".join(s[3] + [tr(CAT[s[1]]["name"], lang)]))
    for p in C.HOME["press"]:
        add("press", tr(p["title"], lang), tr(p["source"], lang), p["url"],
            " ".join([tr(p["source"], lang), plain(tr(p["blurb"], lang)), "future 5 acquire elteve inunity nymblr nimbler"]), x=1)
    add("action", ui("print", lang), "", "#print", "pdf resume cv", a="print")
    add("action", tr(C.UI["actions"]["lang"], lang), "", page_path(OTHER[lang], "x") if False else home(OTHER[lang]),
        "language idioma español english")
    add("action", tr(C.UI["actions"]["linkedin"], lang), "", SITE["linkedin"], "contact", x=1)
    add("action", tr(C.UI["actions"]["privacy"], lang), "", page_path(lang, "privacy"), "cookies gdpr")
    write(f"{PREFIX[lang].strip('/')}/search-index.json".lstrip("/"), json.dumps(items, ensure_ascii=False, separators=(",", ":")))


def build_sitemap():
    today = datetime.date.today().isoformat()
    pages = [{lg: home(lg) for lg in LANGS}] + [{lg: page_path(lg, k) for lg in LANGS} for k in C.COMPANY_PAGES]
    pages.append({lg: page_path(lg, "timeline") for lg in LANGS})
    pages.append({lg: page_path(lg, "privacy") for lg in LANGS})
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for alts in pages:
        for lg in LANGS:
            out.append(f"  <url><loc>{URL + alts[lg]}</loc><lastmod>{today}</lastmod>")
            for l2 in LANGS:
                out.append(f'    <xhtml:link rel="alternate" hreflang="{l2}" href="{URL + alts[l2]}"/>')
            out.append(f'    <xhtml:link rel="alternate" hreflang="x-default" href="{URL + alts["en"]}"/>')
            out.append("  </url>")
    out.append("</urlset>")
    write("sitemap.xml", "\n".join(out) + "\n")
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {URL}/sitemap.xml\n")


def build_consent_js():
    stub = open(os.path.join(HERE, "posthog-stub.js"), encoding="utf-8").read().strip()
    tmpl = open(os.path.join(HERE, "consent.tmpl.js"), encoding="utf-8").read()
    write("consent.js", tmpl.replace("/*POSTHOG_STUB*/", stub))


def validate():
    ids = {s[0] for s in C.SKILLS}
    for p in C.PROJECTS:
        for s in p["skills"] + p["stack"]:
            assert s in ids, (p["id"], s)
        assert p["role"] in ROLE, p["id"]
    for r in C.ROLES:
        for s in r["skills"]:
            assert s in ids, (r["id"], s)
    for s in C.SKILLS:
        assert s[1] in CAT, s


if __name__ == "__main__":
    validate()
    for lg in LANGS:
        build_home(lg)
        for key in C.COMPANY_PAGES:
            build_company(lg, key)
        build_privacy(lg)
        build_timeline(lg)
        build_index(lg)
    build_sitemap()
    build_consent_js()
    print("built", len(C.PROJECTS), "projects,", len(C.SKILLS), "skills,", len(C.ROLES), "roles ×", len(LANGS), "languages")
