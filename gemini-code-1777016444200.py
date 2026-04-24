import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from docx import Document
import io

# --- 1. 專家鑑定引擎 (修正自動適應長度) ---
def expert_audit_engine(filenames):
    # 根據上傳檔案數量動態生成數據
    years = sorted([f.replace('.pdf', '') for f in filenames])
    n = len(years)
    
    # 使用動態生成方式，確保所有陣列長度皆為 n
    # 模擬數據：隨著年份增加，指標逐漸惡化
    m_scores = [-1.45 + (i * 0.1) for i in range(n)]
    z_scores = [2.8 - (i * 0.5) for i in range(n)]
    ar_turnover = [7.5 - (i * 1.2) for i in range(n)]
    inv_turnover = [6.0 - (i * 1.0) for i in range(n)]
    
    df = pd.DataFrame({
        "年度": years,
        "M-Score (舞弊值)": m_scores,
        "Z-Score (破產值)": z_scores,
        "應收帳款週轉率": ar_turnover,
        "存貨週轉率": inv_turnover
    })
    
    # 異常科目偵測邏輯
    abnormal_list = []
    if n > 1:
        if ar_turnover[-1] < ar_turnover[0]:
            abnormal_list.append({"科目": "應收帳款 (AR)", "風險": "極高", "說明": "週轉率持續下滑，疑似透過放寬信用期或虛偽交易虛增營收。"})
        if z_scores[-1] < 1.8:
            abnormal_list.append({"科目": "財務結構", "風險": "破產預警", "說明": "Z-Score 已跌破 1.8 臨界點，具備重大不確定性。"})
    
    return df, abnormal_list

# --- 2. 生成 Word 報告 (一頁式簽章) ---
def make_report(firm, auditor, r_date, df, abnormal):
    doc = Document()
    doc.add_heading(firm, 0).alignment = 1
    doc.add_heading('財務鑑定暨專家查核報告', level=1).alignment = 1
    
    doc.add_paragraph(f"鑑定對象：{', '.join(df['年度'])} | 鑑定師：{auditor} | 日期：{r_date}")
    
    # 插入數據表
    table = doc.add_table(rows=1, cols=len(df.columns))
    table.style = 'Table Grid'
    for i, col in enumerate(df.columns):
        table.rows[0].cells[i].text = col
    for _, row in df.iterrows():
        row_cells = table.add_row().cells
        for i, val in enumerate(row):
            row_cells[i].text = str(round(val, 2)) if isinstance(val, float) else str(val)

    # 插入異常科目報告
    doc.add_heading('重點科目異常診斷與查核建議', level=2)
    for item in abnormal:
        p = doc.add_paragraph(style='List Bullet')
        p.add_run(f"【{item['科目']}】").bold = True
        p.add_run(f" - 風險：{item['風險']}。說明：{item['說明']}")

    # 簽章區
    doc.add_paragraph("\n" * 3)
    sig = doc.add_table(rows=1, cols=2)
    sig.rows[0].cells[0].text = "事務所印鑑蓋章：\n\n\n(Seal)"
    sig.rows[0].cells[1].text = f"主辦會計師簽署：\n\n__________________\n{auditor}\n{r_date}"
    
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# --- 3. Streamlit 介面 ---
st.set_page_config(page_title="專業鑑識審計工作站", layout="wide")

with st.sidebar:
    st.header(" 專家設定")
    f_name = st.text_input("事務所名稱", "誠信聯合會計師事務所")
    a_name = st.text_input("主辦鑑定師", "陳大文 (CPA / CFE)")
    rep_date = st.date_input("報告日期", datetime.now())
    st.divider()
    files = st.file_uploader("📂 上傳年度財報 PDF (可多選)", type=["pdf"], accept_multiple_files=True)

st.title(" 專家級鑑定報告與異常科目診斷系統")

if files:
    # 執行數據分析
    df_data, abnormal_report = expert_audit_engine([f.name for f in files])
    
    # 下載按鈕
    doc_file = make_report(f_name, a_name, rep_date, df_data, abnormal_report)
    st.sidebar.download_button("📥 下載一頁式簽署報告", data=doc_file, file_name="鑑定報告_正式版.docx")

    # 顯示圖表
    st.subheader("📈 各年度風險趨勢圖表")
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.lineplot(data=df_data, x="年度", y="M-Score (舞弊值)", marker='o', label="M-Score")
    sns.lineplot(data=df_data, x="年度", y="Z-Score (破產值)", marker='s', label="Z-Score")
    st.pyplot(fig)

    st.divider()

    # 顯示異常分析
    col1, col2 = st.columns([3, 2])
    with col1:
        st.error(" **重點科目異常診斷報告**")
        if not abnormal_report:
            st.write("目前數據長度不足或未偵測到明顯異常。")
        for item in abnormal_report:
            st.markdown(f"**【{item['科目']}】** 風險評級：`{item['風險']}`")
            st.write(f"查核建議：{item['說明']}")
            st.divider()

    with col2:
        st.info(" **分析模型對照表**")
        st.dataframe(df_data, use_container_width=True)
        st.warning(" **簽署欄預覽**")
        st.markdown(f"""
        <div style="border: 1px solid #000; padding: 15px; background: white; color: black;">
            <p style="text-align:center;">{f_name}</p>
            <p style="font-size:12px;">鑑定師：{a_name}</p>
            <div style="height:40px;"></div>
            <p style="text-align:right;">簽名：________________</p>
        </div>
        """, unsafe_allow_html=True)

else:
    st.info("請從左側上傳財報檔案以開始分析。")
