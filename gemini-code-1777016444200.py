import streamlit as st
import pandas as pd
import pdfplumber
import re
from datetime import datetime
from docx import Document
import io
import matplotlib.pyplot as plt

st.title("財報鑑識與風險分析系統")

company = st.text_input("公司名稱")
auditor = st.text_input("會計師姓名")
firm = st.text_input("事務所名稱")
report_date = st.text_input("查核日期", datetime.now().strftime("%Y/%m/%d"))

files = st.file_uploader("上傳PDF", type=["pdf"], accept_multiple_files=True)


def read_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text


def extract(text):
    def get(p):
        try:
            return float(re.search(p, text).group(1).replace(",", ""))
        except:
            return None

    return {
        "營收": get(r"營業收入[\s:：]*([\d,]+)"),
        "應收": get(r"應收帳款[\s:：]*([\d,]+)"),
        "資產": get(r"資產總計[\s:：]*([\d,]+)"),
        "負債": get(r"流動負債[\s:：]*([\d,]+)"),
        "現金流": get(r"營業活動.*?([\d,]+)")
    }


def calc(df):
    df["M"] = -4.84 + 0.92 * (df["應收"] / df["營收"])
    df["Z"] = (
        1.2 * (df["現金流"] / df["資產"]) +
        1.4 * (df["營收"] / df["資產"]) +
        3.3 * (df["營收"] / df["負債"])
    )
    return df


def risk(row):
    fraud = 0
    embezzle = 0
    scandal = 0

    if row["M"] and row["M"] > -1.78:
        fraud += 1

    if row["現金流"] and row["現金流"] < 0:
        fraud += 1

    if row["應收"] and row["營收"] and row["營收"] > 0:
        if (row["應收"] / row["營收"]) > 0.5:
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


if files:

    data = []

    for f in files:
        text = read_pdf(f)
        d = extract(text)
        d["年度"] = f.name
        data.append(d)

    df = pd.DataFrame(data).fillna(0)
    df = calc(df)
    df["風險"] = df.apply(risk, axis=1)

    st.dataframe(df)

    fig, ax = plt.subplots()
    ax.plot(df["年度"], df["營收"], label="營收")
    ax.plot(df["年度"], df["M"], label="M-score")
    ax.plot(df["年度"], df["Z"], label="Z-score")
    ax.legend()
    ax.set_title("財務趨勢分析")

    st.pyplot(fig)

    doc = Document()
    doc.add_heading("財報查核報告", 0)

    doc.add_paragraph("公司：" + str(company))
    doc.add_paragraph("會計師：" + str(auditor))
    doc.add_paragraph("事務所：" + str(firm))
    doc.add_paragraph("日期：" + str(report_date))

    doc.add_paragraph("分析結果")

    for _, r in df.iterrows():
        doc.add_paragraph(str(r["年度"]) + "：" + str(r["風險"]))

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    st.download_button("下載報告", buffer, "audit_report.docx")

else:
    st.info("請上傳PDF")
