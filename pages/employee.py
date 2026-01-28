# ======================================================
# PROJECT: CELLpick Intelligence System
# MODULE: Staff Performance Dashboard
# VERSION: EMPINTELLIGENCE – MARK 1.2.3 (DASH + PDF FIXED)
# ======================================================

import streamlit as st
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from io import BytesIO
from datetime import date

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(
    page_title="CELLPOINT | EMP Intelligence – Mark 1",
    layout="wide"
)

st.title("👥 CELLPOINT EMPLOYEE INTELLIGENCE – MARK 1")
st.caption("Separate Handset & Accessories Performance Intelligence")
st.markdown("---")

# ==============================
# META INPUTS
# ==============================
c1, c2 = st.columns(2)

with c1:
    report_date = st.date_input("📅 Report As On Date", value=date.today())

with c2:
    branch_name = st.selectbox(
        "🏬 Select Branch",
        ["CellPoint 1", "CellPoint 2"]
    )

st.markdown("---")

# ==============================
# FILE UPLOAD
# ==============================
uploaded_file = st.file_uploader(
    "📂 Upload Staff Performance Excel",
    type=["xlsx"]
)

# ==============================
# STATUS LOGIC
# ==============================
def status_logic(p):
    if p >= 91:
        return "🟢 Top performer, role model"
    elif p >= 61:
        return "🟡 Performing well, push to excellent"
    elif p >= 31:
        return "🟠 Need strong improvement"
    else:
        return "🔴 Immediate correction required"

