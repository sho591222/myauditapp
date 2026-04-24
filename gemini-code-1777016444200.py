import streamlit as st
import pandas as pd
import pdfplumber
import re
import numpy as np
from datetime import datetime
from docx import Document
import io
import matplotlib.pyplot as plt

st.title("財報鑑識分析系統（穩定重建版）")

company = st.text_input("公司名稱")
auditor = st.text_input("會計師姓名")
firm = st.text_input("事務所名稱")
report_date = st.text_input("查核日期", datetime.now().strftime("%Y/%m/%d"))

files = st.file_uploader("上傳PDF", type=["pdf"], accept_multiple_files=True)

# -------------------------
# PDF讀取
# -------------------------
def read_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for p in pdf.pages:
            text += p.extract_text() or ""
    return text

# -------------------------
# 數據擷取
# -------------------------
def extract(text):

    def get(p):
        m = re.search(p, text)
        if m:
            return float(m.group(1).replace(",", ""))
        return None

    return {
        "營收": get(r"營業收入[\s:：]*([\d,]+)"),
        "應收": get(r"應收帳款[\s:：]*([\d,]+)"),
        "資產": get(r"資產總計[\s:：]*([\d,]+)"),
        "負債": get(r"流動負債[\s:：]*([\d,]+)"),
        "現金流": get(r"營業活動.*?([\d,]+)")
    }

# -------------------------
# 安全除法
# -------------------------
def safe_div(a, b):
    if b is None or b == 0 or a is None:
        return None
    return a / b

# -------------------------
# 計算模型
# -------------------------
def calc(df):

    df["M"] = df.apply(
        lambda r: -4.84 + 0.92 * safe_div(r["應收"], r["營收"])
        if safe_div(r["應收"], r["營收"]) is not None else None,
        axis=1
    )

    df["Z"] = df.apply(
        lambda r: (
            1.2 * safe_div(r["現金流"], r["資產"]) +
            1.4 * safe_div(r["營收"], r["資產"]) +
            3.3 * safe_div(r["營收"], r["負債"])
        ) if all([
            r["現金流"], r["資產"], r["營收"], r["負債"]
        ]) else None,
        axis=1
    )

    return df

# -------------------------
# 風險分析
# -------------------------
def risk(row):

    fraud = 0
    embezzle = 0
    scandal = 0

    if row["M"] and row["M"] > -1.78:
        fraud += 1

    if row["現金流"] and row["現金流"] < 0:
        fraud += 1

    if row["應收"] and row["營收"]:
        if safe_div(row["應收"], row["營收"]) and safe_div(row["應收"], row["營收"]) > 0.5:
            embezzle += 1

    if row["Z"] and row["Z"] < 1.81:
        scandal += 1

    if row["資產"] and row["負債"] and row["負債"] > row["資產"]:
        scandal += 1

    result = []

    if fraud >= 2:
        result.append("財報不實風險")

    if embezzle >= 2:
        result.append("疑似資產掏空")

    if scandal >= 2:
        result.append("重大財務異常")

    return " / ".join(result) if result else "正常"

# -------------------------
# 主流程
# -------------------------
if files:

    rows = []

    for f in files:
        text = read_pdf(f)
        d = extract(text)
        d["年度"] = f.name
        rows.append(d)

    df = pd.DataFrame(rows)

    df = calc(df)

    df["風險"] = df.apply(risk, axis=1)

    st.dataframe(df)

    # -------------------------
    # 趨勢圖
    # -------------------------
    fig, ax = plt.subplots()
    ax.plot(df["年度"], df["營收"], label="營收")
    ax.plot(df["年度"], df["M"], label="M-score")
    ax.plot(df["年度"], df["Z"], label="Z-score")
    ax.legend()
    ax.set_title("財務趨勢分析")

    st.pyplot(fig)

    # -------------------------
    # Word報告
    # -------------------------
    doc = Document()
    doc.add_heading("財報查核報告", 0)

    doc.add_paragraph(f"公司：{company}")
    doc.add_paragraph(f"會計師：{auditor}")
    doc.add_paragraph(f"事務所：{firm}")
    doc.add_paragraph(f"日期：{report_date}")

    doc.add_paragraph("分析結果：")

    for _, r in df.iterrows():
        doc.add_paragraph(f"{r['年度']}：{r['風險']}")

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    st.download_button("下載查核報告", buffer, "audit_report.docx")

else:
    st.info("請上傳PDF")
