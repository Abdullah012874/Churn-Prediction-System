"""
Professional PDF Report Generator for Customer Churn Prediction System.
Uses ReportLab. High-contrast black/dark text throughout for readability.
Handles empty history, missing values, multi-page, and MongoDB ObjectIds.
"""

from io import BytesIO
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)


# ─── Colour palette ──────────────────────────────────────────────────────────
BLACK        = colors.HexColor("#111111")
DARK         = colors.HexColor("#222222")
HEADER_BG    = colors.HexColor("#111111")   # table header background
ROW_ALT      = colors.HexColor("#F7F7F7")   # alternating row (very light)
WHITE        = colors.white
LABEL_BG     = colors.HexColor("#DDDDDD")   # label cell background
LABEL_TEXT   = colors.HexColor("#111111")   # label cell text
VALUE_TEXT   = colors.HexColor("#111111")   # value cell text
GRID_COLOR   = colors.HexColor("#CCCCCC")


# ─── Page header / footer ────────────────────────────────────────────────────
def _on_page(canvas, doc):
    canvas.saveState()
    w, h = letter

    # Header bar — solid black
    canvas.setFillColor(BLACK)
    canvas.rect(0, h - 44, w, 44, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawString(0.4 * inch, h - 27, "AI Customer Churn Predictor")
    canvas.setFont("Helvetica", 9)
    canvas.drawRightString(w - 0.4 * inch, h - 27,
                           f"Generated: {datetime.now().strftime('%Y-%m-%d  %H:%M')}")

    # Footer
    canvas.setFillColor(BLACK)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(0.4 * inch, 0.3 * inch,
                      "CUSTOMER CHURN PREDICTION REPORT — CONFIDENTIAL")
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(w - 0.4 * inch, 0.3 * inch, f"Page {doc.page}")

    canvas.restoreState()


# ─── Safe string ─────────────────────────────────────────────────────────────
def _safe(value, default="N/A"):
    if value is None:
        return default
    s = str(value).strip()
    return s if s else default


# ─── Main generator ──────────────────────────────────────────────────────────
def generate_pdf_report(predictions):
    """Return PDF as bytes. predictions = list of MongoDB dicts."""
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.5 * inch,
        leftMargin=0.5 * inch,
        topMargin=0.85 * inch,
        bottomMargin=0.6 * inch,
        title="Customer Churn Prediction Report",
        author="AI Customer Churn Predictor"
    )

    # ── Styles ───────────────────────────────────────────────────────────────
    base = getSampleStyleSheet()

    s_title = ParagraphStyle(
        "ReportTitle", parent=base["Title"],
        fontSize=20, textColor=BLACK,
        alignment=TA_CENTER, spaceAfter=4,
        fontName="Helvetica-Bold"
    )
    s_subtitle = ParagraphStyle(
        "Subtitle", parent=base["Normal"],
        fontSize=9, textColor=DARK,
        alignment=TA_CENTER, spaceAfter=16
    )
    s_section = ParagraphStyle(
        "Section", parent=base["Normal"],
        fontSize=12, textColor=WHITE,
        fontName="Helvetica-Bold",
        spaceBefore=14, spaceAfter=6
    )
    s_pred_num = ParagraphStyle(
        "PredNum", parent=base["Normal"],
        fontSize=10, textColor=WHITE,
        fontName="Helvetica-Bold",
        spaceBefore=10, spaceAfter=4
    )
    s_sugg = ParagraphStyle(
        "Sugg", parent=base["Normal"],
        fontSize=8, textColor=DARK,
        leftIndent=8, spaceAfter=2
    )
    s_empty = ParagraphStyle(
        "Empty", parent=base["Normal"],
        fontSize=10, textColor=DARK,
        alignment=TA_CENTER, spaceBefore=30
    )

    # helper: dark section heading with white text rendered as a 1-row table
    def section_heading(text):
        t = Table([[text]], colWidths=[7.5 * inch])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), HEADER_BG),
            ("TEXTCOLOR",  (0, 0), (-1, -1), WHITE),
            ("FONTNAME",   (0, 0), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE",   (0, 0), (-1, -1), 11),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("LEFTPADDING",   (0, 0), (-1, -1), 10),
        ]))
        return t

    elements = []

    # ── Title block ──────────────────────────────────────────────────────────
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph("CUSTOMER CHURN PREDICTION REPORT", s_title))
    elements.append(Paragraph(
        f"Project: AI Customer Churn Predictor   |   "
        f"Date: {datetime.now().strftime('%B %d, %Y   %I:%M %p')}",
        s_subtitle
    ))
    elements.append(HRFlowable(width="100%", thickness=1.5,
                               color=BLACK, spaceAfter=12))

    # ── Summary ──────────────────────────────────────────────────────────────
    total      = len(predictions)
    high_risk  = sum(1 for p in predictions if _safe(p.get("risk_level")) == "High")
    safe_cust  = sum(1 for p in predictions if _safe(p.get("risk_level")) == "Low")
    churn_cnt  = sum(1 for p in predictions if "Churn" in _safe(p.get("prediction"), ""))
    churn_rate = f"{round(churn_cnt / total * 100, 1)}%" if total > 0 else "N/A"

    model_counts = {}
    for p in predictions:
        m = _safe(p.get("selected_model") or p.get("used_model"), "Unknown")
        model_counts[m] = model_counts.get(m, 0) + 1
    most_used = max(model_counts, key=model_counts.get) if model_counts else "N/A"

    elements.append(section_heading("Executive Summary"))
    elements.append(Spacer(1, 6))

    summary_data = [
        ["Total Predictions", str(total),       "Churn Rate",           churn_rate],
        ["High Risk Customers", str(high_risk), "Safe Customers",        str(safe_cust)],
        ["Most Used Classifier", most_used,     "Records in Report",     str(total)],
    ]
    col_w = [1.7 * inch, 1.2 * inch, 1.8 * inch, 1.2 * inch]
    summary_table = Table(summary_data, colWidths=col_w)
    summary_table.setStyle(TableStyle([
        # label columns
        ("BACKGROUND",  (0, 0), (0, -1), LABEL_BG),
        ("BACKGROUND",  (2, 0), (2, -1), LABEL_BG),
        ("FONTNAME",    (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME",    (2, 0), (2, -1), "Helvetica-Bold"),
        ("TEXTCOLOR",   (0, 0), (-1, -1), LABEL_TEXT),
        # value columns
        ("FONTNAME",    (1, 0), (1, -1), "Helvetica"),
        ("FONTNAME",    (3, 0), (3, -1), "Helvetica"),
        ("FONTSIZE",    (0, 0), (-1, -1), 9),
        ("PADDING",     (0, 0), (-1, -1), 8),
        ("GRID",        (0, 0), (-1, -1), 0.7, GRID_COLOR),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [WHITE, ROW_ALT]),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 16))

    # ── Per-prediction details ────────────────────────────────────────────────
    elements.append(section_heading("Prediction Details"))
    elements.append(Spacer(1, 8))

    if not predictions:
        elements.append(Paragraph(
            "No predictions recorded yet. Run a prediction to populate this report.",
            s_empty
        ))
    else:
        for idx, p in enumerate(predictions, start=1):
            if not isinstance(p, dict):
                continue

            cust   = p.get("customer_data", {}) or {}
            model  = _safe(p.get("selected_model") or p.get("used_model"), "Unknown")
            pred   = _safe(p.get("prediction"))
            prob   = p.get("probability")
            risk   = _safe(p.get("risk_level"))
            ts     = _safe(p.get("timestamp"))
            suggs  = p.get("suggestions", []) or []
            prob_str = f"{round(float(prob) * 100, 1)}%" if prob is not None else "N/A"

            block = []

            # Prediction header bar
            hdr = Table(
                [[f"  Prediction #{idx}   —   {ts}"]],
                colWidths=[7.5 * inch]
            )
            hdr.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, -1), DARK),
                ("TEXTCOLOR",     (0, 0), (-1, -1), WHITE),
                ("FONTNAME",      (0, 0), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE",      (0, 0), (-1, -1), 9),
                ("TOPPADDING",    (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            block.append(hdr)
            block.append(Spacer(1, 3))

            # Result summary (model, prediction, probability, risk)
            res_data = [
                ["Selected Model", model,    "Prediction",  pred],
                ["Probability",   prob_str,  "Risk Level",  risk],
            ]
            res_table = Table(res_data,
                              colWidths=[1.4*inch, 1.6*inch, 1.2*inch, 1.6*inch])
            res_table.setStyle(TableStyle([
                ("BACKGROUND",  (0, 0), (0, -1), LABEL_BG),
                ("BACKGROUND",  (2, 0), (2, -1), LABEL_BG),
                ("FONTNAME",    (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME",    (2, 0), (2, -1), "Helvetica-Bold"),
                ("TEXTCOLOR",   (0, 0), (-1, -1), LABEL_TEXT),
                ("FONTNAME",    (1, 0), (1, -1), "Helvetica"),
                ("FONTNAME",    (3, 0), (3, -1), "Helvetica"),
                ("FONTSIZE",    (0, 0), (-1, -1), 8),
                ("PADDING",     (0, 0), (-1, -1), 6),
                ("GRID",        (0, 0), (-1, -1), 0.6, GRID_COLOR),
                ("ROWBACKGROUNDS", (0, 0), (-1, -1), [WHITE, ROW_ALT]),
            ]))
            block.append(res_table)
            block.append(Spacer(1, 3))

            # Customer details
            cust_data = [
                ["Age",          _safe(cust.get("age")),
                 "Gender",       _safe(cust.get("gender")),
                 "Tenure (mo.)", _safe(cust.get("tenure"))],
                ["Usage Freq.",  _safe(cust.get("usage_frequency")),
                 "Support Calls",_safe(cust.get("support_calls")),
                 "Payment Delay",_safe(cust.get("payment_delay"))],
                ["Subscription", _safe(cust.get("subscription_type")),
                 "Contract",     _safe(cust.get("contract_length")),
                 "Total Spend",  f"${_safe(cust.get('total_spend'))}"],
                ["Last Interaction", _safe(cust.get("last_interaction")),
                 "", "", "", ""],
            ]
            cust_table = Table(
                cust_data,
                colWidths=[1.1*inch, 0.9*inch, 1.1*inch, 0.9*inch, 1.1*inch, 1.2*inch]
            )
            cust_table.setStyle(TableStyle([
                ("BACKGROUND",  (0, 0), (0, -1), LABEL_BG),
                ("BACKGROUND",  (2, 0), (2, -1), LABEL_BG),
                ("BACKGROUND",  (4, 0), (4, -1), LABEL_BG),
                ("FONTNAME",    (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME",    (2, 0), (2, -1), "Helvetica-Bold"),
                ("FONTNAME",    (4, 0), (4, -1), "Helvetica-Bold"),
                ("TEXTCOLOR",   (0, 0), (-1, -1), LABEL_TEXT),
                ("FONTNAME",    (1, 0), (1, -1), "Helvetica"),
                ("FONTNAME",    (3, 0), (3, -1), "Helvetica"),
                ("FONTNAME",    (5, 0), (5, -1), "Helvetica"),
                ("FONTSIZE",    (0, 0), (-1, -1), 8),
                ("PADDING",     (0, 0), (-1, -1), 5),
                ("GRID",        (0, 0), (-1, -1), 0.6, GRID_COLOR),
                ("ROWBACKGROUNDS", (0, 0), (-1, -1), [WHITE, ROW_ALT]),
            ]))
            block.append(cust_table)

            # Retention suggestions
            if suggs:
                block.append(Spacer(1, 4))
                sugg_rows = [["Retention Suggestions"]]
                for s in suggs:
                    sugg_rows.append([f"  •  {_safe(s)}"])
                sugg_table = Table(sugg_rows, colWidths=[7.5 * inch])
                sugg_table.setStyle(TableStyle([
                    ("BACKGROUND",    (0, 0), (-1, 0), LABEL_BG),
                    ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("TEXTCOLOR",     (0, 0), (-1, -1), LABEL_TEXT),
                    ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE",      (0, 0), (-1, -1), 8),
                    ("TOPPADDING",    (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("LEFTPADDING",   (0, 0), (-1, -1), 8),
                    ("GRID",          (0, 0), (-1, -1), 0.6, GRID_COLOR),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, ROW_ALT]),
                ]))
                block.append(sugg_table)

            block.append(Spacer(1, 10))
            block.append(HRFlowable(width="100%", thickness=0.5,
                                    color=GRID_COLOR, spaceAfter=6))

            try:
                elements.append(KeepTogether(block))
            except Exception:
                elements.extend(block)

    # ── Build ─────────────────────────────────────────────────────────────────
    doc.build(elements, onFirstPage=_on_page, onLaterPages=_on_page)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
