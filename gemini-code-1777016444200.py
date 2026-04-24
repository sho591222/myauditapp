import streamlit as st
import pandas as pd
import pdfplumber
import re
import matplotlib.pyplot as plt
from docx import Document
import io
import os
import requests
import matplotlib.font_manager as fm

# =========================
# 字體處理
# =========================

@st.cache_resource
def load_chinese_font():
    font_url = "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/TraditionalChinese/NotoSansCJKtc-Regular.otf"
    font_path = "NotoSansCJKtc-Regular.otf"

    if not os.path.exists(font_path):
        try:
            r = requests.get(font_url)
            with open(font_path, "wb") as f:
                f.write(r.content)
        except:
            return None
    return font_path


font_path = load_chinese_font()

if font_path:
    custom_font = fm.FontProperties(fname=font_path)
    plt.rcParams["font.family"] = custom_font.get_name()
    fm.fontManager.addfont(font_path)
    plt.rcParams["axes.unicode_minus"] = False


# =========================
# PDF 財報解析
# =========================

def extract_number(text, keyword):
    pattern = rf"{keyword}\s*([\d,]+)"
    match = re.search(pattern, text)
    if match:
        return float(match.group(1).replace(",", ""))
    return 0


def parse_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for p in pdf.pages:
            text += p.extract_text() or ""

    return {
        "cash": extract_number(text, "現金"),
        "ar": extract_number(text, "應收帳款"),
        "inventory": extract_number(text, "存貨"),
        "revenue": extract_number(text, "營業收入"),
        "net_income": extract_number(text, "本期淨利")
    }


# =========================
# 科目標準化
# =========================

def normalize(data):
    return {
        "cash": data["cash"],
        "ar": data["ar"],
        "inventory": data["inventory"],
        "revenue": data["revenue"],
        "net_income": data["net_income"]
    }


# =========================
# 財務分析引擎（DuPont）
# =========================

def financial_engine(d):
    revenue = d["revenue"]
    ni = d["net_income"]

    assets = d["cash"] + d["ar"] + d["inventory"]
    equity = assets * 0.6 if assets else 1

    roe = (ni / revenue) * (revenue / assets) * (assets / equity) if revenue else 0

    return {
        "ROE": roe,
        "Net Margin": ni / revenue if revenue else 0,
        "Asset Turnover": revenue / assets if assets else 0
    }


# =========================
# 查核異常偵測（四大核心）
# =========================

def forensic_engine(curr, prev):

    flags = []

    if prev:
        if curr["ar"] > prev["ar"] * 1.3:
            flags.append("應收帳款異常增加（可能提前認列收入）")

        if curr["inventory"] > prev["inventory"] * 1.3:
            flags.append("存貨異常增加（可能滯銷或虛增資產）")

        if curr["cash"] < curr["net_income"]:
            flags.append("現金流弱於盈餘（盈餘品質疑慮）")

    if not flags:
        flags.append("未偵測重大查核異常")

    return flags


# =========================
# Word 報告
# =========================

def generate_report(company, results, insights):

    doc = Document()
    doc.add_heading("Audit Analytics Report", 0)

    doc.add_paragraph(f"Company: {company}")

    doc.add_heading("Financial & Audit Summary", level=1)

    for r in results:
        doc.add_paragraph(
            f"{r['year']} | ROE: {r['roe']:.2f} | Flags: {r['flags']}"
        )

    doc.add_heading("Key Audit Findings", level=1)

    for i in insights:
        doc.add_paragraph(i)

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf


# =========================
# UI
# =========================

st.title("四大會計師事務所查核分析系統（Audit Analytics System）")

company = st.text_input("公司名稱", "XX股份有限公司")
files = st.file_uploader("上傳財報 PDF", type=["pdf"], accept_multiple_files=True)


# =========================
# 主流程
# =========================

if files:

    results = []
    prev = None
    insights = []

    for f in sorted(files, key=lambda x: x.name):

        raw = parse_pdf(f)
        data = normalize(raw)

        fin = financial_engine(data)

        flags = forensic_engine(data, prev)

        roe = fin["ROE"]

        results.append({
            "year": f.name,
            "roe": roe,
            "flags": ", ".join(flags)
        })

        insights.extend(flags)
        prev = data

    df = pd.DataFrame(results)

    # =========================
    # Dashboard
    # =========================

    st.subheader("財務查核分析結果")
    st.dataframe(df)

    # ROE trend
    st.subheader("ROE 趨勢")

    fig, ax = plt.subplots()
    ax.plot(df["year"], df["roe"], marker="o")
    ax.set_title("ROE Trend")
    st.pyplot(fig)

    # =========================
    # 查核發現
    # =========================

    st.subheader("查核發現")

    for i in insights:
        st.write("•", i)

    # =========================
    # 報告下載
    # =========================

    report = generate_report(company, results, insights)

    st.download_button(
        "下載查核報告 (Word)",
        report,
        file_name=f"{company}_audit_report.docx"
    )

else:
    st.info("請上傳財報 PDF 開始分析")
