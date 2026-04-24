import streamlit as st
import sqlite3
import hashlib
import pandas as pd
import pdfplumber
import matplotlib.pyplot as plt
import networkx as nx
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
# SESSION
# =========================

if "login" not in st.session_state:
    st.session_state.login = False
    st.session_state.role = None


# =========================
# UI
# =========================

st.title("玄武會計師事務所｜AI 財報查核系統 v26")


page = st.sidebar.radio("系統入口", ["註冊", "登入", "主系統"])


# =========================
# REGISTER
# =========================

if page == "註冊":

    st.subheader("建立帳號")

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
# MAIN SYSTEM
# =========================

if page == "主系統":

    if not st.session_state.login:
        st.warning("請先登入")
        st.stop()


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
    # ANALYSIS CORE
    # =========================

    if data:

        df = pd.DataFrame(data)

        st.dataframe(df)

        df["margin"] = df["profit"] / df["revenue"]
        df["leverage"] = df["liabilities"] / df["assets"]


        # =========================
        # CHART
        # =========================

        st.subheader("財務趨勢圖")

        fig, ax = plt.subplots()

        ax.plot(df["year"], df["revenue"], label="營收")
        ax.plot(df["year"], df["profit"], label="淨利")

        ax.legend()

        st.pyplot(fig)


        # =========================
        # FRAUD SCORE
        # =========================

        st.subheader("財報造假風險（0-100）")

        score = 0

        if df["profit"].mean() < 0:
            score += 30

        if df["leverage"].mean() > 0.7:
            score += 25

        if df["margin"].mean() < 0.1:
            score += 20

        score = min(score, 100)

        st.write("Risk Score：", score)


        # =========================
        # ISA 700 OPINION
        # =========================

        if score < 30:
            opinion = "無保留意見"
        elif score < 60:
            opinion = "保留意見"
        elif score < 85:
            opinion = "否定意見風險"
        else:
            opinion = "無法表示意見"

        st.write("ISA 700：", opinion)


        # =========================
        # COMPANY / AUDIT MODE
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
                "資本效率分析",
                "財務槓桿分析"
            ])


        # =========================
        # STOCK STRUCTURE (股譜)
        # =========================

        st.subheader("股譜分析")

        if df["assets"].mean() > df["revenue"].mean() * 2:
            st.write("資產效率異常")

        if df["profit"].mean() / df["assets"].mean() < 0.05:
            st.write("資本效率偏低")


        # =========================
        # FRAUD ANALYSIS
        # =========================

        st.subheader("掏空分析")

        if df["profit"].mean() < 0 and df["assets"].mean() > 0:
            st.write("資產增加但虧損（異常）")

        if df["liabilities"].mean() > df["assets"].mean() * 0.8:
            st.write("高負債風險")


        # =========================
        # QUALITY ANALYSIS
        # =========================

        st.subheader("財報品質")

        if df["profit"].mean() > df["revenue"].mean() * 0.3:
            st.write("利潤異常偏高")

        if df["assets"].mean() > df["revenue"].mean() * 3:
            st.write("資產過重需減損")


        # =========================
        # REPORT EXPORT
        # =========================

        if st.button("產出查核報告"):

            doc = Document()
            doc.add_heading("AI 查核報告 v26", 0)

            doc.add_paragraph(f"Risk Score: {score}")
            doc.add_paragraph(f"ISA 700: {opinion}")

            buffer = io.BytesIO()
            doc.save(buffer)
            buffer.seek(0)

            st.download_button(
                "下載報告",
                buffer,
                file_name="audit_v26.docx"
            )
