import streamlit as st
import pandas as pd
import pdfplumber
import numpy as np
import re
import matplotlib.pyplot as plt
from docx import Document
import io
from datetime import datetime

st.set_page_config(layout="wide")

st.title("財報審計分析儀表板")

# -----------------------
# 基本資料
# -----------------------
company_input = st.text_input("公司名稱")
auditor = st.text_input("會計師")
firm = st.text_input("事務所")
date = st.text_input("日期", datetime.now().strftime("%Y/%m/%d"))

files = st.file_uploader("上傳財報PDF", type=["pdf"], accept_multiple_files=True)

# -----------------------
# PDF解析
# -----------------------
def read_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for p in pdf.pages:
            t = p.extract_text()
            if t:
                text += t + "\n"
    return text

# -----------------------
# 公司名稱
# -----------------------
def extract_company(text):
    m = re.search(r"(.*股份有限公司|.*有限公司|.*公司)", text)
    return m.group(1) if m else None

# -----------------------
# 數字抓取
# -----------------------
def get_num(text, key):
    if key not in text:
        return None
    try:
        idx = text.index(key)
        chunk = text[idx:idx+80]
        num = ""
        for c in chunk:
            if c.replace(",", "").replace(".", "").isdigit():
                num += c
            elif num:
                break
        return float(num.replace(",", "")) if num else None
    except:
        return None

# -----------------------
# 風險模型（你原本的升級版）
# -----------------------
def risk_model(r):

    risk_score = 0
    risks = []
    audit = []

    if r["營收"] and r["營收"] < 0:
        risk_score += 30
        risks.append("營收異常")
        audit.append("ISA240 收入查核")

    if r["應收"] and r["營收"]:
        if r["營收"] != 0 and r["應收"]/r["營收"] > 0.5:
            risk_score += 25
            risks.append("應收過高")
            audit.append("ISA505 函證應收帳款")

    if r["現金流"] and r["現金流"] < 0:
        risk_score += 20
        risks.append("現金流異常")
        audit.append("營運現金流分析")

    if r["負債"] and r["資產"]:
        if r["負債"] > r["資產"]:
            risk_score += 25
            risks.append("資不抵債")
            audit.append("ISA570 持續經營")

    return risk_score, risks, audit

# -----------------------
# 主流程
# -----------------------
if files:

    data = []

    for f in files:

        text = read_pdf(f)

        company = extract_company(text) or company_input

        row = {
            "年度": f.name,
            "公司": company,
            "營收": get_num(text, "營業收入"),
            "應收": get_num(text, "應收帳款"),
            "資產": get_num(text, "資產總計"),
            "負債": get_num(text, "流動負債"),
            "現金流": get_num(text, "營業活動")
        }

        score, risks, audit = risk_model(row)

        row["風險分數"] = score
        row["風險"] = " / ".join(risks) if risks else "正常"
        row["查核建議"] = "；".join(audit) if audit else "標準查核程序"

        data.append(row)

    df = pd.DataFrame(data).fillna(0)

    # -----------------------
    # KPI卡片
    # -----------------------
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("營收", f"{df['營收'].sum():,.0f}")
    col2.metric("應收", f"{df['應收'].sum():,.0f}")
    col3.metric("現金流", f"{df['現金流'].sum():,.0f}")
    col4.metric("平均風險分數", f"{df['風險分數'].mean():.1f}")

    # -----------------------
    # 圖表區（重點）
    # -----------------------
    st.subheader("財務趨勢圖")

    fig, ax = plt.subplots()
    ax.plot(df["年度"], df["營收"], marker="o", label="營收")
    ax.plot(df["年度"], df["應收"], marker="s", label="應收")
    ax.set_title("營收與應收趨勢")
    ax.legend()
    st.pyplot(fig)

    fig2, ax2 = plt.subplots()
    ax2.bar(df["年度"], df["風險分數"])
    ax2.set_title("風險分數分布")
    st.pyplot(fig2)

    # -----------------------
    # 逐年分析
    # -----------------------
    st.subheader("逐年查核分析")

    for _, r in df.iterrows():

        with st.expander(f"{r['年度']}（風險分數 {r['風險分數']}）"):

            st.write("公司：", r["公司"])
            st.write("營收：", r["營收"])
            st.write("應收：", r["應收"])
            st.write("資產：", r["資產"])
            st.write("負債：", r["負債"])
            st.write("現金流：", r["現金流"])

            st.write("風險：", r["風險"])
            st.write("查核建議：", r["查核建議"])

    # -----------------------
    # Word報告
    # -----------------------
    doc = Document()
    doc.add_heading("財報審計分析報告", 0)

    doc.add_paragraph(f"公司：{df['公司'].iloc[0]}")
    doc.add_paragraph(f"會計師：{auditor}")
    doc.add_paragraph(f"事務所：{firm}")
    doc.add_paragraph(f"日期：{date}")

    doc.add_paragraph(f"平均風險分數：{df['風險分數'].mean():.1f}")

    for _, r in df.iterrows():

        doc.add_heading(r["年度"], level=2)

        doc.add_paragraph(f"營收：{r['營收']}")
        doc.add_paragraph(f"應收：{r['應收']}")
        doc.add_paragraph(f"資產：{r['資產']}")
        doc.add_paragraph(f"負債：{r['負債']}")
        doc.add_paragraph(f"現金流：{r['現金流']}")
        doc.add_paragraph(f"風險分數：{r['風險分數']}")
        doc.add_paragraph(f"風險：{r['風險']}")
        doc.add_paragraph(f"查核建議：{r['查核建議']}")
        doc.add_paragraph("-" * 50)

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    st.download_button("下載審計報告", buffer, "audit_report.docx")

else:
    st.info("請上傳PDF財報")
