
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pdfplumber
from docx import Document
from docx.shared import Inches
import io


# =====================================================
# 🏢 系統標題
# =====================================================

st.markdown("""
# 🏢 玄武會計師事務所
## AI 四大財務查核整合系統 v60
---
""")


# =====================================================
# 🔐 登入角色（影響全部輸出）
# =====================================================

role = st.selectbox("選擇使用者類型", [
    "公司使用者",
    "會計師事務所"
])


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
# 🧠 核心分析（統一資料來源）
# =====================================================

def analyze(text, role):

    core = []
    suggestions = []

    # =========================
    # 四大報表解析
    # =========================

    if "資產" in text:
        core.append(("資產負債表", "流動性與資產品質分析", 70))

    if "負債" in text:
        core.append(("負債結構", "償債能力分析", 60))

    if "現金流量" in text:
        core.append(("現金流量", "營運現金穩定性", 55))

    if "損益" in text:
        core.append(("損益表", "收入與費用匹配", 65))


    # =========================
    # 風險分析
    # =========================

    if "虛增" in text:
        core.append(("財報不實", "收入可能虛增", 90))
        suggestions.append("應查：收入 / 應收帳款")

    if "資金流向" in text:
        core.append(("掏空風險", "資金異常流動", 85))
        suggestions.append("應查：現金 / 關係人交易")

    if "偽造" in text:
        core.append(("舞弊風險", "文件異常", 95))
        suggestions.append("應查：憑證 / 銀行對帳")


    # =========================
    # 事務所模式加強（你要的）
    # =========================

    if role == "會計師事務所":

        suggestions += [
            "查核重點：收入認列",
            "查核重點：應收帳款",
            "查核重點：存貨跌價",
            "查核重點：關係人交易",
            "查核重點：現金流量合理性"
        ]

    return core, suggestions


# =====================================================
# 📊 圖表（頁面顯示 + Word用）
# =====================================================

def make_chart(core):

    labels = [c[0] for c in core]
    values = [c[2] for c in core]

    fig, ax = plt.subplots()

    ax.bar(labels, values)

    ax.set_title("財務風險分析圖")

    return fig


# =====================================================
# 📄 Word（含圖表 + 詳細說明）
# =====================================================

def make_word(core, suggestions, fig):

    doc = Document()

    doc.add_heading("ISA 700 財務查核報告", 0)

    # =========================
    # 分析內容
    # =========================

    doc.add_heading("財務報表分析", level=1)

    for c in core:
        doc.add_paragraph(
            f"{c[0]}：{c[1]}（風險值 {c[2]}）"
        )

    # =========================
    # 查核建議
    # =========================

    doc.add_heading("查核建議", level=1)

    for s in suggestions:
        doc.add_paragraph(s)

    # =========================
    # 圖表插入（重點）
    # =========================

    image_path = "chart.png"
    fig.savefig(image_path)

    doc.add_heading("風險圖表", level=1)
    doc.add_picture(image_path, width=Inches(5))

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    return buffer


# =====================================================
# 📊 Excel（完整數據）
# =====================================================

def make_excel(core, suggestions):

    output = io.BytesIO()

    df1 = pd.DataFrame(core, columns=["項目", "說明", "風險值"])
    df2 = pd.DataFrame(suggestions, columns=["查核建議"])

    with pd.ExcelWriter(output, engine="openpyxl") as writer:

        df1.to_excel(writer, sheet_name="財務分析")
        df2.to_excel(writer, sheet_name="查核建議")

    output.seek(0)

    return output


# =====================================================
# 🖥️ UI（結果頁面）
# =====================================================

file = st.file_uploader("請上傳PDF財報")

if file:

    text = parse_pdf(file)

    core, suggestions = analyze(text, role)


    # =================================================
    # 📊 頁面分析結果（你要的）
    # =================================================

    st.subheader("財務分析結果")

    for c in core:
        st.write(f"{c[0]} - {c[1]}（風險值 {c[2]}）")


    # =================================================
    # 📌 查核建議
    # =================================================

    st.subheader("查核 / 異常建議")

    for s in suggestions:
        st.write(s)


    # =================================================
    # 📊 圖表（頁面顯示）
    # =================================================

    fig = make_chart(core)

    st.subheader("財務風險圖表")
    st.pyplot(fig)


    # =================================================
    # 📄 Word下載（含圖表 + 詳細分析）
    # =================================================

    st.download_button(
        "下載 Word 查核報告（含圖表）",
        make_word(core, suggestions, fig),
        file_name="ISA700_full_report.docx"
    )


    # =================================================
    # 📊 Excel下載
    # =================================================

    st.download_button(
        "下載 Excel 財務分析",
        make_excel(core, suggestions),
        file_name="financial_analysis.xlsx"
    )
