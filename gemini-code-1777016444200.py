import streamlit as st
import pandas as pd
import pdfplumber
import re
import matplotlib.pyplot as plt
from docx import Document
import io
import os
import requests
import matplotlib.font_manager as fm

# =========================
# Google Sheets + Drive
# =========================
import gspread
from google.oauth2.service_account import Credentials
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive


# =========================
# 字體
# =========================

@st.cache_resource
def load_font():
    url = "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/TraditionalChinese/NotoSansCJKtc-Regular.otf"
    path = "NotoSansCJKtc-Regular.otf"

    if not os.path.exists(path):
        try:
            r = requests.get(url)
            with open(path, "wb") as f:
                f.write(r.content)
        except:
            return None
    return path


font_path = load_font()

if font_path:
    font = fm.FontProperties(fname=font_path)
    plt.rcParams["font.family"] = font.get_name()
    fm.fontManager.addfont(font_path)
    plt.rcParams["axes.unicode_minus"] = False


# =========================
# Google Sheets
# =========================

def connect_sheet():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_file(
        "service_account.json",
        scopes=scope
    )

    client = gspread.authorize(creds)
    sheet = client.open("Audit_Log").sheet1
    return sheet


def save_sheet(sheet, company, df, insights):

    for _, r in df.iterrows():
        sheet.append_row([
            company,
            r["year"],
            r["cash"],
            r["ar"],
            r["inventory"],
            r["roe"],
            r["flags"]
        ])

    for i in insights:
        sheet.append_row([company, "INSIGHT", i])


# =========================
# Google Drive
# =========================

def upload_drive(file_buffer, filename):

    gauth = GoogleAuth()
    gauth.LoadServiceConfigFile("service_account.json")
    gauth.ServiceAuth()

    drive = GoogleDrive(gauth)

    file = drive.CreateFile({'title': filename})
    file.SetContentString(file_buffer.getvalue().decode("latin1"))
    file.Upload()

    return file['id']


# =========================
# UI
# =========================

st.set_page_config(layout="wide")
st.title("四大會計師雲端查核系統（Audit Cloud System）")

with st.sidebar:
    company = st.text_input("公司名稱", "XX股份有限公司")
    auditor = st.text_input("會計師", "陳會計師")
    firm = st.text_input("事務所", "四大會計師事務所")

    st.divider()
    files = st.file_uploader("上傳財報 PDF", type=["pdf"], accept_multiple_files=True)


# =========================
# PDF 解析
# =========================

def extract(text, key):
    m = re.search(rf"{key}\s*([\d,]+)", text)
    return float(m.group(1).replace(",", "")) if m else 0


def parse_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for p in pdf.pages:
            text += p.extract_text() or ""

    return {
        "cash": extract(text, "現金"),
        "ar": extract(text, "應收帳款"),
        "inventory": extract(text, "存貨"),
        "revenue": extract(text, "營業收入"),
        "net_income": extract(text, "本期淨利"),
    }


# =========================
# 財務模型
# =========================

def financial(d):

    revenue = d["revenue"]
    ni = d["net_income"]

    assets = d["cash"] + d["ar"] + d["inventory"]
    equity = assets * 0.6 if assets else 1

    roe = (ni / revenue) * (revenue / assets) * (assets / equity) if revenue else 0

    return {"roe": roe}


# =========================
# 查核模型
# =========================

def forensic(curr, prev):

    flags = []

    if prev:
        if curr["ar"] > prev["ar"] * 1.3:
            flags.append("應收帳款異常增加")

        if curr["inventory"] > prev["inventory"] * 1.3:
            flags.append("存貨異常增加")

        if curr["cash"] < curr["net_income"]:
            flags.append("現金流弱於盈餘")

    if not flags:
        flags.append("未發現重大異常")

    return flags


# =========================
# Word report
# =========================

def build_report(company, df, insights):

    doc = Document()
    doc.add_heading("四大會計師查核報告", 0)

    doc.add_paragraph(f"公司：{company}")
    doc.add_paragraph(f"事務所：{firm}")
    doc.add_paragraph(f"會計師：{auditor}")

    for _, r in df.iterrows():
        doc.add_paragraph(f"{r['year']} | ROE:{r['roe']:.2f} | {r['flags']}")

    doc.add_heading("查核發現", level=1)

    for i in insights:
        doc.add_paragraph(i)

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf


# =========================
# 主流程
# =========================

if files:

    results = []
    prev = None
    insights = []

    for f in sorted(files, key=lambda x: x.name):

        data = parse_pdf(f)
        fin = financial(data)
        flags = forensic(data, prev)

        results.append({
            "year": f.name.replace(".pdf", ""),
            "cash": data["cash"],
            "ar": data["ar"],
            "inventory": data["inventory"],
            "roe": fin["roe"],
            "flags": ", ".join(flags)
        })

        insights.extend(flags)
        prev = data

    df = pd.DataFrame(results)

    # =========================
    # Dashboard
    # =========================

    st.subheader("財務分析")

    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots()
        ax.plot(df["year"], df["cash"], label="現金")
        ax.plot(df["year"], df["ar"], label="應收")
        ax.plot(df["year"], df["inventory"], label="存貨")
        ax.legend()
        st.pyplot(fig)

    with col2:
        fig2, ax2 = plt.subplots()
        ax2.plot(df["year"], df["roe"], marker="o", color="red")
        st.pyplot(fig2)

    st.subheader("查核發現")

    for i in insights:
        st.write("•", i)

    st.subheader("明細")
    st.dataframe(df)

    # =========================
    # Word export
    # =========================

    report = build_report(company, df, insights)

    st.sidebar.download_button(
        "下載查核報告",
        report,
        file_name=f"{company}_audit.docx"
    )

    # =========================
    # ☁️ Google Sheets
    # =========================

    if st.button("存入 Google Sheets"):

        sheet = connect_sheet()
        save_sheet(sheet, company, df, insights)

        st.success("已寫入雲端 Audit Log")

    # =========================
    # ☁️ Google Drive
    # =========================

    if st.button("上傳 Word 到 Google Drive"):

        file_id = upload_drive(report, f"{company}_audit.docx")

        st.success(f"已上傳 Google Drive：{file_id}")

else:
    st.info("請上傳 PDF 財報")
