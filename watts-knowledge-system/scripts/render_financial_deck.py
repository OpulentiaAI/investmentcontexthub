#!/usr/bin/env python3
"""Render the Watts financial-analysis demo deck from JSON.

The renderer is deliberately deterministic: it validates the mock/live input,
recomputes simple totals, and writes a self-contained HTML deck plus a message
file. It never invents values and never performs external calls.
"""

from __future__ import annotations

import html
import json
import math
import sys
from pathlib import Path

HUB = Path(__file__).resolve().parents[1]
DATA_PATH = HUB / "research" / "financial-demo-data.json"
HTML_PATH = HUB / "research" / "financial-analysis-demo.html"
MESSAGE_PATH = HUB / "research" / "financial-analysis-demo-message.txt"

REQUIRED_TOP = [
    "title",
    "subtitle",
    "disclaimer",
    "portfolio",
    "positions",
    "exposure",
    "signals",
    "forecasts",
    "decisions",
    "message",
]
PORTFOLIO_FIELDS = [
    "name",
    "navUsd",
    "inceptionNavUsd",
    "totalReturnPct",
    "benchmarkReturnPct",
    "ytdReturnPct",
    "volatilityPct",
    "sharpe",
    "maxDrawdownPct",
    "cashPct",
]
POSITION_FIELDS = ["name", "ticker", "weightPct", "returnPct", "sector", "conviction", "thesis"]
SECTOR_FIELDS = ["name", "weightPct"]
SIGNAL_FIELDS = ["asset", "analyst", "conviction", "horizonDays", "thesis", "evidence"]
FORECAST_FIELDS = ["subject", "horizon", "method", "output", "confidence"]
DECISION_FIELDS = ["asset", "decision", "rationale", "costCeilingUsd", "signalRefs"]
DECISIONS = {"paper", "no-trade", "watch", "escalate", "reject"}
CONFIDENCE = {"low", "medium", "high"}


def fail(errors: list[str]) -> None:
    for error in errors:
        print(f"error: {error}", file=sys.stderr)
    raise SystemExit(1)


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def finite_number(value: object, label: str, errors: list[str]) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        errors.append(f"{label}: expected finite number, got {value!r}")
        return None
    number = float(value)
    if not math.isfinite(number):
        errors.append(f"{label}: expected finite number, got {value!r}")
        return None
    return number


def require_fields(obj: dict, fields: list[str], label: str, errors: list[str]) -> None:
    for field in fields:
        if field not in obj:
            errors.append(f"{label}: missing required field `{field}`")


