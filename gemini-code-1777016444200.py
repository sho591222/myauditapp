import streamlit as st
import pandas as pd
import pdfplumber
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from docx import Document
import io

st.title("財報鑑識穩定分析系統")

company = st.text_input("公司名稱")
auditor = st.text_input("會計師姓名")
firm = st.text_input("事務所名稱")
report_date = st.text_input("查核日期", datetime.now().strftime("%Y/%m/%d"))

files = st.file_uploader("上傳PDF", type=["pdf"], accept_multiple_files=True)

# -------------------------
# PDF文字抽取
# -------------------------
def read_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for p in pdf.pages:
            t = p.extract_text()
            if t:
                text += t
    return text

# -------------------------
# 穩定數字解析（不靠單一 regex）
# -------------------------
def extract_number(text, keywords):
    for k in keywords:
        if k in text:
            try:
                idx = text.index(k)
                chunk = text[idx:idx+50]
                num = ""
                for c in chunk:
                    if c.replace(",", "").replace(".", "").isdigit():
                        num += c
                    elif num:
                        break
                return float(num.replace(",", "")) if num else None
            except:
                continue
    return None

# -------------------------
# safe division
# -------------------------
def div(a, b):
    if a is None or b is None or b == 0:
        return None
    return a / b

# -------------------------
# 主模型
# -------------------------
def calc(df):

    df["M"] = df.apply(
        lambda r: -4.84 + 0.92 * div(r["應收"], r["營收"])
        if div(r["應收"], r["營收"]) is not None else None,
        axis=1
    )

    df["Z"] = df.apply(
        lambda r: (
            1.2 * div(r["現金流"], r["資產"]) +
            1.4 * div(r["營收"], r["資產"]) +
            3.3 * div(r["營收"], r["負債"])
        ) if all([r["資產"], r["負債"]]) else None,
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

    if row["營收"] and row["應收"]:
        r = div(row["應收"], row["營收"])
        if r and r > 0.5:
            embezzle += 1

    if row["Z"] and row["Z"] < 1.81:
        scandal += 1

    if row["資產"] and row["負債"] and row["負債"] > row["資產"]:
        scandal += 1

    res = []

    if fraud >= 2:
        res.append("財報不實風險")

    if embezzle >= 2:
        res.append("疑似掏空")

    if scandal >= 2:
        res.append("重大財務異常")

    return " / ".join(res) if res else "正常"

# -------------------------
# 主流程
# -------------------------
if files:

    rows = []

    for f in files:

        text = read_pdf(f)

        # DEBUG（非常重要）
        st.text(text[:300])

        d = {
            "年度": f.name,
            "營收": extract_number(text, ["營業收入", "營收"]),
            "應收": extract_number(text, ["應收帳款"]),
            "資產": extract_number(text, ["資產總計"]),
            "負債": extract_number(text, ["流動負債"]),
            "現金流": extract_number(text, ["營業活動"])
        }

        rows.append(d)

    df = pd.DataFrame(rows)

    # 防炸核心
    df = df.dropna(how="all", subset=["營收", "應收", "資產"])

    if df.empty:
        st.error("PDF沒有成功解析到財務數據（可能是掃描PDF或格式不同）")
        st.stop()

    df = calc(df)
    df["風險"] = df.apply(risk, axis=1)

    st.dataframe(df)

    # -------------------------
    # 圖表（穩定版）
    # -------------------------
    df = df.sort_values("年度")

    fig, ax = plt.subplots()

    ax.plot(df["年度"], df["營收"], marker="o", label="營收")
    ax.plot(df["年度"], df["M"], marker="o", label="M-score")
    ax.plot(df["年度"], df["Z"], marker="o", label="Z-score")

    ax.set_title("財務趨勢分析")
    ax.legend()

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
