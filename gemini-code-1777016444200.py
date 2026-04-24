
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io


# =====================================================
# 🏢 UI
# =====================================================

st.title("玄武會計師事務所")

st.subheader("審計及財務報表分析系統")


# =====================================================
# 🚀 進入系統
# =====================================================

if "enter" not in st.session_state:
    st.session_state.enter = False

if not st.session_state.enter:

    if st.button("進入系統"):
        st.session_state.enter = True

    st.stop()


# =====================================================
# 📊 假財報資料
# =====================================================

df = pd.DataFrame({
    "年度": ["2022", "2023", "2024"],
    "營收": [100, 120, 90],
    "獲利": [10, 15, -5],
    "資產": [200, 220, 210],
    "負債": [80, 100, 130]
})


# =====================================================
# 🧠 分析核心（全部整合）
# =====================================================

def analyze(df):

    risk = []

    # 財報不實
    if df["獲利"].iloc[-1] < 0:
        risk.append("財報不實風險（虧損異常）")

    # 掏空（負債上升）
    if df["負債"].iloc[-1] > df["負債"].iloc[0]:
        risk.append("掏空風險（資金異常流出）")

    # 幣安（資金異常交易概念）
    if df["營收"].iloc[-1] < df["營收"].iloc[0]:
        risk.append("交易異常風險（類幣安資金波動）")

    # 舞弊
    risk.append("舞弊風險（內控缺失可能）")

    return risk


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
# 📄 PDF 產生（含頁碼概念）
# =====================================================

def generate_pdf(df, risk):

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()
    content = []

    content.append(Paragraph("第1頁：財務分析報告", styles["Title"]))
    content.append(Spacer(1, 12))

    content.append(Paragraph(str(df.to_string()), styles["Normal"]))

    content.append(Spacer(1, 12))
    content.append(Paragraph("第2頁：風險分析", styles["Title"]))

    for r in risk:
        content.append(Paragraph(r, styles["Normal"]))

    doc.build(content)

    buffer.seek(0)
    return buffer


# =====================================================
# 📊 Excel 輸出
# =====================================================

def generate_excel(df, risk):

    buffer = io.BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:

        df.to_excel(writer, sheet_name="財報")
        pd.DataFrame(risk, columns=["風險"]).to_excel(writer, sheet_name="風險")

    buffer.seek(0)

    return buffer


# =====================================================
# 🚀 主畫面（結果頁）
# =====================================================

risk = analyze(df)


st.subheader("📊 財務分析")
st.write(df)

st.subheader("⚠️ 風險分析")
st.write(risk)

st.subheader("📈 圖表")
st.pyplot(chart(df))


# =====================================================
# 📦 下載區
# =====================================================

st.download_button(
    "下載 PDF 報告",
    generate_pdf(df, risk),
    file_name="audit_report.pdf"
)

st.download_button(
    "下載 Excel 報告",
    generate_excel(df, risk),
    file_name="audit_report.xlsx"
)
