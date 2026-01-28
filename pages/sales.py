import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import calendar
from datetime import date
from io import BytesIO
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="CELLPOINT | Owner Intelligence",
    layout="wide"
)

st.title("📊 CELLPOINT SMARTPHONE GALLERY")
st.subheader("Owner Daily–Monthly Performance Intelligence")

# ======================================================
# DATE INPUT
# ======================================================
report_date = st.date_input("📅 Report As On Date", value=date.today())

branch_name = st.selectbox("🏬 Select Branch", ["CellPoint 1", "CellPoint 2"])

year = report_date.year
month = report_date.month
days_completed = report_date.day
total_days = calendar.monthrange(year, month)[1]
days_remaining = total_days - days_completed

st.caption(
    f"📆 Month Days: {total_days} | "
    f"Days Completed: {days_completed} | "
    f"Days Remaining: {days_remaining}"
)

st.markdown("---")

# ======================================================
# FILE UPLOAD
# ======================================================
uploaded_file = st.file_uploader(
    "📂 Upload Monthly Excel Report",
    type=["xlsx"]
)

# ======================================================
# HELPER: PREDICTION GRAPH IMAGE (PDF)
# ======================================================
def prediction_graph_image(company_ach, predicted_final, company_trgt):
    buf = BytesIO()
    fig, ax = plt.subplots(figsize=(7, 3))

    ax.plot([0, days_completed], [0, company_ach], label="Actual", linewidth=2)
    ax.plot(
        [days_completed, total_days],
        [company_ach, predicted_final],
        linestyle="--",
        label="Predicted",
        linewidth=2
    )
    ax.axhline(company_trgt, linestyle=":", label="Monthly Target")

    ax.set_xlabel("Day")
    ax.set_ylabel("Cumulative Sales")
    ax.set_title("Actual vs Predicted Business Performance")
    ax.legend()

    plt.tight_layout()
    fig.savefig(buf, format="png", dpi=200)
    plt.close(fig)
    buf.seek(0)
    return buf

