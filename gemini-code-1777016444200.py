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

st.title("玄武會計師事務所｜雙用途企業查核系統 v14")


# =========================
# BRAND HEADER
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


st.sidebar.subheader("登入")

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
# DATABASE
# =========================

conn = sqlite3.connect("v14.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT,
    account TEXT,
    value REAL,
    created_at TEXT
)
""")

conn.commit()


# =========================
# ROLE ENGINE（核心）
# =========================

def mode():

    if st.session_state.role == "audit":
        return "事務所模式"
    return "公司模式"


# =========================
# COMPANY MODE（禁止 audit 用語）
# =========================

def company_analysis(value):

    result = []

    if value < 1000000:
        result.append("營運規模可持續優化")

    if value > 5000000:
        result.append("建議檢視資本配置效率")

    return result


# =========================
# AUDIT MODE（查核模式）
# =========================

def audit_analysis(value):

    result = []

    if value > 1000000:
        result.append("應收帳款增加需執行函證程序")

    if value > 5000000:
        result.append("需進一步執行實質性查核程序")

    return result


# =========================
# MAIN SYSTEM
# =========================

if st.session_state.login:

    st.subheader("目前模式：" + mode())

    company = st.text_input("公司名稱", "ABC股份有限公司")

    account = st.selectbox("科目", ["應收帳款", "存貨", "營收"])

    value = st.number_input("金額", 0)

    if st.button("執行分析"):

        # store data
        c.execute("""
            INSERT INTO data (company, account, value, created_at)
            VALUES (?, ?, ?, ?)
        """, (company, account, value, str(datetime.datetime.now())))

        conn.commit()

        st.subheader("分析結果")

        if mode() == "公司模式":
            st.write(company_analysis(value))
        else:
            st.write(audit_analysis(value))


# =========================
# DATABASE VIEW
# =========================

st.subheader("系統資料庫")

df = pd.read_sql_query("SELECT * FROM data", conn)

st.dataframe(df)


# =========================
# WORKING PAPER EXPORT
# =========================

if st.button("下載工作底稿"):

    doc = Document()

    doc.add_heading("雙用途企業查核系統 v14", 0)

    doc.add_paragraph("Engagement Information")
    doc.add_paragraph("會計師事務所：" + firm_name)
    doc.add_paragraph("主辦會計師：" + partner)
    doc.add_paragraph("查核日期：" + str(report_date))
    doc.add_paragraph("模式：" + mode())

    doc.add_paragraph("資料")

    for row in df.values:
        doc.add_paragraph(str(row))

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    st.download_button(
        "下載工作底稿",
        buffer,
        file_name="玄武會計師事務所_v14.docx"
    )
