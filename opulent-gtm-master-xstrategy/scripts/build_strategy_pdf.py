from __future__ import annotations

import json
import math
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "artifacts" / "opulent-gtm-master-xstrategy.pdf"
PROFILE = ROOT / "research" / "evidence" / "diego-workbook-profile.json"
FIELD_CORPUS = ROOT / "research" / "evidence" / "field-theory-gtm-sales-corpus.json"
USE_CASE_CATALOG = ROOT / "research" / "evidence" / "opulent-use-cases.json"
SLIDES = ROOT / "source-pack" / "gtm-engineering-template"

PAGE = (960, 540)
W, H = PAGE
BG = colors.HexColor("#F4F5FA")
PAPER = colors.HexColor("#FCFCFE")
INK = colors.HexColor("#1D2130")
MUTED = colors.HexColor("#6E7283")
LINE = colors.HexColor("#D9DCE7")
PINK = colors.HexColor("#F04777")
ORANGE = colors.HexColor("#FF824D")
RED = colors.HexColor("#D72B4E")
LILAC = colors.HexColor("#E7E0F4")
GREEN = colors.HexColor("#1F8C72")
BLUE = colors.HexColor("#4066D8")
YELLOW = colors.HexColor("#F2B84B")


def pstyle(size=13, color=INK, leading=None, bold=False, align=TA_LEFT):
    return ParagraphStyle(
        "body",
        fontName="Helvetica-Bold" if bold else "Helvetica",
        fontSize=size,
        leading=leading or size * 1.25,
        textColor=color,
        alignment=align,
        spaceAfter=0,
        spaceBefore=0,
    )


def para(c, text, x, y_top, width, height, size=13, color=INK, leading=None, bold=False):
    story = Paragraph(text, pstyle(size, color, leading, bold))
    _, used = story.wrap(width, height)
    story.drawOn(c, x, y_top - used)
    return used


def footer(c, page_num, section="OPULENT GTM MASTER XSTRATEGY"):
    c.setStrokeColor(LINE)
    c.line(42, 28, W - 42, 28)
    c.setFont("Helvetica", 7.5)
    c.setFillColor(MUTED)
    c.drawString(42, 15, section)
    c.drawRightString(W - 42, 15, f"{page_num:02d}")


