import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import calendar
from datetime import date
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors


# ======================================================
# PAGE CONFIG
# ======================================================
st.set_page_config(
    page_title="CELLPOINT | Owner Intelligence System",
    layout="wide"
)

st.title("📊 CELLPOINT SMARTPHONE GALLERY")
st.subheader("Owner Intelligence • CELLSUM • MRI • Store Control")

# ======================================================
# DATE INPUT
# ======================================================
report_date = st.date_input("📅 Report As On Date", value=date.today())

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
file_cp1 = st.file_uploader("📂 Upload CellPoint 1 Excel", type=["xlsx"])
file_cp2 = st.file_uploader("📂 Upload CellPoint 2 Excel", type=["xlsx"])

# ======================================================
# HELPERS
# ======================================================
def load_branch_excel(file):
    df = pd.read_excel(file)
    df.columns = df.columns.str.strip().str.upper()
    df = df[~df["BRAND NAME"].astype(str).str.contains("TOTAL", case=False)]
    for col in ["MONTHLY TARGET", "ACHIEVEMENT", "BALANCE TO DO", "DAILY TARGET"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df

# ---------- CELLSUM RISK ----------
def cellsum_risk(p):
    if p > 100: return "🟢 Extra Ordinary"
    elif p >= 91: return "🟢 Excellent"
    elif p >= 61: return "🟡 Good"
    elif p >= 31: return "🟠 Average"
    else: return "🔴 Very High"

def cellsum_rank(r):
    return {
        "🟢 Extra Ordinary": 1,
        "🟢 Excellent": 2,
        "🟡 Good": 3,
        "🟠 Average": 4,
        "🔴 Very High": 5
    }.get(r, 99)

# ---------- MRI RISK ----------
def mri_risk(p):
    if p >= 100: return "🟢 Aligned"
    elif p >= 85: return "🟡 Slight Gap"
    elif p >= 70: return "🟠 Misaligned"
    else: return "🔴 High Risk"

def mri_rank(r):
    return {
        "🟢 Aligned": 1,
        "🟡 Slight Gap": 2,
        "🟠 Misaligned": 3,
        "🔴 High Risk": 4
    }.get(r, 99)

def company_status(p):
    if p > 100: return "🟢 EXTRA ORDINARY"
    elif p >= 91: return "🟢 EXCELLENT"
    elif p >= 61: return "🟡 GOOD"
    elif p >=31: return "🟠 AVERAGE"
    else: return "🔴 CRITICAL"

# ======================================================
# MRI PERMANENT TARGETS (₹ in Lakhs)
# ======================================================
MRI_TARGETS = {
    "IPHONE": 70,
    "REALME": 32,
    "OPPO": 31,
    "VIVO": 45,
    "NOTHING": 15,
    "REDMI": 10,
    "MOTO": 20,
    "OTHERS": 10,
    "SAMSUNG": 20,
    "ONEPLUS": 25
}
# ======================================================
# PDF GENERATOR – CELLSUM & MRI
# ======================================================

def generate_cellsum_mri_pdf(
    cellsum_df, total_trgt, total_ach, total_pct,
    run_rate, predicted_final, cellsum_carrier,
    mri_df, mri_pct
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

    def color_status(text):
        if "🟢" in text:
           return Paragraph(f"<font color='green'>{text}</font>", styles["Normal"])
        elif "🟡" in text:
           return Paragraph(f"<font color='orange'>{text}</font>", styles["Normal"])
        elif "🟠" in text:
           return Paragraph(f"<font color='#d35400'>{text}</font>", styles["Normal"])
        elif "🔴" in text:
           return Paragraph(f"<font color='red'>{text}</font>", styles["Normal"])
        else:
           return Paragraph(text, styles["Normal"])

    elements = []

    # ---------------- HEADER ----------------
    elements.append(Paragraph(
        "<b>CELLPOINT – CELLSUM & MRI REPORT</b><br/>"
        "Owner Intelligence Summary<br/><br/>",
        styles["Title"]
    ))

    # ---------------- SUMMARY ----------------
    elements.append(Paragraph(
        f"<b>Total Target:</b> ₹{int(total_trgt):,}<br/>"
        f"<b>Total Achieved:</b> ₹{int(total_ach):,}<br/>"
        f"<b>Achievement %:</b> {total_pct:.1f}%<br/>"
        f"<b>Run Rate:</b> ₹{run_rate/1e5:.2f} L / day<br/>"
        f"<b>Predicted Final:</b> ₹{int(predicted_final):,}<br/>"
        f"<b>CELLSUM Carrier:</b> {cellsum_carrier}<br/><br/>",
        styles["Normal"]
    ))

    # ---------------- CELLSUM TABLE ----------------
    elements.append(Paragraph("<b>Brand Performance Summary</b>", styles["Heading2"]))

    table_data = [[
        "Brand", "Target", "Achieved", "Achievement %", "Risk Level"
    ]]

    for _, r in cellsum_df.iterrows():
        table_data.append([
            r["BRAND NAME"],
            f"{int(r['MONTHLY TARGET']):,}",
            f"{int(r['ACHIEVEMENT']):,}",
            f"{r['ACHIEVEMENT %']:.1f}%",
            color_status(r["RISK LEVEL"])
        ])

    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.4, colors.black),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("FONTSIZE", (0,0), (-1,-1), 8),
        ("ALIGN", (1,1), (-1,-1), "CENTER"),
    ]))

    elements.append(table)


    # ---------------- MRI SECTION ----------------
    elements.append(Spacer(1, 16))
    elements.append(Paragraph(
    "<b>🧠 MRI – Internal Brand-Mix Intelligence</b>",
    styles["Heading2"]
))

    elements.append(Paragraph(
    f"<b>Overall MRI Alignment:</b> "
    f"{color_status(mri_risk(mri_pct)).text} "
    f"({mri_pct:.1f}%)<br/><br/>",
    styles["Normal"]
))


    mri_table = [[
    "Brand", "MRI Target", "Achieved", "MRI %", "MRI Status"
]]

    for _, r in mri_df.iterrows():
        mri_table.append([
        r["BRAND NAME"],
        f"{int(r['MRI TARGET']):,}",
        f"{int(r['ACHIEVEMENT']):,}",
        f"{r['MRI %']:.1f}%",
        color_status(r["MRI STATUS"])
    ])

    tbl = Table(mri_table, repeatRows=1)
    tbl.setStyle(TableStyle([
    ("GRID", (0,0), (-1,-1), 0.4, colors.black),
    ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
    ("FONTSIZE", (0,0), (-1,-1), 8),
    ("ALIGN", (1,1), (-1,-1), "CENTER"),
]))

    elements.append(tbl)


    doc.build(elements)
    buffer.seek(0)
    return buffer
    




