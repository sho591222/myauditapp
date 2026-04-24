
import streamlit as st
import sqlite3
import hashlib
import pandas as pd
import matplotlib.pyplot as plt
import pdfplumber
from docx import Document
import io


# =====================================================
# 🏢 系統標題（固定玄武會計師事務所）
# =====================================================

st.markdown("""
#  玄武會計師事務所
## AI 四大報表年度分析舞弊查核整合系統
---
""")


# =====================================================
# 🗄️ DB（修正版：避免 crash）
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
# 🧾 註冊（已修復：防重複）
# =====================================================

def register(email, pw, role, company, firm):

    try:

        # 🔍 防止重複
        c.execute("SELECT email FROM users WHERE email=?", (email,))
        if c.fetchone():
            st.error("Email 已存在")
            return

        c.execute(
            "INSERT INTO users VALUES (?,?,?,?,?)",
            (email, hash_pw(pw), role, company, firm)
        )

        conn.commit()

        st.success("註冊成功")

    except Exception as e:
        st.error(str(e))


# =====================================================
# 🔐 login
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
# 🧾 註冊（互斥欄位：你要求的）
# =====================================================

if mode == "註冊":

    role = st.selectbox("身分", roles)

    company = ""
    firm = ""

    if role == "公司使用者":

        company = st.text_input("公司名稱（只能填這個）")
        st.write("公司模式：不可填事務所")

    elif role == "會計師事務所":

        firm = st.text_input("會計師事務所名稱（只能填這個）")
        st.write("事務所模式：不可填公司")


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
# 📄 PDF（多選）
# =====================================================

pdf_files = st.file_uploader(
    "上傳PDF（可多選）",
    type=["pdf"],
    accept_multiple_files=True
)


# =====================================================
# 📊 Excel
# =====================================================

excel_file = st.file_uploader("上傳Excel")


# =====================================================
# 📄 PDF解析
# =====================================================

def parse_pdfs(files):

    text = ""

    for f in files:
        with pdfplumber.open(f) as pdf:
            for p in pdf.pages:
                text += p.extract_text() or ""

    return text


# =====================================================
# 📊 年度資料（含比較）
# =====================================================

def yearly_data():

    return pd.DataFrame({
        "年度": ["2022", "2023", "2024"],
        "營收": [100, 120, 90],
        "獲利": [10, 15, -5],
        "資產": [200, 220, 210],
        "負債": [80, 100, 130]
    })


# =====================================================
# 🧠 核心分析（全部整合）
# =====================================================

def analyze(text, df, role):

    core = []
    suggestions = []
    yearly_notes = []

    # =========================
    # 四大報表
    # =========================

    if "資產" in text:
        core.append(("資產負債表", "流動性分析", 70))

    if "負債" in text:
        core.append(("負債結構", "償債能力", 60))

    if "損益" in text:
        core.append(("損益表", "收入認列", 65))

    if "現金流量" in text:
        core.append(("現金流量表", "現金流分析", 55))


    # =========================
    # 舞弊 / 掏空 / 不實
    # =========================

    if "虛增" in text:
        core.append(("財報不實", "收入虛增", 90))
        suggestions.append("查：收入/應收帳款")

    if "資金流向" in text:
        core.append(("掏空", "資金異常", 85))
        suggestions.append("查：現金/關係人")

    if "偽造" in text:
        core.append(("舞弊", "文件異常", 95))
        suggestions.append("查：憑證")


    # =========================
    # 年度分析（你要的）
    # =========================

    df["營收成長率"] = df["營收"].pct_change()

    if df["營收"].iloc[-1] < df["營收"].iloc[0]:
        yearly_notes.append("營收下降")

    if df["獲利"].iloc[-1] < 0:
        yearly_notes.append("虧損出現")

    if df["負債"].iloc[-1] > df["負債"].iloc[0]:
        yearly_notes.append("負債上升")


    # =========================
    # 事務所模式
    # =========================

    if role == "會計師事務所":

        suggestions += [
            "查核：收入認列",
            "查核：應收帳款",
            "查核：存貨",
            "查核：關係人",
            "查核：現金流"
        ]


    return core, suggestions, yearly_notes, df


# =====================================================
# 📊 圖表（年度）
# =====================================================

def chart(df):

    fig, ax = plt.subplots()

    ax.plot(df["年度"], df["營收"], label="營收")
    ax.plot(df["年度"], df["獲利"], label="獲利")

    ax.legend()

    return fig


# =====================================================
# 📄 Word
# =====================================================

def make_word(core, suggestions, yearly, df, fig):

    doc = Document()

    doc.add_heading("ISA700 查核報告", 0)

    doc.add_heading("財務分析", 1)

    for c in core:
        doc.add_paragraph(str(c))

    doc.add_heading("年度分析", 1)

    for y in yearly:
        doc.add_paragraph(y)

    doc.add_paragraph(str(df))

    doc.add_heading("查核建議", 1)

    for s in suggestions:
        doc.add_paragraph(s)

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

def make_excel(core, suggestions, yearly, df):

    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:

        pd.DataFrame(core).to_excel(writer, sheet_name="分析")
        pd.DataFrame(suggestions).to_excel(writer, sheet_name="查核")
        pd.DataFrame(yearly).to_excel(writer, sheet_name="年度")
        df.to_excel(writer, sheet_name="數據")

    output.seek(0)

    return output


# =====================================================
# 🚀 主流程
# =====================================================

if pdf_files:

    text = parse_pdfs(pdf_files)

    df = yearly_data()

    core, suggestions, yearly, df = analyze(text, df, role)


    st.subheader("財務分析")
    for c in core:
        st.write(c)


    st.subheader("年度分析")
    for y in yearly:
        st.write(y)


    fig = chart(df)
    st.pyplot(fig)


    st.download_button("Word報告", make_word(core, suggestions, yearly, df, fig))
    st.download_button("Excel報告", make_excel(core, suggestions, yearly, df))
