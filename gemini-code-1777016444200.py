import streamlit as st
import pandas as pd
import pdfplumber
import numpy as np
import re
import matplotlib.pyplot as plt
from docx import Document
import io
from datetime import datetime

st.title("財報 + 附註整合解析系統")

company = st.text_input("公司名稱")
auditor = st.text_input("會計師")
firm = st.text_input("事務所")
date = st.text_input("日期", datetime.now().strftime("%Y/%m/%d"))

files = st.file_uploader("上傳財報PDF（含附註）", type=["pdf"], accept_multiple_files=True)

# -------------------------
# PDF讀取（主體 + 附註）
# -------------------------
def read_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    return text

# -------------------------
# 附註數字抓取（強化版）
# -------------------------
def extract_all_numbers(text, keywords):

    results = {}

    for k in keywords:

        pattern = rf"{k}[\s:：]*([\d,]+)"
        m = re.search(pattern, text)

        if m:
            try:
                results[k] = float(m.group(1).replace(",", ""))
            except:
                results[k] = None
        else:
            results[k] = None

    return results

# -------------------------
# 附註補抓（掃全文數字）
# -------------------------
def fallback_numbers(text):

    nums = re.findall(r"[\d]{3,}", text.replace(",", ""))

    nums = [float(n) for n in nums[:10]]  # 只取前10個避免爆

    return nums if nums else []

# -------------------------
# 風險分析
# -------------------------
def risk(row):

    r = []

    if row["營收"] and row["營收"] < 0:
        r.append("營收異常")

    if row["應收"] and row["營收"]:
        if row["營收"] != 0 and row["應收"] / row["營收"] > 0.5:
            r.append("應收過高（可能虛增營收）")

    if row["現金流"] and row["現金流"] < 0:
        r.append("現金流異常")

    if row["資產"] and row["負債"]:
        if row["負債"] > row["資產"]:
            r.append("資不抵債")

    return " / ".join(r) if r else "正常"

# -------------------------
# 主流程
# -------------------------
if files:

    data = []

    for f in files:

        text = read_pdf(f)

        st.text(text[:300])  # debug

        # -------------------------
        # 主財報 + 附註一起抓
        # -------------------------
        numbers = extract_all_numbers(text, [
            "營業收入",
            "應收帳款",
            "資產總計",
            "流動負債",
            "營業活動現金流"
        ])

        # fallback（如果全部空）
        if all(v is None for v in numbers.values()):
            fb = fallback_numbers(text)

            numbers = {
                "營收": fb[0] if len(fb) > 0 else None,
                "應收": fb[1] if len(fb) > 1 else None,
                "資產": fb[2] if len(fb) > 2 else None,
                "負債": fb[3] if len(fb) > 3 else None,
                "現金流": fb[4] if len(fb) > 4 else None
            }

        row = {
            "年度": f.name,
            "營收": numbers.get("營業收入"),
            "應收": numbers.get("應收帳款"),
            "資產": numbers.get("資產總計"),
            "負債": numbers.get("流動負債"),
            "現金流": numbers.get("營業活動現金流")
        }

        row["風險"] = risk(row)

        data.append(row)

    df = pd.DataFrame(data)

    # -------------------------
    # 如果完全沒資料
    # -------------------------
    if df["營收"].isna().all():
        st.error("PDF解析失敗（可能是掃描檔或附註為影像）")
        st.stop()

    df = df.fillna(0)
    df = df.sort_values("年度")

    st.dataframe(df)

    # -------------------------
    # 圖表（保證有）
    # -------------------------
    fig, ax = plt.subplots()

    ax.plot(df["年度"], df["營收"], marker="o", label="營收")
    ax.set_title("財務趨勢")
    ax.legend()

    st.pyplot(fig)

    # -------------------------
    # Word輸出（含附註分析）
    # -------------------------
    doc = Document()
    doc.add_heading("財報 + 附註查核報告", 0)

    doc.add_paragraph(f"公司：{company}")
    doc.add_paragraph(f"會計師：{auditor}")
    doc.add_paragraph(f"事務所：{firm}")
    doc.add_paragraph(f"日期：{date}")

    for _, r in df.iterrows():

        doc.add_heading(r["年度"], level=2)

        doc.add_paragraph(f"營收：{r['營收']}")
        doc.add_paragraph(f"應收：{r['應收']}")
        doc.add_paragraph(f"資產：{r['資產']}")
        doc.add_paragraph(f"負債：{r['負債']}")
        doc.add_paragraph(f"現金流：{r['現金流']}")
        doc.add_paragraph(f"風險：{r['風險']}")

        doc.add_paragraph("附註查核建議：")
        doc.add_paragraph("1. 應收帳款附註 → 檢查帳齡分析")
        doc.add_paragraph("2. 關係人交易附註 → 查 ISA 550")
        doc.add_paragraph("3. 現金流附註 → 核對現金流調整項目")

        doc.add_paragraph("-" * 40)

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    st.download_button("下載完整查核報告", buffer, "audit_report.docx")

else:
    st.info("請上傳PDF")
