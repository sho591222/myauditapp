import streamlit as st
import sqlite3
import hashlib
import pandas as pd
import pdfplumber
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
    password TEXT,
    role TEXT
)
""")

conn.commit()


def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


def register_user(u, p, r):
    try:
        c.execute("INSERT INTO users VALUES (?,?,?)", (u, hash_pw(p), r))
        conn.commit()
        return True
    except:
        return False


def login_user(u, p):
    c.execute("SELECT password, role FROM users WHERE username=?", (u,))
    d = c.fetchone()

    if d and d[0] == hash_pw(p):
        return True, d[1]

    return False, None


# =========================
# SESSION INIT
# =========================

if "login" not in st.session_state:
    st.session_state.login = False
    st.session_state.role = None


# =========================
# UI HEADER
# =========================

st.title("玄武會計師事務所｜AI 查核系統 v27")


# =========================
# AUTH BLOCK（唯一入口）
# =========================

page = st.sidebar.radio("入口", ["登入", "註冊"])


# =========================
# REGISTER
# =========================

if page == "註冊":

    st.subheader("註冊")

    u = st.text_input("帳號")
    p = st.text_input("密碼", type="password")
    r = st.selectbox("角色", ["公司", "事務所"])

    if st.button("註冊"):

        if register_user(u, p, r):
            st.success("註冊成功")
        else:
            st.error("帳號已存在")


# =========================
# LOGIN
# =========================

if page == "登入":

    st.subheader("登入")

    u = st.text_input("帳號")
    p = st.text_input("密碼", type="password")

    if st.button("登入"):

        ok, role = login_user(u, p)

        if ok:
            st.session_state.login = True
            st.session_state.role = role
            st.success("登入成功")

        else:
            st.error("錯誤")


# =========================
# 🚨 MAIN SYSTEM (ONLY AFTER LOGIN)
# =========================

if st.session_state.login:


    st.divider()

    st.subheader("財報分析主系統")

    st.write("角色：", st.session_state.role)


    # =========================
    # PDF UPLOAD
    # =========================

    files = st.file_uploader(
        "上傳財報 PDF",
        type="pdf",
        accept_multiple_files=True
    )


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
                "liabilities": extract(t, "負債總額")
            })


    # =========================
    # ANALYSIS ENGINE
    # =========================

    if data:

        df = pd.DataFrame(data)

        st.dataframe(df)


        # chart
        fig, ax = plt.subplots()

        ax.plot(df["year"], df["revenue"], label="營收")
        ax.plot(df["year"], df["profit"], label="淨利")

        ax.legend()

        st.pyplot(fig)


        # ratio
        df["margin"] = df["profit"] / df["revenue"]
        df["leverage"] = df["liabilities"] / df["assets"]


        # =========================
        # MODE LOGIC
        # =========================

        st.subheader("分析建議")

        if st.session_state.role == "事務所":

            st.write([
                "應收帳款函證",
                "收入 cut-off test",
                "存貨盤點",
                "關係人交易查核",
                "ISA 240 舞弊風險"
            ])

        else:

            st.write([
                "獲利能力分析",
                "成本結構分析",
                "財務槓桿分析"
            ])


        # =========================
        # FRAUD SCORE
        # =========================

        score = 0

        if df["profit"].mean() < 0:
            score += 30

        if df["leverage"].mean() > 0.7:
            score += 25

        if df["margin"].mean() < 0.1:
            score += 20

        score = min(score, 100)

        st.subheader("風險分數")
        st.write(score)


        # =========================
        # ISA 700
        # =========================

        if score < 30:
            st.write("ISA 700：無保留意見")

        elif score < 60:
            st.write("ISA 700：保留意見")

        elif score < 85:
            st.write("ISA 700：否定意見風險")

        else:
            st.write("ISA 700：無法表示意見")


        # =========================
        # REPORT EXPORT
        # =========================

        if st.button("產出報告"):

            doc = Document()
            doc.add_heading("AI 查核報告 v27", 0)

            doc.add_paragraph(f"Risk Score: {score}")

            buffer = io.BytesIO()
            doc.save(buffer)
            buffer.seek(0)

            st.download_button(
                "下載報告",
                buffer,
                file_name="audit_v27.docx"
            )

else:

    st.warning("請先登入才能使用財報分析系統")
