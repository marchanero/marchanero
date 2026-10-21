"""Scrape the personal website and rewrite the METRICS and PUBS blocks in README.md."""
import re, urllib.request

html = urllib.request.urlopen("https://robertosanchezreolid.netlify.app/").read().decode()

vals = {
    label: value
    for value, label in re.findall(
        r'readout-value">\s*([\d.,]+)\s*</div>\s*<div class="readout-label">([^<]+)<', html)
}
cit, h, i10, papers = (vals[k] for k in ("Citas", "h-index", "i10-index", "Papers"))
metrics = (
    f"![Citations](https://img.shields.io/badge/Citations-{cit}-4285F4?style=flat-square&logo=googlescholar&logoColor=white)\n"
    f"![h-index](https://img.shields.io/badge/h--index-{h}-success?style=flat-square)\n"
    f"![i10-index](https://img.shields.io/badge/i10--index-{i10}-success?style=flat-square)\n"
    f"![Papers](https://img.shields.io/badge/Papers-{papers}-informational?style=flat-square)"
)

pubs = []
for art in re.findall(r"<article.*?</article>", html, flags=re.S):
    m = re.search(r'<h3[^>]*>\s*<a href="([^"]+)"[^>]*>\s*(.*?)\s*</a>', art, flags=re.S)
    v = re.search(r'<p[^>]*mb-3[^>]*>\s*(.*?)\s*</p>', art, flags=re.S)
    if m and v:
        pubs.append(f"- [{m[2]}]({m[1].replace('&amp;', '&')}). *{v[1]}*")
assert pubs, "no publications found, site markup changed?"


def swap(s, name, body):
    return re.sub(rf"<!-- {name}:START -->.*?<!-- {name}:END -->",
                  lambda _: f"<!-- {name}:START -->\n{body}\n<!-- {name}:END -->", s, flags=re.S)


s = open("README.md").read()
s = swap(swap(s, "METRICS", metrics), "PUBS", "\n".join(pubs))
open("README.md", "w").write(s)
