import streamlit as st
import pandas as pd
import sqlite3
import datetime
from docx import Document
import io


# =========================
# SYSTEM CONFIG
# =========================

st.set_page_config(layout="wide")
st.title("玄武會計師事務所｜雲端企業查核系統 v13")


# =========================
# ENGAGEMENT HEADER
# =========================

firm_name = "玄武會計師事務所"

st.sidebar.subheader("查核資訊")

partner = st.sidebar.text_input("主辦會計師", "玄武主持會計師")
report_date = st.sidebar.date_input("查核日期")


# =========================
# LOGIN SYSTEM
# =========================

USERS = {
    "audit": {"pw": "1234", "role": "audit"},
    "client": {"pw": "1234", "role": "company"}
}

if "login" not in st.session_state:
    st.session_state.login = False


st.sidebar.subheader("登入系統")

user = st.sidebar.text_input("帳號")
pw = st.sidebar.text_input("密碼", type="password")

if st.sidebar.button("登入"):
    if user in USERS and USERS[user]["pw"] == pw:
        st.session_state.login = True
        st.session_state.role = USERS[user]["role"]
        st.success("登入成功")
    else:
        st.error("登入失敗")


# =========================
# DATABASE LAYER
# =========================

conn = sqlite3.connect("v13.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS evidence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT,
    account TEXT,
    value REAL,
    risk TEXT,
    created_at TEXT
)
""")

conn.commit()


# =========================
# EVIDENCE ENGINE v6
# =========================

class EvidenceEngine:

    def create(self, company, account, value):

        risk = "High" if value > 1000000 else "Low"

        c.execute("""
            INSERT INTO evidence (company, account, value, risk, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            company,
            account,
            value,
            risk,
            str(datetime.datetime.now())
        ))

        conn.commit()

        return {
            "company": company,
            "account": account,
            "value": value,
            "risk": risk,
            "isa": self.map_isa(account),
            "procedure": self.procedure(account),
            "conclusion": self.conclusion(value)
        }


    def map_isa(self, account):

        if account == "應收帳款":
            return ["ISA 315", "ISA 505", "ISA 330"]

        if account == "營收":
            return ["ISA 240"]

        return ["ISA 330"]


    def procedure(self, account):

        if account == "應收帳款":
            return ["函證", "期後收款測試", "合約查核"]

        if account == "存貨":
            return ["盤點", "成本測試"]

        return ["基本查核程序"]


    def conclusion(self, value):

        if value > 1000000:
            return "需進一步實質性查核"
        return "可接受"


engine = EvidenceEngine()


# =========================
# ROLE SYSTEM
# =========================

def mode():
    if st.session_state.role == "audit":
        return "事務所模式"
    return "公司模式"


# =========================
# MAIN SYSTEM
# =========================

if st.session_state.login:

    st.subheader("系統模式：" + mode())

    company = st.text_input("公司名稱", "ABC股份有限公司")

    account = st.selectbox("科目", ["應收帳款", "存貨", "營收"])

    value = st.number_input("金額", 0)

    if st.button("執行分析"):

        result = engine.create(company, account, value)

        st.subheader("查核結果")

        st.write(result)


# =========================
# DATABASE VIEW
# =========================

st.subheader("查核資料庫")

df = pd.read_sql_query("SELECT * FROM evidence", conn)

st.dataframe(df)


# =========================
# WORKING PAPER EXPORT
# =========================

if st.button("下載工作底稿"):

    doc = Document()

    doc.add_heading("雲端企業查核工作底稿 v13", 0)

    doc.add_paragraph("Engagement Information")
    doc.add_paragraph("會計師事務所：" + firm_name)
    doc.add_paragraph("主辦會計師：" + partner)
    doc.add_paragraph("查核日期：" + str(report_date))
    doc.add_paragraph("模式：" + mode())

    doc.add_paragraph("查核資料")

    for row in df.values:
        doc.add_paragraph(str(row))

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    st.download_button(
        "下載工作底稿",
        buffer,
        file_name="玄武會計師事務所_v13.docx"
    )
