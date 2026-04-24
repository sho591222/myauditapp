
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pdfplumber
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io


# =====================================================
# 🏢 UI
# =====================================================

st.title("玄武會計師事務所")
st.subheader("審計及財務報表分析系統")


# =====================================================
# 🚪 進入系統（單按鈕）
# =====================================================

if "enter" not in st.session_state:
    st.session_state.enter = False

if not st.session_state.enter:

    if st.button("進入系統"):
        st.session_state.enter = True

    st.stop()


# =====================================================
# 👥 使用者類型
# =====================================================

role = st.selectbox(
    "選擇使用者類型",
    ["公司使用者", "會計師事務所"]
)


# =====================================================
# 📂 PDF 上傳（可多選）
# =====================================================

files = st.file_uploader(
    "上傳財務報表 PDF",
    type=["pdf"],
    accept_multiple_files=True
)


# =====================================================
# 📊 模擬財報
# =====================================================

df = pd.DataFrame({
    "年度": ["2022", "2023", "2024"],
    "營收": [100, 120, 90],
    "獲利": [10, 15, -5],
    "資產": [200, 220, 210],
    "負債": [80, 100, 130]
})


# =====================================================
# 🧠 分析核心
# =====================================================

def analyze(df, role):

    result = {
        "財報分析": [
            "資產負債表",
            "損益表",
            "現金流量表"
        ],
        "異常點": [],
        "建議": [],
        "查核科目": [],
        "風險": []
    }


    # =========================
    # 異常分析（公司）
    # =========================

    if df["獲利"].iloc[-1] < 0:
        result["異常點"].append("獲利異常（虧損）")

    if df["負債"].iloc[-1] > df["負債"].iloc[0]:
        result["異常點"].append("負債增加異常")


    # =========================
    # 風險
    # =========================

    result["風險"] = [
        "財報不實風險",
        "掏空風險",
        "舞弊風險",
        "資金異常流動"
    ]


    # =========================
    # 會計師專屬
    # =========================

    if role == "會計師事務所":

        result["查核科目"] = [
            "應收帳款",
            "存貨",
            "收入認列",
            "關係人交易",
            "現金及約當現金"
        ]

        result["建議"] = [
            "執行函證程序",
            "存貨盤點",
            "收入切割測試",
            "關係人交易查核",
            "內控制度測試"
        ]


    else:

        result["建議"] = [
            "改善財務結構",
            "降低負債比",
            "強化內控"
        ]


    return result


# =====================================================
# 📊 圖表
# =====================================================

def chart(df):

    fig, ax = plt.subplots()

    ax.plot(df["年度"], df["營收"], label="營收")
    ax.plot(df["年度"], df["獲利"], label="獲利")

    ax.legend()

    return fig


# =====================================================
# 📄 PDF 報告（自動生成）
# =====================================================

def generate_pdf(df, result, role):

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()
    content = []

    content.append(Paragraph("財務分析報告", styles["Title"]))
    content.append(Spacer(1, 12))

    content.append(Paragraph(str(df.to_string()), styles["Normal"]))
    content.append(Spacer(1, 12))

    content.append(Paragraph("異常點", styles["Heading2"]))
    for i in result["異常點"]:
        content.append(Paragraph(i, styles["Normal"]))

    content.append(Spacer(1, 12))

    content.append(Paragraph("風險分析", styles["Heading2"]))
    for i in result["風險"]:
        content.append(Paragraph(i, styles["Normal"]))

    content.append(Spacer(1, 12))

    if role == "會計師事務所":

        content.append(Paragraph("查核科目", styles["Heading2"]))
        for i in result["查核科目"]:
            content.append(Paragraph(i, styles["Normal"]))

        content.append(Paragraph("查核建議", styles["Heading2"]))
        for i in result["建議"]:
            content.append(Paragraph(i, styles["Normal"]))

    else:

        content.append(Paragraph("改善建議", styles["Heading2"]))
        for i in result["建議"]:
            content.append(Paragraph(i, styles["Normal"]))

    doc.build(content)

    buffer.seek(0)

    return buffer


# =====================================================
# 🚀 主畫面（結果頁）
# =====================================================

if files:

    result = analyze(df, role)

    st.subheader(" 財報分析")
    st.write(result["財報分析"])

    st.subheader(" 異常點")
    st.write(result["異常點"])

    st.subheader(" 風險分析")
    st.write(result["風險"])

    st.subheader(" 建議")
    st.write(result["建議"])

    if role == "會計師事務所":
        st.subheader(" 查核科目")
        st.write(result["查核科目"])

    st.subheader(" 圖表")
    st.pyplot(chart(df))

    st.download_button(
        "下載 PDF 報告",
        generate_pdf(df, result, role),
        file_name="audit_report.pdf"
    )
