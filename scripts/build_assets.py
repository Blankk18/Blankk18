#!/usr/bin/env python3
"""
Builds every animated SVG used by the profile README into ../assets/.
No dependencies. Run from the repo root:   python scripts/build_assets.py

Edit the CONFIG block below (name, typed lines, skills, projects), re-run, commit.
"""
import math
import os
import textwrap
from xml.sax.saxutils import escape

# ───────────────────────────── CONFIG ─────────────────────────────
NAME = "Om Nathwani"
ROLE = "Electronics & Computer Science student"
TYPED_LINES = [
    "learning Python + DSA",
    "building NeuroSaathi",
    "turning ideas into working software",
    "learn -> build -> debug -> repeat",
]
TERMINAL = [  # ("cmd", text) | ("out", [(color_key, text), ...])
    ("cmd", "whoami"),
    ("out", [("text", "Electronics & Computer Science student @ Shah & Anchor Kutchhi Engineering College")]),
    ("cmd", "cat now.txt"),
    ("out", [("gold", "building  "), ("text", "NeuroSaathi (cognitive games + caregiver tools)")]),
    ("out", [("gold", "learning  "), ("text", "Python, Data Structures & Algorithms")]),
    ("cmd", "./next_step.sh"),
    ("out", [("cyan", "learn -> build -> debug -> repeat")]),
]
SKILLS_ROW_1 = ["Java", "C", "Python", "JavaScript", "TypeScript", "HTML", "CSS"]   # languages
SKILLS_ROW_2 = ["React", "Supabase", "MySQL", "Git", "GitHub", "Power BI"]          # tools
PROJECTS = [
    dict(slug="neurosaathi", title="NeuroSaathi", kind="React web app", accent="cyan", live=True,
         desc="AI-powered cognitive games and memory assistance for older adults, with family-memory experiences and caregiver-support tools.",
         tags=["React", "TypeScript", "Supabase"]),
    dict(slug="supermarket-pos", title="Smart Supermarket POS", kind="Java desktop app", accent="gold", live=False,
         desc="Point-of-sale and self-checkout system covering product management, billing and customer transactions.",
         tags=["Java", "OOP", "MySQL"]),
    dict(slug="farmers-marketplace", title="Farmers' Marketplace", kind="Web app", accent="mint", live=False,
         desc="A marketplace that connects producers directly with customers to discover and buy fresh agricultural products.",
         tags=["HTML", "CSS", "JavaScript"]),
    dict(slug="hospital-dashboard", title="Hospital Dashboard", kind="Data visualization", accent="copper", live=False,
         desc="Power BI dashboard that turns hospital data into charts and KPIs you can filter and explore.",
         tags=["Power BI", "Data viz"]),
]
FOOTER_LINE = "Build something useful. Learn something new. Repeat."
# ───────────────────────────────────────────────────────────────────

# Palette: "PCB at night". Gold = hardware signal, cyan = the AI side.
BOARD, BOARD2, GRID, LINE = "#08161B", "#0C1F25", "#12303A", "#1A3B43"
COPPER, GOLD, CYAN, MINT = "#C98B4A", "#FFD08A", "#3DD9EB", "#8FD9AE"
TEXT, SOFT, MUTED = "#E8F1EE", "#B9CFCB", "#8FB0AD"
COLORS = dict(copper=COPPER, gold=GOLD, cyan=CYAN, mint=MINT, text=TEXT, muted=MUTED)
MONO = "'JetBrains Mono','Fira Code',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
SANS = "'Segoe UI Variable Display','Segoe UI',system-ui,-apple-system,'Helvetica Neue',Arial,sans-serif"

OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets"))
os.makedirs(OUT, exist_ok=True)


def write(name, svg):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"  wrote assets/{name}  ({len(svg)/1024:.1f} KB)")


def svg_open(w, h, title, desc, css=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'role="img" aria-labelledby="t d"><title id="t">{escape(title)}</title><desc id="d">{escape(desc)}</desc>'
        f"<style>text{{font-family:{SANS}}}.m{{font-family:{MONO};white-space:pre}}{css}"
        "@media (prefers-reduced-motion:reduce){*{animation:none!important}.rm{display:none}}</style>"
    )


