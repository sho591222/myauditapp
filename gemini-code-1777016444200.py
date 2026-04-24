import streamlit as st
import pandas as pd
import pdfplumber
import re
from docx import Document
import io
from datetime import datetime

st.set_page_config(page_title="財報鑑識系統", layout="wide")
st.title("📂 PDF 財報上傳與鑑識報告系統")

uploaded_files = st.file_uploader(
    "上傳財報PDF（可多檔）",
    type=["pdf"],
    accept_multiple_files=True
)

# --- 1. 抓文字 ---
def extract_text(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

# --- 2. 抓財報數據 ---
def extract_data(text):
    patterns = {
        "營收": r"營業收入[\s:：]*([\d,]+)",
        "應收帳款": r"應收帳款[\s:：]*([\d,]+)",
        "總資產": r"資產總計[\s:：]*([\d,]+)",
        "流動負債": r"流動負債[\s:：]*([\d,]+)",
        "營業現金流": r"營業活動之淨現金流入[\s:：]*([\d,]+)"
    }

    data = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        data[key] = float(match.group(1).replace(",", "")) if match else None

    return data

# --- 3. 計算 ---
def calculate(df):
    df["DSRI"] = df["應收帳款"] / df["營收"]
    df["M-Score"] = -4.84 + 0.92 * df["DSRI"]

    df["Z-Score"] = (
        1.2 * (df["營業現金流"] / df["總資產"]) +
        1.4 * (df["營收"] / df["總資產"]) +
        3.3 * (df["營收"] / df["流動負債"])
    )
    return df

# --- 4. 判斷 ---
def analyze(row):
    warnings = []

    if row["M-Score"] > -1.78:
        warnings.append("疑似財報不實")

    if row["Z-Score"] < 1.81:
        warnings.append("可能倒閉風險")

    if row["營業現金流"] < 0:
        warnings.append("現金流異常")

    return "；".join(warnings) if warnings else "正常"

# --- 5. Word 報告 ---
def create_doc(df):
    doc = Document()
    doc.add_heading("財報鑑識分析報告", 0)

    doc.add_paragraph(f"報告日期：{datetime.now().strftime('%Y/%m/%d')}")
    doc.add_paragraph("本報告依據財務數據與舞弊模型分析產出")

    table = doc.add_table(rows=1, cols=len(df.columns))
    for i, col in enumerate(df.columns):
        table.rows[0].cells[i].text = col

    for _, row in df.iterrows():
        cells = table.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = str(val)

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- 主流程 ---
if uploaded_files:
    all_data = []

    for file in uploaded_files:
        text = extract_text(file)
        data = extract_data(text)

        year = re.findall(r"\d{4}", file.name)
        data["年度"] = year[0] if year else file.name

        all_data.append(data)

    df = pd.DataFrame(all_data)
    df = df.dropna()

    if not df.empty:
        df = calculate(df)
        df["分析結果"] = df.apply(analyze, axis=1)

        st.success("✅ 分析完成，可下載報告")

        doc_file = create_doc(df)
        st.download_button(
            "📥 下載 Word 鑑識報告",
            data=doc_file,
            file_name="財報鑑識報告.docx"
        )

    else:
        st.error("❌ 無法解析PDF（格式不支援）")

else:
    st.info("請上傳財報PDF")
