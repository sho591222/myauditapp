import streamlit as st
import pandas as pd
import sqlite3
import datetime
from docx import Document
import io


# =========================
# SYSTEM CONFIG
# =========================

st.set_page_config(layout="wide")
st.title("玄武會計師事務所｜企業雙層財報分析系統 v15")


# =========================
# MODE SELECT
# =========================

mode = st.sidebar.selectbox(
    "使用模式",
    ["公司內部分析模式", "會計師事務所模式", "玄武會計師事務所模式"]
)


# =========================
# FIRM SETTINGS（鎖定邏輯）
# =========================

if mode == "玄武會計師事務所模式":

    firm_name = "玄武會計師事務所"
    partner = "玄武主持會計師"
    report_date = datetime.date.today()

    st.sidebar.text_input("會計師名稱（鎖定）", partner, disabled=True)
    st.sidebar.date_input("查核日期（鎖定）", report_date, disabled=True)

else:

    firm_name = st.sidebar.text_input("事務所名稱", "玄武會計師事務所")
    partner = st.sidebar.text_input("會計師名稱", "玄武主持會計師")
    report_date = st.sidebar.date_input("查核日期")


# =========================
# INPUT
# =========================

company = st.text_input("公司名稱", "ABC股份有限公司")

revenue = st.number_input("營收", 0)
profit = st.number_input("淨利", 0)
assets = st.number_input("資產總額", 0)
liabilities = st.number_input("負債總額", 0)


# =========================
# FINANCIAL ANALYSIS CORE
# =========================

def ratios():

    margin = profit / revenue if revenue else 0
    leverage = liabilities / assets if assets else 0

    return margin, leverage


# =========================
# COMPANY MODE
# =========================

def company_analysis(margin, leverage):

    result = []

    if margin < 0.2:
        result.append("建議改善獲利能力")

    if leverage > 0.6:
        result.append("財務槓桿偏高，建議調整資本結構")

    return result


# =========================
# AUDIT MODE
# =========================

def audit_analysis(margin, leverage):

    result = []

    if margin < 0.2:
        result.append("毛利率偏低，需評估收入認列合理性（ISA 240）")

    if leverage > 0.6:
        result.append("負債比例偏高，需執行持續經營評估（ISA 570）")

    return result


# =========================
# XUANWU MODE（更細查核）
# =========================

def xuanwu_analysis(margin, leverage):

    result = []

    result.append("進階財報拆解分析啟動")

    if revenue > 10000000:
        result.append("需進行收入分層測試（Revenue Cut-off Test）")

    if liabilities / assets > 0.7:
        result.append("高負債結構風險，需壓力測試（Stress Test）")

    if margin < 0.15:
        result.append("盈餘品質偏低，需測試應計項目（Accrual Testing）")

    return result


# =========================
# EXECUTE
# =========================

if st.button("執行分析"):

    margin, leverage = ratios()

    st.subheader("分析結果")

    if mode == "公司內部分析模式":
        st.write(company_analysis(margin, leverage))

    elif mode == "會計師事務所模式":
        st.write(audit_analysis(margin, leverage))

    else:
        st.write(xuanwu_analysis(margin, leverage))


# =========================
# REPORT EXPORT
# =========================

if st.button("下載工作底稿"):

    doc = Document()

    doc.add_heading("企業財報分析系統 v15", 0)

    doc.add_paragraph("模式：" + mode)
    doc.add_paragraph("公司：" + company)
    doc.add_paragraph("事務所：" + firm_name)
    doc.add_paragraph("會計師：" + partner)
    doc.add_paragraph("查核日期：" + str(report_date))

    margin, leverage = ratios()

    doc.add_paragraph(f"毛利率：{margin}")
    doc.add_paragraph(f"槓桿比率：{leverage}")

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    st.download_button(
        "下載Word工作底稿",
        buffer,
        file_name="v15_report.docx"
    )
