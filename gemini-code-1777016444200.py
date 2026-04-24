
import streamlit as st
from modules.parser import parse_pdf, parse_word, parse_excel
from modules.analysis import audit_engine
from modules.report import generate_word_report, generate_excel_report
from modules.charts import make_chart


# =====================================================
# 🏢 玄武會計師事務所
# =====================================================

st.markdown("""
#  玄武會計師事務所
## 雲端AI財務查核系統 v53
---
""")


# =====================================================
# UI
# =====================================================

st.title("四大 AI 財務審計平台")

pdf_files = st.file_uploader("PDF（可多選）", type=["pdf"], accept_multiple_files=True)
word_files = st.file_uploader("Word（可多選）", type=["docx"], accept_multiple_files=True)
excel_files = st.file_uploader("Excel（可多選）", type=["xlsx"], accept_multiple_files=True)


# =====================================================
# 解析
# =====================================================

text = ""
df = None

if pdf_files:
    text += parse_pdf(pdf_files)

if word_files:
    text += parse_word(word_files)

if excel_files:
    df = parse_excel(excel_files)


# =====================================================
# 分析
# =====================================================

if pdf_files or word_files or excel_files:

    issues = audit_engine(text, df)

    st.subheader("查核結果")

    for i in issues:
        st.write(i)

    st.subheader("財務圖表")
    st.pyplot(make_chart())


    # =================================================
    # Word 報告下載
    # =================================================

    word_file = generate_word_report(issues)

    st.download_button(
        "下載 Word 查核報告",
        word_file,
        file_name="ISA700_report.docx"
    )


    # =================================================
    # Excel 報告下載
    # =================================================

    excel_file = generate_excel_report(df, issues)

    st.download_button(
        "下載 Excel 財務分析",
        excel_file,
        file_name="financial_analysis.xlsx"
    )
