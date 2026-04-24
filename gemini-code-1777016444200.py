import streamlit as st
import pandas as pd
import pdfplumber
import re
from datetime import datetime
from docx import Document
import io


# =========================
# ROLE SYSTEM
# =========================

role = st.sidebar.selectbox(
    "使用者角色",
    ["Company User", "Auditor (CPA)", "Viewer"]
)


# =========================
# CASE MANAGEMENT
# =========================

company = st.sidebar.text_input("Company Name", "ABC Corp")
case_id = f"{company}_{datetime.now().strftime('%Y%m%d')}"


# =========================
# AUDIT TRAIL LOG
# =========================

audit_log = []


# =========================
# PDF PARSER (with trace)
# =========================

def extract(text, keywords, file_name):

    for k in keywords:
        m = re.search(rf"{k}.*?([\d,]+)", text, re.DOTALL)

        if m:
            value = float(m.group(1).replace(",", ""))

            audit_log.append({
                "case": case_id,
                "file": file_name,
                "keyword": k,
                "value": value
            })

            return value

    return 0


def parse_pdf(file):

    text = ""

    with pdfplumber.open(file) as pdf:
        for p in pdf.pages:
            text += p.extract_text() or ""

    return {
        "bs": {
            "cash": extract(text, ["現金"], file.name),
            "ar": extract(text, ["應收帳款"], file.name),
            "inventory": extract(text, ["存貨"], file.name),
            "assets": extract(text, ["資產總計"], file.name),
            "liabilities": extract(text, ["負債總計"], file.name),
            "equity": extract(text, ["權益總計"], file.name),
        },
        "is": {
            "revenue": extract(text, ["營業收入"], file.name),
            "net_income": extract(text, ["本期淨利"], file.name),
        },
        "cf": {
            "ocf": extract(text, ["營業活動現金流量"], file.name)
        }
    }


# =========================
# FINANCIAL ENGINE
# =========================

def financial(data):

    bs = data["bs"]
    is_ = data["is"]
    cf = data["cf"]

    assets = bs["assets"] if bs["assets"] else 1
    equity = bs["equity"] if bs["equity"] else 1

    return {
        "roe": is_["net_income"] / equity,
        "roa": is_["net_income"] / assets,
        "margin": is_["net_income"] / is_["revenue"] if is_["revenue"] else 0,
        "ocf_ratio": cf["ocf"] / is_["net_income"] if is_["net_income"] else 0,
        "leverage": bs["liabilities"] / equity
    }


# =========================
# COMPANY MODE
# =========================

def company_analysis(fin):

    insights = []

    if fin["ocf_ratio"] < 1:
        insights.append("現金轉換能力偏弱")

    if fin["leverage"] > 2:
        insights.append("槓桿偏高，建議調整資本結構")

    return insights


# =========================
# AUDIT MODE (ISA style)
# =========================

def audit_analysis(data, prev):

    findings = []

    if data["is"]["net_income"] > 0 and data["cf"]["ocf"] < 0:
        findings.append("盈餘品質疑慮（ISA 315）")

    if prev:
        if data["bs"]["ar"] > prev["bs"]["ar"] * 1.3:
            findings.append("應收帳款異常增加（收入認列風險）")

        if data["bs"]["inventory"] > prev["bs"]["inventory"] * 1.3:
            findings.append("存貨異常增加（可能估值風險）")

    return findings


# =========================
# FRAUD MODEL
# =========================

def fraud_score(data):

    score = 0

    if data["is"]["revenue"] > 0:
        margin = data["is"]["net_income"] / data["is"]["revenue"]
        if margin < 0.2:
            score += 1

    if data["cf"]["ocf"] < data["is"]["net_income"]:
        score += 1

    return score


# =========================
# UI
# =========================

st.title("Audit Analytics Platform （事務所系統）")


files = st.sidebar.file_uploader(
    "Upload Financial Statements",
    type="pdf",
    accept_multiple_files=True
)


# =========================
# MAIN ENGINE
# =========================

if files:

    results = []
    prev = None

    for f in sorted(files, key=lambda x: x.name):

        data = parse_pdf(f)
        fin = financial(data)

        if role == "Company User":
            output = company_analysis(fin)
        else:
            output = audit_analysis(data, prev)

        score = fraud_score(data)

        results.append({
            "file": f.name,
            "output": output,
            "fraud_score": score
        })

        prev = data


    df = pd.DataFrame(results)

    st.subheader("Analysis Result")

    for r in results:

        st.write(r["file"])

        if role == "Company User":
            st.write("Management Insight:", r["output"])
        else:
            st.write("Audit Findings:", r["output"])

        st.write("Fraud Score:", r["fraud_score"])


    st.subheader("Working Paper Data")

    st.dataframe(df)


    # =========================
    # WORKING PAPER EXPORT
    # =========================

    doc = Document()
    doc.add_heading("Audit Working Paper v3", 0)
    doc.add_paragraph(f"Case ID: {case_id}")

    for r in results:
        doc.add_paragraph(f"{r['file']}")
        doc.add_paragraph(str(r["output"]))

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)

    st.sidebar.download_button(
        "Download Working Paper",
        buf,
        file_name=f"{case_id}_WP.docx"
    )


else:
    st.info("Please upload financial PDF files")


# =========================
# AUDIT TRAIL VIEW
# =========================

st.subheader("Audit Trail")

st.dataframe(pd.DataFrame(audit_log))
