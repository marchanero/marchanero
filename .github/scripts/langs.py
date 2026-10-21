"""Rewrite the LANGS block in README.md with top languages across the user's non-fork repos."""
import json, os, re, urllib.request

USER = "marchanero"
EXCLUDE = {"mechanical_qmk"}  # vendored keyboard firmware, skews the C share
H = {"Accept": "application/vnd.github+json"}
if os.environ.get("GH_TOKEN"):
    H["Authorization"] = "Bearer " + os.environ["GH_TOKEN"]


def get(url):
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=H)))


repos = get(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner")
totals = {}
for r in repos:
    if r["fork"] or r["name"] in EXCLUDE:
        continue
    for lang, n in get(r["languages_url"]).items():
        totals[lang] = totals.get(lang, 0) + n

top = sorted(totals.items(), key=lambda x: -x[1])[:8]
total = sum(totals.values())
rows = "\n".join(
    f"| {l} | `{'█' * round(n / total * 20)}{'░' * (20 - round(n / total * 20))}` | {n / total:.1%} |"
    for l, n in top
)
block = f"<!-- LANGS:START -->\n| | | |\n|---|---|---|\n{rows}\n<!-- LANGS:END -->"
for f in ("README.md", "README.es.md"):
    s = open(f).read()
    open(f, "w").write(re.sub(r"<!-- LANGS:START -->.*?<!-- LANGS:END -->", lambda _: block, s, flags=re.S))