def validate(data: dict) -> list[str]:
    errors: list[str] = []
    for key in REQUIRED_TOP:
        if key not in data:
            errors.append(f"missing required top-level key `{key}`")
    if errors:
        return errors

    for key in ["title", "subtitle", "disclaimer", "message"]:
        if not isinstance(data[key], str) or not data[key].strip():
            errors.append(f"{key}: expected non-empty string")

    portfolio = data["portfolio"]
    if not isinstance(portfolio, dict):
        errors.append("portfolio: expected object")
    else:
        require_fields(portfolio, PORTFOLIO_FIELDS, "portfolio", errors)
        for field in PORTFOLIO_FIELDS[1:]:
            if field in portfolio:
                finite_number(portfolio[field], f"portfolio.{field}", errors)

    positions = data["positions"]
    if not isinstance(positions, list) or not positions:
        errors.append("positions: expected non-empty list")
    else:
        weight_sum = 0.0
        for i, position in enumerate(positions):
            label = f"positions[{i}]"
            if not isinstance(position, dict):
                errors.append(f"{label}: expected object")
                continue
            require_fields(position, POSITION_FIELDS, label, errors)
            weight = finite_number(position.get("weightPct"), f"{label}.weightPct", errors)
            finite_number(position.get("returnPct"), f"{label}.returnPct", errors)
            finite_number(position.get("conviction"), f"{label}.conviction", errors)
            if weight is not None:
                weight_sum += weight
        cash = portfolio.get("cashPct") if isinstance(portfolio, dict) else None
        if isinstance(cash, (int, float)) and not isinstance(cash, bool):
            total = weight_sum + float(cash)
            if abs(total - 100.0) > 0.51:
                errors.append(f"positions weights plus cashPct = {total:.2f}, expected ~100")

    exposure = data["exposure"]
    if not isinstance(exposure, dict):
        errors.append("exposure: expected object")
    else:
        sectors = exposure.get("sectors")
        if not isinstance(sectors, list) or not sectors:
            errors.append("exposure.sectors: expected non-empty list")
        else:
            sector_sum = 0.0
            for i, sector in enumerate(sectors):
                label = f"exposure.sectors[{i}]"
                if not isinstance(sector, dict):
                    errors.append(f"{label}: expected object")
                    continue
                require_fields(sector, SECTOR_FIELDS, label, errors)
                weight = finite_number(sector.get("weightPct"), f"{label}.weightPct", errors)
                if weight is not None:
                    sector_sum += weight
            if abs(sector_sum - 100.0) > 0.51:
                errors.append(f"exposure.sectors weights sum = {sector_sum:.2f}, expected ~100")

    for name, items, fields in [
        ("signals", data["signals"], SIGNAL_FIELDS),
        ("forecasts", data["forecasts"], FORECAST_FIELDS),
        ("decisions", data["decisions"], DECISION_FIELDS),
    ]:
        if not isinstance(items, list) or not items:
            errors.append(f"{name}: expected non-empty list")
            continue
        for i, item in enumerate(items):
            label = f"{name}[{i}]"
            if not isinstance(item, dict):
                errors.append(f"{label}: expected object")
                continue
            require_fields(item, fields, label, errors)
            if name == "signals":
                finite_number(item.get("conviction"), f"{label}.conviction", errors)
                finite_number(item.get("horizonDays"), f"{label}.horizonDays", errors)
            if name == "decisions":
                if item.get("decision") not in DECISIONS:
                    errors.append(f"{label}.decision: expected one of {sorted(DECISIONS)}")
                finite_number(item.get("costCeilingUsd"), f"{label}.costCeilingUsd", errors)
                if not isinstance(item.get("signalRefs"), list):
                    errors.append(f"{label}.signalRefs: expected list")
            if name == "forecasts" and item.get("confidence") not in CONFIDENCE:
                errors.append(f"{label}.confidence: expected one of {sorted(CONFIDENCE)}")
    return errors


def money(value: float) -> str:
    return f"${value:,.0f}"


def pct(value: float) -> str:
    return f"{value:.1f}%"


def slide(title: str, body: str) -> str:
    return f"""
<section class="slide">
  <h2>{esc(title)}</h2>
  {body}
</section>
"""


