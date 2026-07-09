#!/usr/bin/env python3
"""Refresh the auto-generated sections of README.md.

Sources:
- https://kenimoto.dev/ai/publications.md  (blog posts, canonical AI-readable feed)
- https://zenn.dev/api/articles?username=kenimo49
- https://qiita.com/api/v2/users/kenimo49/items

Stdlib only. Sections are delimited by <!-- name starts --> / <!-- name ends -->.
"""
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone, timedelta

README = "README.md"
UA = {"User-Agent": "kenimo49-profile-readme"}
N_ITEMS = 5


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as res:
        return res.read().decode("utf-8")


def blog_entries():
    md = fetch("https://kenimoto.dev/ai/publications.md")
    m = re.search(r"## Blog Articles\s+### English\n(.*?)(?=\n###? )", md, re.S)
    if not m:
        raise RuntimeError("Blog Articles section not found in publications.md")
    entries = re.findall(r"- \[(.+?)\]\((\S+?)\) — (\d{4}-\d{2}-\d{2})", m.group(1))
    return [f"[{t}]({u}) — {d}" for t, u, d in entries[:N_ITEMS]]


def zenn_entries():
    data = json.loads(fetch("https://zenn.dev/api/articles?username=kenimo49&count=5&order=latest"))
    return [
        f"[{a['title']}](https://zenn.dev{a['path']}) — {a['published_at'][:10]}"
        for a in data["articles"][:N_ITEMS]
    ]


def qiita_entries():
    data = json.loads(fetch("https://qiita.com/api/v2/users/kenimo49/items?per_page=5&page=1"))
    return [f"[{a['title']}]({a['url']}) — {a['created_at'][:10]}" for a in data[:N_ITEMS]]


def replace_section(text, name, lines):
    block = "\n\n".join(lines)
    pattern = re.compile(
        rf"(<!-- {name} starts -->).*?(<!-- {name} ends -->)", re.S
    )
    if not pattern.search(text):
        raise RuntimeError(f"markers for section '{name}' not found in README")
    return pattern.sub(rf"\1\n{block}\n\2", text)


def main():
    with open(README, encoding="utf-8") as f:
        text = f.read()

    text = replace_section(text, "blog", blog_entries())
    text = replace_section(text, "zenn", zenn_entries())
    text = replace_section(text, "qiita", qiita_entries())

    jst_now = datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M JST")
    text = replace_section(text, "updated", [f"Last refreshed: {jst_now}"])

    with open(README, "w", encoding="utf-8") as f:
        f.write(text)
    print("README.md refreshed")


if __name__ == "__main__":
    sys.exit(main())
