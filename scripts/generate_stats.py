#!/usr/bin/env python3
"""
Renders assets/stats.svg straight from the GitHub API, so you never depend on a
third-party stats service that can rate-limit or go down.

Runs inside GitHub Actions (see .github/workflows/stats.yml). Locally:
    GH_USER=Blankk18 GITHUB_TOKEN=<token> python scripts/generate_stats.py
    python scripts/generate_stats.py --demo      # sample numbers, no network
    python scripts/generate_stats.py --placeholder
Pure standard library, no installs.
"""
import datetime as dt
import json
import os
import sys
import urllib.request
from xml.sax.saxutils import escape

USER = os.environ.get("GH_USER", "Blankk18")
TOKEN = os.environ.get("GITHUB_TOKEN", "")

BOARD, BOARD2, LINE = "#08161B", "#0C1F25", "#1A3B43"
COPPER, GOLD, CYAN, MINT, VIOLET = "#C98B4A", "#FFD08A", "#3DD9EB", "#8FD9AE", "#A99BFF"
TEXT, SOFT, MUTED = "#E8F1EE", "#B9CFCB", "#8FB0AD"
LANG_COLORS = [CYAN, GOLD, MINT, COPPER, VIOLET, "#5C7C80"]
MONO = "'JetBrains Mono','Fira Code',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
SANS = "'Segoe UI Variable Display','Segoe UI',system-ui,-apple-system,'Helvetica Neue',Arial,sans-serif"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "stats.svg")


