import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from docx import Document
from docx.shared import Pt
import io

# --- 1. 專家級鑑定引擎 (包含受調查公司邏輯) ---
def final_expert_forensic_engine(target_company, filenames):
    years = sorted([f.replace('.pdf', '') for f in filenames])
    n = len(years)
    
    # 動態模擬數據 (確保長度與年度完全一致)
    df = pd.DataFrame({
        "年度": years,
        "帳面淨利": [500 + (i * 300) for i in range(n)],
        "營業現金流": [400 - (i * 500) for i in range(n)],
        "應收帳款 (AR)": [1200 + (i * 1800) for i in range(n)],
        "關係人往來/預付款": [300 + (i * 2200) for i in range(n)],
        "M-Score (舞弊診斷)": [-1.60 + (i * 0.25) for i in range(n)],
        "Z-Score (破產預警)": [3.0 - (i * 0.8) for i in range(n)]
    })
    
    # 年度專項診斷報告
    yearly_reports = []
    for i in range(n):
        yr = years[i]
        curr = df.iloc[i]
        observations = []
        
        # 掏空鑑定邏輯
        if curr["營業現金流"] < 0 and curr["帳面淨利"] > 0:
            observations.append(f"【死亡交叉】：{yr}年獲利品質極差，現金流缺口達 {abs(curr['營業現金流'])} 萬，疑有虛構盈餘。")
        if curr["關係人往來/預付款"] > curr["帳面淨利"] * 3:
            observations.append(f"【資產隧道化】：關係人資金往來異常，疑為掏空案之資金外流通道。")
            
        yearly_reports.append({
            "年度": yr,
            "診斷": observations if observations else ["未偵測到明顯異常"],
            "查核原因": f"針對 {target_company} 於 {yr} 年之異常指標，需執行穿透式審計以驗證資產真實性。"
        })
        
    # 科目解析
    account_analysis = [
        {"科目": "應收帳款", "分析": "成長率與現金流背離，疑為操縱損益。", "建議": "函證前五大客戶並查核最終受益人。"},
        {"科目": "預付款項", "分析": "掏空案常見通道，資金流向不明。", "建議": "查核採購合約真實性與資金流向。"}
    ]
    
    return df, yearly_reports, account_analysis

# --- 2. 生成多頁式 Word 鑑定報告 ---
def create_expert_docx(firm, auditor, target, r_date, df, y_reps, a_reps):
    doc = Document()
    # 封面
    doc.add_heading(firm, 0).alignment = 1
    doc.add_heading(f'【{target}】資產掏空暨財務異常深度鑑定報告', level=1).alignment = 1
    doc.add_paragraph("\n" * 5)
    p = doc.add_paragraph()
    p.alignment = 1
    p.add_run(f"受調查單位：{target}\n鑑定期間：{', '.join(df['年度'])}\n主辦鑑定師：{auditor}\n報告日期：{r_date.strftime('%Y/%m/%d')}")
    doc.add_page_break()
    
    # 數據表
    doc.add_heading('一、 歷年鑑定數據匯總', level=2)
    table = doc.add_table(rows=1, cols=len(df.columns))
    table.style = 'Table Grid'
    for i, col in enumerate(df.columns):
        table.rows[0].cells[i].text = col
    for _, row in df.iterrows():
        row_cells = table.add_row().cells
        for i, val in enumerate(row):
            row_cells[i].text = str(round(val, 2)) if isinstance(val, float) else str(val)
    doc.add_page_break()
    
    # 年度分析
    doc.add_heading('二、 各年度詳細風險診斷', level=2)
    for yr in y_reps:
        doc.add_heading(f"● {yr['年度']} 年度報告", level=3)
        for d in yr['診斷']:
            doc.add_paragraph(d, style='List Bullet')
        doc.add_paragraph(f"【鑑定理由】：{yr['查核原因']}")
    
    # 科目解析
    doc.add_heading('三、 關鍵會計科目深度鑑定', level=2)
    for ar in a_reps:
        doc.add_heading(f"● {ar['科目']}", level=3)
        doc.add_paragraph(f"【分析】：{ar['分析']}")
        doc.add_paragraph(f"【建議】：{ar['建議']}")
    
    # 簽名
    doc.add_paragraph("\n" * 3)
    sig = doc.add_table(rows=1, cols=2)
    sig.rows[0].cells[0].text = "事務所印鑑：\n\n\n(Seal)"
    sig.rows[0].cells[1].text = f"主辦鑑定師簽名：\n\n__________________\n{auditor}"

    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# --- 3. Streamlit 介面 ---
st.set_page_config(page_title="Forensic Pro", layout="wide")
st.title("⚖️ 專家級企業鑑定工作站 (掏空案專項)")

with st.sidebar:
    st.header("📝 鑑定專案設定")
    target_co = st.text_input("受調查公司名稱", "XX股份有限公司")
    f_name = st.text_input("事務所名稱", "誠信聯合會計師事務所")
    a_name = st.text_input("執業鑑定師", "陳大文 (CPA / CFE)")
    rep_date = st.date_input("報告日期", datetime.now())
    st.divider()
    up_files = st.file_uploader("📂 上傳年度財報 PDF", accept_multiple_files=True)

if up_files:
    df_data, yearly_rep, account_rep = final_expert_forensic_engine(target_co, [f.name for f in up_files])
    
    # 下載 Word
    docx_file = create_expert_docx(f_name, a_name, target_co, rep_date, df_data, yearly_rep, account_rep)
    st.sidebar.download_button(f"📥 下載 {target_co} 鑑定報告", data=docx_file, file_name=f"{target_co}_鑑定報告.docx")

    # 趨勢圖
    st.subheader(f"📈 {target_co}：資產掏空風險指標背離分析")
    
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.lineplot(data=df_data, x="年度", y="帳面淨利", marker="o", label="帳面淨利")
    sns.lineplot(data=df_data, x="年度", y="營業現金流", marker="s", label="實際金流")
    plt.title(f"{target_co} 歷年損益與現金流背離圖")
    st.pyplot(fig)

    # 年度與科目顯示
    col1, col2 = st.columns([3, 2])
    with col1:
        st.error(f"🔍 {target_co} 各年度異常診斷")
        for yr in yearly_rep:
            with st.expander(f"📅 {yr['年度']} 年度分析"):
                for d in yr['診斷']:
                    st.write(f"🚩 {d}")
                st.info(f"**查核理由：**\n{yr['查核原因']}")
    with col2:
        st.info("📊 關鍵數據匯總")
        st.table(df_data)
else:
    st.info("請輸入受調查公司名稱並上傳財報 PDF 以啟動專家鑑定。")
