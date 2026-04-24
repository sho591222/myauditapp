
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pdfplumber
from docx import Document
import io


# =====================================================
# 🏢 系統標題
# =====================================================

st.markdown("""
# 🏢 玄武會計師事務所
## AI 財務分析與查核系統 v57
---
""")


# =====================================================
# 📄 PDF解析
# =====================================================

def parse_pdf(file):

    text = ""

    with pdfplumber.open(file) as pdf:
        for p in pdf.pages:
            text += p.extract_text() or ""

    return text


# =====================================================
# 🧠 財務分析（核心）
# =====================================================

def analyze(text):

    result = []
    notes = []

    # 四大報表分析
    if "資產" in text:
        result.append("資產負債表：需注意資產品質與流動性")

    if "負債" in text:
        result.append("負債結構：短期償債壓力分析")

    if "現金流量" in text:
        result.append("現金流量表：營運現金是否穩定")

    if "損益" in text:
        result.append("損益表：收入與費用匹配性")

    # 財報風險
    if "虛增" in text:
        result.append("財報不實風險")
        notes.append("建議查：收入 / 應收帳款")

    if "資金流向" in text:
        result.append("掏空風險")
        notes.append("建議查：現金 / 關係人交易")

    if "偽造" in text:
        result.append("舞弊風險")
        notes.append("建議查：憑證 / 銀行對帳單")

    return result, notes


# =====================================================
# 📊 圖表
# =====================================================

def chart():

    df = pd.DataFrame({
        "年度": ["2022", "2023", "2024"],
        "營收": [100, 120, 90],
        "獲利": [10, 15, -5]
    })

    fig, ax = plt.subplots()

    ax.plot(df["年度"], df["營收"], label="營收")
    ax.plot(df["年度"], df["獲利"], label="獲利")

    ax.legend()

    return fig


# =====================================================
# 📄 Word報告（你要的分析報告）
# =====================================================

def make_word(result, notes):

    doc = Document()

    doc.add_heading("財務分析報告", 0)

    doc.add_paragraph("本報告基於AI分析財務報表產出")

    doc.add_heading("分析結果", level=1)

    for r in result:
        doc.add_paragraph(r)

    doc.add_heading("查核建議", level=1)

    for n in notes:
        doc.add_paragraph(n)

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    return buffer


# =====================================================
# 📊 Excel報告（數據版）
# =====================================================

def make_excel(result, notes):

    output = io.BytesIO()

    df1 = pd.DataFrame(result, columns=["分析結果"])
    df2 = pd.DataFrame(notes, columns=["查核建議"])

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df1.to_excel(writer, sheet_name="分析")
        df2.to_excel(writer, sheet_name="查核")

    output.seek(0)

    return output


# =====================================================
# 🖥️ UI
# =====================================================

file = st.file_uploader("請上傳PDF財報")

if file:

    text = parse_pdf(file)

    result, notes = analyze(text)


    # =================================================
    # 📌 分析結果
    # =================================================

    st.subheader("財務分析結果")

    for r in result:
        st.write(r)


    # =================================================
    # 📌 查核建議
    # =================================================

    st.subheader("查核建議")

    for n in notes:
        st.write(n)


    # =================================================
    # 📊 圖表
    # =================================================

    st.subheader("財務圖表")
    st.pyplot(chart())


    # =================================================
    # 📄 Word下載
    # =================================================

    st.download_button(
        "下載 Word 報告",
        make_word(result, notes),
        file_name="財務分析報告.docx"
    )


    # =================================================
    # 📊 Excel下載
    # =================================================

    st.download_button(
        "下載 Excel 報告",
        make_excel(result, notes),
        file_name="財務分析.xlsx"
    )
