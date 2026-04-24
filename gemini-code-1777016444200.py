import streamlit as st
import sqlite3
import hashlib
import pdfplumber
import pandas as pd
import matplotlib.pyplot as plt
import io
import re
from docx import Document


# =========================
# DATABASE
# =========================

conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT
)
""")

conn.commit()


# =========================
# HASH
# =========================

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


# =========================
# REGISTER
# =========================

def register(u, p):

    try:
        c.execute("INSERT INTO users VALUES (?,?)", (u, hash_pw(p)))
        conn.commit()
        return True
    except:
        return False


# =========================
# LOGIN
# =========================

def login(u, p):

    c.execute("SELECT password FROM users WHERE username=?", (u,))
    d = c.fetchone()

    if d and d[0] == hash_pw(p):
        return True

    return False


# =========================
# SESSION
# =========================

if "auth" not in st.session_state:
    st.session_state.auth = False

if "role" not in st.session_state:
    st.session_state.role = None

if "step" not in st.session_state:
    st.session_state.step = "login"


# =========================
# UI TITLE
# =========================

st.title("玄武會計師事務所｜AI 查核系統 v31（完整門禁版）")


# =========================
# STEP 1 - REGISTER
# =========================

if st.session_state.step == "register":

    st.subheader("註冊")

    u = st.text_input("帳號")
    p = st.text_input("密碼", type="password")

    if st.button("建立帳號"):

        if register(u, p):
            st.success("註冊成功，請登入")
            st.session_state.step = "login"
        else:
            st.error("帳號已存在")


# =========================
# STEP 2 - LOGIN
# =========================

if st.session_state.step == "login":

    st.subheader("登入")

    u = st.text_input("帳號")
    p = st.text_input("密碼", type="password")

    if st.button("登入"):

        if login(u, p):

            st.session_state.auth = True
            st.success("登入成功")

            st.session_state.step = "role"

        else:
            st.error("帳號或密碼錯誤")


# =========================
# STEP 3 - ROLE SELECT
# =========================

if st.session_state.step == "role":

    st.subheader("選擇使用者類型（重要）")

    role = st.selectbox("角色", ["公司內部", "會計師事務所"])

    if st.button("進入系統"):

        st.session_state.role = role
        st.session_state.step = "main"


# =========================
# BLOCK MAIN IF NOT AUTH
# =========================

if not st.session_state.auth:
    st.warning("請先登入")
    st.stop()


# =========================
# STEP 4 - MAIN SYSTEM
# =========================

if st.session_state.step == "main":

    st.subheader("財報分析系統")

    st.write("目前角色：", st.session_state.role)


    files = st.file_uploader("上傳PDF", type="pdf", accept_multiple_files=True)


    def parse(file):

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


    data = []


    if files:

        for f in files:

            t = parse(f)

            data.append({
                "year": f.name,
                "revenue": extract(t, "營業收入"),
                "profit": extract(t, "本期淨利"),
                "assets": extract(t, "資產總額"),
                "liabilities": extract(t, "負債總額"),
                "ar": extract(t, "應收帳款"),
                "inventory": extract(t, "存貨")
            })


    if data:

        df = pd.DataFrame(data)

        st.dataframe(df)


        # =========================
        # CHART
        # =========================

        fig, ax = plt.subplots()

        ax.plot(df["year"], df["revenue"], label="營收")
        ax.plot(df["year"], df["profit"], label="淨利")

        ax.legend()

        st.pyplot(fig)


        # =========================
        # MODE LOGIC
        # =========================

        st.subheader("查核建議")

        if st.session_state.role == "會計師事務所":

            st.write([
                "收入 cut-off",
                "應收帳款函證",
                "存貨盤點",
                "關係人交易查核",
                "負債完整性"
            ])

        else:

            st.write([
                "應收帳款回收性",
                "存貨風險",
                "費用異常",
                "現金流量分析"
            ])


        # =========================
        # SCORE
        # =========================

        score = 0

        if df["profit"].mean() < 0:
            score += 30

        if df["liabilities"].mean() > df["assets"].mean() * 0.7:
            score += 25

        score = min(score, 100)

        st.write("風險分數：", score)


        # =========================
        # REPORT EXPORT
        # =========================

        if st.button("產出報告"):

            doc = Document()

            doc.add_heading("AI 查核報告 v31", 0)

            doc.add_paragraph(f"角色：{st.session_state.role}")
            doc.add_paragraph(f"風險分數：{score}")

            buffer = io.BytesIO()
            doc.save(buffer)
            buffer.seek(0)

            st.download_button(
                "下載報告",
                buffer,
                file_name="audit_v31.docx"
            )


# =========================
# NAVIGATION
# =========================

st.sidebar.write("流程控制")

if st.sidebar.button("去註冊"):
    st.session_state.step = "register"

if st.sidebar.button("去登入"):
    st.session_state.step = "login"
