#!/usr/bin/env python3
"""Render Jeremy-facing hub pages to static HTML with resolved wikilinks.

Used to prove the graph reads as pages when au-host is not on this box.
Does not replace the engine compile.

    python3 scripts/render_preview.py --out /tmp/watts-render
"""
from __future__ import annotations

import argparse
import html
import pathlib
import re

HUB = pathlib.Path(__file__).resolve().parent.parent
WIKILINK = re.compile(r"\[\[([^\]|:]+?)(?:\|([^\]]+))?\]\]")
FM = re.compile(r"^---\n(.*?)\n---\n", re.S)

PAGES = [
    "start here.md",
    "README.md",
    "ONBOARDING.md",
    "entities/scoreboard.md",
    "entities/watts-brand.md",
    "entities/connection-inventory.md",
    "entities/icp-context.md",
    "entities/intent-score.md",
    "catalogs/playbook-catalog.md",
    "catalogs/automation-dictionary.md",
    "catalogs/skill-catalog.md",
    "catalogs/signal-catalog.md",
    "catalogs/tactic-catalog.md",
    "playbooks/routing.md",
    "playbooks/signals.md",
    "playbooks/icp.md",
    "playbooks/email.md",
    "playbooks/sequencing.md",
    "playbooks/channels.md",
    "entities/email-components.md",
    "playbooks/social-queue.md",
    "playbooks/longform.md",
    "playbooks/newsletter.md",
    "playbooks/announcement.md",
    "playbooks/review.md",
    "playbooks/facts.md",
    "entities/watts-writing-prefs.md",
    "runbooks/hub-init.md",
    "catalogs/channel-catalog.md",
    "research/spear-automation-map.md",
    "research/icp-reconstruction.md",
    "research/voice-profile.md",
    "research/bonagura-outbound-state-machine.md",
    "research/igartua-event-ops-thin-layer.md",
    "intent-ranking-2026-09-21.md",
    "signal-digest-2026-09-21.md",
    "automations/intent-score-pass.md",
    "automations/signal-triggered-outbound.md",
    "automations/held-state-recheck.md",
    "automations/event-ops-pass.md",
]


def slug(path: pathlib.Path) -> str:
    return path.stem.replace(" ", "-")


def collect_stems() -> dict[str, pathlib.Path]:
    out: dict[str, pathlib.Path] = {}
    for p in HUB.rglob("*.md"):
        if ".git" in p.parts:
            continue
        out[p.stem] = p
    return out


INLINE_BOLD = re.compile(r"\*\*([^*]+)\*\*")
INLINE_CODE = re.compile(r"`([^`]+)`")


def inline(text: str) -> str:
    """Inline marks applied to already-linked HTML fragments."""
    text = INLINE_BOLD.sub(r"<strong>\1</strong>", text)
    text = INLINE_CODE.sub(r"<code>\1</code>", text)
    return text


def md_to_html(text: str, stems: dict[str, pathlib.Path]) -> str:
    body = FM.sub("", text)
    def link(m: re.Match[str]) -> str:
        target = m.group(1).strip()
        label = (m.group(2) or target).strip()
        dest = stems.get(target)
        if dest is None:
            return f'<span class="missing">[[{html.escape(target)}]]</span>'
        # label is already HTML-escaped by the caller (render_text).
        return f'<a href="{html.escape(slug(dest))}.html">{label}</a>'

    def render_text(s: str) -> str:
        # Escape raw markdown text first so things like <date> aren't
        # swallowed as real tags, then link wikilinks and apply inline marks.
        return inline(WIKILINK.sub(link, html.escape(s)))

    lines = body.splitlines()
    out: list[str] = []
    in_code = False
    in_ul = False
    in_table = False
    for line in lines:
        if line.startswith("```"):
            if in_ul:
                out.append("</ul>")
                in_ul = False
            if in_table:
                out.append("</table>")
                in_table = False
            if not in_code:
                out.append("<pre><code>")
                in_code = True
            else:
                out.append("</code></pre>")
                in_code = False
            continue
        if in_code:
            out.append(html.escape(line))
            continue
        if re.match(r"^\|.+\|$", line):
            if re.match(r"^\|[\s:|-]+\|$", line):
                continue
            cells = [render_text(c.strip()) for c in line.strip("|").split("|")]
            tag = "th" if not in_table else "td"
            if not in_table:
                if in_ul:
                    out.append("</ul>")
                    in_ul = False
                out.append("<table>")
                in_table = True
            out.append("<tr>" + "".join(f"<{tag}>{c}</{tag}>" for c in cells) + "</tr>")
            continue
        if in_table:
            out.append("</table>")
            in_table = False
        if line.startswith("- "):
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{render_text(line[2:])}</li>")
            continue
        if in_ul:
            out.append("</ul>")
            in_ul = False
        if line.startswith("# "):
            out.append(f"<h1>{render_text(line[2:])}</h1>")
        elif line.startswith("## "):
            out.append(f"<h2>{render_text(line[3:])}</h2>")
        elif line.startswith("### "):
            out.append(f"<h3>{render_text(line[4:])}</h3>")
        elif line.strip() == "":
            out.append("")
        else:
            out.append(f"<p>{render_text(line)}</p>")
    if in_ul:
        out.append("</ul>")
    if in_table:
        out.append("</table>")
    if in_code:
        out.append("</code></pre>")
    return "\n".join(out)