def keyframes(name, T, events, prop):
    """Step-function keyframes. events = [(seconds, value)], value holds until the next event."""
    pts = {}
    for t, v in events:
        pts[round(100 * t / T, 3)] = v
    pts.setdefault(0, events[0][1])
    return f"@keyframes {name}{{" + "".join(f"{p}%{{{prop}:{v}}}" for p, v in sorted(pts.items())) + "}"


def typing_events(n, t0, cps):
    return [(k, t0 + k / cps) for k in range(1, n + 1)]


# ───────────────────────────── header ─────────────────────────────
def header():
    W, H = 1000, 320
    nx = [640, 750, 860, 950]
    layers = [[82, 134, 186, 238], [56, 108, 160, 212, 264], [82, 134, 186, 238], [134, 186]]
    starts = [50, 120, 200, 270]

    css = (
        ".pulse{fill:none;stroke:%s;stroke-width:2.6;stroke-linecap:round;stroke-dasharray:9 91;"
        "animation:flow 6s linear infinite}"
        "@keyframes flow{0%%{stroke-dashoffset:9}37%%{stroke-dashoffset:-91}100%%{stroke-dashoffset:-91}}"
        ".nd{fill:%s;stroke:%s;stroke-width:1.6;animation:glow 6s infinite}"
        "@keyframes glow{0%%{fill:%s}5%%{fill:%s}22%%{fill:%s}100%%{fill:%s}}"
        ".halo{fill:%s;opacity:0;animation:halo 6s infinite}"
        "@keyframes halo{0%%{opacity:0}5%%{opacity:.4}22%%{opacity:0}100%%{opacity:0}}"
        ".eg{opacity:.3;animation:edge 6s infinite}"
        "@keyframes edge{0%%{opacity:.3}6%%{opacity:1}24%%{opacity:.3}100%%{opacity:.3}}"
        ".blink{animation:blink 1s step-end infinite}@keyframes blink{50%%{opacity:0}}"
        % (GOLD, BOARD, CYAN, BOARD, CYAN, BOARD, BOARD, CYAN)
    )

    # typed line
    cw, size, x0, ty = 10.8, 18, 70, 252
    C = 5.0
    T = C * len(TYPED_LINES)
    clips, texts, cur_events = "", "", [(0, "translateX(0px)")]
    for i, line in enumerate(TYPED_LINES):
        n = len(line)
        t0 = i * C + 0.35
        ev = [(0, "scaleX(0)")] + [(t, f"scaleX({k / n:.4f})") for k, t in typing_events(n, t0, 15)]
        ev.append((i * C + C - 0.3, "scaleX(0)"))
        css += keyframes(f"ty{i}", T, ev, "transform")
        css += f".ty{i}{{animation:ty{i} {T}s step-end infinite;transform-box:fill-box;transform-origin:0 50%}}"
        clips += f'<clipPath id="c{i}"><rect class="ty{i}" x="{x0}" y="{ty - 20}" width="{n * cw:.1f}" height="28"/></clipPath>'
        texts += (
            f'<text class="m{" rm" if i else ""}" x="{x0}" y="{ty}" font-size="{size}" fill="{GOLD}" '
            f'textLength="{n * cw:.1f}" lengthAdjust="spacing" clip-path="url(#c{i})">{escape(line)}</text>'
        )
        cur_events += [(t0 - 0.01, "translateX(0px)")] + [(t, f"translateX({k * cw:.1f}px)") for k, t in typing_events(n, t0, 15)]
        cur_events.append((i * C + C - 0.3, "translateX(0px)"))
    css += keyframes("cur", T, cur_events, "transform") + f".cur{{animation:cur {T}s step-end infinite}}"

    s = svg_open(W, H, f"{NAME}: software, AI and electronics",
                 f"Animated banner: gold signal pulses run along circuit traces into a glowing neural network. {NAME}, {ROLE}.", css)
    s += (
        f'<defs><pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="{GRID}"/></pattern>'
        f'<radialGradient id="glow" cx="800" cy="160" r="300" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{CYAN}" stop-opacity=".13"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>'
        f'<linearGradient id="ng" x1="0" x2="1"><stop offset="0" stop-color="{TEXT}"/><stop offset=".6" stop-color="{TEXT}"/><stop offset="1" stop-color="{GOLD}"/></linearGradient>'
        f'<clipPath id="card"><rect width="{W}" height="{H}" rx="18"/></clipPath>{clips}</defs>'
        f'<g clip-path="url(#card)"><rect width="{W}" height="{H}" fill="{BOARD}"/><rect width="{W}" height="{H}" fill="url(#dots)"/>'
        f'<rect width="{W}" height="{H}" fill="url(#glow)"/>'
    )

    # decorative copper traces (left side) and input traces into the network
    deco = [("M0,26 H70 L96,52 H300", 1.5), ("M0,300 H120 L146,274 H360", 3.2)]
    traces = []
    for sy, ny in zip(starts, layers[0]):
        traces.append(f"M470,{sy} H520 L{520 + abs(ny - sy)},{ny} H{nx[0] - 8}")
    for d in [d for d, _ in deco] + traces:
        s += f'<path d="{d}" fill="none" stroke="{COPPER}" stroke-opacity=".45" stroke-width="1.6"/>'
    for d, delay in deco:
        s += f'<path class="pulse" pathLength="100" d="{d}" style="animation-delay:{delay}s"/>'
    for i, d in enumerate(traces):
        s += f'<path class="pulse" pathLength="100" d="{d}" style="animation-delay:{i * 0.28:.2f}s"/>'
    for sy in starts:
        s += f'<circle cx="470" cy="{sy}" r="4" fill="{BOARD}" stroke="{COPPER}" stroke-width="1.6"/>'

    # neural network
    for k in range(3):
        s += f'<g class="eg" style="animation-delay:{2.2 + k * 0.45:.2f}s">'
        for a in layers[k]:
            for b in layers[k + 1]:
                s += f'<line x1="{nx[k]}" y1="{a}" x2="{nx[k + 1]}" y2="{b}" stroke="{CYAN}" stroke-opacity=".5" stroke-width="1"/>'
        s += "</g>"
    for k, ys in enumerate(layers):
        d = f"{2.2 + k * 0.45:.2f}s"
        for y in ys:
            s += f'<circle class="halo" cx="{nx[k]}" cy="{y}" r="15" style="animation-delay:{d}"/>'
            s += f'<circle class="nd" cx="{nx[k]}" cy="{y}" r="7" style="animation-delay:{d}"/>'

    # text block
    s += (
        f'<text x="48" y="150" font-size="60" font-weight="800" fill="url(#ng)" textLength="{len(NAME) * 33.5:.0f}" lengthAdjust="spacingAndGlyphs">{escape(NAME)}</text>'
        f'<text x="50" y="190" font-size="19" fill="{MUTED}" textLength="{len(ROLE) * 9.6:.0f}" lengthAdjust="spacingAndGlyphs">{escape(ROLE)}</text>'
        f'<text class="m" x="48" y="{ty}" font-size="{size}" fill="{COPPER}">&gt;</text>'
        + texts +
        f'<g class="cur rm"><rect class="blink" x="{x0}" y="{ty - 16}" width="9" height="21" fill="{CYAN}"/></g>'
        f'</g><rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="{LINE}"/></svg>'
    )
    write("header.svg", s)


