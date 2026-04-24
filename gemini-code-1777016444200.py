import streamlit as st
import pandas as pd
import pdfplumber
import re
import matplotlib.pyplot as plt
from docx import Document
import io


# =========================
# PDF PARSER
# =========================

def extract(text, keywords):
    for k in keywords:
        m = re.search(rf"{k}.*?([\d,]+)", text, re.DOTALL)
        if m:
            return float(m.group(1).replace(",", ""))
    return 0


def parse_pdf(file):

    text = ""

    with pdfplumber.open(file) as pdf:
        for p in pdf.pages:
            text += p.extract_text() or ""

    return {
        "bs": {
            "cash": extract(text, ["現金"]),
            "ar": extract(text, ["應收帳款"]),
            "inventory": extract(text, ["存貨"]),
            "assets": extract(text, ["資產總計"]),
            "liabilities": extract(text, ["負債總計"]),
            "equity": extract(text, ["權益總計"]),
        },
        "is": {
            "revenue": extract(text, ["營業收入"]),
            "gross_profit": extract(text, ["營業毛利"]),
            "net_income": extract(text, ["本期淨利"]),
        },
        "cf": {
            "ocf": extract(text, ["營業活動現金流量"])
        }
    }


# =========================
# FINANCIAL ANALYSIS
# =========================

def financial(data):

    bs = data["bs"]
    is_ = data["is"]
    cf = data["cf"]

    assets = bs["assets"] if bs["assets"] else 1
    equity = bs["equity"] if bs["equity"] else 1

    roe = is_["net_income"] / equity
    roa = is_["net_income"] / assets
    margin = is_["net_income"] / is_["revenue"] if is_["revenue"] else 0
    ocf_ratio = cf["ocf"] / is_["net_income"] if is_["net_income"] else 0
    leverage = bs["liabilities"] / equity

    return {
        "roe": roe,
        "roa": roa,
        "margin": margin,
        "ocf_ratio": ocf_ratio,
        "leverage": leverage
    }


# =========================
# AUDIT ENGINE (四大版本)
# =========================

def audit_engine(curr, prev=None):

    alerts = []

    bs = curr["bs"]
    is_ = curr["is"]
    cf = curr["cf"]

    if is_["net_income"] > 0 and cf["ocf"] < 0:
        alerts.append("盈餘品質風險：淨利為正但OCF為負")

    if prev:
        if bs["ar"] > prev["bs"]["ar"] * 1.3:
            alerts.append("應收帳款異常增加（收入認列風險）")

        if bs["inventory"] > prev["bs"]["inventory"] * 1.3:
            alerts.append("存貨異常增加（可能虛增資產）")

        if bs["cash"] < prev["bs"]["cash"] * 0.5:
            alerts.append("現金大幅下降（流動性風險）")

    leverage = bs["liabilities"] / bs["equity"] if bs["equity"] else 0

    if leverage > 2:
        alerts.append("高財務槓桿風險")

    return alerts


# =========================
# FRAUD MODEL
# =========================

def fraud_model(curr, prev=None):

    score = 0

    bs = curr["bs"]
    is_ = curr["is"]

    if prev:
        if prev["bs"]["ar"] > 0:
            if bs["ar"] / prev["bs"]["ar"] > 1.2:
                score += 1

        if prev["bs"]["inventory"] > 0:
            if bs["inventory"] / prev["bs"]["inventory"] > 1.2:
                score += 1

    if is_["revenue"] > 0:
        if (is_["gross_profit"] / is_["revenue"]) < 0.2:
            score += 1

    if curr["cf"]["ocf"] < curr["is"]["net_income"]:
        score += 1

    level = "High" if score >= 3 else "Medium" if score == 2 else "Low"

    return score, level


# =========================
# BENCHMARK (同業比較)
# =========================

industry = {
    "roe": 0.12,
    "margin": 0.25,
    "leverage": 1.5
}