def render_html(data: dict) -> str:
    portfolio = data["portfolio"]
    positions = data["positions"]
    exposure = data["exposure"]
    signals = data["signals"]
    forecasts = data["forecasts"]
    decisions = data["decisions"]

    position_rows = "".join(
        "<tr>"
        f"<td>{esc(p['name'])}</td><td>{esc(p['ticker'])}</td><td>{esc(p['sector'])}</td>"
        f"<td>{pct(float(p['weightPct']))}</td><td>{pct(float(p['returnPct']))}</td>"
        f"<td>{float(p['conviction']):.2f}</td>"
        "</tr>"
        for p in positions
    )
    position_details = "".join(
        f"<li><strong>{esc(p['name'])}</strong> — {esc(p['thesis'])}</li>" for p in positions[:4]
    )
    sector_bars = "".join(
        "<div class='bar-row'><span>"
        + esc(s["name"])
        + "</span><div class='bar'><div style='width:"
        + str(float(s["weightPct"]))
        + "%'></div></div><strong>"
        + pct(float(s["weightPct"]))
        + "</strong></div>"
        for s in exposure["sectors"]
    )
    signal_rows = "".join(
        "<tr>"
        f"<td>{esc(s['asset'])}</td><td>{esc(s['analyst'])}</td>"
        f"<td>{float(s['conviction']):.2f}</td><td>{esc(s['horizonDays'])}</td>"
        f"<td>{esc(s['thesis'])}</td><td>{esc(s['evidence'])}</td>"
        "</tr>"
        for s in signals
    )
    forecast_rows = "".join(
        "<tr>"
        f"<td>{esc(f['subject'])}</td><td>{esc(f['horizon'])}</td>"
        f"<td>{esc(f['method'])}</td><td>{esc(f['output'])}</td><td>{esc(f['confidence'])}</td>"
        "</tr>"
        for f in forecasts
    )
    decision_rows = "".join(
        "<tr>"
        f"<td>{esc(d['asset'])}</td><td><span class='pill {esc(d['decision'])}'>{esc(d['decision'])}</span></td>"
        f"<td>{esc(d['rationale'])}</td><td>{money(float(d['costCeilingUsd']))}</td>"
        f"<td>{esc(', '.join(d['signalRefs']))}</td>"
        "</tr>"
        for d in decisions
    )

    slides = [
        slide(
            "1. Portfolio efficiency",
            f"""
<div class="metrics">
  <div class="metric"><span>NAV</span><strong>{money(float(portfolio['navUsd']))}</strong></div>
  <div class="metric"><span>Total return</span><strong>{pct(float(portfolio['totalReturnPct']))}</strong><em>vs benchmark {pct(float(portfolio['benchmarkReturnPct']))}</em></div>
  <div class="metric"><span>YTD return</span><strong>{pct(float(portfolio['ytdReturnPct']))}</strong></div>
  <div class="metric"><span>Volatility</span><strong>{pct(float(portfolio['volatilityPct']))}</strong></div>
  <div class="metric"><span>Sharpe</span><strong>{float(portfolio['sharpe']):.2f}</strong></div>
  <div class="metric"><span>Max drawdown</span><strong>{pct(float(portfolio['maxDrawdownPct']))}</strong></div>
  <div class="metric"><span>Cash</span><strong>{pct(float(portfolio['cashPct']))}</strong></div>
</div>
<p class="note">{esc(portfolio['name'])} — synthetic mock portfolio for demo only.</p>
""",
        ),
        slide(
            "2. Exposure and concentration",
            f"""
<div class="two-col">
  <div>
    <h3>Sector exposure</h3>
    {sector_bars}
  </div>
  <div>
    <h3>Top positions</h3>
    <table><thead><tr><th>Name</th><th>Ticker</th><th>Sector</th><th>Weight</th><th>Return</th><th>Conviction</th></tr></thead><tbody>{position_rows}</tbody></table>
    <h3>Thesis excerpts</h3>
    <ul>{position_details}</ul>
  </div>
</div>
<p class="note">Concentration flag: {esc(exposure.get('concentrationFlag', 'UNVERIFIED'))}; top position {pct(float(exposure.get('topPositionPct', 0.0)))}.</p>
""",
        ),
        slide(
            "3. Signals and forecasts",
            f"""
<h3>Investment signals</h3>
<table><thead><tr><th>Asset</th><th>Analyst</th><th>Conviction</th><th>Horizon</th><th>Thesis</th><th>Evidence</th></tr></thead><tbody>{signal_rows}</tbody></table>
<h3>Forecasts / scorecard</h3>
<table><thead><tr><th>Subject</th><th>Horizon</th><th>Method</th><th>Output</th><th>Confidence</th></tr></thead><tbody>{forecast_rows}</tbody></table>
""",
        ),
        slide(
            "4. Decisions and next actions",
            f"""
<table><thead><tr><th>Asset</th><th>Decision</th><th>Rationale</th><th>Cost ceiling</th><th>Signal refs</th></tr></thead><tbody>{decision_rows}</tbody></table>
<p class="note">{esc(data['message'])}</p>
<p class="disclaimer">{esc(data['disclaimer'])}</p>
""",
        ),
    ]

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(data['title'])}</title>
<style>
  :root {{ color-scheme: light; --ink:#17202a; --muted:#5d6b7a; --line:#d8e0e8; --accent:#0f6b5c; --warn:#9a5b00; --bad:#9b2226; }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color:var(--ink); background:#f5f7f9; }}
  .slide {{ min-height: 100vh; padding: 64px 8vw; border-bottom: 1px solid var(--line); background: white; }}
  h1, h2, h3 {{ margin: 0 0 18px; letter-spacing: 0; }}
  h1 {{ font-size: clamp(34px, 5vw, 68px); line-height: 1; }}
  h2 {{ font-size: clamp(26px, 3vw, 42px); }}
  h3 {{ font-size: 18px; margin-top: 24px; }}
  p, li, td, th {{ font-size: 15px; line-height: 1.45; }}
  .subtitle {{ color: var(--muted); font-size: 20px; margin-top: 12px; }}
  .metrics {{ display:grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 14px; margin: 28px 0; }}
  .metric {{ border:1px solid var(--line); border-radius: 14px; padding: 16px; background:#fbfcfd; }}
  .metric span {{ display:block; color:var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .08em; }}
  .metric strong {{ display:block; font-size: 28px; margin-top: 8px; }}
  .metric em {{ display:block; color:var(--muted); font-style: normal; margin-top: 6px; }}
  table {{ width:100%; border-collapse: collapse; margin: 14px 0 22px; }}
  th, td {{ border-bottom:1px solid var(--line); padding: 10px 8px; text-align:left; vertical-align: top; }}
  th {{ color:var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .06em; }}
  .two-col {{ display:grid; grid-template-columns: minmax(260px, .9fr) minmax(420px, 1.4fr); gap: 32px; }}
  .bar-row {{ display:grid; grid-template-columns: 110px 1fr 58px; gap: 10px; align-items:center; margin: 10px 0; }}
  .bar {{ height: 12px; background:#eef2f5; border-radius: 999px; overflow:hidden; }}
  .bar div {{ height:100%; background: var(--accent); }}
  .pill {{ display:inline-block; border-radius:999px; padding:4px 10px; font-size:12px; font-weight:700; }}
  .pill.paper {{ background:#e7f4ef; color:#0f6b5c; }}
  .pill.watch {{ background:#fff4d6; color:var(--warn); }}
  .pill.no-trade, .pill.reject {{ background:#fde8e8; color:var(--bad); }}
  .pill.escalate {{ background:#e8efff; color:#274b9f; }}
  .note, .disclaimer {{ color:var(--muted); }}
  .disclaimer {{ border-top:1px solid var(--line); padding-top:16px; margin-top:24px; }}
  ul {{ padding-left: 20px; }}
  @media (max-width: 900px) {{ .two-col {{ grid-template-columns: 1fr; }} .slide {{ padding: 42px 6vw; }} }}
  @media print {{ .slide {{ min-height:auto; page-break-after: always; }} }}
</style>
</head>
<body>
<section class="slide">
  <h1>{esc(data['title'])}</h1>
  <p class="subtitle">{esc(data['subtitle'])}</p>
  <p class="disclaimer">{esc(data['disclaimer'])}</p>
</section>
{''.join(slides)}
</body>
</html>
"""


def render_message(data: dict) -> str:
    portfolio = data["portfolio"]
    decisions = data["decisions"]
    counts = {name: sum(1 for d in decisions if d["decision"] == name) for name in sorted(DECISIONS)}
    lines = [
        "Watts financial analysis demo: PASS",
        f"Artifacts: research/financial-analysis-demo.html, research/financial-analysis-demo-message.txt",
        f"Data: research/financial-demo-data.json",
        f"Portfolio: {portfolio['name']} NAV {money(float(portfolio['navUsd']))}, total return {pct(float(portfolio['totalReturnPct']))} vs benchmark {pct(float(portfolio['benchmarkReturnPct']))}",
        f"Decisions: " + ", ".join(f"{k}={v}" for k, v in counts.items() if v),
        "Proof: JSON validated, HTML rendered, totals recomputed by scripts/render_financial_deck.py",
        "Blockers: none",
        "Safety: mock/research-only; no live trading, sends, contact, payments, publishing, or automation enablement.",
        "",
        data["message"],
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    try:
        data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail([f"missing data file: {DATA_PATH.relative_to(HUB)}"])
    except json.JSONDecodeError as exc:
        fail([f"invalid JSON in {DATA_PATH.relative_to(HUB)}: {exc}"])
    if not isinstance(data, dict):
        fail(["financial-demo-data.json: expected top-level object"])

    errors = validate(data)
    if errors:
        fail(errors)

    HTML_PATH.write_text(render_html(data), encoding="utf-8")
    MESSAGE_PATH.write_text(render_message(data), encoding="utf-8")
    print(f"wrote {HTML_PATH.relative_to(HUB)}")
    print(f"wrote {MESSAGE_PATH.relative_to(HUB)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