# ======================================================
# MAIN LOGIC
# ======================================================
if file_cp1 and file_cp2:

    # ---------------- LOAD ----------------
    df1 = load_branch_excel(file_cp1)
    df2 = load_branch_excel(file_cp2)

    # ======================================================
    # CELLSUM (UNIVERSE)
    # ======================================================
    cellsum_df = (
        pd.concat([df1, df2])
        .groupby("BRAND NAME", as_index=False)
        .sum()
    )

    cellsum_df["ACHIEVEMENT %"] = (
        cellsum_df["ACHIEVEMENT"] / cellsum_df["MONTHLY TARGET"] * 100
    )
    cellsum_df["RISK LEVEL"] = cellsum_df["ACHIEVEMENT %"].apply(cellsum_risk)
    cellsum_df["RANK"] = cellsum_df["RISK LEVEL"].apply(cellsum_rank)

    # BEST → WORST hierarchy
    cellsum_df = cellsum_df.sort_values(
        ["RANK", "ACHIEVEMENT %"], ascending=[True, False]
    ).drop(columns="RANK")

    total_ach = cellsum_df["ACHIEVEMENT"].sum()
    total_trgt = cellsum_df["MONTHLY TARGET"].sum()
    total_pct = (total_ach / total_trgt) * 100

    run_rate = total_ach / days_completed if days_completed > 0 else 0
    predicted_final = total_ach + run_rate * days_remaining

    # ======================================================
    # CELLSUM SNAPSHOT
    # ======================================================
    st.markdown("## 🧮 CELLSUM – CellPoint Universe")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("🎯 Target", f"₹{int(total_trgt):,}")
    c2.metric("✅ Achieved", f"₹{int(total_ach):,}", f"{total_pct:.1f}%")
    c3.metric("📈 Run Rate", f"₹{run_rate/1e5:.2f} L / day")
    c4.metric("🔮 Predicted", f"₹{int(predicted_final):,}")
    c5.metric("🏢 Status", company_status(total_pct))

    st.subheader("📋 Brand Performance (Best → Worst)")
    st.dataframe(cellsum_df, use_container_width=True)

    # ======================================================
    # STORE CONTRIBUTION – CELLSUM
    # ======================================================
    cp1_cellsum = df1["ACHIEVEMENT"].sum()
    cp2_cellsum = df2["ACHIEVEMENT"].sum()
    universe_total = cp1_cellsum + cp2_cellsum

    cp1_pct = (cp1_cellsum / universe_total) * 100
    cp2_pct = (cp2_cellsum / universe_total) * 100

    st.markdown("## 🏬 Store Contribution – CELLSUM")

    c1, c2, c3 = st.columns(3)
    c1.metric("🏬 CP1 Contribution", f"₹{int(cp1_cellsum):,}", f"{cp1_pct:.1f}%")
    c2.metric("🏬 CP2 Contribution", f"₹{int(cp2_cellsum):,}", f"{cp2_pct:.1f}%")

    cellsum_carrier = "CellPoint 1" if cp1_pct > cp2_pct else "CellPoint 2"
    c3.metric("💪 CELLSUM Carrier", cellsum_carrier)


   

    # ======================================================
    # MRI – INTERNAL DETAILED ANALYSIS
    # ======================================================
    st.markdown("---")
    st.markdown("## 🧠 MRI – Internal Brand-Mix Intelligence")
    st.caption("🔒 Internal only • Strategic view")

    if st.button("🚨 Run MRI Assessment"):

        # -------- MRI BRAND LEVEL --------
        mri_df = cellsum_df.copy()
        mri_df["BRAND NAME"] = mri_df["BRAND NAME"].str.upper()

        mri_targets_df = pd.DataFrame([
            {"BRAND NAME": k, "MRI TARGET": v * 1_00_000}
            for k, v in MRI_TARGETS.items()
        ])

        mri_df = mri_df.merge(mri_targets_df, on="BRAND NAME", how="inner")

        mri_df["MRI %"] = (mri_df["ACHIEVEMENT"] / mri_df["MRI TARGET"]) * 100
        mri_df["MRI STATUS"] = mri_df["MRI %"].apply(mri_risk)
        mri_df["RANK"] = mri_df["MRI STATUS"].apply(mri_rank)

        # BEST → WORST hierarchy
        mri_df = mri_df.sort_values(
            ["RANK", "MRI %"], ascending=[True, False]
        ).drop(columns="RANK")

        # -------- MRI TOTALS --------
        mri_ach = mri_df["ACHIEVEMENT"].sum()
        mri_trgt = mri_df["MRI TARGET"].sum()
        mri_run = mri_ach / days_completed if days_completed > 0 else 0
        mri_pred = mri_ach + mri_run * days_remaining
        mri_pct = (mri_pred / mri_trgt) * 100


         # ================= DOWNLOAD REPORT =================
        st.markdown("## 📄 Download CELLSUM Intelligence Report")

        st.download_button(
        "⬇️ Download A4 CELLSUM Intelligence Report",
        generate_cellsum_mri_pdf(
            cellsum_df,
            total_trgt,
            total_ach,
            total_pct,
            run_rate,
            predicted_final,
            cellsum_carrier,
            mri_df,
            mri_pct
        ),
        "CELLPOINT_CELLSUM_MRI_Report.pdf",
        "application/pdf"
    )

        # -------- MRI SNAPSHOT --------
        st.markdown("### 🧠 MRI Snapshot")

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("🎯 MRI Target", f"₹{int(mri_trgt):,}")
        c2.metric("✅ MRI Achieved", f"₹{int(mri_ach):,}", f"{(mri_ach/mri_trgt)*100:.1f}%")
        c3.metric("📈 MRI Run Rate", f"₹{mri_run/1e5:.2f} L / day")
        c4.metric("🔮 MRI Predicted", f"₹{int(mri_pred):,}")
        c5.metric("🏢 MRI Status", mri_risk(mri_pct))

        st.subheader("📋 MRI Brand Analysis (Best → Worst)")
        st.dataframe(mri_df[[
            "BRAND NAME",
            "MRI TARGET",
            "ACHIEVEMENT",
            "MRI %",
            "MRI STATUS"
        ]], use_container_width=True)

        # -------- STORE MRI CONTRIBUTION --------
        def store_mri_ach(df):
            d = df.copy()
            d["BRAND NAME"] = d["BRAND NAME"].str.upper()
            d = d.merge(mri_targets_df, on="BRAND NAME", how="inner")
            return d["ACHIEVEMENT"].sum()

        cp1_mri = store_mri_ach(df1)
        cp2_mri = store_mri_ach(df2)
        mri_total = cp1_mri + cp2_mri

        cp1_mri_pct = (cp1_mri / mri_total) * 100 if mri_total else 0
        cp2_mri_pct = (cp2_mri / mri_total) * 100 if mri_total else 0

        st.markdown("### 🏬 MRI – Store Contribution")

        c1, c2, c3 = st.columns(3)
        c1.metric("🏬 CP1 MRI", f"₹{int(cp1_mri):,}", f"{cp1_mri_pct:.1f}%")
        c2.metric("🏬 CP2 MRI", f"₹{int(cp2_mri):,}", f"{cp2_mri_pct:.1f}%")

        mri_carrier = "CellPoint 1" if cp1_mri_pct > cp2_mri_pct else "CellPoint 2"
        c3.metric("⚠️ MRI Carrier", mri_carrier)

        if cellsum_carrier != mri_carrier:
            st.error(
                f"🚨 STRATEGIC CONFLICT: {cellsum_carrier} carries revenue, "
                f"but {mri_carrier} carries strategy."
            )

else:
    st.info("⬆️ Upload BOTH Excel files to start analysis")
