import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from docx import Document
import io
from datetime import datetime

# --- 1. 設定頁面 ---
st.set_page_config(page_title="財報舞弊預警系統", layout="wide")
st.title(" 財報舞弊預警與鑑識分析系統")

# --- 2. 上傳 Excel ---
uploaded_file = st.file_uploader("📂 上傳財報Excel", type=["xlsx"])

# --- 3. 核心分析 ---
def calculate_scores(df):
    # M-Score
    df["DSRI"] = df["應收帳款"] / df["營收"]
    df["GMI"] = df["毛利率"].shift(1) / df["毛利率"]
    df["M-Score"] = -4.84 + 0.92 * df["DSRI"] + 0.528 * df["GMI"]

    # Z-Score
    df["Z-Score"] = (
        1.2 * (df["營業現金流"] / df["總資產"]) +
        1.4 * (df["營收"] / df["總資產"]) +
        3.3 * (df["營收"] / df["流動負債"])
    )
    return df

# --- 4. 鑑定邏輯 ---
def analyze(df):
    results = []
    for i in range(len(df)):
        row = df.iloc[i]
        warnings = []

        if row["M-Score"] > -1.78:
            warnings.append(" 疑似盈餘操縱（M-score 異常）")

        if row["Z-Score"] < 1.81:
            warnings.append(" 財務危機風險（Z-score 過低）")

        if row["營業現金流"] < 0:
            warnings.append(" 現金流異常（可能虛增獲利）")

        results.append({
            "年度": row["年度"],
            "警訊": warnings if warnings else [" 正常"]
        })
    return results

# --- 5. Word 報告 ---
def create_doc(df, results):
    doc = Document()
    doc.add_heading("財報鑑識分析報告", 0)

    doc.add_paragraph(f"報告時間：{datetime.now().strftime('%Y/%m/%d')}")
    doc.add_paragraph("本報告依據財務比率分析與舞弊偵測模型編製")

    for r in results:
        doc.add_heading(f"{r['年度']} 年度", level=2)
        for w in r["警訊"]:
            doc.add_paragraph(w)

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- 6. 主流程 ---
if uploaded_file:
    df = pd.read_excel(uploaded_file)

    st.subheader(" 原始資料")
    st.dataframe(df)

    df = calculate_scores(df)

    st.subheader(" 計算結果")
    st.dataframe(df)

    results = analyze(df)

    # --- 圖表 ---
    st.subheader(" 趨勢圖")
    fig, ax = plt.subplots()

    sns.lineplot(data=df, x="年度", y="M-Score", marker="o", label="M-Score")
    sns.lineplot(data=df, x="年度", y="Z-Score", marker="s", label="Z-Score")

    plt.axhline(y=-1.78, linestyle='--')
    plt.axhline(y=1.81, linestyle='--')

    st.pyplot(fig)

    # --- 預警 ---
    st.subheader("鑑定結果")
    for r in results:
        with st.expander(f"{r['年度']} 年度"):
            for w in r["警訊"]:
                st.write(w)

    # --- 下載報告 ---
    doc_file = create_doc(df, results)
    st.download_button(
        "📥 下載鑑識報告",
        data=doc_file,
        file_name="財報分析報告.docx"
    )

else:
    st.info("請上傳 Excel 檔案（需包含：年度、營收、應收帳款、毛利率、總資產、流動負債、營業現金流）")
