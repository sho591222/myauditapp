
import streamlit as st
import sqlite3
import hashlib
import pandas as pd
import matplotlib.pyplot as plt
import pdfplumber
from docx import Document
import io


# =====================================================
# 🏢 標題
# =====================================================

st.markdown("""
# 玄武會計師事務所
## AI 財務分析查核系統 ##
---
""")


# =====================================================
#  DB（修正版：穩定不爆）
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

conn.commit()


# =====================================================
# 🔐 hash
# =====================================================

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


# =====================================================
# 🧾 註冊（已修復：不再 OperationalError）
# =====================================================

def register(email, pw, role, company, firm):

    # 防呆：空值
    if not email or not pw:
        st.error("Email 或密碼不可為空")
        return

    # 已存在
    c.execute("SELECT 1 FROM users WHERE email=?", (email,))
    if c.fetchone():
        st.error("Email 已存在")
        return

    # 寫入
    c.execute("""
        INSERT INTO users (email, password, role, company, firm)
        VALUES (?, ?, ?, ?, ?)
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
# 🧾 UI（登入 / 註冊）
# =====================================================

mode = st.selectbox("入口", ["登入", "註冊"])

email = st.text_input("Email")
pw = st.text_input("密碼", type="password")

roles = ["公司使用者", "會計師事務所", "外部使用者"]


# =====================================================
# 🧾 註冊（互斥邏輯）
# =====================================================

if mode == "註冊":

    role = st.selectbox("身分", roles)

    company = ""
    firm = ""

    if role == "公司使用者":
        company = st.text_input("公司名稱（只能填這個）")

    elif role == "會計師事務所":
        firm = st.text_input("會計師事務所名稱（只能填這個）")


    if st.button("註冊"):
        register(email, pw, role, company, firm)


# =====================================================
# 🔐 登入
# =====================================================

if mode == "登入":

    if st.button("登入"):

        if login(email, pw):

            st.session_state.auth = True
            st.session_state.role = get_role(email)

            st.success("登入成功")

        else:
            st.error("登入失敗")


# =====================================================
# 🚫 保護
# =====================================================

if not st.session_state.get("auth"):
    st.stop()


role = st.session_state.role

st.subheader(f"目前身分：{role}")


# =====================================================
# 📄 PDF 多檔
# =====================================================

files = st.file_uploader("上傳PDF（可多選）", type=["pdf"], accept_multiple_files=True)


# =====================================================
# 📄 PDF解析
# =====================================================

def parse_pdf(files):

    text = ""

    for f in files:
        with pdfplumber.open(f) as pdf:
            for p in pdf.pages:
                text += p.extract_text() or ""

    return text


# =====================================================
# 📊 年度資料
# =====================================================

def yearly_df():

    return pd.DataFrame({
        "年度": ["2022", "2023", "2024"],
        "營收": [100, 120, 90],
        "獲利": [10, 15, -5],
        "資產": [200, 220, 210],
        "負債": [80, 100, 130]
    })


# =====================================================
# 🧠 分析引擎
# =====================================================

def analyze(text, df, role):

    core = []
    risk = []
    yearly = []

    # 四大報表
    if "資產" in text:
        core.append(("資產負債表", "流動性"))

    if "損益" in text:
        core.append(("損益表", "獲利能力"))

    if "現金流" in text:
        core.append(("現金流量表", "現金狀況"))

    if "負債" in text:
        core.append(("負債表", "償債能力"))


    # 舞弊
    if "虛增" in text:
        risk.append("財報不實風險")

    if "資金流" in text:
        risk.append("掏空風險")

    if "偽造" in text:
        risk.append("舞弊風險")


    # 年度分析
    df["成長率"] = df["營收"].pct_change()

    if df["營收"].iloc[-1] < df["營收"].iloc[0]:
        yearly.append("營收下降")

    if df["獲利"].iloc[-1] < 0:
        yearly.append("虧損出現")

    if df["負債"].iloc[-1] > df["負債"].iloc[0]:
        yearly.append("負債增加")


    # 事務所模式加強
    if role == "會計師事務所":
        risk += ["查核：收入", "查核：應收帳款", "查核：關係人"]


    return core, risk, yearly, df


# =====================================================
# 📊 圖表
# =====================================================

def chart(df):

    fig, ax = plt.subplots()

    ax.plot(df["年度"], df["營收"])
    ax.plot(df["年度"], df["獲利"])

    return fig


# =====================================================
# 📄 Word
# =====================================================

def make_word(core, risk, yearly, df, fig):

    doc = Document()

    doc.add_heading("查核報告 v67", 0)

    doc.add_heading("財務分析", 1)
    for c in core:
        doc.add_paragraph(str(c))

    doc.add_heading("風險分析", 1)
    for r in risk:
        doc.add_paragraph(r)

    doc.add_heading("年度分析", 1)
    for y in yearly:
        doc.add_paragraph(y)

    doc.add_paragraph(str(df))

    img = "chart.png"
    fig.savefig(img)

    doc.add_picture(img)

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    return buffer


# =====================================================
# 📊 Excel
# =====================================================

def make_excel(core, risk, yearly, df):

    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:

        pd.DataFrame(core).to_excel(writer, sheet_name="分析")
        pd.DataFrame(risk).to_excel(writer, sheet_name="風險")
        pd.DataFrame(yearly).to_excel(writer, sheet_name="年度")
        df.to_excel(writer, sheet_name="數據")

    output.seek(0)

    return output


# =====================================================
# 🚀 主流程
# =====================================================

if files:

    text = parse_pdf(files)

    df = yearly_df()

    core, risk, yearly, df = analyze(text, df, role)


    st.subheader("財務分析")
    st.write(core)

    st.subheader("風險分析")
    st.write(risk)

    st.subheader("年度分析")
    st.write(yearly)

    st.pyplot(chart(df))


    st.download_button("Word報告", make_word(core, risk, yearly, df, chart(df)))
    st.download_button("Excel報告", make_excel(core, risk, yearly, df))