# ───────────────────────────── terminal ─────────────────────────────
def terminal():
    W, H = 900, 316
    cw, fs, x0, y0, lh = 9.0, 15, 28, 92, 28
    prompt = "om@github:~$ "
    px = len(prompt) * cw
    t = 0.7
    events = []  # (kind, y, payload, start, cps)
    y = y0
    for kind, payload in TERMINAL:
        if kind == "cmd":
            events.append(("cmd", y, payload, t, 18))
            t += 0.3 + len(payload) / 18 + 0.55
        else:
            n = sum(len(x[1]) for x in payload)
            events.append(("out", y, payload, t, 80))
            t += n / 80 + 0.2
        y += lh
    events.append(("end", y, None, t, 0))
    T = round(t + 4.5, 2)

    css = ".blink{animation:blink 1s step-end infinite}@keyframes blink{50%{opacity:0}}"
    body, clips = "", ""
    for i, (kind, yy, payload, st, cps) in enumerate(events):
        if kind in ("cmd", "end"):
            css += keyframes(f"p{i}", T, [(0, 0), (st, 1)], "opacity") + f".p{i}{{animation:p{i} {T}s step-end infinite}}"
            body += (
                f'<text class="m p{i}" x="{x0}" y="{yy}" font-size="{fs}" textLength="{len(prompt) * cw:.1f}" lengthAdjust="spacing">'
                f'<tspan fill="{CYAN}">om@github</tspan><tspan fill="{MUTED}">:~$ </tspan></text>'
            )
        if kind == "end":
            css += keyframes("endc", T, [(0, 0), (st, 1)], "opacity") + f".endc{{animation:endc {T}s step-end infinite}}"
            body += f'<g class="endc rm"><rect class="blink" x="{x0 + px:.1f}" y="{yy - 15}" width="9" height="20" fill="{GOLD}"/></g>'
            continue
        if kind == "cmd":
            tx, ts = x0 + px, st + 0.3
            n = len(payload)
            tspans = f'<tspan fill="{TEXT}">{escape(payload)}</tspan>'
        else:
            n = sum(len(x[1]) for x in payload)
            tx, ts = x0, st
            tspans = "".join(f'<tspan fill="{COLORS[c]}">{escape(s_)}</tspan>' for c, s_ in payload)
        ev = [(0, "scaleX(0)")] + [(tt, f"scaleX({k / n:.4f})") for k, tt in typing_events(n, ts, cps)]
        css += keyframes(f"c{i}", T, ev, "transform") + f".c{i}{{animation:c{i} {T}s step-end infinite;transform-box:fill-box;transform-origin:0 50%}}"
        clips += f'<clipPath id="k{i}"><rect class="c{i}" x="{tx:.1f}" y="{yy - 18}" width="{n * cw:.1f}" height="26"/></clipPath>'
        body += (f'<text class="m" x="{tx:.1f}" y="{yy}" font-size="{fs}" textLength="{n * cw:.1f}" lengthAdjust="spacing" '
                 f'clip-path="url(#k{i})">{tspans}</text>')

    s = svg_open(W, H, "Terminal intro", "An animated terminal typing out who I am, what I'm building and what I'm learning.", css)
    s += (
        f'<defs><clipPath id="win"><rect width="{W}" height="{H}" rx="14"/></clipPath>{clips}</defs>'
        f'<g clip-path="url(#win)"><rect width="{W}" height="{H}" fill="{BOARD2}"/>'
        f'<rect width="{W}" height="44" fill="{BOARD}"/><line x1="0" y1="44" x2="{W}" y2="44" stroke="{LINE}"/>'
        f'<circle cx="26" cy="22" r="6" fill="{COPPER}"/><circle cx="48" cy="22" r="6" fill="{GOLD}"/><circle cx="70" cy="22" r="6" fill="{CYAN}"/>'
        f'<text class="m" x="{W / 2}" y="27" font-size="13" fill="{MUTED}" text-anchor="middle">om@github: ~</text>'
        + body + f'</g><rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="none" stroke="{LINE}"/></svg>'
    )
    write("terminal.svg", s)


