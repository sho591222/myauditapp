import streamlit as st
import sqlite3
import hashlib
import random
import string
import pdfplumber
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from docx import Document
import io


# =====================================================
# DATABASE
# =====================================================

conn = sqlite3.connect("audit.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    email TEXT PRIMARY KEY,
    password TEXT,
    company TEXT
)
""")

conn.commit()


# =====================================================
# AUTH SYSTEM
# =====================================================

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


# =====================================================
# PDF ENGINE
# =====================================================

def parse_pdf(file):
    text = ""

    with pdfplumber.open(file) as pdf:
        for i, page in enumerate(pdf.pages):
            text += f"PAGE {i+1}\n"
            text += page.extract_text() or ""

    return text


def audit_engine(text, role):

    issues = []

    pages = text.split("PAGE")

    for i, p in enumerate(pages):

        if "應收帳款" in p:
            issues.append((i, "應收帳款異常"))

        if "存貨" in p:
            issues.append((i, "存貨風險"))

        if "關係人" in p:
            issues.append((i, "關係人交易"))

        if role == "會計師事務所":

            if "收入" in p:
                issues.append((i, "cut-off test"))

            if "費用" in p:
                issues.append((i, "完整性測試"))

        else:

            if "費用" in p:
                issues.append((i, "費用異常"))

    return issues


# =====================================================
# CHART ENGINE
# =====================================================

def make_chart():

    df = pd.DataFrame({
        "year": ["2021", "2022", "2023"],
        "revenue": [1000, 1200, 900],
        "profit": [100, 150, -50]
    })

    fig, ax = plt.subplots()

    ax.plot(df["year"], df["revenue"])
    ax.plot(df["year"], df["profit"])

    return fig


# =====================================================
# GRAPH ENGINE
# =====================================================

def build_graph():

    G = nx.Graph()

    G.add_edges_from([
        ("公司A", "子公司B"),
        ("公司A", "關係人C"),
        ("關係人C", "供應商D")
    ])

    nx.draw(G, with_labels=True)


# =====================================================
# WORD REPORT
# =====================================================

def generate_report(email, role, issues, score):

    doc = Document()

    doc.add_heading("四大查核報告 v43", 0)

    doc.add_paragraph("Email: " + email)
    doc.add_paragraph("Role: " + role)
    doc.add_paragraph("Risk Score: " + str(score))

    doc.add_paragraph("Audit Findings")

    for p, i in issues:
        doc.add_paragraph(f"Page {p}: {i}")

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    return buffer


# =====================================================
# STREAMLIT UI
# =====================================================

st.title("四大雲端查核系統 v43")

mode = st.selectbox("模式", ["登入", "註冊"])

email = st.text_input("Email")
pw = st.text_input("Password", type="password")
company = st.text_input("Company")


# =========================
# REGISTER
# =========================

if mode == "註冊":

    if st.button("註冊"):
        if register(email, pw, company):
            st.success("註冊成功")
        else:
            st.error("失敗")


# =========================
# LOGIN
# =========================

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
# AUTH CHECK
# =========================

if not st.session_state.get("auth"):
    st.stop()


# =========================
# ROLE
# =========================

role = st.selectbox("模式", ["公司內部", "會計師事務所"])


# =========================
# FILE UPLOAD
# =========================

file = st.file_uploader("上傳PDF", type="pdf")

issues = []
score = None


# =========================
# MAIN ANALYSIS
# =========================

if file:

    text = parse_pdf(file)

    issues = audit_engine(text, role)

    score = min(len(issues) * 10, 100)

    st.subheader("查核發現")

    for p, i in issues:
        st.write("Page", p, ":", i)

    st.subheader("財務圖表")

    st.pyplot(make_chart())

    st.subheader("關係人架構")

    build_graph()

    st.write("Risk Score:", score)


# =========================
# REPORT EXPORT
# =========================

if st.button("產出報告"):

    if file is None:
        st.error("請先上傳PDF")
        st.stop()

    buffer = generate_report(email, role, issues, score)

    st.download_button(
        "下載Word報告",
        buffer,
        file_name="audit_report.docx"
    )
