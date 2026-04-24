import streamlit as st
import pandas as pd
import pdfplumber
import re
import matplotlib.pyplot as plt


# =========================
# PDF 解析
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
# 財務分析
# =========================

def financial(f):

    bs = f["bs"]
    is_ = f["is"]
    cf = f["cf"]

    assets = bs["assets"] if bs["assets"] else 1

    roe = is_["net_income"] / bs["equity"] if bs["equity"] else 0
    roa = is_["net_income"] / assets
    margin = is_["net_income"] / is_["revenue"] if is_["revenue"] else 0
    ocf_ratio = cf["ocf"] / is_["net_income"] if is_["net_income"] else 0

    return {
        "roe": roe,
        "roa": roa,
        "margin": margin,
        "ocf_ratio": ocf_ratio
    }


# =========================
# 查核分析
# =========================

def audit(curr, prev=None):

    alerts = []

    bs = curr["bs"]
    is_ = curr["is"]
    cf = curr["cf"]

    if is_["net_income"] > 0 and cf["ocf"] < 0:
        alerts.append("盈餘品質疑慮：淨利為正但現金流為負")

    if prev:
        if bs["ar"] > prev["bs"]["ar"] * 1.3:
            alerts.append("應收帳款異常增加")

        if bs["inventory"] > prev["bs"]["inventory"] * 1.3:
            alerts.append("存貨異常增加")

    if bs["liabilities"] > bs["equity"] * 2:
        alerts.append("高財務槓桿風險")

    return alerts


# =========================
# 舞弊風險
# =========================

def fraud(curr, prev=None):

    score = 0

    bs = curr["bs"]
    is_ = curr["is"]

    if prev and prev["bs"]["ar"] > 0:
        if bs["ar"] / prev["bs"]["ar"] > 1.2:
            score += 1

    if is_["revenue"] > 0:
        if (is_["gross_profit"] / is_["revenue"]) < 0.2:
            score += 1

    if curr["cf"]["ocf"] < curr["is"]["net_income"]:
        score += 1

    level = "High" if score >= 2 else "Medium" if score == 1 else "Low"

    return score, level


# =========================
# UI
# =========================

st.set_page_config(layout="wide")

st.title("四大會計師財報分析系統")

files = st.file_uploader("上傳財報PDF（可多檔）", type="pdf", accept_multiple_files=True)


# =========================
# 主流程
# =========================

if files:

    results = []
    prev = None

    for f in sorted(files, key=lambda x: x.name):

        data = parse_pdf(f)
        fin = financial(data)
        alerts = audit(data, prev)
        fscore, frisk = fraud(data, prev)

        results.append({
            "year": f.name,
            "cash": data["bs"]["cash"],
            "ar": data["bs"]["ar"],
            "inventory": data["bs"]["inventory"],
            "revenue": data["is"]["revenue"],
            "net_income": data["is"]["net_income"],
            "ROE": fin["roe"],
            "ROA": fin["roa"],
            "margin": fin["margin"],
            "OCF_ratio": fin["ocf_ratio"],
            "audit_flags": alerts,
            "fraud_score": fscore,
            "risk": frisk
        })

        prev = data

    df = pd.DataFrame(results)

    # =========================
    # 財務趨勢
    # =========================

    st.subheader("財務趨勢分析")

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
    # 查核結果
    # =========================

    st.subheader("查核發現")

    for r in results:
        st.write(r["year"])
        st.write(r["audit_flags"])
        st.write("Fraud Score:", r["fraud_score"], "Risk:", r["risk"])

    # =========================
    # 表格
    # =========================

    st.subheader("完整財務資料")

    st.dataframe(df)

else:
    st.info("請上傳財報PDF")