# ───────────────────────────── skills (IC chips) ─────────────────────────────
def chip(x, y, label, accent, idx):
    w, h = 128, 62
    pins = "".join(f'<rect x="{x + 14 + i * 22}" y="{y - 8}" width="8" height="9" rx="1.5" fill="{COPPER}"/>'
                   f'<rect x="{x + 14 + i * 22}" y="{y + h - 1}" width="8" height="9" rx="1.5" fill="{COPPER}"/>' for i in range(5))
    return (
        pins +
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="{BOARD2}" stroke="{accent}" stroke-opacity=".75"/>'
        f'<circle cx="{x + 13}" cy="{y + 13}" r="3" fill="none" stroke="{MUTED}" stroke-opacity=".6"/>'
        f'<circle class="led" cx="{x + w - 14}" cy="{y + 13}" r="3.2" fill="{accent}" style="animation-delay:{(idx * 0.37) % 2.6:.2f}s"/>'
        f'<text class="m" x="{x + w / 2}" y="{y + 39}" font-size="14" font-weight="700" fill="{TEXT}" text-anchor="middle">{escape(label)}</text>'
    )


def skills():
    W, H, pitch = 1000, 232, 150
    css = ".led{animation:led 2.6s ease-in-out infinite}@keyframes led{0%,100%{opacity:.25}50%{opacity:1}}"
    rows = ""
    for r, (labels, accent, ytop, rev) in enumerate([(SKILLS_ROW_1, GOLD, 30, False), (SKILLS_ROW_2, CYAN, 134, True)]):
        period = len(labels) * pitch
        copies = math.ceil(W / period) + 1
        inner = ""
        for c in range(copies):
            for i, lab in enumerate(labels):
                inner += chip(c * period + i * pitch + 12, ytop, lab, accent, i + c * len(labels) + r * 3)
        frm, to = (-period, 0) if rev else (0, -period)
        css += (f"@keyframes sc{r}{{from{{transform:translateX({frm}px)}}to{{transform:translateX({to}px)}}}}"
                f".r{r}{{animation:sc{r} {period / 38:.1f}s linear infinite}}")
        rows += (f'<line x1="0" y1="{ytop + 31}" x2="{W}" y2="{ytop + 31}" stroke="{COPPER}" stroke-opacity=".28" stroke-dasharray="2 6"/>'
                 f'<g class="r{r}">{inner}</g>')
    s = svg_open(W, H, "Toolbox", f"Two rows of chip-shaped labels scrolling: {', '.join(SKILLS_ROW_1 + SKILLS_ROW_2)}.", css)
    s += (
        f'<defs><clipPath id="card"><rect width="{W}" height="{H}" rx="16"/></clipPath>'
        f'<linearGradient id="fl"><stop offset="0" stop-color="{BOARD}"/><stop offset="1" stop-color="{BOARD}" stop-opacity="0"/></linearGradient>'
        f'<linearGradient id="fr"><stop offset="0" stop-color="{BOARD}" stop-opacity="0"/><stop offset="1" stop-color="{BOARD}"/></linearGradient></defs>'
        f'<g clip-path="url(#card)"><rect width="{W}" height="{H}" fill="{BOARD}"/>{rows}'
        f'<rect width="110" height="{H}" fill="url(#fl)"/><rect x="{W - 110}" width="110" height="{H}" fill="url(#fr)"/></g>'
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="16" fill="none" stroke="{LINE}"/></svg>'
    )
    write("skills.svg", s)


