import streamlit as st
import pandas as pd
import pdfplumber
import re
from docx import Document
import io
from datetime import datetime

st.title("財報分析系統")

files = st.file_uploader("上傳PDF", type=["pdf"], accept_multiple_files=True)

if files:

    results = []

    for f in files:

        text = ""
        with pdfplumber.open(f) as pdf:
            for p in pdf.pages:
                text += p.extract_text() or ""

        try:
            revenue = float(re.search(r"營業收入[\s:：]*([\d,]+)", text).group(1).replace(",", ""))
        except:
            revenue = None

        try:
            ar = float(re.search(r"應收帳款[\s:：]*([\d,]+)", text).group(1).replace(",", ""))
        except:
            ar = None

        try:
            assets = float(re.search(r"資產總計[\s:：]*([\d,]+)", text).group(1).replace(",", ""))
        except:
            assets = None

        try:
            cl = float(re.search(r"流動負債[\s:：]*([\d,]+)", text).group(1).replace(",", ""))
        except:
            cl = None

        try:
            ocf = float(re.search(r"營業活動.*?([\d,]+)", text).group(1).replace(",", ""))
        except:
            ocf = None

        if revenue and ar:
            dsri = ar / revenue
            m_score = -4.84 + 0.92 * dsri
        else:
            m_score = None

        if revenue and assets and cl and ocf:
            z_score = 1.2*(ocf/assets) + 1.4*(revenue/assets) + 3.3*(revenue/cl)
        else:
            z_score = None

        warning = []

        if m_score and m_score > -1.78:
            warning.append("財報操縱風險")

        if z_score and z_score < 1.81:
            warning.append("財務風險偏高")

        if ocf and ocf < 0:
            warning.append("現金流異常")

        results.append({
            "檔名": f.name,
            "營收": revenue,
            "應收帳款": ar,
            "M-score": m_score,
            "Z-score": z_score,
            "結果": " / ".join(warning) if warning else "正常"
        })

    df = pd.DataFrame(results)
    st.dataframe(df)

    doc = Document()
    doc.add_heading("財報分析報告", 0)
    doc.add_paragraph(str(datetime.now()))

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

    st.download_button("下載報告", buffer, "report.docx")

else:
    st.info("請上傳PDF")
