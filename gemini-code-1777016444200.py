import streamlit as st
import pandas as pd
import pdfplumber
import re
from docx import Document
import io
import time


# =========================
# PAGE CONFIG
# =========================

st.set_page_config(layout="wide")
st.title("四大會計師事務所｜財報分析與查核系統 v7（Production）")


# =========================
# MODE SELECT
# =========================

模式 = st.sidebar.selectbox(
    "分析模式",
    ["公司內部分析（Management）", "會計師查核模式（Audit）"]
)

公司 = st.sidebar.text_input("公司名稱", "ABC股份有限公司")


# =========================
# UPLOAD
# =========================

files = st.sidebar.file_uploader(
    "上傳財報 PDF",
    type="pdf",
    accept_multiple_files=True
)


# =========================
# AUDIT TRAIL
# =========================

audit_trail = []


# =========================
# PDF PARSER
# =========================

def parse_pdf(file):

    text = ""

    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""

    return text


def extract(text, keyword):

    m = re.search(rf"{keyword}.*?([\d,]+)", text, re.DOTALL)

    if m:
        return float(m.group(1).replace(",", ""))

    return 0


# =========================
# EVIDENCE ENGINE v2
# =========================

class EvidenceEngine:

    def create(self, file, text, account, keyword, page=1):

        value = extract(text, keyword)

        evidence = {
            "account": account,
            "value": value,
            "source": file.name,
            "page": page,
            "risk": "High" if value > 1000000 else "Low",
            "isa": self.map_isa(account),
            "procedure": self.procedure(account),
            "conclusion": self.conclusion(value)
        }

        audit_trail.append(evidence)

        return evidence


    def map_isa(self, account):

        if account == "應收帳款":
            return ["ISA 315", "ISA 505"]

        if account == "營收":
            return ["ISA 240"]

        return ["ISA 330"]


    def procedure(self, account):

        if account == "應收帳款":
            return [
                "函證測試",
                "期後收款測試",
                "合約查核"
            ]

        if account == "存貨":
            return [
                "盤點",
                "成本測試"
            ]

        return ["基本查核程序"]


    def conclusion(self, value):

        if value > 1000000:
            return "需進一步實質性查核"
        return "可接受"


engine = EvidenceEngine()


# =========================
# MANAGEMENT MODE
# =========================

def management(fin):

    result = []

    if fin["margin"] < 0.2:
        result.append("獲利能力偏弱")

    if fin["leverage"] > 2:
        result.append("槓桿偏高")

    return result


# =========================
# AUDIT MODE
# =========================

def audit(fin, evidence):

    result = []

    if evidence["value"] > 1000000:
        result.append("應收帳款異常增加（ISA 505）")

    if fin["margin"] < 0.1:
        result.append("盈餘品質疑慮（ISA 240）")

    return result


# =========================
# MAIN PROCESS
# =========================

if files:

    results = []

    for f in files:

        st.subheader(f"處理：{f.name}")

        with st.spinner("解析 PDF 中..."):
            text = parse_pdf(f)

        # 模擬科目
        acc = "應收帳款"

        evidence = engine.create(
            file=f,
            text=text,
            account=acc,
            keyword="應收帳款"
        )

        # 財務簡化模型
        revenue = extract(text, "營業收入")
        profit = extract(text, "本期淨利")

        margin = profit / revenue if revenue else 0
        leverage = 2.5  # 模擬

        fin = {
            "margin": margin,
            "leverage": leverage
        }

        if 模式.startswith("公司"):
            output = management(fin)
        else:
            output = audit(fin, evidence)

        results.append({
            "file": f.name,
            "evidence": evidence,
            "analysis": output
        })

        st.success("完成")


    # =========================
    # DASHBOARD
    # =========================

    st.subheader("分析結果")

    df = pd.DataFrame(results)
    st.dataframe(df)


    # =========================
    # WORKING PAPER EXPORT
    # =========================

    doc = Document()
    doc.add_heading("四大會計師事務所｜Working Paper v7", 0)
    doc.add_paragraph(f"公司：{公司}")
    doc.add_paragraph(f"模式：{模式}")

    for r in results:

        doc.add_paragraph("=== 查核發現 ===")
        doc.add_paragraph(str(r["evidence"]))
        doc.add_paragraph(str(r["analysis"]))

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    st.sidebar.download_button(
        "下載工作底稿",
        buffer,
        file_name=f"{公司}_WP_v7.docx"
    )


# =========================
# AUDIT TRAIL
# =========================

st.subheader("查核軌跡（Audit Trail）")

st.dataframe(pd.DataFrame(audit_trail))