def page_base(c, page_num, kicker, title, subtitle=None):
    c.setFillColor(BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(PINK)
    c.roundRect(42, H - 45, 74, 17, 8, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(79, H - 39.5, kicker.upper())
    c.setFillColor(INK)
    title_width = stringWidth(title, "Helvetica-Bold", 28)
    title_size = min(28, 28 * (W - 84) / title_width) if title_width else 28
    c.setFont("Helvetica-Bold", max(18, title_size))
    c.drawString(42, H - 83, title)
    if subtitle:
        para(c, subtitle, 42, H - 96, 790, 42, size=11.5, color=MUTED, leading=15)
    footer(c, page_num)


def card(c, x, y, w, h, title, body, accent=PINK, title_size=12, body_size=10.5):
    c.setFillColor(PAPER)
    c.setStrokeColor(LINE)
    c.roundRect(x, y, w, h, 10, fill=1, stroke=1)
    c.setFillColor(accent)
    c.roundRect(x + 12, y + h - 25, 28, 5, 2.5, fill=1, stroke=0)
    para(c, title, x + 14, y + h - 35, w - 28, 30, size=title_size, bold=True)
    para(c, body, x + 14, y + h - 68, w - 28, h - 72, size=body_size, color=MUTED, leading=body_size * 1.28)


def callout(c, x, y, w, h, label, value, detail="", accent=PINK):
    c.setFillColor(PAPER)
    c.setStrokeColor(LINE)
    c.roundRect(x, y, w, h, 10, fill=1, stroke=1)
    c.setFillColor(accent)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x + 14, y + h - 20, label.upper())
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(x + 14, y + h - 52, value)
    if detail:
        para(c, detail, x + 14, y + h - 61, w - 28, h - 70, size=9.2, color=MUTED, leading=12)


def bar(c, x, y, w, label, value, maximum, color=PINK, value_label=None):
    c.setFont("Helvetica-Bold", 9.5)
    c.setFillColor(INK)
    c.drawString(x, y + 10, label)
    c.setFillColor(LINE)
    c.roundRect(x, y - 3, w, 7, 3.5, fill=1, stroke=0)
    c.setFillColor(color)
    c.roundRect(x, y - 3, max(2, w * value / maximum), 7, 3.5, fill=1, stroke=0)
    c.setFont("Helvetica", 8.5)
    c.setFillColor(MUTED)
    c.drawRightString(x + w, y + 10, value_label or str(value))


def arrow(c, x1, y1, x2, y2, color=MUTED):
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(1.2)
    c.line(x1, y1, x2, y2)
    angle = math.atan2(y2 - y1, x2 - x1)
    for delta in (2.65, -2.65):
        c.line(x2, y2, x2 + 8 * math.cos(angle + delta), y2 + 8 * math.sin(angle + delta))


def source_line(c, text, x, y, width=850):
    return para(c, text, x, y, width, 30, size=7.7, color=MUTED, leading=9.5)


def fit_text(text, font, size, max_width):
    if stringWidth(text, font, size) <= max_width:
        return text
    suffix = "..."
    low, high = 0, len(text)
    while low < high:
        mid = (low + high + 1) // 2
        candidate = text[:mid].rstrip() + suffix
        if stringWidth(candidate, font, size) <= max_width:
            low = mid
        else:
            high = mid - 1
    return text[:low].rstrip() + suffix


def cover(c):
    c.linearGradient(0, 0, W, H, (colors.HexColor("#FFB071"), colors.HexColor("#F04C71"), colors.HexColor("#B61F56")), (0, 0.56, 1))
    c.setFillColor(colors.Color(1, 1, 1, alpha=0.12))
    c.circle(W - 40, H + 10, 260, fill=1, stroke=0)
    c.circle(120, -40, 210, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(56, H - 54, "OPULENTIA.AI")
    c.setFont("Helvetica-Bold", 46)
    c.drawString(56, 330, "Opulent GTM")
    c.drawString(56, 278, "Master XStrategy")
    para(c, "A source-backed operating system for relationship data, signal-led research, human-approved outreach, disciplined sales execution, and compounding account memory.", 58, 242, 620, 92, size=17, color=colors.white, leading=23)
    c.setFillColor(colors.white)
    c.roundRect(58, 102, 314, 34, 17, fill=1, stroke=0)
    c.setFillColor(RED)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(215, 115, "EVIDENCE -> DECISION -> ACTION -> LEARNING")
    c.setFillColor(colors.white)
    c.setFont("Helvetica", 9)
    c.drawString(58, 58, "Prepared 2026-08-05 | Opulent GTM Engineering")


def build():
    profile = json.loads(PROFILE.read_text())
    field = json.loads(FIELD_CORPUS.read_text())
    use_case_catalog = json.loads(USE_CASE_CATALOG.read_text())
    use_cases = use_case_catalog["use_cases"]
    field_count = field.get("uniqueBookmarkCount", 0)
    query_count = len(field.get("queryStats", []))
    c = canvas.Canvas(str(OUTPUT), pagesize=PAGE)
    c.setTitle("Opulent GTM Master XStrategy")
    c.setAuthor("Opulentia")
    page = 1

    cover(c)
    c.showPage()
    page += 1

    page_base(c, page, "THESIS", "Engineer the learning rate, not the send volume", "Opulent wins when every account interaction improves evidence, message fit, workflow proof, or sales execution. The unit of progress is a better decision, not another automated touch.")
    callout(c, 42, 285, 272, 120, "Primary objective", "Qualified pull", "Create credible demand for one workflow and one buyer wedge.", PINK)
    callout(c, 344, 285, 272, 120, "Operating moat", "Account memory", "Shared context, corrections, playbooks, and proof compound after every run.", ORANGE)
    callout(c, 646, 285, 272, 120, "Control point", "Human approval", "Draft freely; gate sends, publishes, enrollments, and CRM overwrites.", BLUE)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(42, 240, "Five strategic choices")
    choices = [
        ("1", "Start warm", "28 high-context connections before any scale motion."),
        ("2", "Narrow the wedge", "Financial services or consulting plus one workflow."),
        ("3", "Reference real signals", "Use current evidence, not token-swapped personalization."),
        ("4", "Sell proof", "Diagnose, demonstrate one workflow, then operationalize it."),
        ("5", "Write back learning", "Every correction changes account memory or a playbook."),
    ]
    for i, (num, title, detail) in enumerate(choices):
        x = 42 + i * 176
        c.setFillColor(PINK if i < 2 else ORANGE if i == 2 else BLUE)
        c.circle(x + 13, 193, 13, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(x + 13, 190, num)
        para(c, title, x + 34, 206, 132, 22, size=10.5, bold=True)
        para(c, detail, x + 4, 166, 158, 54, size=8.7, color=MUTED, leading=11.2)
    c.showPage(); page += 1

    page_base(c, page, "EVIDENCE", "The strategy is grounded in independent source layers", "Mailbox artifacts reveal the operating bottleneck; Opulent product sources define the thesis and offer surface; Field Theory expands the pattern set; repositories contribute production architecture.")
    card(c, 42, 290, 205, 125, "Diego mailbox + Excel", "2 emails, 3 workbooks, 4,366 network rows, a 336-contact ICP filter, a 135-contact refined list, and 28 warm Jeremy connections.", PINK)
    card(c, 266, 290, 205, 125, "Opulent product sources", "43 rendered GTM slides plus 44 live use cases. Together they define the operating thesis, buyer surface, proof inventory, and expansion paths.", ORANGE)
    card(c, 490, 290, 205, 125, "Field Theory CLI", f"v{field.get('fieldTheoryVersion','1.3.22')}; 869-bookmark local corpus. {query_count} search lenses produced {field_count} unique GTM and sales candidates after union and gap checks.", BLUE)
    card(c, 714, 290, 205, 125, "Reference repos", "Vercel eve supplies specialist ownership and approval gates. Browserbase supplies staged research, evidence capture, traces, and browser-to-API promotion.", GREEN)
    c.setFont("Helvetica-Bold", 18); c.setFillColor(INK); c.drawString(42, 244, "Evidence hierarchy")
    levels = [
        ("1", "First-party", "Mailbox bodies, workbooks, source deck, repo code"),
        ("2", "Observed", "Rendered slides, workbook profiles, commit inspections"),
        ("3", "External hypotheses", "Field Theory social posts and reported case metrics"),
        ("4", "Strategy inference", "Opulent sequencing, gates, offers, and scorecard"),
    ]
    for i, (n, t, d) in enumerate(levels):
        y = 194 - i * 37
        c.setFillColor((PINK, ORANGE, BLUE, LILAC)[i]); c.roundRect(42, y, 31, 24, 7, fill=1, stroke=0)
        c.setFillColor(colors.white if i < 3 else INK); c.setFont("Helvetica-Bold", 9); c.drawCentredString(57.5, y + 8, n)
        c.setFillColor(INK); c.setFont("Helvetica-Bold", 10.5); c.drawString(88, y + 12, t)
        c.setFillColor(MUTED); c.setFont("Helvetica", 9.5); c.drawString(205, y + 12, d)
    c.showPage(); page += 1

    page_base(c, page, "DATA LADDER", "The network is an evidence backlog, not an outreach list", "Scale is earned by moving accounts through identity, fit, signal, proof, and ownership gates.")
    ladder = [
        ("RAW NETWORK", 4245, "Named contacts", colors.HexColor("#D8DCEA")),
        ("FILTERED ICP", 336, "Segment-filtered contacts", colors.HexColor("#BFC8E9")),
        ("REFINED ICP", 135, "Use-case-mapped accounts", colors.HexColor("#F9B084")),
        ("WARM WEDGE", 28, "Jeremy connections + draft messages", PINK),
    ]
    widths = [800, 610, 430, 250]
    for i, ((label, value, detail, col), width) in enumerate(zip(ladder, widths)):
        y = 360 - i * 72
        x = 42 + (800 - width) / 2
        c.setFillColor(col); c.roundRect(x, y, width, 50, 10, fill=1, stroke=0)
        c.setFillColor(INK if i < 3 else colors.white); c.setFont("Helvetica-Bold", 10); c.drawString(x + 15, y + 30, label)
        c.setFont("Helvetica-Bold", 20); c.drawRightString(x + width - 15, y + 24, f"{value:,}")
        c.setFont("Helvetica", 8.5); c.drawString(x + 15, y + 12, detail)
    c.setFillColor(INK); c.setFont("Helvetica-Bold", 14); c.drawString(42, 75, "Rule: enrich only after the account passes fit, signal, and owner gates.")
    source_line(c, "Source: Diego Outlook attachments and PII-safe workbook profile. Raw records remain outside the reusable skill.", 42, 58)
    c.showPage(); page += 1

    page_base(c, page, "DIAGNOSIS", "The hard problem is reliable enrichment; messaging is downstream", "Diego's own notes show that company classification required the most prompting and still left many firms unresolved.")
    card(c, 42, 285, 205, 125, "Company identity", "Resolve domain, legal entity, and current company before industry or ICP classification. Generic names cannot be classified from text alone.", RED)
    card(c, 266, 285, 205, 125, "Evidence-backed fit", "Map a use case to observed operations, a current signal, and a reachable owner. A segment label is not enough.", ORANGE)
    card(c, 490, 285, 205, 125, "Contactability", "The raw network has only 77 email addresses; the filtered ICP set has 7. Do not confuse a LinkedIn URL with a verified channel.", BLUE)
    card(c, 714, 285, 205, 125, "Message generation", "Warm LinkedIn messaging was rated easy. Keep it last so the copy reflects verified evidence and sender voice.", GREEN)
    c.setFont("Helvetica-Bold", 18); c.setFillColor(INK); c.drawString(42, 242, "Operational consequences")
    impacts = [
        ("Normalize ownership", "Cell color is not a durable owner field."),
        ("Preserve provenance", "Every enriched field points back to source and capture time."),
        ("Keep fact separate", "Models may propose inferences; evidence decides truth."),
        ("Sample before scale", "Review accepted and rejected accounts from every batch."),
    ]
    for i, (t, d) in enumerate(impacts):
        x = 42 + i * 218
        c.setFillColor(PAPER); c.setStrokeColor(LINE); c.roundRect(x, 105, 200, 105, 9, fill=1, stroke=1)
        c.setFillColor((PINK, ORANGE, BLUE, GREEN)[i]); c.circle(x + 20, 184, 7, fill=1, stroke=0)
        para(c, t, x + 34, 194, 150, 26, size=10.5, bold=True)
        para(c, d, x + 14, 157, 172, 48, size=9, color=MUTED, leading=11.5)
    c.showPage(); page += 1

    page_base(c, page, "WEDGE", "Start where relationship access, proof, and pain overlap", "The refined list is concentrated in financial services and consulting. Use that concentration as an advantage, not as permission to stay broad.")
    c.setFont("Helvetica-Bold", 15); c.setFillColor(INK); c.drawString(42, 405, "Refined 135-contact segment mix")
    segments = [("Financial services", 60, PINK), ("Consulting", 34, ORANGE), ("Manufacturing", 12, BLUE), ("Legal", 7, GREEN), ("Professional services", 6, YELLOW), ("Insurance", 6, LILAC)]
    for i, (label, value, col) in enumerate(segments):
        bar(c, 42, 370 - i * 38, 380, label, value, 60, col, f"{value} contacts")
    card(c, 470, 292, 215, 122, "Wedge A", "Financial services + deal-flow triage, portfolio intelligence, pre-call briefs, or review-heavy financial analysis.", PINK)
    card(c, 704, 292, 215, 122, "Wedge B", "Consulting + agent-run analysis, proposal support, knowledge synthesis, or client-delivery quality control.", ORANGE)
    card(c, 470, 142, 215, 122, "Selection gate", "Choose one buyer and one workflow where Opulent can show a complete input-to-reviewed-output proof in days.", BLUE)
    card(c, 704, 142, 215, 122, "Expansion logic", "Expand inside the account after workflow proof; expand to another segment only after repeatable pull and a clear counterfactual.", GREEN)
    c.showPage(); page += 1

    page_base(c, page, "USE-CASE PORTFOLIO", "Use one portfolio to narrow the offer, not broaden it", "The live catalog is a proof and expansion map. Source-published labels are preserved; buyer, value, lifecycle, and portfolio-role labels are editorial GTM classifications.")
    role_counts = use_case_catalog["counts"]["portfolio_roles"]
    category_counts = use_case_catalog["counts"]["site_categories"]
    summary_cards = [
        ("LIVE USE CASES", str(use_case_catalog["count"]), "Every index card extracted and source-linked", PINK),
        ("SITE CATEGORIES", str(len(category_counts)), "From GTM and finance to engineering optimization", ORANGE),
        ("FEATURED", str(use_case_catalog["counts"]["featured"]), "Observed source signal, not a GTM ranking", BLUE),
        ("PRIMARY WEDGES", str(role_counts.get("Primary wedge", 0)), "Editorial shortlist; validate against buyer evidence", GREEN),
    ]
    for i,(label,value,detail,col) in enumerate(summary_cards):
        callout(c,42+i*224,306,205,92,label,value,detail,col)
    c.setFillColor(INK); c.setFont("Helvetica-Bold",14); c.drawString(42,268,"Live portfolio by source category")
    category_items = list(category_counts.items())
    for i,(label,value) in enumerate(category_items):
        col=i//5; row=i%5; x=42+col*448; y=232-row*30
        bar(c,x,y,405,label,value,max(category_counts.values()),(PINK,ORANGE,BLUE,GREEN,RED)[row],str(value))
    role_line = " | ".join(f"{label}: {value}" for label,value in role_counts.items())
    c.setFillColor(INK); c.setFont("Helvetica-Bold",9); c.drawString(42,76,fit_text(role_line,"Helvetica-Bold",9,865))
    source_line(c,f"Source: {use_case_catalog['source_url']} | Captured {use_case_catalog['retrieved_at']} | Full observed and editorial labels: references/opulent-use-case-catalog.md",42,58)
    c.showPage(); page += 1

    chunks = [use_cases[0:15], use_cases[15:30], use_cases[30:44]]
    for chunk_index, chunk in enumerate(chunks, 1):
        page_base(c, page, "LABELED CATALOG", f"All 44 use cases, labeled for commercial use ({chunk_index}/3)", "Each row shows the published title plus source category and the editorial buyer, value, lifecycle, and portfolio-role labels. Full summaries and capability tags remain in the catalog reference.")
        for i,row in enumerate(chunk):
            y=387-i*23
            observed=row["observed"]; labels=row["gtm_labels"]
            c.setFillColor(PAPER if i%2==0 else colors.HexColor("#F0F1F6")); c.setStrokeColor(LINE)
            c.roundRect(42,y-12,876,21,5,fill=1,stroke=0)
            c.setFillColor((PINK,ORANGE,BLUE,GREEN,RED)[i%5]); c.circle(54,y-1,7,fill=1,stroke=0)
            c.setFillColor(colors.white); c.setFont("Helvetica-Bold",6.3); c.drawCentredString(54,y-3,str(row["ordinal"]))
            featured = "  [FEATURED]" if observed["featured"] else ""
            title = fit_text(row["title"]+featured,"Helvetica-Bold",8.2,820)
            c.setFillColor(INK); c.setFont("Helvetica-Bold",8.2); c.drawString(69,y+1,title)
            detail = f"{observed['site_category']} | buyer: {labels['buyer_group']} | value: {labels['value_motion']} | lifecycle: {labels['lifecycle_stage']} | role: {labels['portfolio_role']}"
            c.setFillColor(MUTED); c.setFont("Helvetica",6.6); c.drawString(69,y-8,fit_text(detail,"Helvetica",6.6,830))
            c.linkURL(row["url"],(42,y-12,918,y+9),relative=0)
        source_line(c,"Observed fields come from the live Opulent use-case index. GTM labels are deterministic editorial classifications; they are not source-site claims.",42,52)
        c.showPage(); page += 1

    page_base(c, page, "OFFER", "Lead with one workflow that is slow, costly, or hard to review", "The commercial story is diagnosis -> proof -> production -> learning retainer. Tools stay backstage.")
    phases = [
        ("1", "DIAGNOSE", "30-minute workflow map\nInputs, owners, review gates, failure cost"),
        ("2", "PROVE", "7-day proof pack\nReal artifact, real evidence, human-reviewed result"),
        ("3", "OPERATIONALIZE", "Production sprint\nConnectors, controls, evaluation, handoff"),
        ("4", "COMPOUND", "Learning retainer\nNew workflows, corrections, measurements, playbooks"),
    ]
    for i, (num, title, body) in enumerate(phases):
        x = 42 + i * 219
        c.setFillColor(PAPER); c.setStrokeColor(LINE); c.roundRect(x, 230, 200, 160, 12, fill=1, stroke=1)
        c.setFillColor((PINK, ORANGE, BLUE, GREEN)[i]); c.circle(x + 28, 354, 18, fill=1, stroke=0)
        c.setFillColor(colors.white); c.setFont("Helvetica-Bold", 11); c.drawCentredString(x + 28, 350, num)
        para(c, title, x + 55, 366, 128, 30, size=12, bold=True)
        para(c, body.replace("\n", "<br/>"), x + 18, 315, 164, 80, size=10, color=MUTED, leading=13)
        if i < 3: arrow(c, x + 201, 310, x + 218, 310)
    c.setFillColor(INK); c.setFont("Helvetica-Bold", 16); c.drawString(42, 178, "Pricing is a hypothesis to test, not a fact to inherit")
    para(c, "Use paid diagnosis and outcome-based implementation as the initial design. Field Theory operators report $3K-$5K audits and $15K-$30K implementations, but Opulent should calibrate ranges against buyer value, delivery cost, and actual close behavior.", 42, 160, 870, 60, size=11, color=MUTED, leading=15)
    source_line(c, "Hypothesis sources: https://x.com/lukepierceops/status/2059606571357720939 and https://x.com/lukepierceops/status/2050545337253675154", 42, 86)
    c.showPage(); page += 1

    page_base(c, page, "LOOP", "One closed loop turns every interaction into leverage", "This is the master system. Channels and tools plug into it; they do not replace it.")
    nodes = [
        ("DEFINE", "Wedge + offer", PINK), ("NORMALIZE", "Identity + owner", ORANGE), ("SIGNAL", "Why now", BLUE),
        ("RESEARCH", "Decision brief", GREEN), ("APPROVE", "Human gate", YELLOW), ("EXECUTE", "Channel + sales", RED),
        ("MEASURE", "Funnel + quality", BLUE), ("WRITE BACK", "Memory + playbook", PINK),
    ]
    positions = [(80,330),(260,390),(470,390),(680,330),(680,190),(470,125),(260,125),(80,190)]
    for i in range(len(nodes)):
        x1,y1=positions[i]; x2,y2=positions[(i+1)%len(nodes)]; arrow(c,x1+68,y1+25,x2+10,y2+25,colors.HexColor("#A4A9B8"))
    for (title,detail,col),(x,y) in zip(nodes,positions):
        c.setFillColor(PAPER); c.setStrokeColor(LINE); c.roundRect(x,y,135,52,10,fill=1,stroke=1)
        c.setFillColor(col); c.roundRect(x+9,y+36,32,5,2.5,fill=1,stroke=0)
        c.setFillColor(INK); c.setFont("Helvetica-Bold",9.5); c.drawString(x+10,y+23,title)
        c.setFillColor(MUTED); c.setFont("Helvetica",8); c.drawString(x+10,y+10,detail)
    c.setFillColor(colors.white); c.setStrokeColor(LINE); c.circle(W/2,265,82,fill=1,stroke=1)
    c.setFillColor(INK); c.setFont("Helvetica-Bold",17); c.drawCentredString(W/2,274,"COMPOUND")
    c.setFillColor(MUTED); c.setFont("Helvetica",9.5); c.drawCentredString(W/2,253,"every correction")
    c.drawCentredString(W/2,240,"improves the system")
    c.showPage(); page += 1

    page_base(c, page, "SIGNALS", "Build a signal factory before an outbound factory", "The system watches a few high-information sources, gates candidates, captures evidence, and only then drafts action.")
    sources = ["Contracts / filings", "Funding / hiring", "Tech / reviews", "Events / partners", "Active LinkedIn"]
    for i, label in enumerate(sources):
        y = 379 - i*58
        c.setFillColor(PAPER); c.setStrokeColor(LINE); c.roundRect(42,y,170,38,9,fill=1,stroke=1)
        c.setFillColor((PINK,ORANGE,BLUE,GREEN,YELLOW)[i]); c.circle(58,y+19,6,fill=1,stroke=0)
        c.setFillColor(INK); c.setFont("Helvetica-Bold",9.5); c.drawString(72,y+14,label)
    stages=[("DISCOVER","Candidate URLs"),("GATE","Fit + freshness"),("CAPTURE","Evidence + trace"),("EXTRACT","Fact + inference"),("SYNTHESIZE","Decision brief")]
    for i,(t,d) in enumerate(stages):
        x=270+i*130
        c.setFillColor(PAPER); c.setStrokeColor(LINE); c.roundRect(x,230,112,106,10,fill=1,stroke=1)
        c.setFillColor((PINK,ORANGE,BLUE,GREEN,RED)[i]); c.roundRect(x+12,308,30,5,2.5,fill=1,stroke=0)
        para(c,t,x+12,298,88,24,size=9.5,bold=True)
        para(c,d,x+12,270,88,40,size=8.7,color=MUTED,leading=11)
        if i<4:arrow(c,x+112,283,x+129,283)
    c.setFillColor(INK); c.setFont("Helvetica-Bold",15); c.drawString(270,188,"Graduation rule")
    para(c,"Exploratory browser steps stay traceable. Stable repeat interactions graduate to typed APIs with redaction, schema validation, and tests. Dynamic UI claims keep screenshots or traces; static claims keep attributable URLs.",270,170,625,70,size=10.5,color=MUTED,leading=14)
    source_line(c,"Reference patterns: https://github.com/browserbase/skills/tree/main/skills at commit 6afe8663693372e59e167dfa5be37932af09ae3d",270,92,625)
    c.showPage(); page += 1

    page_base(c, page, "ACCOUNT ACTION", "Every account brief must support a decision", "A good brief answers why this account, why now, what to propose, and what evidence would prove the hypothesis wrong.")
    fields=[("WHY THIS ACCOUNT","Fit, relationship, segment"),("WHY NOW","Current, attributable signal"),("WORKFLOW","One reviewed outcome"),("BUYER","Owner, champion, blocker"),("COUNTER-EVIDENCE","What could disconfirm fit"),("NEXT ACTION","Safe, low-pressure step")]
    for i,(t,d) in enumerate(fields):
        x=42+(i%3)*294; y=298-(i//3)*126
        card(c,x,y,270,102,t,d,(PINK,ORANGE,BLUE,GREEN,YELLOW,RED)[i],title_size=10.5,body_size=9.2)
    c.setFillColor(INK); c.setFont("Helvetica-Bold",15); c.drawString(42,145,"Message contract")
    msg="1. Observed signal or real relationship.   2. Likely operational consequence as a hypothesis.   3. One useful workflow or proof.   4. One low-pressure ask with permission to decline."
    para(c,msg,42,126,865,70,size=11.2,color=MUTED,leading=16)
    c.showPage(); page += 1

    page_base(c, page, "MOTIONS", "Run four motions from the same evidence spine", "Warm relationships lead; signal-led outbound adds reach; authority compounds trust; partners and events create distribution without list saturation.")
    card(c,42,270,205,140,"1. Warm network","Pilot 10-15 accounts per week from the 28 warm connections. Human review every message. Use discovery to validate the use-case map.",PINK)
    card(c,266,270,205,140,"2. Signal-led outbound","Monitor two or three source families per wedge. Contact only when fit, evidence, freshness, and a safe channel are present.",ORANGE)
    card(c,490,270,205,140,"3. Authority","Turn delivery artifacts into founder and employee field notes, technical explainers, case proof, and useful ideas for the same buyer wedge.",BLUE)
    card(c,714,270,205,140,"4. Partners + events","Activate agencies, integrations, referrals, platforms, affiliates, and high-density events. Agents prepare evidence; humans build relationships.",GREEN)
    c.setFillColor(INK); c.setFont("Helvetica-Bold",15); c.drawString(42,216,"Channel rules")
    rules=["One owner per channel","One proof per claim","One next action","No irreversible action without approval"]
    for i,r in enumerate(rules):
        x=42+i*218; c.setFillColor(PAPER); c.setStrokeColor(LINE); c.roundRect(x,130,200,55,9,fill=1,stroke=1)
        c.setFillColor((PINK,ORANGE,BLUE,GREEN)[i]); c.circle(x+18,158,6,fill=1,stroke=0)
        para(c,r,x+32,169,150,28,size=9.5,bold=True)
    c.showPage(); page += 1

    page_base(c, page, "SALES", "The sales process is the proof-delivery system", "AI should eliminate dropped context and commitments, while humans own diagnosis, trust, judgment, and commercial decisions.")
    sales=[("PREP","Account brief, attendees, hypothesis, relevant proof"),("DISCOVER","Current workflow, consequence, owner, urgency, constraints"),("DEMO","Only the workflow that answers the diagnosed problem"),("COMMIT","Decision, owner, deadline, promised artifact"),("FOLLOW UP","Recap, evidence, ROI, implementation path, proposal")]
    for i,(t,d) in enumerate(sales):
        x=42+i*176
        c.setFillColor(PAPER); c.setStrokeColor(LINE); c.roundRect(x,255,158,145,11,fill=1,stroke=1)
        c.setFillColor((PINK,ORANGE,BLUE,GREEN,RED)[i]); c.roundRect(x+12,372,42,6,3,fill=1,stroke=0)
        para(c,t,x+12,360,132,26,size=11,bold=True)
        para(c,d,x+12,324,132,72,size=9.2,color=MUTED,leading=12)
        if i<4:arrow(c,x+158,328,x+175,328)
    c.setFillColor(INK); c.setFont("Helvetica-Bold",15); c.drawString(42,208,"No forgotten commitments")
    para(c,"Meeting notes, CRM state, inbox, and internal messages should converge into one commitment log: who promised what, by when, what evidence is missing, and what the seller must do next. Automated reminders are useful only when the underlying commitment is explicit.",42,190,865,75,size=11,color=MUTED,leading=15)
    source_line(c,"Field Theory examples: https://x.com/fivosaresti/status/2072032494912704777 and https://x.com/jasonlk/status/2060878172632105002",42,102)
    c.showPage(); page += 1

    page_base(c, page, "OPERATING MODEL", "One lead, clear specialists, one shared commercial context", "Borrow the strongest architectural constraint from the Vercel eve template: shared state has one owner, briefs are self-contained, and irreversible actions are gated.")
    c.setFillColor(PAPER); c.setStrokeColor(LINE); c.roundRect(42,300,170,95,11,fill=1,stroke=1)
    para(c,"STRATEGY OWNER",58,374,138,25,size=11,bold=True); para(c,"Wedge, offer, claims, Brand and Revenue Context",58,342,138,50,size=9,color=MUTED,leading=12)
    specialists=[("RESEARCH + DATA","Identity, signals, evidence"),("CAMPAIGN LEAD","Brief, cohort, experiment"),("CHANNEL OWNER","Adapt, draft, operate"),("SALES OWNER","Discover, commit, close")]
    for i,(t,d) in enumerate(specialists):
        x=270+i*164
        c.setFillColor(PAPER); c.setStrokeColor(LINE); c.roundRect(x,300,145,95,11,fill=1,stroke=1)
        c.setFillColor((PINK,ORANGE,BLUE,GREEN)[i]); c.roundRect(x+12,370,32,5,2.5,fill=1,stroke=0)
        para(c,t,x+12,360,120,30,size=9.2,bold=True); para(c,d,x+12,326,120,35,size=8.5,color=MUTED,leading=11)
        arrow(c,212 if i==0 else x-19,347,x,347)
    c.setFillColor(PINK); c.roundRect(225,174,510,62,15,fill=1,stroke=0)
    c.setFillColor(colors.white); c.setFont("Helvetica-Bold",14); c.drawCentredString(480,207,"BRAND + REVENUE CONTEXT / ACCOUNT MEMORY")
    c.setFont("Helvetica",9); c.drawCentredString(480,190,"One owner per field. Every specialist reads before work and writes only defined outcomes.")
    for x in [127,342,506,670,834]: arrow(c,x,300,480,236,colors.HexColor("#9CA1B2"))
    source_line(c,"Reference: https://github.com/vercel-labs/marketing-team-eve-template at commit 7ccaa5f406edf179cbef4d81bcb200fd3ee9da67",42,107)
    c.showPage(); page += 1

    page_base(c, page, "90 DAYS", "Sequence proof before scale", "Each phase has an exit gate. Calendar progress never substitutes for evidence.")
    phases90=[
        ("DAYS 0-14","FOUNDATION","One wedge, context, schema, baseline","Identity + owner + evidence on every pilot account",PINK),
        ("DAYS 15-30","WARM WEDGE","10-15 high-context accounts per week","One message-workflow combination shows pull",ORANGE),
        ("DAYS 31-50","SIGNAL ENGINE","2-3 monitored source families","Fresh evidence and bounded false positives",BLUE),
        ("DAYS 51-70","AUTHORITY + PARTNERS","Proof-led content and one partner route","Distribution originates from real delivery evidence",GREEN),
        ("DAYS 71-90","SCALE OR KILL","Compare wedges, offers, channels","Keep, kill, or revise every play",RED),
    ]
    for i,(days,t,body,gate,col) in enumerate(phases90):
        x=42+i*176
        c.setFillColor(PAPER); c.setStrokeColor(LINE); c.roundRect(x,210,158,200,12,fill=1,stroke=1)
        c.setFillColor(col); c.roundRect(x,378,158,32,12,fill=1,stroke=0); c.rect(x,378,158,16,fill=1,stroke=0)
        c.setFillColor(colors.white); c.setFont("Helvetica-Bold",9); c.drawCentredString(x+79,389,days)
        para(c,t,x+14,356,130,35,size=11,bold=True); para(c,body,x+14,316,130,58,size=9,color=MUTED,leading=12)
        c.setStrokeColor(LINE); c.line(x+14,264,x+144,264)
        c.setFillColor(col); c.setFont("Helvetica-Bold",7.5); c.drawString(x+14,248,"EXIT GATE")
        para(c,gate,x+14,235,130,55,size=8.5,color=MUTED,leading=11)
        if i<4:arrow(c,x+158,310,x+175,310)
    c.setFillColor(INK); c.setFont("Helvetica-Bold",14); c.drawString(42,162,"Default constraint: expand only one dimension at a time")
    para(c,"More accounts, another signal source, another channel, or another segment - never all four in the same experiment.",42,143,820,45,size=10.5,color=MUTED,leading=14)
    c.showPage(); page += 1

    page_base(c, page, "CADENCE", "A weekly rhythm keeps research, sales, and learning synchronized", "The cadence turns the strategy into an operating habit and makes approvals visible.")
    week=[("MON","Evidence refresh","Choose hypothesis"),("TUE","Account briefs","Approve target set"),("WED","Outreach + prep","Execute safely"),("THU","Discovery + demos","Capture commitments"),("FRI","Review + write-back","Keep, kill, revise")]
    for i,(day,a,b) in enumerate(week):
        x=42+i*176
        c.setFillColor(PAPER); c.setStrokeColor(LINE); c.roundRect(x,275,158,120,11,fill=1,stroke=1)
        c.setFillColor((PINK,ORANGE,BLUE,GREEN,RED)[i]); c.roundRect(x,363,158,32,11,fill=1,stroke=0); c.rect(x,363,158,16,fill=1,stroke=0)
        c.setFillColor(colors.white); c.setFont("Helvetica-Bold",10); c.drawCentredString(x+79,374,day)
        para(c,a,x+14,342,130,28,size=10,bold=True); para(c,b,x+14,307,130,35,size=9,color=MUTED,leading=12)
    c.setFont("Helvetica-Bold",15); c.setFillColor(INK); c.drawString(42,224,"Approval gates")
    gates=["Identity + recipient","Evidence freshness","Message fit","Channel basis","Sender + next action","CRM write-back"]
    for i,g in enumerate(gates):
        x=42+(i%3)*294; y=167-(i//3)*48
        c.setFillColor(PAPER); c.setStrokeColor(LINE); c.roundRect(x,y,270,34,8,fill=1,stroke=1)
        c.setFillColor((PINK,ORANGE,BLUE,GREEN,YELLOW,RED)[i]); c.circle(x+17,y+17,5,fill=1,stroke=0)
        c.setFillColor(INK); c.setFont("Helvetica-Bold",9); c.drawString(x+30,y+13,g)
    c.showPage(); page += 1

    page_base(c, page, "MEASUREMENT", "Measure data health, funnel quality, learning speed, and economics", "Activity counts are diagnostic. Commercial decisions require quality and downstream outcomes.")
    card(c,42,270,205,140,"Data health","Identity coverage, dedupe rate, domain resolution, verified channel coverage, current signals, owner coverage, evidence freshness.",PINK)
    card(c,266,270,205,140,"Research quality","Candidate acceptance, unsupported claims, false positives by source, signal-to-brief latency, correction reasons.",ORANGE)
    card(c,490,270,205,140,"Funnel quality","Approved targets -> positive replies -> discovery -> qualified opportunity -> proposal -> win, by cohort.",BLUE)
    card(c,714,270,205,140,"Learning + economics","Experiments per week, playbook reuse, correction capture, human minutes, cost per accepted account, payback.",GREEN)
    c.setFont("Helvetica-Bold",15); c.setFillColor(INK); c.drawString(42,220,"Experiment rule")
    para(c,"Baseline first. Change one variable. Define the cohort, leading indicator, revenue-quality outcome, guardrail, stop date, and keep-kill-revise decision before execution.",42,202,860,50,size=11,color=MUTED,leading=15)
    c.setFillColor(INK); c.setFont("Helvetica-Bold",13); c.drawString(42,128,"North-star operating metric")
    c.setFillColor(PINK); c.setFont("Helvetica-Bold",20); c.drawString(42,92,"Qualified pipeline created per human hour")
    c.setFillColor(MUTED); c.setFont("Helvetica",9.5); c.drawString(42,69,"Guard with win quality, evidence accuracy, and customer payback.")
    c.showPage(); page += 1

    page_base(c, page, "DECK INHERITANCE", "The master strategy preserves the strongest Opulent GTM patterns", "The source deck was rendered slide by slide. These four representative frames anchor the strategy's visual and narrative inheritance.")
    frames=[(1,"GTM as engineering"),(8,"Six-layer system"),(17,"Reusable company research"),(39,"Sales from outreach to signature")]
    for i,(num,label) in enumerate(frames):
        path=SLIDES/f"slide-{num}.png"; x=42+i*221
        if path.exists():
            img=ImageReader(str(path)); c.drawImage(img,x,210,205,116,preserveAspectRatio=True,anchor='c',mask='auto')
        c.setFillColor(INK); c.setFont("Helvetica-Bold",9.5); c.drawString(x,192,label)
        c.setFillColor(MUTED); c.setFont("Helvetica",8); c.drawString(x,177,f"Source slide {num}")
    card(c,42,54,421,100,"What was retained","Outcome delegation, signal-led research, minimal modular infrastructure, bounded outreach, disciplined discovery, relevant demos, proof, pricing, and reviewed delivery.",PINK,title_size=10.5,body_size=8.8)
    card(c,480,54,439,100,"What was added","Diego's actual data ladder, PII and provenance gates, explicit ownership, 90-day sequencing, weekly approvals, experiment contracts, and learning economics.",BLUE,title_size=10.5,body_size=8.8)
    c.showPage(); page += 1

    page_base(c, page, "RISKS", "Five failure modes can erase the advantage", "The strategy is only useful if its non-negotiables survive pressure to move faster.")
    risks=[
        ("Raw-list automation","High volume from weak identity and stale fit creates noise and reputation risk.","Gate by identity, fit, signal, owner, and channel basis."),
        ("Synthetic confidence","A filled cell looks true even when classification is inferred.","Preserve evidence, confidence, expiry, and human review."),
        ("Specialist overlap","Multiple agents rewrite positioning and lose accountability.","One owner per shared artifact and one-level delegation."),
        ("Unapproved action","A good draft becomes a bad external effect.","Require human approval for sends, publishes, enrollments, and overwrites."),
        ("Vanity scale","More sends and meetings hide weak opportunity quality.","Track adjacent-stage conversion, disqualification, economics, and learning."),
    ]
    for i,(t,d,m) in enumerate(risks):
        y=350-i*64
        c.setFillColor(PAPER); c.setStrokeColor(LINE); c.roundRect(42,y,876,52,9,fill=1,stroke=1)
        c.setFillColor((RED,ORANGE,PINK,BLUE,GREEN)[i]); c.roundRect(42,y,8,52,4,fill=1,stroke=0)
        para(c,t,64,y+38,150,24,size=10.5,bold=True)
        para(c,d,225,y+39,330,32,size=8.8,color=MUTED,leading=11)
        para(c,"CONTROL: "+m,570,y+39,330,32,size=8.5,color=INK,leading=11,bold=True)
    c.showPage(); page += 1

    page_base(c, page, "NEXT 10 DAYS", "Turn the strategy into one controlled revenue experiment", "The immediate goal is not to automate the GTM stack. It is to produce one trustworthy learning loop with a real buyer cohort.")
    actions=[
        ("1","Select","Choose financial services or consulting plus one workflow and buyer."),
        ("2","Normalize","Convert ownership colors into data; resolve company domains for the 28 warm contacts."),
        ("3","Brief","Create 10 decision-ready account briefs with current signals and counter-evidence."),
        ("4","Approve","Review sender voice, channel basis, message, and CRM write-back for each."),
        ("5","Execute","Run outreach, discovery, and one relevant proof. Record commitments immediately."),
        ("6","Decide","Compare with baseline; keep, kill, or revise the wedge-message-workflow play."),
    ]
    for i,(n,t,d) in enumerate(actions):
        x=42+(i%3)*294; y=282-(i//3)*135
        c.setFillColor(PAPER); c.setStrokeColor(LINE); c.roundRect(x,y,270,108,11,fill=1,stroke=1)
        c.setFillColor((PINK,ORANGE,BLUE,GREEN,YELLOW,RED)[i]); c.circle(x+28,y+78,16,fill=1,stroke=0)
        c.setFillColor(colors.white); c.setFont("Helvetica-Bold",10); c.drawCentredString(x+28,y+74,n)
        para(c,t,x+55,y+90,190,28,size=11,bold=True); para(c,d,x+18,y+58,234,48,size=9.2,color=MUTED,leading=12)
    c.setFillColor(INK); c.setFont("Helvetica-Bold",16); c.drawString(42,105,"Decision at day 10")
    c.setFillColor(PINK); c.setFont("Helvetica-Bold",24); c.drawString(42,70,"Do we have evidence of qualified pull worth compounding?")
    c.showPage(); page += 1

    page_base(c, page, "SOURCES", "Primary artifacts and repository references")
    sources1=[
        "Outlook: Diego Waelter, Initial ICP Pass, received 2026-07-23; attachments All_Opulentia_Connections.xlsx and Opulentia_ICP_Connections_V1.xlsx.",
        "Outlook: Diego Waelter, ICP List, received 2026-07-30; attachment 26-0730_Opulentia_Connections_List.xlsx.",
        "Opulent GTM source deck: gtm-engineering-at-opulent-deck.pptx, 43 slides, SHA-256 b46be927998ea833f749f34d51b7d287192cb17bc0e5217d52d5308a7816304b.",
        "Vercel Labs marketing-team-eve-template: https://github.com/vercel-labs/marketing-team-eve-template commit 7ccaa5f406edf179cbef4d81bcb200fd3ee9da67.",
        "Browserbase skills: https://github.com/browserbase/skills/tree/main/skills commit 6afe8663693372e59e167dfa5be37932af09ae3d.",
        f"Field Theory CLI: v{field.get('fieldTheoryVersion','1.3.22')}; local 869-bookmark corpus; {query_count} query lenses; {field_count} unique GTM and sales candidate records in the union used for this report.",
        f"Opulent use-case index: {use_case_catalog['source_url']} captured {use_case_catalog['retrieved_at']}; {use_case_catalog['count']} source-linked cards with observed and editorial GTM label layers.",
    ]
    y=404
    for i,s in enumerate(sources1,1):
        c.setFillColor(PINK); c.circle(51,y-5,9,fill=1,stroke=0); c.setFillColor(colors.white); c.setFont("Helvetica-Bold",7); c.drawCentredString(51,y-8,str(i))
        used=para(c,s,70,y+5,830,44,size=8.8,color=INK,leading=11.5); y-=max(44,used+14)
    c.setFillColor(MUTED); c.setFont("Helvetica-Oblique",8); c.drawString(42,50,"Direct identifiers and personalized messages were not reproduced in this PDF.")
    c.showPage(); page += 1

    page_base(c, page, "SOURCES", "Field Theory references used as strategy hypotheses", "Social-post claims are directional evidence. Verify metrics and applicability before using them as client-facing proof.")
    ft_sources=[
        ("Compounding GTM context", "https://x.com/ParthGujare_/status/2080716441041465427"),
        ("Notion enterprise wedge", "https://x.com/Prerrrrna_/status/2076678433904755134"),
        ("Creative-idea outreach", "https://x.com/chrispisarski/status/2077880639055941693"),
        ("Pre-call enrichment", "https://x.com/fivosaresti/status/2072032494912704777"),
        ("Public intent sources", "https://x.com/scaling_shields/status/2018594563594846557"),
        ("LinkedIn activity signals", "https://x.com/draprints/status/2019410722137198655"),
        ("Company-research skill", "https://x.com/JaySahnan/status/2047730585313980499"),
        ("Forkable GTM system", "https://x.com/kathrynwu1/status/2041909258988745013"),
        ("Trust and product-led growth", "https://x.com/HarryStebbings/status/2032847555432730961"),
        ("Sales-call follow-through", "https://x.com/jasonlk/status/2060878172632105002"),
        ("Discovery structure", "https://x.com/Kazanjy/status/2043766982852464724"),
        ("Executive demo structure", "https://x.com/Kazanjy/status/2017326782161023141"),
        ("Follow-up sequence", "https://x.com/Kazanjy/status/2017660471084564610"),
        ("Partnership channels", "https://x.com/dan__rosenthal/status/2048839660902740455"),
        ("Pricing hypotheses", "https://x.com/lukepierceops/status/2059606571357720939"),
    ]
    for i,(label,url) in enumerate(ft_sources):
        col=i%2; row=i//2; x=42+col*440; y=401-row*43
        c.setFillColor((PINK,BLUE)[col]); c.circle(x+6,y+3,4,fill=1,stroke=0)
        c.setFillColor(INK); c.setFont("Helvetica-Bold",8.7); c.drawString(x+18,y+8,label)
        c.setFillColor(MUTED); c.setFont("Helvetica",7.2); c.drawString(x+18,y-6,url)
        c.linkURL(url,(x+16,y-10,x+420,y+14),relative=0)
    c.showPage(); page += 1

    c.linearGradient(0, 0, W, H, (colors.HexColor("#FFB071"), colors.HexColor("#F04C71"), colors.HexColor("#B61F56")), (0, 0.56, 1))
    c.setFillColor(colors.Color(1, 1, 1, alpha=0.12))
    c.circle(W - 40, H + 10, 260, fill=1, stroke=0)
    c.circle(120, -40, 210, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(58, H - 58, "OPULENTIA.AI")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(58, 385, "THE OPERATING PRINCIPLE")
    para(c,"Research deeply. Narrow the wedge. Prove one workflow. Gate external action. Write every correction back into the system.",58,354,760,148,size=28,color=colors.white,leading=36,bold=True)
    c.setFillColor(colors.white)
    c.roundRect(58, 118, 314, 34, 17, fill=1, stroke=0)
    c.setFillColor(RED)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(215, 131, "EVIDENCE -> DECISION -> ACTION -> LEARNING")
    c.setFillColor(colors.white)
    c.setFont("Helvetica", 9)
    c.drawString(58, 58, "Opulent GTM Master XStrategy | 2026-08-05")
    c.save()
    print(OUTPUT)


if __name__ == "__main__":
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    build()
