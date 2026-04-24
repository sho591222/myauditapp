import streamlit as st
import pandas as pd
import pdfplumber
import camelot
import pytesseract
from PIL import Image
import re
from docx import Document
import io
from datetime import datetime

st.set_page_config(page_title="整合財報解析系統", layout="wide")
st.title("📊 PDF + OCR + 表格 財報整合分析系統")

uploaded_files = st.file_uploader(
    "上傳財報PDF（可多檔）",
    type=["pdf"],
    accept_multiple_files=True
)

# =========================
# 1️⃣ PDF 文字解析
# =========================
def extract_text_pdfplumber(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

# =========================
# 2️⃣ 表格解析（Camelot）
# =========================
def extract_tables(file_path):
    try:
        tables = camelot.read_pdf(file_path, pages="all")
        if tables:
            return tables[0].df
    except:
        pass
    return None

# =========================
# 3️⃣ OCR（掃描PDF）
# =========================
def extract_text_ocr(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            img = page.to_image(resolution=300).original
            text += pytesseract.image_to_string(img, lang="chi_tra")
    return text

# =========================
# 4️⃣ 多層解析（核心）
# =========================
def smart_extract(file):
    file.seek(0)

    # ① 先文字
    text = extract_text_pdfplumber(file)

    if len(text.strip()) > 50:
        return text

    # ② 表格 fallback
    file.seek(0)
    tables = extract_tables(file.name)
    if tables is not None:
        return tables.to_string()

    # ③ OCR fallback
    file.seek(0)
    text = extract_text_ocr(file)
    return text

# =========================
# 5️⃣ 抓財務數據
# =========================
def extract_financial(text):
    patterns = {
        "營收": r"營業收入[\s:：]*([\d,]+)",
        "應收帳款": r"應收帳款[\s:：]*([\d,]+)",
        "總資產": r"資產總計[\s:：]*([\d,]+)",
        "流動負債": r"流動負債[\s:：]*([\d,]+)",
        "營業現金流": r"營業活動.*?([\d,]+)"
    }

    data = {}
    for k, p in patterns.items():
        m = re.search(p, text)
        data[k] = float(m.group(1).replace(",", "")) if m else None

    return data

# =========================
# 6️⃣ 模型
# =========================
def calculate(df):
    df["DSRI"] = df["應收帳款"] / df["營收"]
    df["M-Score"] = -4.84 + 0.92 * df["DSRI"]

    df["Z-Score"] = (
        1.2 * (df["營業現金流"] / df["總資產"]) +
        1.4 * (df["營收"] / df["總資產"]) +
        3.3 * (df["營收"] / df["流動負債"])
    )
    return df

# =========================
# 7️⃣ Word 報告
# =========================
def create_report(df):
    doc = Document()
    doc.add_heading("財報整合分析報告", 0)

    doc.add_paragraph(f"生成時間：{datetime.now()}")

    table = doc.add_table(rows=1, cols=len(df.columns))
    for i, c in enumerate(df.columns):
        table.rows[0].cells[i].text = c

    for _, r in df.iterrows():
        row_cells = table.add_row().cells
        for i, v in enumerate(r):
            row_cells[i].text = str(v)

    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# =========================
# 主流程
# =========================
if uploaded_files:

    all_data = []

    for file in uploaded_files:
        st.write(f"📄 處理：{file.name}")

        text = smart_extract(file)
        data = extract_financial(text)

        year = re.findall(r"\d{4}", file.name)
        data["年度"] = year[0] if year else file.name

        all_data.append(data)

    df = pd.DataFrame(all_data)

    st.subheader("📊 擷取結果")
    st.dataframe(df)

    df = df.dropna()

    if not df.empty:
        df = calculate(df)

        st.subheader("📈 分析結果")
        st.dataframe(df)

        # 判斷
        st.subheader("🚨 預警")
        for _, r in df.iterrows():
            st.write(f"📅 {r['年度']}")
            if r["M-Score"] > -1.78:
                st.error("疑似財報操縱")
            if r["Z-Score"] < 1.81:
                st.warning("財務風險偏高")

        # Word
        report = create_report(df)

        st.download_button(
            "📥 下載報告",
            data=report,
            file_name="財報整合分析.docx"
        )

    else:
        st.error("❌ 無法解析財報（PDF格式太特殊）")

else:
    st.info("請上傳 PDF")
