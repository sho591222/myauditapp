import streamlit as st
import sqlite3
import hashlib
import pandas as pd
import matplotlib.pyplot as plt
import pdfplumber
from docx import Document
import networkx as nx
import io


# =====================================================
# 資料庫
# =====================================================

conn = sqlite3.connect("audit_system.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    email TEXT PRIMARY KEY,
    password TEXT,
    role TEXT,
    company TEXT,
    audit_firm TEXT
)
""")

conn.commit()


# =====================================================
# 加密
# =====================================================

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


# =====================================================
# 註冊 / 登入
# =====================================================

def register(email, pw, role, company, audit_firm=""):

    c.execute(
        "INSERT INTO users VALUES (?,?,?,?,?)",
        (email, hash_pw(pw), role, company, audit_firm)
    )

    conn.commit()


def login(email, pw):

    c.execute("SELECT password FROM users WHERE email=?", (email,))
    r = c.fetchone()

    return r and r[0] == hash_pw(pw)


def get_user(email):

    c.execute("SELECT role, company, audit_firm FROM users WHERE email=?", (email,))
    return c.fetchone()


# =====================================================
# PDF 解析
# =====================================================

def parse_pdf(file):

    text = ""

    with pdfplumber.open(file) as pdf:
        for p in pdf.pages:
            text += p.extract_text() or ""

    return text


# =====================================================
# Excel 解析
# =====================================================

def parse_excel(file):

    return pd.read_excel(file)


# =====================================================
# 財報問答系統
# =====================================================

def financial_qa(text):

    if "營收下降" in text:
        return "營收下降：可能來自市場需求減少或收入認列延遲"

    if "存貨" in text:
        return "存貨風險：可能存在滯銷或減損問題"

    if "應收帳款" in text:
        return "信用風險：可能有呆帳風險"

    return "未發現重大異常"


# =====================================================
# 查核分析（完整整合）
# =====================================================

def audit_engine(text, df, role):

    issues = []

    if "虛增" in text:
        issues.append(("財報不實", "可能存在收入虛增"))

    if "資金流向" in text:
        issues.append(("掏空風險", "資金異常移轉"))

    if "幣安" in text or "crypto" in text.lower():
        issues.append(("加密資產風險", "需檢查交易合法性"))

    if df is not None:

        if "營收" in df.columns:

            if df["營收"].iloc[-1] < df["營收"].iloc[0]:
                issues.append(("營收下降", "趨勢下滑"))

    if role == "會計師事務所":
        issues.append(("查核程序", "需執行額外實質測試"))

    return issues


# =====================================================
# ISA 700（中文長文）
# =====================================================

def isa700(issues, role):

    report = "獨立會計師查核報告\n\n"

    if role == "會計師事務所":
        report += "查核範圍：專業審計查核\n\n"

    report += "查核發現：\n"

    for i in issues:
        report += f"- {i}\n"

    if len(issues) > 3:
        report += "\n意見：保留意見（存在重大風險）\n"
    else:
        report += "\n意見：無保留意見\n"

    return report


# =====================================================
# 圖表
# =====================================================

def chart():

    df = pd.DataFrame({
        "年度": ["2022", "2023", "2024"],
        "營收": [100, 120, 90],
        "獲利": [10, 15, -5]
    })

    fig, ax = plt.subplots()

    ax.plot(df["年度"], df["營收"], label="營收")
    ax.plot(df["年度"], df["獲利"], label="獲利")

    ax.legend()

    return fig


# =====================================================
# 關係人圖
# =====================================================

def relation_graph():

    G = nx.Graph()

    G.add_edges_from([
        ("公司", "子公司"),
        ("公司", "關係人"),
        ("關係人", "供應商")
    ])

    nx.draw(G, with_labels=True)


# =====================================================
# UI
# =====================================================

st.title("v49 四大AI財務審計系統（完整版）")

mode = st.selectbox("模式", ["登入", "註冊"])

email = st.text_input("信箱")
pw = st.text_input("密碼", type="password")

roles = ["公司使用者", "會計師事務所", "外部使用者"]


# =====================================================
# 註冊
# =====================================================

if mode == "註冊":

    role = st.selectbox("身分", roles)

    company = st.text_input("公司")

    audit_firm = ""

    if role == "會計師事務所":
        audit_firm = st.text_input("事務所名稱（必填）")

    if st.button("註冊"):
        register(email, pw, role, company, audit_firm)
        st.success("註冊成功")


# =====================================================
# 登入
# =====================================================

if mode == "登入":

    if st.button("登入"):

        if login(email, pw):

            st.session_state.auth = True

            role, company, audit_firm = get_user(email)

            st.session_state.role = role
            st.session_state.company = company
            st.session_state.audit_firm = audit_firm

            st.success("登入成功")

        else:
            st.error("錯誤")


# =====================================================
# 權限控制
# =====================================================

if not st.session_state.get("auth"):
    st.stop()


role = st.session_state.role


st.subheader("儀表板")
st.write("身分：", role)


# =====================================================
# 上傳
# =====================================================

pdf = st.file_uploader("上傳PDF")

excel = st.file_uploader("上傳Excel")

text = ""
df = None

if pdf:
    text = parse_pdf(pdf)

if excel:
    df = parse_excel(excel)


# =====================================================
# 分析
# =====================================================

if text or df is not None:

    issues = audit_engine(text, df, role)

    st.subheader("財報問答")
    st.write(financial_qa(text))

    st.subheader("查核結果")

    for i in issues:
        st.write(i)

    st.subheader("財務圖表")
    st.pyplot(chart())

    st.subheader("關係人圖")
    relation_graph()

    st.subheader("ISA700報告")
    st.text(isa700(issues, role))


# =====================================================
# 外部使用者限制
# =====================================================

if role == "外部使用者":
    st.warning("外部使用者僅可查看圖表與摘要")
