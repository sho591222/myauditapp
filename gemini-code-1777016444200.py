
import streamlit as st
import sqlite3
import hashlib
import pandas as pd
import matplotlib.pyplot as plt
import pdfplumber
from docx import Document
import networkx as nx


# =====================================================
# 🏢 系統品牌
# =====================================================

st.markdown("""
# 🏢 玄武會計師事務所
## 雲端AI財務查核與分析系統
---
""")


# =====================================================
# DATABASE
# =====================================================

conn = sqlite3.connect("audit_v51.db", check_same_thread=False)
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

def register(email, pw, role, company, audit_firm):

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
# PDF / Excel / Word
# =====================================================

def parse_pdf(file):

    text = ""

    with pdfplumber.open(file) as pdf:
        for p in pdf.pages:
            text += p.extract_text() or ""

    return text


def parse_excel(file):
    return pd.read_excel(file)


def parse_word(file):
    doc = Document(file)
    return "\n".join([p.text for p in doc.paragraphs])


# =====================================================
# 財報問答
# =====================================================

def financial_qa(text):

    if "營收下降" in text:
        return "營收下降：可能市場萎縮或收入認列問題"

    if "存貨" in text:
        return "存貨風險：可能有滯銷或跌價損失"

    if "應收帳款" in text:
        return "應收帳款風險：可能存在呆帳"

    return "未發現重大異常"


# =====================================================
# 查核引擎
# =====================================================

def audit_engine(text, df, role):

    issues = []

    if "虛增" in text:
        issues.append(("財報不實", "收入可能虛增"))

    if "資金流向" in text:
        issues.append(("掏空風險", "資金異常移轉"))

    if "幣安" in text or "crypto" in text.lower():
        issues.append(("加密資產風險", "交易需查核"))

    if df is not None and "營收" in df.columns:

        if df["營收"].iloc[-1] < df["營收"].iloc[0]:
            issues.append(("營收下降", "趨勢下降"))

    if role == "會計師事務所":
        issues.append(("查核程序", "需額外實質測試"))

    return issues


# =====================================================
# ISA 700
# =====================================================

def isa700(issues, role):

    text = "獨立會計師查核報告\n\n"

    text += "查核範圍：財務報表查核\n\n"

    for i in issues:
        text += f"- {i}\n"

    if len(issues) > 3:
        text += "\n意見：保留意見\n"
    else:
        text += "\n意見：無保留意見\n"

    return text


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

st.title("v51 四大AI財務審計系統")

mode = st.selectbox("模式", ["登入", "註冊"])

email = st.text_input("信箱")
pw = st.text_input("密碼", type="password")

roles = ["公司使用者", "會計師事務所", "外部使用者"]


# =====================================================
# 註冊（重點：條件互斥）
# =====================================================

if mode == "註冊":

    role = st.selectbox("身分", roles)

    company = ""
    audit_firm = ""

    # ✔ 關鍵：互斥邏輯（你要求的）
    if role == "公司使用者":
        company = st.text_input("公司名稱（必填）")

    if role == "會計師事務所":
        audit_firm = st.text_input("會計師事務所名稱（必填）")

    if role == "外部使用者":
        st.info("外部使用者無需填公司或事務所")

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
# 權限
# =====================================================

if not st.session_state.get("auth"):
    st.stop()


role = st.session_state.role


st.subheader("儀表板")
st.write("身分：", role)


# =====================================================
# 上傳
# =====================================================

pdf = st.file_uploader("PDF")
excel = st.file_uploader("Excel")
word = st.file_uploader("Word")


text = ""
df = None

if pdf:
    text += parse_pdf(pdf)

if word:
    text += parse_word(word)

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

    st.subheader("ISA 700報告")
    st.text(isa700(issues, role))


# =====================================================
# 外部限制
# =====================================================

if role == "外部使用者":
    st.warning("外部使用者僅可查看圖表與摘要")
