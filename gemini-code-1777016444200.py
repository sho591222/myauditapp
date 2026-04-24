import streamlit as st
import pandas as pd
import pdfplumber
import re
import matplotlib.pyplot as plt
from docx import Document
import io


# =========================
# PDF解析
# =========================

def extract(text, keywords):
    for k in keywords:
        m = re.search(rf"{k}.*?([\d,]+)", text, re.DOTALL)
        if m:
            return float(m.group(1).replace(",", ""))
    return 0


def parse_pdf(file):

    text = ""

    with pdfplumber.open(file) as pdf:
        for p in pdf.pages:
            text += p.extract_text() or ""

    return {
        "bs": {
            "cash": extract(text, ["現金"]),
            "ar": extract(text, ["應收帳款"]),
            "inventory": extract(text, ["存貨"]),
            "assets": extract(text, ["資產總計"]),
            "liabilities": extract(text, ["負債總計"]),
            "equity": extract(text, ["權益總計"]),
        },
        "is": {
            "revenue": extract(text, ["營業收入"]),
            "gross_profit": extract(text, ["營業毛利"]),
            "net_income": extract(text, ["本期淨利"]),
        },
        "cf": {
            "ocf": extract(text, ["營業活動現金流量"])
        }
    }


# =========================
# 財務分析（升級）
# =========================

def financial(data):

    bs = data["bs"]
    is_ = data["is"]
    cf = data["cf"]

    assets = bs["assets"] if bs["assets"] else 1

    roe = is_["net_income"] / bs["equity"] if bs["equity"] else 0
    roa = is_["net_income"] / assets
    margin = is_["net_income"] / is_["revenue"] if is_["revenue"] else 0
    ocf_ratio = cf["ocf"] / is_["net_income"] if is_["net_income"] else 0

    return roe, roa, margin, ocf_ratio


# =========================
# 查核分析（四大版本）
# =========================

def audit(curr, prev=None):

    alerts = []

    bs = curr["bs"]
    is_ = curr["is"]
    cf = curr["cf"]

    if is_["net_income"] > 0 and cf["ocf"] < 0:
        alerts.append("盈餘品質疑慮（淨利為正但OCF為負）")

    if prev:
        if bs["ar"] > prev["bs"]["ar"] * 1.3:
            alerts.append("應收帳款異常增加")

        if bs["inventory"] > prev["bs"]["inventory"] * 1.3:
            alerts.append("存貨異常增加")

    if bs["liabilities"] > bs["equity"] * 2:
        alerts.append("高槓桿風險")

    if not alerts:
        alerts.append("未發現重大異常")

    return alerts


# =========================
# UI（完全保留你的版面）
# =========================

st.set_page_config(layout="wide")

st.title("專業鑑識會計鑑定系統：雲端串接與風險預測儀表板")


# -------------------------
# sidebar（完全不改）
# -------------------------
with st.sidebar:
    st.header("雲端硬碟連線")
    drive_path = st.text_input("請輸入雲端資料夾連結 (Google Drive)")
    if st.button("確認連線"):
        st.success("已模擬建立雲端連線")

    st.divider()

    st.header("鑑定專案資訊")
    co_name = st.text_input("受調查公司名稱", "XX股份有限公司")
    auditor = st.text_input("主辦會計師", "陳會計師 (CPA)")
    firm = st.text_input("會計師事務所", "誠信聯合會計師事務所")

    st.divider()

    files = st.file_uploader("上傳年度財報 PDF", type=["pdf"], accept_multiple_files=True)


# =========================
# 主流程
# =========================

if files:

    results = []
    prev = None

    for f in sorted(files, key=lambda x: x.name):

        data = parse_pdf(f)
        roe, roa, margin, ocf_ratio = financial(data)
        alerts = audit(data, prev)

        results.append({
            "年度": f.name.replace(".pdf", ""),
            "營收": data["is"]["revenue"],
            "應收": data["bs"]["ar"],
            "存貨": data["bs"]["inventory"],
            "ROE": roe,
            "ROA": roa,
            "利潤率": margin,
            "OCF比率": ocf_ratio,
            "結論": alerts
        })

        prev = data

    df = pd.DataFrame(results)


    # =========================
    # 圖表區（版面完全保留）
    # =========================

    st.subheader(f"{co_name} 鑑定圖表分析")

    col1, col2 = st.columns(2)

    with col1:
        fig1, ax1 = plt.subplots()
        ax1.plot(df["年度"], df["營收"], label="營收")
        ax1.plot(df["年度"], df["應收"], label="應收")
        ax1.plot(df["年度"], df["存貨"], label="存貨")
        ax1.set_title("資產負債表趨勢")
        ax1.legend()
        st.pyplot(fig1)

    with col2:
        fig2, ax2 = plt.subplots()
        ax2.plot(df["年度"], df["ROE"], label="ROE")
        ax2.plot(df["年度"], df["ROA"], label="ROA")
        ax2.set_title("獲利能力分析")
        ax2.legend()
        st.pyplot(fig2)


    # =========================
    # 查核結果（原區塊）
    # =========================

    st.subheader("查核發現")

    for r in results:
        st.write(r["年度"])
        st.write(r["結論"])


    # =========================
    # 明細表
    # =========================

    st.subheader("明細資料")

    st.dataframe(df)


    # =========================
    # Word報告（保留）
    # =========================

    doc = Document()
    doc.add_heading("鑑識會計查核報告", 0)

    doc.add_paragraph(f"公司：{co_name}")
    doc.add_paragraph(f"事務所：{firm}")
    doc.add_paragraph(f"會計師：{auditor}")

    for r in results:
        doc.add_paragraph(f"{r['年度']}：{r['結論']}")

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)

    st.sidebar.download_button(
        "下載 Word 報告",
        buf,
        file_name=f"{co_name}_查核報告.docx"
    )

else:
    st.info("請上傳年度財報 PDF")
