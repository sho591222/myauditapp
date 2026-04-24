import streamlit as st
import sqlite3
import hashlib
import random
import string
import pdfplumber
import pandas as pd
import matplotlib.pyplot as plt
import io
import re
from docx import Document
from docx.shared import Inches


# =====================================================
# 1️⃣ DATABASE
# =====================================================

conn = sqlite3.connect("audit.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    email TEXT PRIMARY KEY,
    password TEXT
)
""")

conn.commit()


# =====================================================
# 2️⃣ AUTH CORE
# =====================================================

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


def valid_email(email):
    return isinstance(email, str) and "@" in email and "." in email


def register(email, pw):

    if not valid_email(email):
        return "invalid"

    try:
        c.execute("INSERT INTO users VALUES (?,?)", (email, hash_pw(pw)))
        conn.commit()
        return "ok"
    except:
        return "exists"


def login(email, pw):

    c.execute("SELECT password FROM users WHERE email=?", (email,))
    r = c.fetchone()

    return r and r[0] == hash_pw(pw)


def reset_password(email):

    c.execute("SELECT email FROM users WHERE email=?", (email,))
    r = c.fetchone()

    if not r:
        return False, None

    new_pw = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

    c.execute("UPDATE users SET password=? WHERE email=?",
              (hash_pw(new_pw), email))
    conn.commit()

    return True, new_pw


# =====================================================
# 3️⃣ SESSION
# =====================================================

if "auth" not in st.session_state:
    st.session_state.auth = False

if "role" not in st.session_state:
    st.session_state.role = None

if "page" not in st.session_state:
    st.session_state.page = "login"


# =====================================================
# 4️⃣ UI HEADER
# =====================================================

st.title("玄武會計師事務所｜AI 四大查核系統 v40（完整企業版）")


# =====================================================
# 5️⃣ NAVIGATION
# =====================================================

st.sidebar.title("系統")

if st.sidebar.button("註冊"):
    st.session_state.page = "register"

if st.sidebar.button("登入"):
    st.session_state.page = "login"

if st.sidebar.button("忘記密碼"):
    st.session_state.page = "reset"


# =====================================================
# 6️⃣ REGISTER
# =====================================================

if st.session_state.page == "register":

    st.subheader("註冊（Email）")

    email = st.text_input("Email")
    pw = st.text_input("密碼", type="password")

    if st.button("註冊"):

        res = register(email, pw)

        if res == "ok":
            st.success("註冊成功")

        elif res == "exists":
            st.error("Email已存在")

        else:
            st.error("Email格式錯誤")


# =====================================================
# 7️⃣ LOGIN
# =====================================================

if st.session_state.page == "login":

    st.subheader("登入")

    email = st.text_input("Email")
    pw = st.text_input("密碼", type="password")

    if st.button("登入"):

        if login(email, pw):

            st.session_state.auth = True
            st.session_state.email = email

            st.success("登入成功")

        else:
            st.error("錯誤")


# =====================================================
# 8️⃣ RESET PASSWORD (EMAIL SIMULATION)
# =====================================================

if st.session_state.page == "reset":

    st.subheader("忘記密碼")

    email = st.text_input("Email")

    if st.button("寄送重設密碼"):

        ok, new_pw = reset_password(email)

        if ok:
            st.success("已重設（模擬Email）")
            st.info(f"新密碼：{new_pw}")
        else:
            st.error("Email不存在")


# =====================================================
# 9️⃣ AUTH BLOCK
# =====================================================

if not st.session_state.auth:
    st.warning("請先登入")
    st.stop()


# =====================================================
# 🔟 ROLE SELECT
# =====================================================

st.subheader("選擇模式")

role = st.selectbox("角色", ["公司內部", "會計師事務所"])

st.session_state.role = role


# =====================================================
# 11️⃣ PDF UPLOAD
# =====================================================

files = st.file_uploader("上傳財報PDF", type="pdf", accept_multiple_files=True)


# =====================================================
# 12️⃣ PDF ANALYSIS ENGINE
# =====================================================

def parse(file):

    text = ""

    with pdfplumber.open(file) as pdf:
        for i, p in enumerate(pdf.pages):

            page_text = p.extract_text() or ""

            text += f"\nPAGE {i+1}\n" + page_text

    return text


def detect(text):

    issues = []

    pages = re.split(r"PAGE \d+", text)

    for i, p in enumerate(pages):

        page_num = i

        if "應收帳款" in p:
            issues.append((page_num, "應收帳款異常"))

        if "存貨" in p:
            issues.append((page_num, "存貨風險"))

        if "關係人" in p:
            issues.append((page_num, "關係人交易"))

        if st.session_state.role == "會計師事務所":

            if "收入" in p:
                issues.append((page_num, "cut-off test"))

            if "費用" in p:
                issues.append((page_num, "完整性測試"))

        else:

            if "費用" in p:
                issues.append((page_num, "費用異常"))

    return issues


# =====================================================
# 13️⃣ ANALYSIS OUTPUT
# =====================================================

if files:

    all_text = ""

    for f in files:
        all_text += parse(f)

    issues = detect(all_text)

    st.subheader("查核發現（頁面級）")

    for p, i in issues:
        st.write(f"第 {p} 頁 → {i}")


# =====================================================
# 14️⃣ SIMPLE FINANCIAL CHART
# =====================================================

df = pd.DataFrame({
    "year": ["2021", "2022", "2023"],
    "revenue": [1000, 1300, 900],
    "profit": [100, 150, -50]
})

fig, ax = plt.subplots()
ax.plot(df["year"], df["revenue"], label="營收")
ax.plot(df["year"], df["profit"], label="淨利")
ax.legend()

st.pyplot(fig)


# =====================================================
# 15️⃣ RISK SCORE
# =====================================================

score = min(len(issues) * 10, 100)

st.subheader("風險分數")
st.write(score)


# =====================================================
# 16️⃣ WORD REPORT (FULL)
# =====================================================

if st.button("產出查核報告"):

    doc = Document()

    doc.add_heading("AI 四大查核報告 v40", 0)

    doc.add_paragraph(f"帳號：{st.session_state.email}")
    doc.add_paragraph(f"模式：{st.session_state.role}")
    doc.add_paragraph(f"風險分數：{score}")

    doc.add_paragraph("\n查核發現")

    for p, i in issues:
        doc.add_paragraph(f"第 {p} 頁 → {i}")

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    st.download_button(
        "下載Word報告",
        buffer,
        file_name="audit_v40.docx"
    )