# ───────────────────────────── project cards ─────────────────────────────
def card(p):
    W, H = 480, 232
    a = COLORS[p["accent"]]
    lines = textwrap.wrap(p["desc"], 54)[:3]
    css = ".dot{animation:dot 1.6s ease-in-out infinite}@keyframes dot{0%,100%{opacity:.3}50%{opacity:1}}"
    s = svg_open(W, H, p["title"], f'{p["title"]}: {p["desc"]} Built with {", ".join(p["tags"])}.', css)
    s += (
        f'<defs><linearGradient id="bd" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{a}"/><stop offset=".55" stop-color="{LINE}"/><stop offset="1" stop-color="{LINE}"/></linearGradient></defs>'
        f'<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="16" fill="{BOARD2}" stroke="url(#bd)" stroke-width="1.5"/>'
        f'<path d="M{W},164 H436 L416,184 H388" fill="none" stroke="{a}" stroke-opacity=".3" stroke-width="1.4"/>'
        f'<circle cx="388" cy="184" r="3.5" fill="{BOARD2}" stroke="{a}" stroke-opacity=".6"/>'
        f'<rect x="28" y="27" width="9" height="9" rx="2" fill="{a}"/>'
        f'<text class="m" x="46" y="36" font-size="12.5" fill="{MUTED}">{escape(p["kind"])}</text>'
    )
    if p["live"]:
        s += (f'<circle class="dot" cx="{W - 28 - 9 * 7.3 - 12:.1f}" cy="32" r="4" fill="{a}"/>'
              f'<text class="m" x="{W - 28}" y="36" font-size="12.5" fill="{a}" text-anchor="end">live demo</text>')
    s += f'<text x="28" y="80" font-size="25" font-weight="700" fill="{TEXT}">{escape(p["title"])}</text>'
    for i, ln in enumerate(lines):
        s += f'<text x="28" y="{108 + i * 21}" font-size="14" fill="{SOFT}">{escape(ln)}</text>'
    x = 28
    for tg in p["tags"]:
        w = len(tg) * 7.3 + 22
        s += (f'<rect x="{x:.1f}" y="{H - 52}" width="{w:.1f}" height="27" rx="13.5" fill="none" stroke="{a}" stroke-opacity=".55"/>'
              f'<text class="m" x="{x + w / 2:.1f}" y="{H - 34}" font-size="12" fill="{TEXT}" text-anchor="middle">{escape(tg)}</text>')
        x += w + 8
    write(f"card-{p['slug']}.svg", s + "</svg>")


