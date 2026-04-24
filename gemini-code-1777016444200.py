import streamlit as st
import pdfplumber
import pandas as pd
import matplotlib.pyplot as plt
import io
import re
from docx import Document
from docx.shared import Inches


# =========================
# UI
# =========================

st.title("玄武會計師事務所｜AI 查核系統 v30（證據定位版）")

mode = st.selectbox("分析模式", ["公司內部", "會計師事務所"])

files = st.file_uploader("上傳財報PDF", type="pdf", accept_multiple_files=True)


# =========================
# PDF PARSER（含頁數）
# =========================

def extract_pdf(file):

    pages_data = []

    with pdfplumber.open(file) as pdf:

        for i, page in enumerate(pdf.pages):

            text = page.extract_text() or ""

            pages_data.append({
                "page": i + 1,
                "text": text
            })

    return pages_data


# =========================
# KEYWORD DETECTION
# =========================

def detect_issues(page_text, page_num, mode):

    issues = []

    # -------------------------
    # COMMON DETECTION
    # -------------------------

    if "應收帳款" in page_text:
        issues.append((page_num, "應收帳款異常或需函證"))

    if "存貨" in page_text:
        issues.append((page_num, "存貨跌價或盤點風險"))

    if "關係人" in page_text:
        issues.append((page_num, "關係人交易需查核"))

    if "負債" in page_text:
        issues.append((page_num, "負債完整性風險"))


    # -------------------------
    # MODE LOGIC
    # -------------------------

    if mode == "會計師事務所":

        if "收入" in page_text:
            issues.append((page_num, "收入 cut-off test"))

        if "費用" in page_text:
            issues.append((page_num, "費用完整性測試"))

        issues.append((page_num, "函證程序（應收帳款）"))

    else:

        if "費用" in page_text:
            issues.append((page_num, "費用異常偏高"))

        if "現金" in page_text:
            issues.append((page_num, "現金流量異常"))

    return issues


# =========================
# DATA STORAGE
# =========================

all_issues = []
page_map = []


if files:

    for f in files:

        pages = extract_pdf(f)

        for p in pages:

            page_map.append({
                "page": p["page"],
                "text": p["text"]
            })

            issues = detect_issues(p["text"], p["page"], mode)

            all_issues.extend(issues)


# =========================
# DISPLAY
# =========================

if page_map:

    st.subheader("PDF頁面分析")

    for p in page_map:

        st.write(f"第 {p['page']} 頁")

        if len(p["text"]) > 200:
            st.text(p["text"][:200] + "...")
        else:
            st.text(p["text"])


# =========================
# ISSUE OUTPUT
# =========================

if all_issues:

    st.subheader("查核發現（頁面定位）")

    for page, issue in all_issues:

        st.write(f"第 {page} 頁 → {issue}")


# =========================
# SIMPLE FINANCIAL MODEL (optional demo)
# =========================

df = pd.DataFrame({
    "year": ["2021", "2022", "2023"],
    "revenue": [1000, 1200, 900],
    "profit": [100, 80, -50]
})

fig, ax = plt.subplots()
ax.plot(df["year"], df["revenue"], label="營收")
ax.plot(df["year"], df["profit"], label="淨利")
ax.legend()

st.pyplot(fig)


# =========================
# RISK SCORE
# =========================

score = 0

if len([x for x in all_issues if "關係人" in x[1]]) > 0:
    score += 30

if len([x for x in all_issues if "存貨" in x[1]]) > 2:
    score += 20

if len([x for x in all_issues if "應收帳款" in x[1]]) > 2:
    score += 20

score = min(score, 100)

st.subheader("風險分數")
st.write(score)


# =========================
# REPORT GENERATION (WORD)
# =========================

if st.button("產出完整查核報告"):

    doc = Document()

    doc.add_heading("AI 查核報告 v30（證據定位版）", 0)

    doc.add_paragraph(f"模式：{mode}")
    doc.add_paragraph(f"風險分數：{score}")

    doc.add_paragraph("\n=== 查核發現（頁面定位） ===")

    for page, issue in all_issues:
        doc.add_paragraph(f"第 {page} 頁 → {issue}")


    doc.add_paragraph("\n=== 查核建議科目 ===")

    if mode == "會計師事務所":

        doc.add_paragraph("應收帳款函證")
        doc.add_paragraph("收入 cut-off")
        doc.add_paragraph("存貨盤點")
        doc.add_paragraph("關係人交易查核")

    else:

        doc.add_paragraph("應收帳款回收性分析")
        doc.add_paragraph("存貨跌價風險")
        doc.add_paragraph("費用異常分析")


    doc.add_paragraph("\n=== 財務圖表已附（系統內） ===")

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    st.download_button(
        "下載查核報告",
        buffer,
        file_name="audit_v30.docx"
    )