# ======================================================
# PDF GENERATOR – COMPLETE REPORT
# ======================================================
# ======================================================
# PDF GENERATOR – COMPLETE REPORT
# ======================================================
def generate_complete_pdf(
    df, company_status, company_pct, top_risk,
    predicted_text, company_ach, predicted_final, company_trgt,
    action_df
):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=20
    )

    styles = getSampleStyleSheet()
    elements = []

    # ---------------- HEADER ----------------
    elements.append(Paragraph(
        "<b>CELLPOINT SMARTPHONE GALLERY</b><br/>"
        f"<b>Branch:</b> {branch_name}<br/>"
        "Morning Sales Review – Full Intelligence Report<br/>"
        f"<b>Report Date:</b> {report_date}<br/><br/>",
        styles["Title"]
    ))

    # ---------------- SUMMARY ----------------
    elements.append(Paragraph(
        f"<b>Total Target:</b> ₹{int(company_trgt):,}<br/>"
        f"<b>Achieved Till Date:</b> ₹{int(company_ach):,}<br/>"
        f"<b>Pending:</b> ₹{int(company_trgt - company_ach):,}<br/>"
        f"<b>Company Status:</b> {company_status} ({company_pct:.1f}%)<br/>"
        f"<b>Days Completed:</b> {days_completed} | "
        f"<b>Days Remaining:</b> {days_remaining}<br/><br/>",
        styles["Normal"]
    ))

    # ---------------- KEY DISCUSSION ----------------
    elements.append(Paragraph("<b>Key Discussion Points</b>", styles["Heading2"]))

    elements.append(Paragraph(
        f"<b>Actual vs Predicted Performance</b><br/>"
        f"Actual Achieved: ₹{int(company_ach):,}<br/>"
        f"Predicted Month-End: ₹{int(predicted_final):,}<br/>"
        f"Monthly Target: ₹{int(company_trgt):,}<br/><br/>"
        f"<b>Biggest Risk Brand</b><br/>"
        f"{top_risk['BRAND NAME']} — BTD ₹{int(top_risk['BALANCE TO DO']):,}<br/><br/>",
        styles["Normal"]
    ))

    # ======================================================
    # HELPER FOR COLOR TEXT
    # ======================================================
    def color_text(text):
        if "🟢" in text:
            return f'<font color="green">{text}</font>'
        if "🟡" in text:
            return f'<font color="orange">{text}</font>'
        if "🟠" in text:
            return f'<font color="darkorange">{text}</font>'
        if "🔴" in text:
            return f'<font color="red">{text}</font>'
        return text

    # ---------------- CURRENT ANALYSIS TABLE ----------------
    elements.append(Paragraph(
        "<b>Current Brand-wise Performance Analysis</b>",
        styles["Heading2"]
    ))

    performance_table = [[
        "Brand", "Target", "Achieved", "BTD", "Achievement %", "Risk Level"
    ]]

    for _, r in df.iterrows():
        performance_table.append([
            r["BRAND NAME"],
            f"{int(r['MONTHLY TARGET']):,}",
            f"{int(r['ACHIEVEMENT']):,}",
            f"{int(r['BALANCE TO DO']):,}",
            f"{r['ACHIEVEMENT %']:.1f}%",
            Paragraph(color_text(r["RISK LEVEL"]), styles["Normal"])
        ])

    pt = Table(performance_table, repeatRows=1)
    pt.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.4, colors.black),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("FONTSIZE", (0,0), (-1,-1), 8),
        ("ALIGN", (1,1), (-1,-1), "CENTER"),
    ]))

    elements.append(pt)
    elements.append(Spacer(1, 12))

    # ---------------- PREDICTION GRAPH ----------------
    elements.append(Paragraph("<b>Business Outcome Prediction</b>", styles["Heading2"]))
    elements.append(
        Image(
            prediction_graph_image(company_ach, predicted_final, company_trgt),
            width=480,
            height=220
        )
    )
    elements.append(Spacer(1, 12))

    # ---------------- ACTION PLAN TABLE ----------------
    elements.append(Paragraph(
        "<b>What To Do Next – Action Plan</b>",
        styles["Heading2"]
    ))

    action_table = [[
        "Brand", "BTD", "Required / Day", "Normal Daily", "Difficulty"
    ]]

    for _, r in action_df.iterrows():
        action_table.append([
            r["Brand"],
            f"{r['BALANCE TO DO']:,}",
            f"{r['Required / Day']:,}",
            f"{r['Normal Daily']:,}",
            Paragraph(color_text(r["Difficulty"]), styles["Normal"])
        ])

    at = Table(action_table, repeatRows=1)
    at.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.4, colors.black),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("FONTSIZE", (0,0), (-1,-1), 8),
        ("ALIGN", (1,1), (-1,-1), "CENTER"),
    ]))

    elements.append(at)
    elements.append(Spacer(1, 14))

    # ---------------- FINAL INSIGHTS ----------------
    elements.append(Paragraph(
        "<b>Morning Sales Meeting – Key Takeaways</b>",
        styles["Heading2"]
    ))

    elements.append(Paragraph(
        '<font color="green">🟢 Excellent:</font> Maintain pace.<br/>'
        '<font color="orange">🟡 Good:</font> Minor push required.<br/>'
        '<font color="darkorange">🟠 Average:</font> Focused selling needed.<br/>'
        '<font color="red">🔴 Very High:</font> Immediate corrective action required.',
        styles["Normal"]
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer




# ======================================================
# MAIN LOGIC
# ======================================================
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip().str.upper()
    df = df[~df["BRAND NAME"].astype(str).str.contains("TOTAL", case=False)]

    for col in ["MONTHLY TARGET", "ACHIEVEMENT", "BALANCE TO DO", "DAILY TARGET"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # ================= ACHIEVEMENT % =================
    df["ACHIEVEMENT %"] = (df["ACHIEVEMENT"] / df["MONTHLY TARGET"]) * 100

    # ================= RISK BASED ON ACHIEVEMENT % =================
    def risk_level_by_pct(p):
        if p > 100:
            return "🟢 Extra Ordinary"
        elif p >= 91:
            return "🟢 Excellent"
        elif p >= 61:
            return "🟡 Good"
        elif p >= 31:
            return "🟠 Average"
        else:
            return "🔴 Very High"

    df["RISK LEVEL"] = df["ACHIEVEMENT %"].apply(risk_level_by_pct)

    # ================= SORT: EXCELLENT → CRITICAL =================
    df = df.sort_values(by="ACHIEVEMENT %", ascending=False)

    # ================= COMPANY METRICS =================
    company_ach = df["ACHIEVEMENT"].sum()
    company_trgt = df["MONTHLY TARGET"].sum()
    company_pct = (company_ach / company_trgt) * 100

    def company_status(p):
        if p >= 91:
            return "🟢 EXCELLENT"
        elif p >= 61:
            return "🟡 AVERAGE"
        elif p >= 31:
            return "🟠 GOOD"
        else:
            return "🔴 VERY HIGH"

    status_text = company_status(company_pct)

    st.markdown(f"## 🏢 COMPANY STATUS: **{status_text}** ({company_pct:.1f}%)")

    # ================= TOP RISK = LAST ROW =================
    top_risk = df.iloc[-1]

    st.error(
        f"🚨 TODAY’S BIGGEST RISK: {top_risk['BRAND NAME']} "
        f"| Achievement {top_risk['ACHIEVEMENT %']:.1f}%"
    )

    # ================= BRAND TABLE =================
    st.subheader("📋 Brand Performance (Excellent → Critical)")
    st.dataframe(df, use_container_width=True)

    # ================= ACTION PLAN =================
    st.markdown("## 📌 What To Do Next (Action for Tomorrow)")
    action_rows = []

    for _, r in df.iterrows():
        if days_remaining == 0:
            req_day = 0
            diff = "⏹ Month Closed"
        else:
            req_day = r["BALANCE TO DO"] / days_remaining
            ratio = req_day / r["DAILY TARGET"] if r["DAILY TARGET"] > 0 else 0

            if ratio <= 1:
                diff = "🟢 Easy"
            elif ratio <= 1.2:
                diff = "🟡 Stretch"
            elif ratio <= 1.5:
                diff = "🟠 Hard"
            else:
                diff = "🔴 Almost Impossible"

        action_rows.append({
            "Brand": r["BRAND NAME"],
            "BALANCE TO DO": int(r["BALANCE TO DO"]),
            "Required / Day": int(req_day),
            "Normal Daily": int(r["DAILY TARGET"]),
            "Difficulty": diff
        })

    action_df = pd.DataFrame(action_rows)
    st.dataframe(action_df, use_container_width=True)

    # ================= PREDICTION =================
    avg_daily = company_ach / days_completed if days_completed > 0 else 0
    predicted_final = company_ach + avg_daily * days_remaining
    predicted_pct = (predicted_final / company_trgt) * 100
    predicted_text = f"{company_status(predicted_pct)} ({predicted_pct:.1f}%)"

      # ================= PREDICTION =================
    avg_daily = company_ach / days_completed if days_completed > 0 else 0
    predicted_final = company_ach + avg_daily * days_remaining
    predicted_pct = (predicted_final / company_trgt) * 100
    predicted_text = f"{company_status(predicted_pct)} ({predicted_pct:.1f}%)"

    # ================= PDF DOWNLOAD =================
    st.markdown("## 📄 Download Full A4 Report")
    st.download_button(
        "⬇️ Download Complete Morning Sales Report",
        generate_complete_pdf(
            df,
            status_text,
            company_pct,
            top_risk,
            predicted_text,
            company_ach,
            predicted_final,
            company_trgt,
            action_df
        ),
        "CELLPOINT_Full_Morning_Sales_Report.pdf",
        "application/pdf"
    )

    # ======================================================
    # 🧠 COPER AI INTELLIGENCE – SEPARATE STRATEGIC LAYER
    # ======================================================
    st.markdown("---")
    st.markdown("## 🧠 COPER AI – Strategic Intelligence")
    st.caption("Forward-looking AI insights • Not part of printable report")

    # ================= AI METRICS =================
    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("🎯 Total Target", f"₹{int(company_trgt):,}")
    c2.metric("✅ Achieved", f"₹{int(company_ach):,}", f"{company_pct:.1f}%")
    c3.metric("📉 Pending", f"₹{int(company_trgt - company_ach):,}")
    c4.metric("📈 AI Predicted Final", f"₹{int(predicted_final):,}")
    c5.metric("🏢 AI Verdict", predicted_text)

    # ================= AI EXECUTIVE SUMMARY =================
    st.markdown("### 🧠 AI Executive Summary")

    st.markdown(f"""
    - **Run Rate:** ₹{int(avg_daily):,} per day  
    - **Days Remaining:** {days_remaining}  
    - **Prediction Model:** Linear velocity projection  
    - **Weakest Brand:** **{top_risk['BRAND NAME']}**  
    - **Risk Focus:** Brands below 75% achievement  
    """)

    # ================= AI TRAJECTORY GRAPH =================
    st.markdown("### 📊 AI Business Trajectory")

    fig_ai, ax_ai = plt.subplots(figsize=(9, 4))

    ax_ai.plot([0, days_completed], [0, company_ach], marker="o", linewidth=2, label="Actual")
    ax_ai.plot([days_completed, total_days], [company_ach, predicted_final],
               linestyle="--", marker="o", linewidth=2, label="AI Projection")
    ax_ai.axhline(company_trgt, linestyle=":", linewidth=2, label="Monthly Target")

    ax_ai.set_xlabel("Day of Month")
    ax_ai.set_ylabel("Cumulative Sales (₹)")
    ax_ai.set_title("COPER AI – Outcome Projection")
    ax_ai.legend()
    ax_ai.grid(True)

    st.pyplot(fig_ai)
    plt.close(fig_ai)

    # ================= BRAND CONTRIBUTION =================
    st.markdown("### 🧩 Brand Contribution Intelligence")

    pie_df = df[df["ACHIEVEMENT"] > 0]

    fig_pie, ax_pie = plt.subplots(figsize=(6, 6))
    ax_pie.pie(pie_df["ACHIEVEMENT"], labels=pie_df["BRAND NAME"],
               autopct="%1.1f%%", startangle=140)

    ax_pie.set_title("Revenue Contribution by Brand")

    st.pyplot(fig_pie)
    plt.close(fig_pie)

    # ================= FINAL AI DECISION =================
    st.markdown("### 🏁 COPER AI – Final Decision")

    if predicted_pct >= 100:
        st.success("🟢 Target exceeded. Scale premium & upsell aggressively.")
    elif predicted_pct >= 85:
        st.warning("🟡 Target achievable with disciplined daily execution.")
    elif predicted_pct >= 75:
        st.error("🟠 Target at risk. Immediate brand-level correction needed.")
    else:
        st.error("🔴 Critical condition. Structural intervention required.")

else:
    st.info("⬆️ Upload Excel file to begin analysis")
