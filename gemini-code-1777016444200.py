import streamlit as st
import pandas as pd
import numpy as np
import pdfplumber
import matplotlib.pyplot as plt
import networkx as nx
import io
import re
import datetime
from docx import Document


# =========================
# 🔐 LOGIN SYSTEM（簡化 SaaS）
# =========================

USERS = {
    "admin": {"password": "1234", "role": "auditor"},
    "company": {"password": "1234", "role": "company"}
}

st.sidebar.subheader("登入系統")

username = st.sidebar.text_input("帳號")
password = st.sidebar.text_input("密碼", type="password")

if username in USERS and USERS[username]["password"] == password:
    role = USERS[username]["role"]
    st.success(f"登入成功：{role}")

else:
    st.warning("請登入")
    st.stop()


# =========================
# 🏢 MODE CONTROL
# =========================

mode = st.selectbox(
    "系統模式",
    ["公司分析", "查核模式（事務所）"]
)


# =========================
# 📄 PDF UPLOAD
# =========================

files = st.file_uploader(
    "上傳財報 PDF",
    type="pdf",
    accept_multiple_files=True
)


# =========================
# PDF PARSER
# =========================

def parse_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for p in pdf.pages:
            text += p.extract_text() or ""
    return text


def extract(text, key):
    m = re.search(rf"{key}.*?([\d,]+)", text)
    if m:
        return float(m.group(1).replace(",", ""))
    return 0


# =========================
# 📊 FINANCIAL ENGINE
# =========================

def ratio(r, p, a, l):
    m = p / r if r else 0
    lev = l / a if a else 0
    return m, lev


# =========================
# 🧠 FRAUD SCORING (0–100)
# =========================

def fraud_score(rev, profit, assets, liab):

    score = 0

    if profit < 0:
        score += 30

    if liab > assets * 0.8:
        score += 20

    if profit / rev < 0.05:
        score += 25

    if assets > rev * 3:
        score += 15

    return min(score, 100)


# =========================
# 🧠 ISA 700 AUDIT OPINION GENERATOR
# =========================

def isa700(score):

    if score < 30:
        return "無保留意見（Unqualified Opinion）"

    elif score < 60:
        return "保留意見（Qualified Opinion）"

    elif score < 85:
        return "否定意見風險（Adverse Risk）"

    else:
        return "無法表示意見（Disclaimer of Opinion）"


# =========================
# 🧠 RELATED PARTY GRAPH
# =========================

def build_graph():

    G = nx.Graph()

    G.add_edge("公司A", "董事長")
    G.add_edge("公司A", "關係企業B")
    G.add_edge("公司A", "供應商C")
    G.add_edge("關係企業B", "董事長")

    fig, ax = plt.subplots()

    nx.draw(G, with_labels=True, node_color="lightblue", node_size=2000, ax=ax)

    st.pyplot(fig)


# =========================
# ☁️ GOOGLE DRIVE（STUB）
# =========================

def google_drive_upload(report_name):

    st.info("Google Drive 上傳（模擬）成功")
    st.write("檔案：" + report_name)


# =========================
# 📊 CHART
# =========================

def draw(df):

    fig, ax = plt.subplots()

    ax.plot(df["year"], df["revenue"], label="營收")
    ax.plot(df["year"], df["profit"], label="淨利")

    ax.legend()
    st.pyplot(fig)


# =========================
# DATA STORAGE
# =========================

data = []


if files:

    for f in files:

        text = parse_pdf(f)

        data.append({
            "year": f.name,
            "revenue": extract(text, "營業收入"),
            "profit": extract(text, "本期淨利"),
            "assets": extract(text, "資產總額"),
            "liabilities": extract(text, "負債總額")
        })


# =========================
# MAIN ENGINE
# =========================

if data:

    df = pd.DataFrame(data)

    st.subheader("財務數據")
    st.dataframe(df)

    df["margin"], df["leverage"] = zip(*df.apply(
        lambda x: ratio(x["revenue"], x["profit"], x["assets"], x["liabilities"]),
        axis=1
    ))

    # =========================
    # 📊 CHART
    # =========================

    st.subheader("財務趨勢圖")
    draw(df)

    # =========================
    # 🧠 FRAUD SCORE
    # =========================

    st.subheader("財報造假風險分數")

    score = fraud_score(
        df["revenue"].mean(),
        df["profit"].mean(),
        df["assets"].mean(),
        df["liabilities"].mean()
    )

    st.write("Risk Score：", score)
    st.write("ISA 700 意見：", isa700(score))

    # =========================
    # 🧠 RELATED PARTY GRAPH
    # =========================

    st.subheader("關係人交易圖（Graph）")
    build_graph()

    # =========================
    # MODE LOGIC
    # =========================

    st.subheader("查核 / 分析建議")

    if mode == "查核模式（事務所）":

        st.write([
            "應收帳款函證",
            "收入 cut-off test",
            "存貨盤點",
            "關係人交易查核",
            "ISA 240 舞弊風險評估"
        ])

    else:

        st.write([
            "獲利能力分析",
            "成本結構分析",
            "資本效率分析"
        ])

    # =========================
    # ☁️ GOOGLE DRIVE EXPORT
    # =========================

    if st.button("上傳Working Paper到雲端"):

        google_drive_upload("audit_report_v23.docx")

    # =========================
    # 📄 REPORT EXPORT
    # =========================

    if st.button("產出查核報告"):

        doc = Document()

        doc.add_heading("AI 查核報告 v23", 0)

        doc.add_paragraph("Risk Score：" + str(score))
        doc.add_paragraph("ISA 700：" + isa700(score))

        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)

        st.download_button(
            "下載報告",
            buffer,
            file_name="v23_audit_report.docx"
        )
