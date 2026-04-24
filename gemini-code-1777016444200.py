import streamlit as st
import sqlite3
import hashlib
import random
import string
import pdfplumber
import pandas as pd
import matplotlib.pyplot as plt
import io
import networkx as nx
from docx import Document


# =========================
# DATABASE
# =========================

conn = sqlite3.connect("audit_v43.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    email TEXT PRIMARY KEY,
    password TEXT,
    company TEXT
)
""")

conn.commit()


# =========================
# AUTH
# =========================

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


def register(email, pw, company):

    try:
        c.execute(
            "INSERT INTO users VALUES (?,?,?)",
            (email, hash_pw(pw), company)
        )
        conn.commit()
        return True
    except:
        return False


def login(email, pw):

    c.execute("SELECT password FROM users WHERE email=?", (email,))
    r = c.fetchone()

    return r and r[0] == hash_pw(pw)


# =========================
# SESSION
# =========================

if "auth" not in st.session_state:
    st.session_state.auth = False


# =========================
# UI
# =========================

st.title("四大雲端查核系統 v43（完整企業整合版）")


# =========================
# LOGIN / REGISTER
# =========================

mode = st.selectbox("模式", ["登入", "註冊"])

email = st.text_input("Email")
pw = st.text_input("Password", type="password")
company = st.text_input("Company (Tenant)")

if mode == "註冊":

    if st.button("註冊"):

        if register(email, pw, company):
            st.success("註冊成功")
        else:
            st.error("註冊失敗")

if mode == "登入":

    if st.button("登入"):

        if login(email, pw):
            st.session_state.auth = True
            st.session_state.email = email
            st.session_state.company = company
            st.success("登入成功")
        else:
            st.error("錯誤")


# =========================
# AUTH BLOCK
# =========================

if not st.session_state.auth:
    st.stop()


# =========================
# ROLE
# =========================

role = st.selectbox("使用模式", ["公司內部", "會計師事務所"])


# =========================
# FILE UPLOAD
# =========================

file = st.file_uploader("上傳 PDF / Excel", type=["pdf", "xlsx"])


issues = []


# =========================
# PDF PARSER
# =========================

def parse_pdf(file):

    text = ""

    with pdfplumber.open(file) as pdf:
        for i, p in enumerate(pdf.pages):
            text += "PAGE " + str(i+1) + "\n"
            text += p.extract_text() or ""

    return text


# =========================
# ANALYSIS ENGINE
# =========================

def analyze(text, role):

    res = []

    pages = text.split("PAGE")

    for i, p in enumerate(pages):

        if "應收帳款" in p:
            res.append((i, "應收帳款異常"))

        if "存貨" in p:
            res.append((i, "存貨風險"))

        if "關係人" in p:
            res.append((i, "關係人交易"))

        if role == "會計師事務所":

            if "收入" in p:
                res.append((i, "cut-off test"))

            if "費用" in p:
                res.append((i, "完整性測試"))

        else:

            if "費用" in p:
                res.append((i, "費用異常"))

    return res


# =========================
# GRAPH
# =========================

def build_graph():

    G = nx.Graph()

    edges = [
        ("公司A", "子公司B"),
        ("公司A", "關係人C"),
        ("關係人C", "供應商D")
    ]

    G.add_edges_from(edges)

    nx.draw(G, with_labels=True)


# =========================
# MAIN PROCESS
# =========================

if file:

    if file.name.endswith(".pdf"):

        text = parse_pdf(file)

        issues = analyze(text, role)

        score = min(len(issues) * 10, 100)

        st.subheader("查核發現")

        for p, i in issues:
            st.write("第", p, "頁:", i)

        st.subheader("風險分數")
        st.write(score)

        st.subheader("財務圖表")

        df = pd.DataFrame({
            "year": ["2021", "2022", "2023"],
            "revenue": [1000, 1200, 900],
            "profit": [100, 150, -50]
        })

        fig, ax = plt.subplots()
        ax.plot(df["year"], df["revenue"])
        ax.plot(df["year"], df["profit"])

        st.pyplot(fig)

        st.subheader("關係人交易圖")
        build_graph()


# =========================
# WORD REPORT
# =========================

if st.button("產出查核報告"):

    doc = Document()

    doc.add_heading("四大查核報告 v43", 0)

    doc.add_paragraph("Email: " + st.session_state.email)
    doc.add_paragraph("Company: " + st.session_state.company)
    doc.add_paragraph("Role: " + role)

    doc.add_paragraph("查核發現")

    for p, i in issues:
        doc.add_paragraph(f"第 {p} 頁: {i}")

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    st.download_button(
        "下載報告",
        buffer,
        file_name="audit_v43.docx"
    )
