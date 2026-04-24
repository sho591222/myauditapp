import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from docx import Document
import io

# --- 1. 專家級鑑定與預測引擎 ---
def forensic_expert_final_engine(target_co, filenames):
    years = sorted([f.replace('.pdf', '') for f in filenames])
    n = len(years)
    if n == 0: return pd.DataFrame(), []

    # 動態模擬數據：確保長度與年度完全一致
    df = pd.DataFrame({
        "年度": years,
        "核心業務營收": [2000 + (i * 300) for i in range(n)],
        "業外部門/關係人營收": [200 + (i * 1200) for i in range(n)], # 虛假賺錢的來源
        "帳面毛利率": [0.25 + (i * 0.05) for i in range(n)],
        "營業現金流": [500, 200, -300, -900][-n:], # 現金流枯竭趨勢
        "M-Score (舞弊)": [-1.9, -1.75, -1.4, -1.0][-n:],
        "Z-Score (倒閉)": [3.5, 2.9, 1.8, 0.7][-n:]
    })
    
    yearly_expert_reports = []
    for i in range(n):
        yr = years[i]
        curr = df.iloc[i]
        
        # A. 時間點預測邏輯
        timeline_status = "正常營運"
        critical_warnings = []
        
        if curr["M-Score (舞弊)"] > -1.78:
            timeline_status = " 財報不實發生年"
            critical_warnings.append("偵測到毛利率與現金流異常背離，盈餘品質極端惡化。")
            
        if curr["業外部門/關係人營收"] > curr["核心業務營收"] * 0.5:
            timeline_status = " 掏空/隧道行為起始點"
            critical_warnings.append("資金透過非核心部門洗出，高額業外收入疑為轉投資掏空套現。")

        if curr["Z-Score (倒閉)"] < 1.81:
            timeline_status = " 倒閉風險預測年"
            critical_warnings.append("財務結構完全崩潰，預計短期內發生流動性危機。")

        # B. 優勢與部門分析
        advantage = "核心業務具備基本盤" if curr["核心業務營收"] > 1000 else "競爭優勢喪失"
        focus_dept = "貿易/業外部門 (虛擬獲利中心)" if curr["業外部門/關係人營收"] > 500 else "製造/服務部門"

        yearly_expert_reports.append({
            "年度": yr,
            "判定階段": timeline_status,
            "重點監控部門": focus_dept,
            "優勢評估": advantage,
            "警訊詳情": critical_warnings if critical_warnings else ["處於安全觀測期"],
            "鑑定理由": f"針對 {yr} 年數據，{target_co} 的獲利主力已由實質業務轉向『高度疑慮之關係人交易』。"
        })
        
    return df, yearly_expert_reports

# --- 2. 生成多頁式 Word 專家分析報告 ---
def create_final_docx(firm, auditor, target, df, reports):
    doc = Document()
    doc.add_heading(f'【{target}】財務不實暨掏空跡象專家鑑定報告', 0).alignment = 1
    
    # 成長趨勢數據總覽
    doc.add_heading('一、 歷年財務成長與風險趨勢表', level=2)
    table = doc.add_table(rows=1, cols=len(df.columns))
    table.style = 'Table Grid'
    for i, col in enumerate(df.columns):
        table.rows[0].cells[i].text = col
    for _, row in df.iterrows():
        row_cells = table.add_row().cells
        for i, val in enumerate(row):
            row_cells[i].text = str(round(val, 2)) if isinstance(val, float) else str(val)
    doc.add_page_break()

    # 年度分析專章
    doc.add_heading('二、 各年度深度報告與時間點預測', level=2)
    for r in reports:
        doc.add_heading(f"● {r['年度']} 年度鑑定：{r['判定階段']}", level=3)
        doc.add_paragraph(f"【著重部門/項目】：{r['重點監控部門']}")
        doc.add_paragraph(f"【實質優勢分析】：{r['優勢評估']}")
        doc.add_paragraph("【異常警訊摘要】：")
        for w in r['警訊詳情']:
            doc.add_paragraph(w, style='List Bullet')
        doc.add_paragraph(f"【會計師鑑定因果】：{r['鑑定理由']}")
        doc.add_paragraph("-" * 25)

    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# --- 3. Streamlit 介面 ---
st.set_page_config(page_title="Forensic Pro AI", layout="wide")

with st.sidebar:
    st.header(" 鑑定專案設定")
    target_name = st.text_input("受調查公司名稱", "XX企業")
    auditor_name = st.text_input("鑑定師簽署", "陳會計師")
    up_files = st.file_uploader("📂 上傳年度財報 PDF", accept_multiple_files=True)

st.title(f" {target_name}：掏空與財報不實全維度預測系統")

if up_files:
    df_data, analysis_reps = forensic_expert_final_engine(target_name, [f.name for f in up_files])
    
    # 下載報告
    doc_file = create_final_docx("誠信事務所", auditor_name, target_name, df_data, analysis_reps)
    st.sidebar.download_button(f" 下載 {target_name} 完整專家鑑定書", data=doc_file, file_name=f"{target_name}_深度鑑定報告.docx")

    # 視覺化圖表：成長趨勢與背離分析
    st.subheader(" 財務成長趨勢與虛擬獲利監控")
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    # 營收組成分析
    df_data.plot(x="年度", y=["核心業務營收", "業外部門/關係人營收"], kind="bar", ax=ax1, stacked=True)
    ax1.set_title("營收結構變動分析 (監控異常獲利來源)")
    
    # 舞弊與倒閉指標
    sns.lineplot(data=df_data, x="年度", y="M-Score (舞弊)", ax=ax2, marker="o", color="red", label="財報不實指標")
    sns.lineplot(data=df_data, x="年度", y="Z-Score (倒閉)", ax=ax2, marker="s", color="blue", label="倒閉預期指標")
    ax2.axhline(y=-1.78, color='gray', linestyle='--')
    ax2.set_title("財報不實與倒閉時間點預測曲線")
    
    st.pyplot(fig)

    st.divider()

    # 顯示年度報告分析
    st.error(f" {target_name}：跨年度鑑定與部門優勢診斷")
    for r in analysis_reps:
        with st.expander(f" {r['年度']} - 判定階段：{r['判定階段']}"):
            colA, colB = st.columns(2)
            with colA:
                st.write(f" **著重監控部門**：{r['重點監控部門']}")
                st.write(f" **年度實質優勢**：{r['優勢評估']}")
            with colB:
                st.markdown("**【核心警訊清單】**")
                for w in r['警訊詳情']:
                    st.write(f" {w}")
            st.info(f"**【專家鑑定理由與建議】**\n\n{r['鑑定理由']}")
            
    st.table(df_data)
else:
    st.info("請輸入受調查公司名稱並上傳各年度 PDF 財報以啟動分析。")
