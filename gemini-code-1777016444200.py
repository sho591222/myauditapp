import streamlit as st
import sqlite3
import hashlib
import datetime
import pandas as pd
import pdfplumber
import openpyxl
from docx import Document
import io
import networkx as nx
import matplotlib.pyplot as plt


# =====================================================
# DATABASE + AUDIT TRAIL
# =====================================================

conn = sqlite3.connect("v45.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    email TEXT PRIMARY KEY,
    password TEXT,
    role TEXT,
    company TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT,
    action TEXT,
    timestamp TEXT,
    hash TEXT
)
""")

conn.commit()


# =====================================================
# SECURITY
# =====================================================

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


def audit_hash(text):
    return hashlib.sha256(text.encode()).hexdigest()


def log_action(email, action):
    ts = str(datetime.datetime.now())
    h = audit_hash(email + action + ts)

    c.execute(
        "INSERT INTO audit_log (email, action, timestamp, hash) VALUES (?,?,?,?)",
        (email, action, ts, h)
    )
    conn.commit()


# =====================================================
# AUTH
# =====================================================

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


# =====================================================
# FILE INGESTION (PDF + EXCEL + XBRL SIMPLIFIED)
# =====================================================

def parse_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for i, p in enumerate(pdf.pages):
            text += f"PAGE {i+1}\n"
            text += p.extract_text() or ""
    return text


def parse_excel(file):

    df = pd.read_excel(file)
    return df.to_string()


# =====================================================
# RAG (SIMPLIFIED FINANCIAL GPT)
# =====================================================

def rag_query(text):

    if "revenue decline" in text.lower():
        return "Revenue下降，需檢查收入認列與cut-off"

    if "inventory" in text.lower():
        return "存貨異常，可能存在過時或減損風險"

    return "未發現重大異常，但建議進一步查核"


# =====================================================
# ISA 700 AI REPORT
# =====================================================

def isa700_ai(issues, score):

    report = ""

    report += "INDEPENDENT AUDITOR'S REPORT\n\n"

    if score > 60:
        report += "Qualified Opinion due to identified risks.\n\n"
    else:
        report += "Unqualified Opinion.\n\n"

    report += "Key Audit Matters:\n"

    for p, i in issues:
        report += f"- Page {p}: {i}\n"

    report += "\nAI Analytical Conclusion:\n"
    report += "Based on RAG analysis and anomaly detection, financial risks evaluated.\n"

    return report


# =====================================================
# AUDIT ENGINE
# =====================================================

def audit_engine(text, role):

    issues = []

    pages = text.split("PAGE")

    for i, p in enumerate(pages):

        if "應收帳款" in p:
            issues.append((i, "AR risk"))

        if "存貨" in p:
            issues.append((i, "inventory risk"))

        if "關係人" in p:
            issues.append((i, "related party"))

        if role == "Audit Firm User":

            if "收入" in p:
                issues.append((i, "cut-off test"))

    return issues


# =====================================================
# GRAPH
# =====================================================

def build_graph():

    G = nx.Graph()

    G.add_edges_from([
        ("Company A", "Subsidiary B"),
        ("Company A", "Related Party C"),
        ("Related Party C", "Vendor D")
    ])

    nx.draw(G, with_labels=True)
    plt.show()


# =====================================================
# UI
# =====================================================

st.title("v45 四大 AI 雲端審計系統")

mode = st.selectbox("Mode", ["Login", "Register"])

email = st.text_input("Email")
pw = st.text_input("Password", type="password")


roles = ["Company User", "Audit Firm User", "Staff", "Manager", "Partner"]


# =========================
# REGISTER
# =========================

if mode == "Register":

    role = st.selectbox("Role", roles)
    company = st.text_input("Company")

    if st.button("Register"):

        if register(email, pw, role, company):
            st.success("OK")
        else:
            st.error("Fail")


# =========================
# LOGIN
# =========================

if mode == "Login":

    if st.button("Login"):

        if login(email, pw):

            st.session_state.auth = True

            role, company = get_user(email)

            st.session_state.role = role
            st.session_state.company = company
            st.session_state.email = email

            log_action(email, "LOGIN")

            st.success("Logged in")

        else:
            st.error("Error")


# =========================
# AUTH
# =========================

if not st.session_state.get("auth"):
    st.stop()


role = st.session_state.role
company = st.session_state.company


st.subheader("Dashboard")
st.write("Role:", role)
st.write("Company:", company)


# =====================================================
# FILE UPLOAD (PDF / EXCEL)
# =====================================================

files = st.file_uploader(
    "Upload PDF / Excel",
    type=["pdf", "xlsx"],
    accept_multiple_files=True
)

all_text = ""
issues = []
score = 0


if files:

    for f in files:

        if f.name.endswith(".pdf"):
            all_text += parse_pdf(f)

        elif f.name.endswith(".xlsx"):
            all_text += parse_excel(f)


    issues = audit_engine(all_text, role)

    score = min(len(issues) * 10, 100)

    st.subheader("Audit Findings")

    for p, i in issues:
        st.write(p, i)

    st.subheader("RAG Analysis")

    st.write(rag_query(all_text))

    st.subheader("ISA 700 AI Report")

    st.text(isa700_ai(issues, score))

    st.subheader("Graph")

    build_graph()

    log_action(email, "UPLOAD_ANALYSIS")


# =====================================================
# AUDIT TRAIL VIEW
# =====================================================

if st.button("Show Audit Trail"):

    c.execute("SELECT * FROM audit_log")
    logs = c.fetchall()

    st.write(logs)
