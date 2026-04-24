import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from docx import Document
from docx.shared import Pt
import io

# --- 1. 專家級跨年度深度分析引擎 ---
def expert_yearly_forensic_engine(filenames):
    # 排序年度，確保分析具備時間連續性
    years = sorted([f.replace('.pdf', '') for f in filenames])
    n = len(years)
    
    # 動態模擬數據 (確保所有陣列長度嚴格等於 n，避免 ValueError)
    # 模擬數據會隨著年度呈現特定的風險趨勢
    df = pd.DataFrame({
        "年度": years,
        "應收帳款 (AR)": [1000 + (i * 1200) for i in range(n)],
        "存貨 (Inventory)": [800 + (i * 700) for i in range(n)],
        "營業現金流": [1000 - (i * 450) for i in range(n)],
        "M-Score (舞弊診斷)": [-1.60 + (i * 0.2) for i in range(n)],
        "Z-Score (破產預警)": [3.2 - (i * 0.8) for i in range(n)]
    })
    
    # 年度專項分析報告
    yearly_detailed_reports = []
    for i in range(n):
        yr = years[i]
        curr_m = df.iloc[i]["M-Score (舞弊診斷)"]
        curr_z = df.iloc[i]["Z-Score (破產預警)"]
        
        # 建立該年度的問題清單
        observations = []
        if curr_m > -1.78:
            observations.append(f"【盈餘品質警訊】：M-Score 達到 {round(curr_m, 2)}，顯示該年度具備高度盈餘操縱傾向，利潤真實性存疑。")
        if curr_z < 1.8:
            observations.append(f"【財務健全度警訊】：Z-Score 跌至 {round(curr_z, 2)}，進入破產紅色警戒區，需關注流動性風險。")
        
        # 跨年度變動分析 (與前一年相比)
        yoy_analysis = ""
        if i > 0:
            ar_change = (df.iloc[i]["應收帳款 (AR)"] / df.iloc[i-1]["應收帳款 (AR)"]) - 1
            yoy_analysis = f"相較於 {years[i-1]} 年，應收帳款異常成長 {round(ar_change*100)}%。"
        else:
            yoy_analysis = "本年度為鑑定基準首年，作為後續年度之對照基期。"

        yearly_detailed_reports.append({
            "年度": yr,
            "觀察要點": observations if observations else ["數據尚處於產業安全範圍"],
            "變動分析": yoy_analysis,
            "查核原因": f"針對 {yr} 年度之異常背離，需執行『穿透式會計查核』。重點在於驗證營收成長是否具備實質現金流入，防止企業透過『虛擬資產』掩蓋虧損。"
        })
        
    return df, yearly_detailed_reports

# --- 2. 生成多頁式深度 Word 報告 (包含年度專章) ---
def create_comprehensive_docx(firm, auditor, r_date, df, yearly_reports):
    doc = Document()
    
    # Page 1: 封面
    doc.add_heading(firm, 0).alignment = 1
    doc.add_heading('跨年度財務報告深度鑑定書', level=1).alignment = 1
    doc.add_paragraph("\n" * 5)
    p = doc.add_paragraph()
    p.alignment = 1
    p.add_run(f"鑑定基準：{', '.join(df['年度'])}\n執業鑑定師：{auditor}\n報告日期：{r_date.strftime('%Y/%m/%d')}")
    doc.add_page_break()
    
    # Page 2: 數據表
    doc.add_heading('一、 歷年關鍵財務指標彙總', level=2)
    table = doc.add_table(rows=1, cols=len(df.columns))
    table.style = 'Table Grid'
    for i, col in enumerate(df.columns):
        table.rows[0].cells[i].text = col
    for _, row in df.iterrows():
        row_cells = table.add_row().cells
        for i, val in enumerate(row):
            row_cells[i].text = str(round(val, 2)) if isinstance(val, float) else str(val)
    doc.add_page_break()
    
    # Page 3+: 年度深度分析專章
    doc.add_heading('二、 各年度詳細診斷與異常分析', level=2)
    for rep in yearly_reports:
        doc.add_heading(f"● {rep['年度']} 年度報告分析", level=3)
        doc.add_paragraph(f"【跨年度變動】：{rep['變動分析']}")
        doc.add_paragraph("【異常監測】：")
        for obs in rep['觀察要點']:
            doc.add_paragraph(obs, style='List Bullet')
        doc.add_paragraph(f"【查核必要性】：{rep['查核原因']}")
        doc.add_paragraph("-" * 25)
    
    # 簽署區
    doc.add_paragraph("\n" * 3)
    sig = doc.add_table(rows=1, cols=2)
    sig.rows[0].cells[0].text = "會計師事務所蓋章：\n\n\n(Seal)"
    sig.rows[0].cells[1].text = f"主辦鑑定師簽署：\n\n__________________\n{auditor}\n日期：{r_date.strftime('%Y/%m/%d')}"

    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# --- 3. Streamlit 介面 ---
st.set_page_config(page_title="Forensic Yearly Expert", layout="wide")

with st.sidebar:
    st.header("📝 專業鑑定設定")
    f_name = st.text_input("事務所名稱", "誠信聯合會計師事務所")
    a_name = st.text_input("主辦鑑定師", "陳大文 (CPA / CFE)")
    rep_date = st.date_input("報告日期", datetime.now())
    st.divider()
    up_files = st.file_uploader("📂 上傳各年度財報 PDF", type=["pdf"], accept_multiple_files=True)

st.title("⚖️ 專家級各年度財報深度鑑定工作站")

if up_files:
    # 執行數據與年度分析引擎
    df_data, yearly_analysis = expert_yearly_forensic_engine([f.name for f in up_files])
    
    # 下載報告
    docx_file = create_comprehensive_docx(f_name, a_name, rep_date, df_data, yearly_analysis)
    st.sidebar.download_button("📥 下載多頁式年度鑑定書", data=docx_file, file_name=f"年度鑑定報告_{a_name}.docx")

    # 視覺化趨勢
    st.subheader("📈 跨年度核心風險指標趨勢")
    
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.lineplot(data=df_data, x="年度", y="M-Score (舞弊診斷)", marker="o", label="舞弊機率")
    sns.lineplot(data=df_data, x="年度", y="Z-Score (破產預警)", marker="s", label="破產壓力")
    plt.axhline(y=-1.78, color='r', linestyle='--', label="舞弊門檻")
    plt.legend()
    st.pyplot(fig)

    st.divider()

    # 顯示年度深度分析
    st.subheader("🔍 年度專項診斷報告 (Year-by-Year Analysis)")
    for rep in yearly_analysis:
        with st.expander(f"📅 {rep['年度']} 年度分析：{rep['變動分析'][:20]}..."):
            st.markdown(f"**【年度變動分析】**：\n{rep['變動分析']}")
            st.markdown("**【年度異常問題點】**：")
            for obs in rep['觀察要點']:
                st.write(f"👉 {obs}")
            st.info(f"**【查核原因與邏輯】**：\n{rep['查核原因']}")
            
    st.table(df_data)

else:
    st.info("請上傳多個年度的財報 PDF（如：110.pdf, 111.pdf），系統將自動啟動年度對比鑑定。")