# =========================
# STREAMLIT UI
# =========================

st.set_page_config(layout="wide")

st.title("四大正式企業財報分析系統 v2")


# =========================
# MODE SELECT
# =========================

mode = st.sidebar.selectbox(
    "分析模式",
    ["公司內部分析 (Management)", "會計師事務所分析 (Audit)"]
)


company = st.sidebar.text_input("公司名稱", "XX股份有限公司")
auditor = st.sidebar.text_input("會計師", "CPA")
firm = st.sidebar.text_input("事務所", "Big4 Firm")

files = st.sidebar.file_uploader(
    "上傳財報 PDF",
    type="pdf",
    accept_multiple_files=True
)


# =========================
# MAIN PROCESS
# =========================

if files:

    results = []
    prev = None

    for f in sorted(files, key=lambda x: x.name):

        data = parse_pdf(f)
        fin = financial(data)

        alerts = audit_engine(data, prev)
        score, level = fraud_model(data, prev)

        benchmark_flags = []

        if fin["roe"] < industry["roe"]:
            benchmark_flags.append("ROE低於產業水準")

        if fin["margin"] < industry["margin"]:
            benchmark_flags.append("毛利率低於產業")

        if fin["leverage"] > industry["leverage"]:
            benchmark_flags.append("槓桿高於產業")

        results.append({
            "year": f.name,
            "revenue": data["is"]["revenue"],
            "net_income": data["is"]["net_income"],
            "cash": data["bs"]["cash"],
            "ar": data["bs"]["ar"],
            "inventory": data["bs"]["inventory"],
            "ROE": fin["roe"],
            "ROA": fin["roa"],
            "margin": fin["margin"],
            "leverage": fin["leverage"],
            "audit_flags": alerts,
            "fraud_score": score,
            "fraud_level": level,
            "benchmark": benchmark_flags
        })

        prev = data

    df = pd.DataFrame(results)


    # =========================
    # DASHBOARD
    # =========================

    st.subheader("財務分析 Dashboard")

    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots()
        ax.plot(df["year"], df["revenue"], label="營收")
        ax.plot(df["year"], df["net_income"], label="淨利")
        ax.set_title("損益趨勢")
        ax.legend()
        st.pyplot(fig)

    with col2:
        fig2, ax2 = plt.subplots()
        ax2.plot(df["year"], df["ROE"], label="ROE")
        ax2.plot(df["year"], df["ROA"], label="ROA")
        ax2.set_title("獲利能力")
        ax2.legend()
        st.pyplot(fig2)


    # =========================
    # MODE OUTPUT
    # =========================

    st.subheader("分析結果")

    for r in results:

        st.write(r["year"])

        if mode.startswith("公司內部"):
            st.write("Management Insights:")
            st.write(r["benchmark"])
        else:
            st.write("Audit Findings:")
            st.write(r["audit_flags"])
            st.write("Fraud:", r["fraud_level"], r["fraud_score"])


    # =========================
    # DATA TABLE
    # =========================

    st.subheader("完整財務資料")

    st.dataframe(df)


    # =========================
    # WORD REPORT
    # =========================

    doc = Document()
    doc.add_heading("四大企業財報分析報告 v2", 0)

    doc.add_paragraph(f"公司：{company}")
    doc.add_paragraph(f"事務所：{firm}")
    doc.add_paragraph(f"會計師：{auditor}")
    doc.add_paragraph(f"分析模式：{mode}")

    for r in results:
        doc.add_paragraph(f"{r['year']}")
        doc.add_paragraph(f"Audit: {r['audit_flags']}")
        doc.add_paragraph(f"Fraud: {r['fraud_level']} ({r['fraud_score']})")

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)

    st.sidebar.download_button(
        "下載查核報告",
        buf,
        file_name=f"{company}_audit_v2.docx"
    )

else:
    st.info("請上傳財報 PDF")
