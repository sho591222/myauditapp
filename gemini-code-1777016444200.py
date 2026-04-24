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
# UI（完全保留你原本風格）
# =========================

st.set_page_config(layout="wide")
st.title("玄武會計師事務所｜財報分析與查核系統 v22")


# =========================
# MODE SELECT
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

url = st.text_input("或輸入PDF網址（選用）")


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
# FINANCIAL CORE
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
# CHART（直接畫在頁面）
# =========================

def draw_chart(df):

    fig, ax = plt.subplots()

    ax.plot(df["year"], df["revenue"], marker="o", label="營收")
    ax.plot(df["year"], df["profit"], marker="o", label="淨利")

    ax.set_title("財務趨勢分析")
    ax.legend()

    st.pyplot(fig)


# =========================
# COMPANY MODE
# =========================

def company_analysis(m, l):

    r = []

    if m < 0.2:
        r.append("獲利能力偏低")

    if l > 0.6:
        r.append("財務槓桿偏高")

    if m > 0.3:
        r.append("獲利能力穩定")

    return r


# =========================
# AUDIT MODE
# =========================

def audit_analysis():

    return [
        "應收帳款 → 函證程序",
        "營收 → cut-off test",
        "存貨 → 實地盤點",
        "負債 → completeness test",
        "收入 → ISA 240 舞弊風險"
    ]


# =========================
# ADVANCED MODULES（你全部要的）
# =========================

def stock_analysis(rev, profit, assets):

    r = []

    if assets > rev * 2:
        r.append("資產效率異常（股譜結構疑慮）")

    if profit / assets < 0.05:
        r.append("ROA偏低（資本效率差）")

    return r


def fraud_analysis(rev, profit, assets, liab):

    r = []

    if profit < 0 and assets > 0:
        r.append("資產增加但持續虧損（潛在資金異常）")

    if liab > assets * 0.8:
        r.append("高負債風險")

    if rev > 0 and profit / rev < 0.05:
        r.append("營收高但利潤偏低（可能成本異常）")

    return r


def earnings_quality(rev, profit, assets):

    r = []

    if profit > rev * 0.3:
        r.append("利潤異常偏高（需驗證收入）")

    if assets > rev * 3:
        r.append("資產過重（可能減損風險）")

    return r


# =========================
# DATA COLLECT
# =========================

data = []


if files:

    for f in files:

        text = parse_pdf(f)

        data.append({
            "year": f.name.replace(".pdf", ""),
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
# MAIN OUTPUT（全部整合在同一頁）
# =========================

if data:

    df = pd.DataFrame(data)

    st.subheader("財務資料")
    st.dataframe(df)


    # ratio
    df["margin"], df["leverage"] = zip(*df.apply(
        lambda x: ratio(x["revenue"], x["profit"], x["assets"], x["liabilities"]),
        axis=1
    ))


    # =========================
    #  圖表（你要求的）
    # =========================

    st.subheader("財務趨勢圖表")
    draw_chart(df)


    # =========================
    #  財務報表（直接顯示在頁面）
    # =========================

    st.subheader("財務報表分析")

    for i in range(len(df)):

        isd, bsd, cf = financial_statements(
            df.loc[i, "revenue"],
            df.loc[i, "profit"],
            df.loc[i, "assets"],
            df.loc[i, "liabilities"]
        )

        st.write(df.loc[i, "year"])
        st.write("損益表", isd)
        st.write("資產負債表", bsd)
        st.write("現金流（概算）", cf)


    # =========================
    #  分析建議（你要的語言）
    # =========================

    st.subheader("分析建議")

    for i in range(len(df)):

        m = df.loc[i, "margin"]
        l = df.loc[i, "leverage"]

        if mode == "公司內部分析":
            for r in company_analysis(m, l):
                st.write(r)
        else:
            for r in audit_analysis():
                st.write(r)


    # =========================
    #  股譜分析（直接顯示）
    # =========================

    st.subheader("股譜分析")

    for r in stock_analysis(
        df["revenue"].mean(),
        df["profit"].mean(),
        df["assets"].mean()
    ):
        st.write(r)


    # =========================
    #  掏空分析（直接顯示）
    # =========================

    st.subheader("掏空風險分析")

    for r in fraud_analysis(
        df["revenue"].mean(),
        df["profit"].mean(),
        df["assets"].mean(),
        df["liabilities"].mean()
    ):
        st.write(r)


    # =========================
    # 🧠 財報品質分析
    # =========================

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

        doc.add_heading("玄武會計師事務所｜完整財報查核報告", 0)

        doc.add_paragraph("模式：" + mode)

        doc.add_paragraph(df.to_string())

        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        st.download_button(
            "下載報告",
            buffer,
            file_name="v22_final_report.docx"
        )
