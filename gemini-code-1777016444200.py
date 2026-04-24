import streamlit as st
import pandas as pd
import pdfplumber
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from docx import Document
import io

st.title("財報逐年分析與查核建議系統")

# -----------------------
# 基本資料
# -----------------------
company = st.text_input("公司名稱")
auditor = st.text_input("會計師姓名")
firm = st.text_input("事務所名稱")
date = st.text_input("查核日期", datetime.now().strftime("%Y/%m/%d"))

files = st.file_uploader("上傳PDF財報", type=["pdf"], accept_multiple_files=True)

# -----------------------
# PDF讀取
# -----------------------
def read_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text()
    return text

# -----------------------
# 穩定數字抓取
# -----------------------
def extract_number(text, keyword):
    if keyword not in text:
        return None

    try:
        idx = text.index(keyword)
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
# 查核建議 + 風險分析
# -----------------------
def audit_engine(row):

    risks = []
    audit = []

    # 營收異常
    if row["營收"] is not None and row["營收"] < 0:
        risks.append("營收異常")
        audit.append("查核收入認列（ISA 240）")

    # 應收過高
    if row["應收"] and row["營收"]:
        if row["營收"] != 0 and row["應收"] / row["營收"] > 0.5:
            risks.append("應收帳款異常")
            audit.append("函證應收帳款 + 壞帳評估（ISA 505）")

    # 現金流異常
    if row["現金流"] is not None and row["現金流"] < 0:
        risks.append("現金流異常")
        audit.append("營運現金流與盈餘差異分析")

    # 負債過高
    if row["資產"] and row["負債"]:
        if row["負債"] > row["資產"]:
            risks.append("資不抵債")
            audit.append("持續經營假設（ISA 570）")

    # 掏空疑慮
    if row["應收"] and row["資產"]:
        if row["資產"] != 0 and row["應收"] / row["資產"] > 0.4:
            risks.append("關係人資金疑慮")
            audit.append("關係人交易查核（ISA 550）")

    return " / ".join(risks) if risks else "正常", "；".join(audit) if audit else "標準查核程序"

# -----------------------
# 主流程
# -----------------------
if files:

    data = []

    for f in files:

        text = read_pdf(f)

        st.text(text[:300])  # debug用

        row = {
            "年度": f.name,
            "營收": extract_number(text, "營業收入"),
            "應收": extract_number(text, "應收帳款"),
            "資產": extract_number(text, "資產總計"),
            "負債": extract_number(text, "流動負債"),
            "現金流": extract_number(text, "營業活動")
        }

        row["風險"], row["查核建議"] = audit_engine(row)

        data.append(row)

    df = pd.DataFrame(data)

    # -----------------------
    # 如果完全沒資料 → 停止
    # -----------------------
    if df["營收"].isna().all():
        st.error("PDF未解析到財務數據（可能是掃描PDF或格式不同）")
        st.stop()

    df = df.fillna(0)
    df = df.sort_values("年度")

    st.subheader("逐年財務分析")
    st.dataframe(df)

    # -----------------------
    # 圖表
    # -----------------------
    fig, ax = plt.subplots()

    ax.plot(df["年度"], df["營收"], marker="o", label="營收")
    ax.set_title("營收趨勢")
    ax.legend()

    st.pyplot(fig)

    # -----------------------
    # 詳細展開（Streamlit）
    # -----------------------
    st.subheader("逐年查核細節")

    doc = Document()
    doc.add_heading("財報查核報告", 0)

    doc.add_paragraph(f"公司：{company}")
    doc.add_paragraph(f"會計師：{auditor}")
    doc.add_paragraph(f"事務所：{firm}")
    doc.add_paragraph(f"日期：{date}")

    for _, r in df.iterrows():

        with st.expander(r["年度"]):

            st.write("營收：", r["營收"])
            st.write("應收：", r["應收"])
            st.write("資產：", r["資產"])
            st.write("負債：", r["負債"])
            st.write("現金流：", r["現金流"])
            st.write("風險：", r["風險"])
            st.write("查核建議：", r["查核建議"])

        # Word同步輸出
        doc.add_heading(r["年度"], level=2)
        doc.add_paragraph(f"營收：{r['營收']}")
        doc.add_paragraph(f"應收：{r['應收']}")
        doc.add_paragraph(f"資產：{r['資產']}")
        doc.add_paragraph(f"負債：{r['負債']}")
        doc.add_paragraph(f"現金流：{r['現金流']}")
        doc.add_paragraph(f"風險：{r['風險']}")
        doc.add_paragraph(f"查核建議：{r['查核建議']}")
        doc.add_paragraph("-" * 40)

    # -----------------------
    # Word下載
    # -----------------------
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    st.download_button(
        "下載查核報告",
        buffer,
        "audit_report.docx"
    )

else:
    st.info("請上傳PDF財報")
