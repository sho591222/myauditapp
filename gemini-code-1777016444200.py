import streamlit as st
import pandas as pd
import pdfplumber
import matplotlib.pyplot as plt
import requests
import io
import re
import datetime
from docx import Document


# =========================
# UI（保持你的原本風格）
# =========================

st.set_page_config(layout="wide")
st.title("玄武會計師事務所｜財報 + 查核智慧系統 v21")


# =========================
# MODE
# =========================

mode = st.selectbox(
    "使用模式",
    ["公司內部分析", "會計師事務所查核"]
)


# =========================
# INPUT
# =========================

files = st.file_uploader(
    "上傳財報 PDF（可多期）",
    type="pdf",
    accept_multiple_files=True
)

url = st.text_input("或輸入PDF網址")


# =========================
# PDF PARSER
# =========================

def parse_pdf(file):

    text = ""

    with pdfplumber.open(file) as pdf:
        for p in pdf.pages:
            text += p.extract_text() or ""

    return text


def extract(text, key):

    m = re.search(rf"{key}.*?([\d,]+)", text)

    if m:
        return float(m.group(1).replace(",", ""))

    return 0


def load_url(url):

    r = requests.get(url)
    return io.BytesIO(r.content)


# =========================
# CORE FINANCIAL ENGINE
# =========================

def ratio(rev, profit, assets, liab):

    margin = profit / rev if rev else 0
    leverage = liab / assets if assets else 0

    return margin, leverage


def financial_statements(rev, profit, assets, liab):

    return (
        {"營收": rev, "淨利": profit},
        {"資產": assets, "負債": liab, "權益": assets - liab},
        profit * 1.1
    )


# =========================
# CHART
# =========================

def chart(df):

    fig, ax = plt.subplots()

    ax.plot(df["year"], df["revenue"], label="營收")
    ax.plot(df["year"], df["profit"], label="淨利")

    ax.set_title("財務趨勢")
    ax.legend()

    st.pyplot(fig)


# =========================
# COMPANY MODE
# =========================

def company_analysis(margin, leverage):

    res = []

    if margin < 0.2:
        res.append("獲利能力偏弱")

    if leverage > 0.6:
        res.append("財務槓桿過高")

    return res


# =========================
# AUDIT MODE
# =========================

def audit_analysis(margin, leverage):

    return [
        "應收帳款 → 函證",
        "營收 → cut-off",
        "存貨 → 盤點",
        "負債 → completeness",
        "ISA 240 舞弊風險"
    ]


# =========================
# 🧠 ① 股譜分析
# =========================

def stock_structure_analysis(rev, profit, assets):

    r = []

    if assets > rev * 2:
        r.append("資產效率異常")

    if profit / assets < 0.05:
        r.append("ROA偏低")

    return r


# =========================
# 🧠 ② 掏空分析
# =========================

def fraud_analysis(rev, profit, assets, liab):

    r = []

    if profit < 0 and assets > 0:
        r.append("資產增加但持續虧損")

    if liab > assets * 0.8:
        r.append("高負債風險")

    if rev > 0 and profit / rev < 0.05:
        r.append("營收高但利潤偏低")

    return r


# =========================
# 🧠 ③ 財報品質分析
# =========================

def earnings_quality(rev, profit, assets):

    r = []

    if profit > rev * 0.3:
        r.append("利潤異常偏高")

    if assets > rev * 3:
        r.append("資產過重需減損測試")

    return r


# =========================
# DATA COLLECT
# =========================

data = []


if files:

    for f in files:

        text = parse_pdf(f)

        data.append({
            "year": f.name,
            "revenue": extract(text, "營業收入"),
            "profit": extract(text, "本期淨利"),
            "assets": extract(text, "資產總額"),
            "liabilities": extract(text, "負債總額")
        })


if url:

    file = load_url(url)
    text = parse_pdf(file)

    data.append({
        "year": "URL",
        "revenue": extract(text, "營業收入"),
        "profit": extract(text, "本期淨利"),
        "assets": extract(text, "資產總額"),
        "liabilities": extract(text, "負債總額")
    })


# =========================
# MAIN PROCESS
# =========================

if data:

    df = pd.DataFrame(data)

    st.subheader("財務資料")
    st.dataframe(df)

    df["margin"], df["leverage"] = zip(*df.apply(
        lambda x: ratio(x["revenue"], x["profit"], x["assets"], x["liabilities"]),
        axis=1
    ))


    # CHART
    chart(df)


    # FINANCIAL STATEMENTS
    st.subheader("財務報表分析")

    for i in range(len(df)):

        isd, bsd, cf = financial_statements(
            df.loc[i, "revenue"],
            df.loc[i, "profit"],
            df.loc[i, "assets"],
            df.loc[i, "liabilities"]
        )

        st.write(df.loc[i, "year"])
        st.write("IS", isd)
        st.write("BS", bsd)
        st.write("CF", cf)


    # =========================
    # MODE OUTPUT
    # =========================

    st.subheader("分析建議")

    for i in range(len(df)):

        m = df.loc[i, "margin"]
        l = df.loc[i, "leverage"]

        if mode == "公司內部分析":
            st.write(company_analysis(m, l))
        else:
            st.write(audit_analysis(m, l))


    # =========================
    # ADVANCED MODULES (你要的全部)
    # =========================

    st.subheader("股譜分析")

    for r in stock_structure_analysis(
        df["revenue"].mean(),
        df["profit"].mean(),
        df["assets"].mean()
    ):
        st.write(r)


    st.subheader("掏空分析")

    for r in fraud_analysis(
        df["revenue"].mean(),
        df["profit"].mean(),
        df["assets"].mean(),
        df["liabilities"].mean()
    ):
        st.write(r)


    st.subheader("財報品質分析")

    for r in earnings_quality(
        df["revenue"].mean(),
        df["profit"].mean(),
        df["assets"].mean()
    ):
        st.write(r)


    # =========================
    # WORD REPORT
    # =========================

    if st.button("產出完整報告"):

        doc = Document()

        doc.add_heading("玄武會計師事務所｜完整財報與查核報告 v21", 0)

        doc.add_paragraph("模式：" + mode)

        doc.add_paragraph(df.to_string())

        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        st.download_button(
            "下載報告",
            buffer,
            file_name="v21_full_report.docx"
        )
