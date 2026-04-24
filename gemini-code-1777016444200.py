import streamlit as st
import pandas as pd
import datetime
from docx import Document
import io


# =========================
# SYSTEM CONFIG
# =========================

st.set_page_config(layout="wide")
st.title("玄武會計師事務所｜企業雙流程系統 v17")


# =========================
# MODE SELECT (三大區塊)
# =========================

mode = st.selectbox(
    "選擇使用模式",
    ["公司內部使用", "跨會計師事務所查核使用"]
)


# =========================
# SYSTEM LOGIC (關鍵：欄位鎖定)
# =========================

if mode == "公司內部使用":

    st.subheader("公司內部分析模式")

    company_name = st.text_input("公司名稱")

    auditor_name = None
    audit_date = None

    system_date = datetime.date.today()

    st.info("公司模式：會計師名稱與查核日期已鎖定（系統自動產生）")


else:

    st.subheader("會計師查核模式")

    company_name = st.text_input("公司名稱")

    auditor_name = st.text_input("會計師名稱")

    audit_date = st.date_input("查核報告日期")

    system_date = None


# =========================
# FINANCIAL INPUT
# =========================

revenue = st.number_input("營收", 0)
profit = st.number_input("淨利", 0)
assets = st.number_input("資產總額", 0)
liabilities = st.number_input("負債總額", 0)


# =========================
# RATIO CALC
# =========================

def calc():

    margin = profit / revenue if revenue else 0
    leverage = liabilities / assets if assets else 0

    return margin, leverage


# =========================
# REPORT ENGINE
# =========================

def company_report(margin, leverage):

    return [
        "建議改善獲利能力",
        "優化成本結構",
        "加強現金流管理"
    ]


def audit_report(margin, leverage):

    return [
        "需執行函證程序（應收帳款）",
        "需評估持續經營能力（ISA 570）",
        "需進一步實質性查核（ISA 330）"
    ]


# =========================
# MAIN EXECUTION
# =========================

if st.button("產出報告"):

    margin, leverage = calc()

    st.subheader("分析結果")

    if mode == "公司內部使用":

        report_type = "公司內部管理建議報告書"

        report_date_final = system_date

        result = company_report(margin, leverage)

    else:

        report_type = "會計師查核建議報告書"

        report_date_final = audit_date

        result = audit_report(margin, leverage)


    st.write({
        "公司": company_name,
        "報告類型": report_type,
        "毛利率": margin,
        "槓桿": leverage,
        "結果": result
    })


# =========================
# WORD REPORT EXPORT
# =========================

if st.button("下載報告書"):

    doc = Document()

    doc.add_heading("玄武會計師事務所｜企業報告書", 0)

    doc.add_paragraph("公司：" + str(company_name))
    doc.add_paragraph("報告類型：" + report_type)

    if mode == "公司內部使用":
        doc.add_paragraph("系統產生日期：" + str(system_date))
    else:
        doc.add_paragraph("會計師：" + str(auditor_name))
        doc.add_paragraph("查核日期：" + str(audit_date))

    margin, leverage = calc()

    doc.add_paragraph(f"毛利率：{margin}")
    doc.add_paragraph(f"槓桿比率：{leverage}")

    doc.add_paragraph("建議事項")

    for r in result:
        doc.add_paragraph("- " + r)

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    st.download_button(
        "下載 Word 報告",
        buffer,
        file_name="玄武企業報告_v17.docx"
    )