# ───────────────────────────── section headings ─────────────────────────────
def section(slug, title, accent, delay):
    W, H = 1000, 44
    tw = len(title) * 12.8
    x1 = 30 + tw + 18
    d = f"M{x1:.0f},22 H962"
    css = (".pulse{fill:none;stroke:%s;stroke-width:2.4;stroke-linecap:round;stroke-dasharray:7 93;animation:flow 7s linear infinite}"
           "@keyframes flow{0%%{stroke-dashoffset:7}45%%{stroke-dashoffset:-93}100%%{stroke-dashoffset:-93}}" % accent)
    s = svg_open(W, H, title, f"Section heading: {title}", css)
    s += (
        f'<rect x="0" y="13" width="18" height="18" rx="3" fill="{accent}"/><rect x="6" y="19" width="6" height="6" rx="1" fill="{BOARD}"/>'
        f'<text x="30" y="30" font-size="23" font-weight="700" fill="{TEXT}" textLength="{tw:.0f}" lengthAdjust="spacingAndGlyphs">{escape(title)}</text>'
        f'<path d="{d}" fill="none" stroke="{LINE}" stroke-width="2"/>'
        f'<path class="pulse" pathLength="100" d="{d}" style="animation-delay:{delay}s"/>'
        f'<circle cx="976" cy="22" r="6" fill="{BOARD}" stroke="{accent}" stroke-width="2"/></svg>'
    )
    write(f"section-{slug}.svg", s)


# ───────────────────────────── footer ─────────────────────────────
def footer():
    W, H = 1000, 190

    def wave(amp, period, y, copies=7):
        pts = [f"M0,{y}"]
        for i in range(copies):
            x = i * period
            pts.append(f"C{x + period / 4},{y - amp} {x + period / 4 * 3},{y + amp} {x + period},{y}")
        return " ".join(pts) + f" V{H} H0 Z"

    css = ("@keyframes w1{to{transform:translateX(-300px)}}@keyframes w2{from{transform:translateX(-420px)}to{transform:translateX(0)}}"
           ".w1{animation:w1 10s linear infinite}.w2{animation:w2 14s linear infinite}")
    s = svg_open(W, H, FOOTER_LINE, "Footer with slow cyan and gold waves.", css)
    s += (
        f'<defs><clipPath id="card"><rect width="{W}" height="{H}" rx="18"/></clipPath>'
        f'<linearGradient id="wc" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{CYAN}" stop-opacity=".30"/><stop offset="1" stop-color="{CYAN}" stop-opacity=".02"/></linearGradient>'
        f'<linearGradient id="wg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{GOLD}" stop-opacity=".28"/><stop offset="1" stop-color="{GOLD}" stop-opacity=".02"/></linearGradient></defs>'
        f'<g clip-path="url(#card)"><rect width="{W}" height="{H}" fill="{BOARD}"/>'
        f'<path class="w2" d="{wave(18, 420, 132)}" fill="url(#wg)"/>'
        f'<path class="w1" d="{wave(22, 300, 150)}" fill="url(#wc)"/>'
        f'<text x="{W / 2}" y="70" font-size="24" font-weight="700" fill="{TEXT}" text-anchor="middle">{escape(FOOTER_LINE)}</text>'
        f'<text class="m" x="{W / 2}" y="100" font-size="14" fill="{MUTED}" text-anchor="middle">thanks for stopping by</text></g>'
        f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="{LINE}"/></svg>'
    )
    write("footer.svg", s)


if __name__ == "__main__":
    print("Building assets...")
    header()
    terminal()
    skills()
    for pr in PROJECTS:
        card(pr)
    for i, (slug, title, acc) in enumerate([("about", "About", GOLD), ("toolbox", "Toolbox", CYAN), ("projects", "Projects", COPPER),
                                              ("activity", "GitHub activity", MINT), ("contributions", "Contribution trail", GOLD)]):
        section(slug, title, acc, i * 0.9)
    footer()
    print("Done.")