# Brand tokens from entities/watts-brand.md (Context.dev extraction, 2026-09-22).
CSS = """
:root { color-scheme: light;
  --brand: #529FA8; --ink: #091747; --accent: #0205D3; --surface: #FFFFFF; }
body { font: 16px/1.5 'Poppins', 'Helvetica Neue', Helvetica, Arial, ui-sans-serif, system-ui, sans-serif;
  max-width: 820px; margin: 2rem auto; padding: 0 1.25rem;
  color: var(--ink); background: var(--surface); }
.brandbar { display: flex; align-items: baseline; gap: 0.6rem;
  border-bottom: 3px solid var(--brand); padding-bottom: 0.5rem; margin-bottom: 1.5rem; }
.brandbar .pair { font-family: 'Poppins', Helvetica, Arial, sans-serif; font-weight: 600;
  font-size: 1.05rem; letter-spacing: 0.02em; color: var(--brand); }
.brandbar .pair em { color: var(--ink); font-style: normal; opacity: 0.55; }
.brandbar img.mark { height: 26px; width: auto; margin-right: 0.15rem; }
nav { font-size: 13px; margin-bottom: 2rem; }
nav a { margin-right: 0.75rem; }
h1, h2, h3 { font-family: 'Poppins', Helvetica, Arial, sans-serif; }
h1 { font-size: 1.6rem; color: var(--ink); }
h2 { font-size: 1.2rem; margin-top: 1.6rem; border-left: 4px solid var(--brand);
  padding-left: 0.5rem; }
table { border-collapse: collapse; width: 100%; font-size: 14px; }
th { background: color-mix(in srgb, var(--brand) 12%, white); }
th, td { border: 1px solid #d9e4e6; padding: 0.35rem 0.5rem; text-align: left; }
pre { background: #f4f8f9; padding: 0.8rem; overflow: auto; border-left: 3px solid var(--brand); }
a { color: var(--accent); }
.missing { color: #a11; }
.meta { color: #555; font-size: 13px; }
"""


BRANDBAR = (
    '<div class="brandbar">'
    '<img class="mark" src="watts-group-logo.svg" alt="Watts Group" '
    'onerror="this.remove()">'
    '<span class="pair">Opulent <em>&times;</em> Watts Group</span></div>'
)


def wrap(title: str, body: str, nav: str) -> str:
    return (
        "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap">'
        f"<title>{html.escape(title)} — Opulent &times; Watts Group</title>"
        f"<style>{CSS}</style></head><body>{BRANDBAR}"
        f"<nav>{nav}</nav>{body}</body></html>\n"
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/tmp/watts-render")
    args = ap.parse_args()
    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    logo = HUB / "assets/brand/watts-group-logo.svg"
    if logo.exists():
        (out / "watts-group-logo.svg").write_bytes(logo.read_bytes())
    stems = collect_stems()
    nav_links = []
    for rel in PAGES:
        p = HUB / rel
        if p.exists():
            nav_links.append(f'<a href="{slug(p)}.html">{html.escape(p.stem)}</a>')
    nav = " ".join(nav_links)
    written = 0
    for rel in PAGES:
        p = HUB / rel
        if not p.exists():
            continue
        text = p.read_text(encoding="utf-8")
        (out / f"{slug(p)}.html").write_text(
            wrap(p.stem, md_to_html(text, stems), nav), encoding="utf-8"
        )
        written += 1
    index = (
        "<h1>Opulent &times; Watts Group</h1>"
        "<p class=\"meta\">Watts context hub — static render of the typed "
        "Ars Umbris graph, branded per entities/watts-brand.md. "
        "Engine compile is the authority.</p><ul>"
        + "".join(f"<li><a href=\"{slug(HUB / rel)}.html\">{html.escape(rel)}</a></li>"
                  for rel in PAGES if (HUB / rel).exists())
        + "</ul>"
    )
    (out / "index.html").write_text(wrap("Opulent × Watts Group", index, nav), encoding="utf-8")
    print(f"wrote {written + 1} pages to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
