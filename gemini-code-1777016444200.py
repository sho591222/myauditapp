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

# --- 字體 ---
@st.cache_resource
def load_chinese_font():
    font_url = "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/TraditionalChinese/NotoSansCJKtc-Regular.otf"
    font_path = "NotoSansCJKtc-Regular.otf"

    if not os.path.exists(font_path):
        try:
            response = requests.get(font_url)
            with open(font_path, "wb") as f:
                f.write(response.content)
        except:
            return None
    return font_path

font_p = load_chinese_font()

def apply_font_logic(font_path):
    if font_path:
        custom_font = fm.FontProperties(fname=font_path)
        plt.rcParams['font.family'] = custom_font.get_name()
        fm.fontManager.addfont(font_path)
        plt.rcParams['axes.unicode_minus'] = False
        return custom_font
    return None

font_prop = apply_font_logic(font_p)

st.set_page_config(layout="wide")
st.title("專業鑑識會計鑑定系統（升級版分析引擎）")

# --- sidebar ---
with st.sidebar:
    st.header("鑑定資訊")
    co_name = st.text_input("公司名稱", "XX股份有限公司")
    auditor = st.text_input("會計師", "陳會計師")
    firm = st.text_input("事務所", "誠信聯合會計師事務所")

    files = st.file_uploader("上傳財報 PDF", type=["pdf"], accept_multiple_files=True)

# =========================
#  核心財務分析引擎
# =========================

def financial_engine(sales, net_income, assets, equity, cfo, capex):
    net_margin = net_income / sales if sales else 0
    asset_turnover = sales / assets if assets else 0
    equity_multiplier = assets / equity if equity else 0
    roe = net_margin * asset_turnover * equity_multiplier

    fcf = cfo - capex
    cfo_ni = cfo / net_income if net_income else 0

    return {
        "ROE": roe,
        "Net Margin": net_margin,
        "Asset Turnover": asset_turnover,
        "Equity Multiplier": equity_multiplier,
        "FCF": fcf,
        "CFO/NI": cfo_ni
    }


def red_flag_detector(cfo, net_income, ar_ratio, inv_ratio):
    flags = []

    if cfo < net_income:
        flags.append("現金流低於淨利（盈餘品質偏弱）")

    if ar_ratio > 0.3:
        flags.append("應收帳款偏高（可能虛增營收）")

    if inv_ratio > 0.3:
        flags.append("存貨異常增加")

    if not flags:
        flags.append("無重大財務異常")

    return flags


# =========================
#  舊鑑識模型（保留）
# =========================

def forensic_model(i, sales, rec):
    m = -2.0 + (i * 0.38)
    z = 3.5 - (i * 0.95)

    status = "穩定營運"
    if m > -1.78:
        status = "財報不實風險"
    elif rec > sales * 0.45:
        status = "資金異常流動"
    elif z < 1.8:
        status = "倒閉風險"

    return m, z, status


# =========================
# 主流程
# =========================

if files:

    results = []

    for i, f in enumerate(sorted(files, key=lambda x: x.name)):

        # 模擬財報（之後可換 PDF parser）
        sales = 3000 + (i * 180)
        ar = 200 + (i * 1550)

        net_income = sales * 0.1
        assets = sales * 2
        equity = assets * 0.6
        cfo = net_income * 0.8
        capex = net_income * 0.3

        engine = financial_engine(sales, net_income, assets, equity, cfo, capex)

        m, z, res = forensic_model(i, sales, ar)

        ar_ratio = ar / sales
        inv_ratio = 0.2 + (i * 0.02)

        flags = red_flag_detector(cfo, net_income, ar_ratio, inv_ratio)

        results.append({
            "年度": f.name.replace(".pdf", ""),
            "營收": sales,
            "應收": ar,
            "ROE": engine["ROE"],
            "CFO/NI": engine["CFO/NI"],
            "FCF": engine["FCF"],
            "M": m,
            "Z": z,
            "結論": res,
            "風險": ", ".join(flags)
        })

    df = pd.DataFrame(results)

    # =========================
    #  圖表區
    # =========================

    st.subheader(f"{co_name} 財務鑑識分析")

    col1, col2 = st.columns(2)

    with col1:
        fig1, ax1 = plt.subplots()
        ax1.plot(df["年度"], df["營收"], marker="o", label="營收")
        ax1.plot(df["年度"], df["應收"], marker="x", label="應收")
        ax1.set_title("收入與應收趨勢", fontproperties=font_prop)
        ax1.legend(prop=font_prop)
        st.pyplot(fig1)

    with col2:
        fig2, ax2 = plt.subplots()
        ax2.plot(df["年度"], df["M"], label="M score", marker="D")
        ax2.plot(df["年度"], df["Z"], label="Z score", marker="s")
        ax2.axhline(-1.78, linestyle="--")
        ax2.set_title("舞弊 / 倒閉風險", fontproperties=font_prop)
        ax2.legend(prop=font_prop)
        st.pyplot(fig2)

    # =========================
    # Insight Layer
    # =========================

    st.subheader("財務分析洞察")

    latest = df.iloc[-1]
    insights = []

    if latest["ROE"] < 0.1:
        insights.append("ROE 偏低，資產運用效率不足")

    if latest["CFO/NI"] < 1:
        insights.append("盈餘品質偏弱（現金轉換不足）")

    if "財報不實" in latest["結論"]:
        insights.append("模型偵測潛在財報異常風險")

    if not insights:
        insights.append("財務結構整體穩定")

    for i in insights:
        st.write("•", i)

    # =========================
    # 📄 Word 報告
    # =========================

    doc = Document()
    doc.add_heading("鑑識會計分析報告", 0)

    doc.add_paragraph(f"公司：{co_name}")
    doc.add_paragraph(f"會計師：{auditor}")
    doc.add_paragraph(f"事務所：{firm}")

    doc.add_heading("分析結果", level=1)

    for _, r in df.iterrows():
        doc.add_heading(f"{r['年度']} - {r['結論']}", level=2)
        doc.add_paragraph(f"風險：{r['風險']}")

    doc.add_heading("財務洞察", level=1)
    for i in insights:
        doc.add_paragraph(i)

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)

    st.sidebar.download_button(
        "下載鑑識報告",
        buf,
        file_name=f"{co_name}_鑑識報告.docx"
    )

else:
    st.info("請上傳財報 PDF 開始分析")
