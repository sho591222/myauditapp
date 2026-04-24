import streamlit as st
import sqlite3
import hashlib
import pdfplumber
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from docx import Document
import io


# =========================
# DATABASE
# =========================

conn = sqlite3.connect("audit.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    email TEXT PRIMARY KEY,
    password TEXT,
    role TEXT,
    company TEXT
)
""")

conn.commit()


# =========================
# AUTH
# =========================

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


def register(email, pw, role, company):
    try:
        c.execute(
            "INSERT INTO users VALUES (?,?,?,?)",
            (email, hash_pw(pw), role, company)
        )
        conn.commit()
        return True
    except:
        return False


def login(email, pw):
    c.execute("SELECT password FROM users WHERE email=?", (email,))
    r = c.fetchone()
    return r and r[0] == hash_pw(pw)


def get_user(email):
    c.execute("SELECT role, company FROM users WHERE email=?", (email,))
    return c.fetchone()


# =========================
# FILE PARSER
# =========================

def parse_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for i, p in enumerate(pdf.pages):
            text += f"PAGE {i+1}\n"
            text += p.extract_text() or ""
    return text


def read_word(file):
    doc = Document(file)
    return "\n".join([p.text for p in doc.paragraphs])


# =========================
# AUDIT ENGINE
# =========================

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

        if role == "Company User":

            if "費用" in p:
                issues.append((i, "費用異常"))

        else:

            if "收入" in p:
                issues.append((i, "cut-off test"))

    return issues


# =========================
# CHART
# =========================

def make_chart():

    df = pd.DataFrame({
        "year": ["2021", "2022", "2023"],
        "revenue": [1000, 1200, 900],
        "profit": [100, 150, -50]
    })

    fig, ax = plt.subplots()

    ax.plot(df["year"], df["revenue"], label="Revenue")
    ax.plot(df["year"], df["profit"], label="Profit")

    ax.legend()

    return fig


# =========================
# GRAPH
# =========================

def build_graph():

    G = nx.Graph()

    G.add_edges_from([
        ("公司A", "子公司B"),
        ("公司A", "關係人C"),
        ("關係人C", "供應商D")
    ])

    nx.draw(G, with_labels=True)


# =========================
# REPORT
# =========================

def generate_report(email, role, company, issues, score):

    doc = Document()

    doc.add_heading("Audit Report", 0)

    doc.add_paragraph(f"Email: {email}")
    doc.add_paragraph(f"Role: {role}")
    doc.add_paragraph(f"Company: {company}")
    doc.add_paragraph(f"Risk Score: {score}")

    doc.add_paragraph("Findings:")

    for p, i in issues:
        doc.add_paragraph(f"Page {p}: {i}")

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    return buffer


# =========================
# UI
# =========================

st.title("四大雲端查核系統 v44")

mode = st.selectbox("模式", ["登入", "註冊"])

email = st.text_input("Email")
pw = st.text_input("Password", type="password")


roles = ["Company User", "Audit Firm User", "Staff", "Manager", "Partner"]


if mode == "註冊":

    role = st.selectbox("角色", roles)
    company = st.text_input("Company")

    if st.button("註冊"):
        if register(email, pw, role, company):
            st.success("成功")
        else:
            st.error("失敗")


if mode == "登入":

    if st.button("登入"):

        if login(email, pw):

            st.session_state.auth = True

            role, company = get_user(email)

            st.session_state.role = role
            st.session_state.company = company
            st.session_state.email = email

            st.success("登入成功")

        else:
            st.error("錯誤")


# =========================
# AUTH CHECK
# =========================

if not st.session_state.get("auth"):
    st.stop()


role = st.session_state.role
company = st.session_state.company


st.subheader("Dashboard")
st.write("Role:", role)
st.write("Company:", company)


# =========================
# MULTI FILE UPLOAD
# =========================

files = st.file_uploader(
    "上傳 PDF / Word（可多選）",
    type=["pdf", "docx"],
    accept_multiple_files=True
)

all_text = ""
issues = []
score = 0


if files:

    for f in files:

        if f.name.endswith(".pdf"):
            all_text += parse_pdf(f)

        elif f.name.endswith(".docx"):
            all_text += read_word(f)


    issues = audit_engine(all_text, role)

    score = min(len(issues) * 10, 100)

    st.subheader("查核結果")

    for p, i in issues:
        st.write("Page", p, ":", i)

    st.subheader("財務圖表")
    st.pyplot(make_chart())

    st.subheader("關係人圖")
    build_graph()

    st.write("Risk Score:", score)


# =========================
# REPORT EXPORT
# =========================

if st.button("產出報告"):

    buffer = generate_report(
        email,
        role,
        company,
        issues,
        score
    )

    st.download_button(
        "下載Word報告",
        buffer,
        file_name="audit_report.docx"
    )