def api(url, body=None):
    headers = {"User-Agent": "profile-readme-stats", "Accept": "application/vnd.github+json"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def fetch_rest():
    user = api(f"https://api.github.com/users/{USER}")
    repos = api(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner")
    own = [r for r in repos if not r["fork"]]
    stars = sum(r["stargazers_count"] for r in own)
    langs = {}
    for r in own:
        try:
            for lang, b in api(r["languages_url"]).items():
                langs[lang] = langs.get(lang, 0) + b
        except Exception as e:  # one broken repo should not kill the run
            print(f"  skipped languages for {r['name']}: {e}", file=sys.stderr)
    return dict(repos=user["public_repos"], stars=stars, langs=langs)


def fetch_graphql():
    """Needs a token. Returns None if unavailable."""
    if not TOKEN:
        return None
    q = """query($login:String!){user(login:$login){contributionsCollection{
      totalCommitContributions totalPullRequestContributions
      contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}"""
    try:
        res = api("https://api.github.com/graphql", {"query": q, "variables": {"login": USER}})
        c = res["data"]["user"]["contributionsCollection"]
    except Exception as e:
        print(f"  GraphQL unavailable: {e}", file=sys.stderr)
        return None
    days = sorted((d["date"], d["contributionCount"]) for w in c["contributionCalendar"]["weeks"] for d in w["contributionDays"])
    longest = run = 0
    for _, n in days:
        run = run + 1 if n else 0
        longest = max(longest, run)
    today = dt.date.today().isoformat()
    cur, i = 0, len(days) - 1
    if i >= 0 and days[i][0] >= today and days[i][1] == 0:
        i -= 1  # today not committed yet: don't break the streak
    while i >= 0 and days[i][1] > 0:
        cur += 1
        i -= 1
    return dict(total=c["contributionCalendar"]["totalContributions"], commits=c["totalCommitContributions"],
                prs=c["totalPullRequestContributions"], streak=cur, longest=longest)


def fmt(v):
    return "n/a" if v is None else f"{v:,}"


def render(rest, gql):
    W, H = 1000, 300
    g = gql or {}
    tiles = [
        ("contributions", "last 12 months", fmt(g.get("total")), CYAN),
        ("commits", "last 12 months", fmt(g.get("commits")), GOLD),
        ("pull requests", "last 12 months", fmt(g.get("prs")), MINT),
        ("public repos", "owned by me", fmt(rest["repos"]), COPPER),
        ("stars earned", "across my repos", fmt(rest["stars"]), GOLD),
        ("current streak", f"longest {fmt(g.get('longest'))} days" if g else "needs a token", fmt(g.get("streak")) + (" days" if g else ""), CYAN),
    ]
    s = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">'
        f'<title id="t">GitHub stats for {escape(USER)}</title>'
        f'<desc id="d">Contributions, commits, pull requests, repositories, stars, streak and top languages.</desc>'
        f"<style>text{{font-family:{SANS}}}.m{{font-family:{MONO};white-space:pre}}"
        ".grow{transform-box:fill-box;transform-origin:0 50%;animation:grow 1.6s cubic-bezier(.2,.7,.2,1) .25s both}"
        "@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}"
        "@media (prefers-reduced-motion:reduce){*{animation:none!important}}</style>"
        f'<defs><clipPath id="card"><rect width="{W}" height="{H}" rx="18"/></clipPath></defs>'
        f'<g clip-path="url(#card)"><rect width="{W}" height="{H}" fill="{BOARD}"/>'
    )
    tw, th, gap, x0, y0 = 176, 104, 14, 28, 28
    for i, (label, sub, val, col) in enumerate(tiles):
        x, y = x0 + (i % 3) * (tw + gap), y0 + (i // 3) * (th + gap)
        s += (
            f'<rect x="{x}" y="{y}" width="{tw}" height="{th}" rx="12" fill="{BOARD2}" stroke="{LINE}"/>'
            f'<rect x="{x}" y="{y + 18}" width="3" height="{th - 36}" rx="1.5" fill="{col}"/>'
            f'<text class="m" x="{x + 20}" y="{y + 30}" font-size="12.5" fill="{MUTED}">{escape(label)}</text>'
            f'<text x="{x + 20}" y="{y + 65}" font-size="34" font-weight="700" fill="{TEXT}">{escape(val)}</text>'
            f'<text class="m" x="{x + 20}" y="{y + 88}" font-size="11.5" fill="{MUTED}">{escape(sub)}</text>'
        )
    # languages
    lx, lw = 626, 346
    s += f'<text class="m" x="{lx}" y="48" font-size="12.5" fill="{MUTED}">most used languages (by code size)</text>'
    langs = sorted(rest["langs"].items(), key=lambda kv: -kv[1])
    top, other = langs[:5], sum(b for _, b in langs[5:])
    if other:
        top.append(("Other", other))
    total = sum(b for _, b in top) or 1
    s += f'<clipPath id="bar"><rect x="{lx}" y="64" width="{lw}" height="14" rx="7"/></clipPath><g clip-path="url(#bar)"><g class="grow">'
    x = lx
    for i, (name, b) in enumerate(top):
        w = lw * b / total
        s += f'<rect x="{x:.1f}" y="64" width="{max(w - 2, 1):.1f}" height="14" fill="{LANG_COLORS[i % len(LANG_COLORS)]}"/>'
        x += w
    s += "</g></g>"
    for i, (name, b) in enumerate(top):
        y = 112 + i * 27
        s += (
            f'<circle cx="{lx + 6}" cy="{y - 5}" r="5" fill="{LANG_COLORS[i % len(LANG_COLORS)]}"/>'
            f'<text x="{lx + 22}" y="{y}" font-size="15" fill="{TEXT}">{escape(name)}</text>'
            f'<text class="m" x="{lx + lw}" y="{y}" font-size="13" fill="{SOFT}" text-anchor="end">{100 * b / total:.1f}%</text>'
        )
    note = "waiting for the first run of the Stats workflow" if rest.get("placeholder") else f"refreshed {dt.date.today().isoformat()} by GitHub Actions"
    s += (f'<text class="m" x="{x0}" y="{H - 14}" font-size="11" fill="{MUTED}">{note}</text>'
          f'</g><rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="{LINE}"/></svg>')
    return s


def main():
    if "--placeholder" in sys.argv:
        rest, gql = dict(repos=None, stars=None, langs={}, placeholder=True), None
    elif "--demo" in sys.argv:
        rest = dict(repos=9, stars=1, langs={"TypeScript": 52000, "Java": 31000, "HTML": 14000, "CSS": 6000, "Python": 3000})
        gql = dict(total=412, commits=367, prs=9, streak=6, longest=21)
    else:
        print(f"Fetching stats for {USER}...")
        rest = fetch_rest()
        gql = fetch_graphql()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(render(rest, gql))
    print(f"wrote {os.path.normpath(OUT)}")


if __name__ == "__main__":
    main()