# ==============================
# MAIN LOGIC
# ==============================
if uploaded_file:

    # ------------------------------
    # READ GROUPED HEADER EXCEL
    # ------------------------------
    df = pd.read_excel(uploaded_file, header=[0, 1])

    # ------------------------------
    # FLATTEN HEADERS
    # ------------------------------
    df.columns = [
        f"{a}_{b}".strip().upper()
        if "UNNAMED" not in str(a).upper()
        else b.strip().upper()
        for a, b in df.columns
    ]

    # ------------------------------
    # FORCE FIRST COLUMN AS SALESMAN
    # ------------------------------
    df = df.rename(columns={df.columns[0]: "SALESMAN"})

    # ------------------------------
    # STANDARDIZE COLUMN NAMES
    # ------------------------------
    df = df.rename(columns={
        "HANDSET_TARGET": "HS_TARGET",
        "HANDSET_ACHIEVEMENT": "HS_ACH",
        "HANDSET_BALANCE": "HS_BAL",
        "ACCESSORIES_TARGET": "ACC_TARGET",
        "ACCESSORIES_ACHIEVEMENT": "ACC_ACH",
        "ACCESSORIES_BALANCE": "ACC_BAL"
    })

    # ------------------------------
    # REMOVE TOTAL ROW
    # ------------------------------
    df = df[df["SALESMAN"].astype(str).str.upper() != "TOTAL"]

    # ------------------------------
    # ANALYSIS
    # ------------------------------
    df["HS_%"] = (df["HS_ACH"] / df["HS_TARGET"]) * 100
    df["ACC_%"] = (df["ACC_ACH"] / df["ACC_TARGET"]) * 100

    df["HS_STATUS"] = df["HS_%"].apply(status_logic)
    df["ACC_STATUS"] = df["ACC_%"].apply(status_logic)

    df["TOTAL_TARGET"] = df["HS_TARGET"] + df["ACC_TARGET"]
    df["TOTAL_ACH"] = df["HS_ACH"] + df["ACC_ACH"]
    df["TOTAL_BAL"] = df["HS_BAL"] + df["ACC_BAL"]
    df["OVERALL_%"] = (df["TOTAL_ACH"] / df["TOTAL_TARGET"]) * 100
    df["FINAL_STATUS"] = df["OVERALL_%"].apply(status_logic)

    # ------------------------------
    # HIERARCHY
    # ------------------------------
    df_handset = df.sort_values("HS_%", ascending=False)
    df_accessory = df.sort_values("ACC_%", ascending=False)
    df_combined = df.sort_values("OVERALL_%", ascending=False)

    # ==============================
    # 🏆 EXECUTIVE DASHBOARD (TOP)
    # ==============================
    top_overall = df_combined.iloc[0]
    top_handset = df_handset.iloc[0]
    top_accessory = df_accessory.iloc[0]

    # ==============================
    # ADMIN OVERRIDE LOGIC (DISPLAY ONLY)
    # ==============================
   
    effective_top = top_overall
    effective_top_handset = top_handset
    effective_top_accessory = top_accessory
    admin_msgs = []

    if str(top_overall["SALESMAN"]).strip().upper() == "ADMIN":
      admin_msgs.append("📌 As per the report, Admin is the Overall Top Performer.")
    
    # Get next best performer safely
    if len(df_combined) > 1:
         effective_top = df_combined.iloc[1]

    if str(top_handset["SALESMAN"]).strip().upper() == "ADMIN":
     admin_msgs.append("📌 As per the report, Admin is the Overall Top Performer.")
    if len(df_handset) > 1:
        effective_top_handset = df_handset.iloc[1]

    if str(top_accessory["SALESMAN"]).strip().upper() == "ADMIN":
      admin_msgs.append("📌 As per the report, Admin is the Overall Top Performer.")
    if len(df_accessory) > 1:
        effective_top_accessory = df_accessory.iloc[1]

    team_avg_pct = df["OVERALL_%"].mean()
    team_status = status_logic(team_avg_pct)

    st.subheader("🏆 Executive Performance Summary")

    for msg in admin_msgs:
        st.info(f"{msg} Showing next best performer for operational view.")



    k1, k2, k3, k4, k5 = st.columns(5)

    k1.metric(
    "🥇 Top Performer",
    effective_top["SALESMAN"],
    f"{effective_top['OVERALL_%']:.1f}%"
)

    k2.metric("📱 Best Handset", effective_top_handset["SALESMAN"], f"{effective_top_handset['HS_%']:.1f}%")
    k3.metric("🎧 Best Accessories", effective_top_accessory["SALESMAN"], f"{effective_top_accessory['ACC_%']:.1f}%")
    k4.metric("📊 Team Avg %", f"{team_avg_pct:.1f}%")
    k5.metric("🚦 Team Status", team_status)

    st.markdown("---")

    # ==============================
    # DASHBOARD TABLES
    # ==============================
    st.subheader("📱 Handset Performance Analysis")
    st.dataframe(
        df_handset[["SALESMAN", "HS_TARGET", "HS_ACH", "HS_BAL", "HS_%", "HS_STATUS"]],
        use_container_width=True
    )

    st.subheader("🎧 Accessories Performance Analysis")
    st.dataframe(
        df_accessory[["SALESMAN", "ACC_TARGET", "ACC_ACH", "ACC_BAL", "ACC_%", "ACC_STATUS"]],
        use_container_width=True
    )

    st.subheader("🧠 Combined Sales Intelligence")
    st.dataframe(
        df_combined[["SALESMAN", "TOTAL_BAL", "OVERALL_%", "FINAL_STATUS"]],
        use_container_width=True
    )

    # ======================================================
    # PDF REPORT
    # ======================================================
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=32,
        leftMargin=32,
        topMargin=28,
        bottomMargin=28
    )

    styles = getSampleStyleSheet()
    styles["Normal"].fontSize = 8
    styles["Normal"].leading = 11
    styles["Heading2"].fontSize = 9
    styles["Heading2"].leading = 12

    elements = []

    # ------------------------------
    # HEADER
    # ------------------------------
    elements.append(Paragraph(
        f"""
        <para align="center">
        <b>CELLPOINT – EMPLOYEE INTELLIGENCE REPORT</b><br/>
        <font size="8">
        Branch: {branch_name} &nbsp;&nbsp;|&nbsp;&nbsp;
        Report Date: {report_date}
        </font>
        </para>
        """,
        styles["Normal"]
    ))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(
    f"""
    <b>🏆 Executive Performance Summary</b><br/>
    • <b>Top Performer:</b> {effective_top['SALESMAN']}
    ({effective_top['OVERALL_%']:.1f}%)<br/>
    • <b>Top Handset:</b> {effective_top_handset['SALESMAN']} 
    ({effective_top_handset['HS_%']:.1f}%)<br/>
    • <b>Top Accessories:</b> {effective_top_accessory['SALESMAN']} 
    ({top_accessory['ACC_%']:.1f}%)<br/>
    • <b>Team Average:</b> {team_avg_pct:.1f}%<br/>
    • <b>Overall Team Status:</b> {team_status}
    """,
    styles["Normal"]
    ))
    elements.append(Spacer(1, 14))

    # ------------------------------
    # STATUS COLOR FUNCTION
    # ------------------------------
    def colored_status(text):
        if text.startswith("🟢"):
            color = "green"
        elif text.startswith("🟡"):
            color = "orange"
        elif text.startswith("🟠"):
            color = "#d35400"
        else:
            color = "red"
        return Paragraph(f"<font color='{color}'>{text}</font>", styles["Normal"])

    # ------------------------------
    # TABLE BUILDER (COMFORT SIZE)
    # ------------------------------
    def add_table(title, cols, dfv):
        elements.append(Paragraph(f"<b>{title}</b>", styles["Heading2"]))
        elements.append(Spacer(1, 6))

        data = [cols]

        for _, r in dfv.iterrows():
            row = []
            for c in cols:
                v = r[c]
                if c in ["HS_STATUS", "ACC_STATUS", "FINAL_STATUS"]:
                    row.append(colored_status(v))
                elif "%" in c:
                    row.append(f"{v:.1f}%")
                elif isinstance(v, (int, float)):
                    row.append(f"{v:,.0f}")
                else:
                    row.append(v)
            data.append(row)

        table = Table(
            data,
            repeatRows=1,
            colWidths=[110] + [65] * (len(cols) - 1)
        )

        table.setStyle(TableStyle([
            ("GRID", (0,0), (-1,-1), 0.5, colors.black),
            ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
            ("ALIGN", (1,1), (-1,-1), "CENTER"),
            ("ALIGN", (0,0), (0,-1), "LEFT"),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("FONTSIZE", (0,0), (-1,-1), 8),
            ("TOPPADDING", (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 12))

    # ------------------------------
    # TABLES
    # ------------------------------
    add_table(
        "📱 Handset Performance",
        ["SALESMAN", "HS_TARGET", "HS_ACH", "HS_BAL", "HS_%", "HS_STATUS"],
        df_handset
    )

    add_table(
        "🎧 Accessories Performance",
        ["SALESMAN", "ACC_TARGET", "ACC_ACH", "ACC_BAL", "ACC_%", "ACC_STATUS"],
        df_accessory
    )

    add_table(
        "🧠 Combined Sales Intelligence",
        ["SALESMAN", "TOTAL_BAL", "OVERALL_%", "FINAL_STATUS"],
        df_combined
    )

    # ------------------------------
    # INSIGHTS
    # ------------------------------
    elements.append(Spacer(1, 8))
    elements.append(Paragraph("<b>📌 Key Insights & Observations</b>", styles["Heading2"]))
    elements.append(Spacer(1, 4))

    elements.append(Paragraph(
        f"""
        • <b>Top Handset Contributor:</b> {effective_top_handset['SALESMAN']} 
        ({effective_top_handset['HS_%']:.1f}%)<br/>

        • <b>Accessories Risk Area:</b> {df_accessory.iloc[-1]['SALESMAN']} 
        ({df_accessory.iloc[-1]['ACC_%']:.1f}%)<br/>

        • <b>Overall Team Status:</b> {status_logic(df['OVERALL_%'].mean())}<br/>

        • <b>Recommendation:</b> Improve accessory attachment rate and
        daily balance clearance for overall uplift.
        """,
        styles["Normal"]
    ))

    # ------------------------------
    # BUILD PDF
    # ------------------------------
    doc.build(elements)
    buffer.seek(0)

    st.download_button(
        "⬇️ Download A4 EMP Intelligence Report (MARK 1)",
        buffer,
        f"EMPINTELLIGENCE_MARK1_{branch_name}_{report_date}.pdf",
        "application/pdf"
    )
else:
    st.info("📌 Upload Excel file to begin")
