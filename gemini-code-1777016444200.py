import streamlit as st
import pandas as pd
import pdfplumber
import re
import matplotlib.pyplot as plt
from docx import Document
import io
import matplotlib.font_manager as fm
import os
import requests

# =========================
# 字體（保留你原本做法）
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
# UI（完全保留你原本風格）
# =========================

st.set_page_config(layout="wide")

st.title("專業鑑識會計鑑定系統：四大查核升級版")

with st.sidebar:
    st.header("鑑定專案資訊")
    co_name = st.text_input("受調查公司名稱", "XX股份有限公司")
    auditor = st.text_input("主辦會計師", "陳會計師")
    firm = st.text_input("會計師事務所", "四大會計師事務所")

    st.divider()
    files = st.file_uploader("上傳年度財報 PDF", type=["pdf"], accept_multiple_files=True)


# =========================
# PDF 解析
# =========================

def extract(text, key):
    m = re.search(rf"{key}\s*([\d,]+)", text)
    return float(m.group(1).replace(",", "")) if m else 0


def parse_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for p in pdf.pages:
            text += p.extract_text() or ""

    return {
        "cash": extract(text, "現金"),
        "ar": extract(text, "應收帳款"),
        "inventory": extract(text, "存貨"),
        "revenue": extract(text, "營業收入"),
        "net_income": extract(text, "本期淨利"),
    }


# =========================
# 財務分析（DuPont）
# =========================

def financial_engine(d):
    revenue = d["revenue"]
    ni = d["net_income"]

    assets = d["cash"] + d["ar"] + d["inventory"]
    equity = assets * 0.6 if assets else 1

    roe = (ni / revenue) * (revenue / assets) * (assets / equity) if revenue else 0

    return {
        "ROE": roe,
        "margin": ni / revenue if revenue else 0,
        "turnover": revenue / assets if assets else 0
    }


# =========================
# 查核引擎（四大核心）
# =========================

def forensic(curr, prev):
    flags = []

    if prev:
        if curr["ar"] > prev["ar"] * 1.3:
            flags.append("應收帳款異常增加（收入可能提前認列）")

        if curr["inventory"] > prev["inventory"] * 1.3:
            flags.append("存貨異常增加（可能滯銷或資產虛增）")

        if curr["cash"] < curr["net_income"]:
            flags.append("現金流弱於盈餘（盈餘品質疑慮）")

    if not flags:
        flags.append("未偵測重大異常")

    return flags


# =========================
# Word 報告
# =========================

def build_report(company, df, insights):

    doc = Document()
    doc.add_heading("鑑識會計查核報告", 0)

    doc.add_paragraph(f"公司：{company}")
    doc.add_paragraph(f"事務所：{firm}")
    doc.add_paragraph(f"會計師：{auditor}")

    doc.add_heading("分析結果", level=1)

    for _, r in df.iterrows():
        doc.add_paragraph(f"{r['year']} | ROE:{r['roe']:.2f} | {r['flags']}")

    doc.add_heading("查核發現", level=1)
    for i in insights:
        doc.add_paragraph(i)

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf


# =========================
# 主流程（UI 保留你的風格）
# =========================

if files:

    results = []
    prev = None
    insights = []

    for f in sorted(files, key=lambda x: x.name):

        raw = parse_pdf(f)

        fin = financial_engine(raw)
        flags = forensic(raw, prev)

        results.append({
            "year": f.name.replace(".pdf", ""),
            "roe": fin["ROE"],
            "cash": raw["cash"],
            "ar": raw["ar"],
            "inventory": raw["inventory"],
            "flags": ", ".join(flags)
        })

        insights.extend(flags)
        prev = raw

    df = pd.DataFrame(results)

 
    # =========================

    st.subheader(f"{co_name} 鑑定圖表分析")

    col1, col2 = st.columns(2)

    with col1:
        fig1, ax1 = plt.subplots()
        ax1.plot(df["year"], df["cash"], label="現金")
        ax1.plot(df["year"], df["ar"], label="應收帳款")
        ax1.plot(df["year"], df["inventory"], label="存貨")
        ax1.set_title("資產結構趨勢")
        ax1.legend()
        st.pyplot(fig1)

    with col2:
        fig2, ax2 = plt.subplots()
        ax2.plot(df["year"], df["roe"], marker="o", color="red")
        ax2.set_title("ROE 趨勢")
        st.pyplot(fig2)

    # =========================
    #  查核結果（新增）
    # =========================

    st.subheader("查核發現（Audit Findings）")

    for i in insights:
        st.write("•", i)

    # =========================
    #  dataframe（保留你習慣）
    # =========================

    st.subheader("詳細數據")
    st.dataframe(df)

    # =========================
    #  Word 報告
    # =========================

    report = build_report(co_name, df, insights)

    st.sidebar.download_button(
        "下載查核報告",
        report,
        file_name=f"{co_name}_audit_report.docx"
    )

else:
    st.info("請上傳財報 PDF 開始分析")
