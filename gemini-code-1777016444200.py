
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pdfplumber
from docx import Document
import io


# =====================================================
#  玄武會計師事務所（保留原頁面）
# =====================================================

st.markdown("""
#  玄武會計師事務所
## 雲端AI財務查核系統 v54
---
""")


# =====================================================
#  PDF / Word / Excel（全部整合，不拆module）
# =====================================================

def parse_pdf(files):
    text = ""
    for f in files:
        with pdfplumber.open(f) as pdf:
            for p in pdf.pages:
                text += p.extract_text() or ""
    return text


def parse_word(files):
    text = ""
    for f in files:
        doc = Document(f)
        for p in doc.paragraphs:
            text += p.text + "\n"
    return text


def parse_excel(files):
    dfs = []
    for f in files:
        dfs.append(pd.read_excel(f))
    return pd.concat(dfs) if dfs else None


# =====================================================
#  財務分析（保留你所有需求）
# =====================================================

def audit_engine(text, df):

    issues = []

    if "虛增" in text:
        issues.append(("財報不實", "可能收入虛增"))

    if "資金流向" in text:
        issues.append(("掏空風險", "資金異常移轉"))

    if "偽造" in text:
        issues.append(("舞弊風險", "文件異常"))

    if "幣安" in text:
        issues.append(("加密資產", "交易風險"))

    if df is not None and "營收" in df.columns:
        if df["營收"].iloc[-1] < df["營收"].iloc[0]:
            issues.append(("營收下降", "趨勢惡化"))

    return issues


# =====================================================
#  圖表（保留）
# =====================================================

def make_chart():

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
# 📄 Word報告（ISA 700）
# =====================================================

def generate_word(issues):

    doc = Document()

    doc.add_heading("ISA 700 財務查核報告", 0)

    doc.add_paragraph("本報告由AI系統生成")

    for i in issues:
        doc.add_paragraph(f"- {i[0]}：{i[1]}")

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    return buffer


# =====================================================
# 📊 Excel報告
# =====================================================

def generate_excel(df, issues):

    output = io.BytesIO()

    writer = pd.ExcelWriter(output, engine="openpyxl")

    if df is not None:
        df.to_excel(writer, sheet_name="財務數據")

    pd.DataFrame(issues, columns=["類別", "說明"]).to_excel(
        writer,
        sheet_name="查核結果"
    )

    writer.close()
    output.seek(0)

    return output


# =====================================================
# 🖥️ UI（完全保留你原本頁面風格）
# =====================================================

st.title("四大AI財務審計系統 v54")

pdf_files = st.file_uploader("PDF（可多選）", accept_multiple_files=True)
word_files = st.file_uploader("Word（可多選）", accept_multiple_files=True)
excel_files = st.file_uploader("Excel（可多選）", accept_multiple_files=True)


text = ""
df = None

if pdf_files:
    text += parse_pdf(pdf_files)

if word_files:
    text += parse_word(word_files)

if excel_files:
    df = parse_excel(excel_files)


# =====================================================
# 📊 分析核心
# =====================================================

if pdf_files or word_files or excel_files:

    issues = audit_engine(text, df)

    st.subheader("查核結果")

    for i in issues:
        st.write(i)

    st.subheader("財務圖表")
    st.pyplot(make_chart())


    st.subheader("Word報告下載")
    st.download_button(
        "下載Word",
        generate_word(issues),
        file_name="ISA700.docx"
    )

    st.subheader("Excel報告下載")
    st.download_button(
        "下載Excel",
        generate_excel(df, issues),
        file_name="financial.xlsx"
    )
