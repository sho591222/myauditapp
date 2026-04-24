
import streamlit as st
import sqlite3
import hashlib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pdfplumber
from docx import Document
import io
from datetime import datetime

from sentence_transformers import SentenceTransformer
import faiss


# =====================================================
# 🏢 系統標題
# =====================================================

st.markdown("""
# 玄武會計師事務所
##財報分析及審計系統
---
""")


# =====================================================
# 🗄️ DB（完整穩定版）
# =====================================================

conn = sqlite3.connect("audit.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    email TEXT PRIMARY KEY,
    password TEXT,
    role TEXT,
    company TEXT,
    firm TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS audit_log (
    email TEXT,
    action TEXT,
    time TEXT
)
""")

conn.commit()


# =====================================================
# 🔐 hash
# =====================================================

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


# =====================================================
# 📜 audit log（不可缺）
# =====================================================

def log(email, action):

    c.execute(
        "INSERT INTO audit_log VALUES (?,?,?)",
        (email, action, datetime.now().isoformat())
    )

    conn.commit()


# =====================================================
# 🧾 註冊（完整企業版）
# =====================================================

def register(email, pw, role, company, firm):

    if not email or not pw:
        st.error("Email / 密碼不可為空")
        return

    c.execute("SELECT 1 FROM users WHERE email=?", (email,))
    if c.fetchone():
        st.error("Email 已存在")
        return

    c.execute("""
        INSERT INTO users VALUES (?,?,?,?,?)
    """, (email, hash_pw(pw), role, company, firm))

    conn.commit()

    st.success("註冊成功")


# =====================================================
# 🔐 登入
# =====================================================

def login(email, pw):

    c.execute("SELECT password FROM users WHERE email=?", (email,))
    r = c.fetchone()

    return r and r[0] == hash_pw(pw)


def get_role(email):

    c.execute("SELECT role FROM users WHERE email=?", (email,))
    r = c.fetchone()

    return r[0] if r else None


# =====================================================
# 📄 PDF解析（多檔）
# =====================================================

def parse_pdf(files):

    text = ""

    for f in files:
        with pdfplumber.open(f) as pdf:
            for p in pdf.pages:
                text += p.extract_text() or ""

    return text


# =====================================================
# 📊 年度財報
# =====================================================

def financial_data():

    return pd.DataFrame({
        "年度": ["2022", "2023", "2024"],
        "營收": [100, 120, 90],
        "獲利": [10, 15, -5],
        "資產": [200, 220, 210],
        "負債": [80, 100, 130]
    })


# =====================================================
# 🧠 AI 財務分析（完整整合）
# =====================================================

def financial_analysis(text, df, role):

    core = []
    risk = []
    audit = []
    yearly = []

    # =========================
    # 四大報表
    # =========================

    if "資產" in text:
        core.append("資產負債表分析")

    if "損益" in text:
        core.append("損益表分析")

    if "現金流" in text:
        core.append("現金流量分析")

    if "負債" in text:
        core.append("負債結構分析")


    # =========================
    # 舞弊 / 掏空 / 不實
    # =========================

    if "虛增" in text:
        risk.append("財報不實風險")

    if "資金流" in text:
        risk.append("掏空風險")

    if "關係人" in text:
        risk.append("關係人交易風險")

    if "偽造" in text:
        risk.append("舞弊風險")


    # =========================
    # 會計師查核建議
    # =========================

    audit += [
        "收入認列測試",
        "應收帳款函證",
        "存貨盤點",
        "關係人交易查核",
        "現金流測試"
    ]


    # =========================
    # 年度分析
    # =========================

    df["成長率"] = df["營收"].pct_change()

    if df["營收"].iloc[-1] < df["營收"].iloc[0]:
        yearly.append("營收下降趨勢")

    if df["獲利"].iloc[-1] < 0:
        yearly.append("出現虧損")

    if df["負債"].iloc[-1] > df["負債"].iloc[0]:
        yearly.append("負債增加")


    # =========================
    # 事務所模式加強
    # =========================

    if role == "會計師事務所":
        audit += ["加強收入查核", "加強關係人揭露"]


    return core, risk, audit, yearly, df


# =====================================================
# 📊 圖表
# =====================================================

def chart(df):

    fig, ax = plt.subplots()

    ax.plot(df["年度"], df["營收"], label="營收")
    ax.plot(df["年度"], df["獲利"], label="獲利")

    ax.legend()

    return fig


# =====================================================
# 🧠 RAG 財報問答（完整）
# =====================================================

model = SentenceTransformer("all-MiniLM-L6-v2")
docs = []
index = None


def rag_add(text):

    docs.append(text)


def rag_build():

    global index

    vecs = model.encode(docs)

    index = faiss.IndexFlatL2(len(vecs[0]))
    index.add(np.array(vecs))


def rag_query(q):

    qv = model.encode([q])

    D, I = index.search(np.array(qv), k=3)

    return [docs[i] for i in I[0]]


# =====================================================
# 📄 Word 報告（完整）
# =====================================================

def make_word(core, risk, audit, yearly, df, fig):

    doc = Document()

    doc.add_heading("v70 Production Audit Report", 0)

    doc.add_heading("財務分析", 1)
    for c in core:
        doc.add_paragraph(c)

    doc.add_heading("風險分析", 1)
    for r in risk:
        doc.add_paragraph(r)

    doc.add_heading("查核建議", 1)
    for a in audit:
        doc.add_paragraph(a)

    doc.add_heading("年度分析", 1)
    for y in yearly:
        doc.add_paragraph(y)

    img = "chart.png"
    fig.savefig(img)

    doc.add_picture(img)

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)

    return buf


# =====================================================
# 📊 Excel
# =====================================================

def make_excel(core, risk, audit, yearly, df):

    buf = io.BytesIO()

    with pd.ExcelWriter(buf, engine="openpyxl") as w:

        pd.DataFrame(core).to_excel(w, sheet_name="分析")
        pd.DataFrame(risk).to_excel(w, sheet_name="風險")
        pd.DataFrame(audit).to_excel(w, sheet_name="查核")
        pd.DataFrame(yearly).to_excel(w, sheet_name="年度")
        df.to_excel(w, sheet_name="財報")

    buf.seek(0)

    return buf


# =====================================================
# 🔐 UI（登入 / 註冊）
# =====================================================

mode = st.selectbox("入口", ["登入", "註冊"])

email = st.text_input("Email")
pw = st.text_input("密碼", type="password")

roles = ["公司使用者", "會計師事務所", "外部使用者"]


if mode == "註冊":

    role = st.selectbox("身分", roles)

    company = ""
    firm = ""

    if role == "公司使用者":
        company = st.text_input("公司名稱")

    if role == "會計師事務所":
        firm = st.text_input("事務所名稱")

    if st.button("註冊"):
        register(email, pw, role, company, firm)


if mode == "登入":

    if st.button("登入"):

        if login(email, pw):

            st.session_state.auth = True
            st.session_state.role = get_role(email)

            log(email, "login")

            st.success("登入成功")

        else:
            st.error("登入失敗")


# =====================================================
# 🚫 gate
# =====================================================

if not st.session_state.get("auth"):
    st.stop()


role = st.session_state.role

st.subheader(f"目前角色：{role}")


# =====================================================
# 📄 upload
# =====================================================

files = st.file_uploader("上傳PDF（可多選）", type=["pdf"], accept_multiple_files=True)


# =====================================================
# 🚀 main analysis
# =====================================================

if files:

    text = parse_pdf(files)

    df = financial_data()

    core, risk, audit, yearly, df = financial_analysis(text, df, role)

    fig = chart(df)


    st.subheader("財務分析")
    st.write(core)

    st.subheader("風險分析")
    st.write(risk)

    st.subheader("查核建議")
    st.write(audit)

    st.subheader("年度分析")
    st.write(yearly)

    st.pyplot(fig)


    st.download_button("Word報告", make_word(core, risk, audit, yearly, df, fig))
    st.download_button("Excel報告", make_excel(core, risk, audit, yearly, df))
