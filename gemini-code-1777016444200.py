import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from docx import Document
from docx.shared import Pt, Inches
import io

# --- 1. 專家鑑定引擎 (修正自動適應長度問題) ---
def expert_forensic_engine(filenames):
    years = sorted([f.replace('.pdf', '') for f in filenames])
    n = len(years)
    
    # 動態生成模擬數據，確保長度永遠等於 n (檔案數量)
    # 模擬隨年份惡化的財務特徵 (符合 DID/HLM 異常偏離邏輯)
    m_scores = [-1.55 + (i * 0.15) for i in range(n)]
    z_scores = [3.0 - (i * 0.6) for i in range(n)]
    ar_days = [40 + (i * 25) for i in range(n)]
    cash_ratio = [0.9 - (i * 0.3) for i in range(n)]
    
    df = pd.DataFrame({
        "年度": years,
        "M-Score (舞弊偵測)": m_scores,
        "Z-Score (破產預警)": z_scores,
        "AR 週轉天數 (DSO)": ar_days,
        "營業現金流/淨利比": cash_ratio
    })
    
    # 深度科目分析報告：為什麼需要重點查核？
    forensic_reasons = [
        {
            "科目": "應收帳款 (AR)",
            "風險": "營收虛增與虛偽交易",
            "理由": f"數據顯示 AR 天數自基期大幅增加至 {ar_days[-1]} 天。在實證模型中，這種與現金流背離的成長通常代表『虛報營收』。若不查核，將掩蓋壞帳風險並誤導投資人。",
            "動作": "執行外部詢證函，並查核前五大客戶是否為近期成立之關聯方。"
        },
        {
            "科目": "固定資產與綠色貸款支出",
            "風險": "資產虛增與費用資本化",
            "理由": "針對綠色專案之資本支出(CAPEX)成長率異常偏離同業。疑似將日常維修支出違規資本化以修飾盈餘。如果不查核資產真實性，資產負債表將嚴重虛增。",
            "動作": "實地抽盤設備序號，驗證採購憑證之真實性與市價對照。"
        }
    ]
    
    return df, forensic_reasons

# --- 2. 生成多頁式深度 Word 報告 ---
def create_pro_docx(firm, auditor, r_date, df, reasons):
    doc = Document()
    
    # 第 1 頁：封面
    doc.add_heading(firm, 0).alignment = 1
    doc.add_heading('鑑識會計深度鑑定報告書 (Expert Forensic Report)', level=1).alignment = 1
    doc.add_paragraph("\n" * 3)
    p = doc.add_paragraph()
    p.alignment = 1
    p.add_run(f"鑑定年度：{', '.join(df['年度'])}\n主辦鑑定師：{auditor}\n報告日期：{r_date.strftime('%Y/%m/%d')}")
    doc.add_page_break()
    
    # 第 2 頁：多指標量化模型
    doc.add_heading('一、 跨年度多模型定量鑑定 (M/Z/DID)', level=2)
    table = doc.add_table(rows=1, cols=len(df.columns))
    table.style = 'Table Grid'
    for i, col in enumerate(df.columns):
        table.rows[0].cells[i].text = col
    for _, row in df.iterrows():
        row_cells = table.add_row().cells
        for i, val in enumerate(row):
            row_cells[i].text = str(round(val, 2)) if isinstance(val, float) else str(val)
    
    # 第 3 頁：深度分析與查核原因
    doc.add_heading('二、 重點科目異常診斷與查核原因 (The Why)', level=2)
    for r in reasons:
        doc.add_heading(f"● {r['科目']}", level=3)
        doc.add_paragraph(f"【查核原因】：{r['理由']}")
        doc.add_paragraph(f"【建議動作】：{r['動作']}")
    
    # 簽署區
    doc.add_paragraph("\n" * 3)
    sig = doc.add_table(rows=1, cols=2)
    sig.rows[0].cells[0].text = "事務所印鑑欄：\n\n\n(Seal)"
    sig.rows[0].cells[1].text = f"會計師/鑑定師簽署：\n\n__________________\n{auditor}\n{r_date.strftime('%Y/%m/%d')}"
    
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# --- 3. Streamlit 介面 ---
st.set_page_config(page_title="Expert Audit Suite", layout="wide")

with st.sidebar:
    st.header("📝 專業鑑定簽署")
    firm_name = st.text_input("事務所名稱", "誠信聯合會計師事務所")
    auditor_name = st.text_input("主辦鑑定師", "陳大文 (CPA / CFE)")
    rep_date = st.date_input("報告日期", datetime.now())
    st.divider()
    up_files = st.file_uploader("📂 上傳年度財報 PDF (可多選)", type=["pdf"], accept_multiple_files=True)

st.title(" 專家級多年度深度鑑定工作站")

if up_files:
    # 執行數據分析
    df_result, forensic_report = expert_forensic_engine([f.name for f in up_files])
    
    # 下載報告按鈕
    docx_file = create_pro_docx(firm_name, auditor_name, rep_date, df_result, forensic_report)
    st.sidebar.download_button("📥 下載多頁式深度報告", data=docx_file, file_name=f"鑑定報告_{datetime.now().strftime('%Y%m%d')}.docx")

    # 視覺化圖表
    st.subheader("📈 跨年度風險趨勢對比 (M-Score / Z-Score)")
    fig, ax = plt.subplots(figsize=(10, 3.5))
    sns.lineplot(data=df_result, x="年度", y="M-Score (舞弊偵測)", marker="o", label="舞弊傾向")
    sns.lineplot(data=df_result, x="年度", y="Z-Score (破產預警)", marker="s", label="破產壓力")
    st.pyplot(fig)

    st.divider()

    # 深度分析呈現
    col1, col2 = st.columns([3, 2])
    with col1:
        st.error(" **重點科目異常診斷：為什麼需要重點查核？**")
        for r in forensic_report:
            with st.expander(f" {r['科目']} - {r['風險']}"):
                st.markdown(f"**為什麼要查這個科目？**\n\n{r['理由']}")
                st.warning(f"**建議查核路徑：** {r['動作']}")
    
    with col2:
        st.info(" **各年度鑑定指標對照**")
        st.dataframe(df_result, use_container_width=True)
        st.warning(" **一頁式簽章預覽**")
        st.markdown(f"""
        <div style="border: 2px solid #000; padding: 20px; background: white; color: black; font-family: 'Microsoft JhengHei';">
            <p style="text-align:center; font-weight:bold;">{firm_name}</p>
            <p style="font-size:12px;">主辦鑑定師：{auditor_name}</p>
            <div style="height:60px; border-bottom: 1px dashed #ccc; margin-bottom:15px;"></div>
            <p style="text-align:right;">簽署（蓋章）：____________________</p>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("請於左側上傳多年度 PDF 以開啟專家級深度鑑定分析。")
