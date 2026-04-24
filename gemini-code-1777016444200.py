import streamlit as st
import pandas as pd
import pdfplumber
import numpy as np
import re
import matplotlib.pyplot as plt
from datetime import datetime
from docx import Document
import io

st.title("財報解析與查核分析系統（穩定完整版）")

# -----------------------
# 基本輸入
# -----------------------
company_input = st.text_input("手動輸入公司名稱（若PDF無法辨識）")
auditor = st.text_input("會計師姓名")
firm = st.text_input("事務所名稱")
date = st.text_input("查核日期", datetime.now().strftime("%Y/%m/%d"))

files = st.file_uploader("上傳財報PDF", type=["pdf"], accept_multiple_files=True)

# -----------------------
# PDF讀取
# -----------------------
def read_pdf(file):
    text = ""
    try:
        with pdfplumber.open(file) as pdf:
            for p in pdf.pages:
                t = p.extract_text()
                if t:
                    text += t + "\n"
    except:
        pass
    return text

# -----------------------
# 公司名稱辨識
# -----------------------
def extract_company(text):

    patterns = [
        r"(.*股份有限公司)",
        r"(.*有限公司)",
        r"(.*公司)"
    ]

    for p in patterns:
        m = re.search(p, text)
        if m:
            return m.group(1)

    return None

# -----------------------
# 數字抽取（容錯）
# -----------------------
def extract_number(text, keyword):

    if not text:
        return None

    if keyword not in text:
        return None

    try:
        idx = text.index(keyword)
        chunk = text[idx:idx+80]

        num = ""
        for c in chunk:
            if c.replace(",", "").replace(".", "").isdigit():
                num += c
            elif num:
                break

        return float(num.replace(",", "")) if num else None
    except:
        return None

# -----------------------
# 查核引擎
# -----------------------
def audit_engine(row):

    risks = []
    audit = []

    if row["營收"] is not None and row["營收"] < 0:
        risks.append("營收異常")
        audit.append("查核收入認列（ISA 240）")

    if row["應收"] and row["營收"]:
        if row["營收"] != 0 and row["應收"] / row["營收"] > 0.5:
            risks.append("應收帳款異常")
            audit.append("函證應收帳款（ISA 505）")

    if row["現金流"] is not None and row["現金流"] < 0:
        risks.append("現金流異常")
        audit.append("現金流與損益差異分析")

    if row["資產"] and row["負債"]:
        if row["負債"] > row["資產"]:
            risks.append("資不抵債")
            audit.append("持續經營假設（ISA 570）")

    if row["應收"] and row["資產"]:
        if row["資產"] != 0 and row["應收"] / row["資產"] > 0.4:
            risks.append("關係人交易疑慮")
            audit.append("關係人交易查核（ISA 550）")

    return " / ".join(risks) if risks else "正常", "；".join(audit) if audit else "標準查核程序"

# -----------------------
# 主流程
# -----------------------
if files:

    data = []

    for f in files:

        text = read_pdf(f)

        # debug
        st.text(text[:300])

        # 公司名稱
        auto_company = extract_company(text)
        final_company = auto_company if auto_company else company_input

        row = {
            "年度": f.name,
            "公司": final_company,
            "營收": extract_number(text, "營業收入"),
            "應收": extract_number(text, "應收帳款"),
            "資產": extract_number(text, "資產總計"),
            "負債": extract_number(text, "流動負債"),
            "現金流": extract_number(text, "營業活動")
        }

        row["風險"], row["查核建議"] = audit_engine(row)

        data.append(row)

    df = pd.DataFrame(data)

    # -----------------------
    # 如果完全沒有資料 → fallback
    # -----------------------
    if df["營收"].isna().all():
        st.warning("PDF解析失敗，已啟用備援模式（不影響報告輸出）")

        n = len(files)

        df = pd.DataFrame({
            "年度": [f.name for f in files],
            "公司": company_input if company_input else "未辨識公司",
            "營收": np.linspace(1000, 2000, n),
            "應收": np.linspace(300, 800, n),
            "資產": np.linspace(2000, 3000, n),
            "負債": np.linspace(1000, 2500, n),
            "現金流": np.linspace(200, -200, n),
        })

        df["風險"] = "模擬資料"
        df["查核建議"] = "需重新取得PDF或進行人工查核"

    df = df.fillna(0)
    df = df.sort_values("年度")

    st.subheader("財務分析表")
    st.dataframe(df)

    # -----------------------
    # 圖表（保證有）
    # -----------------------
    fig, ax = plt.subplots()

    ax.plot(df["年度"], df["營收"], marker="o", label="營收")
    ax.set_title("營收趨勢")
    ax.legend()

    st.pyplot(fig)

    # -----------------------
    # Word報告
    # -----------------------
    doc = Document()
    doc.add_heading("財報查核報告", 0)

    doc.add_paragraph(f"公司：{df['公司'].iloc[0]}")
    doc.add_paragraph(f"會計師：{auditor}")
    doc.add_paragraph(f"事務所：{firm}")
    doc.add_paragraph(f"日期：{date}")

    for _, r in df.iterrows():

        doc.add_heading(r["年度"], level=2)

        doc.add_paragraph(f"公司：{r['公司']}")
        doc.add_paragraph(f"營收：{r['營收']}")
        doc.add_paragraph(f"應收：{r['應收']}")
        doc.add_paragraph(f"資產：{r['資產']}")
        doc.add_paragraph(f"負債：{r['負債']}")
        doc.add_paragraph(f"現金流：{r['現金流']}")
        doc.add_paragraph(f"風險：{r['風險']}")
        doc.add_paragraph(f"查核建議：{r['查核建議']}")
        doc.add_paragraph("-" * 40)

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    st.download_button(
        "下載完整查核報告",
        buffer,
        "audit_report.docx"
    )

else:
    st.info("請上傳PDF財報")
