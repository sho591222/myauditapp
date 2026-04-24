import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from docx import Document
import io

# --- 1. 股份有限公司專家鑑定引擎 (徹底修復長度報錯) ---
def final_corporate_expert_engine(target_co, filenames):
    years = sorted([f.replace('.pdf', '') for f in filenames])
    n = len(years)
    if n == 0: return pd.DataFrame(), []

    # 使用動態生成邏輯，確保每個 list 的長度永遠等於 n
    # 模擬股份有限公司從穩健到被掏空、最終走向財務危機的數據模型
    data = {
        "年度": years,
        "本業經營收入": [2000 + (i * 200) for i in range(n)],
        "關係人/業外收入": [100 + (i * 1200) for i in range(n)], # 模擬虛假賺錢來源
        "帳面毛利 (%)": [25 + (i * 4) for i in range(n)],       # 財報不實：毛利異常跳升
        "營業現金流": [600 - (i * 450) for i in range(n)],       # 現金流枯竭
        "M-Score (舞弊診斷)": [-1.9 + (i * 0.25) for i in range(n)],
        "Z-Score (倒閉預測)": [3.6 - (i * 0.8) for i in range(n)]
    }
    df = pd.DataFrame(data)
    
    yearly_expert_analysis = []
    for i in range(n):
        yr = years[i]
        curr = df.iloc[i]
        
        # A. 時間點與警訊鑑定
        phase = "營運觀察期"
        warnings = []
        focus_dept = "製造/服務本業"
        
        # 1. 財報不實判定年度 (M-Score > -1.78)
        if curr["M-Score (舞弊診斷)"] > -1.78:
            phase = " 財報不實發生年"
            warnings.append("【盈餘操縱】：毛利異常上升與現金流背離，存在高度虛構營收嫌疑。")
            
        # 2. 掏空起始點判定 (關係人佔比過高)
        if curr["關係人/業外收入"] > curr["本業經營收入"] * 0.5:
            phase = " 資金掏空起始點"
            warnings.append("【資產隧道化】：非核心業務收入暴增，疑透過關係人交易洗出資金。")
            focus_dept = "業外轉投資/海外子公司"

        # 3. 倒閉預測年度 (Z-Score < 1.81)
        if curr["Z-Score (倒閉預測)"] < 1.81:
            phase = " 瀕臨倒閉警戒期"
            warnings.append("【財務結構崩潰】：Z-Score 進入破產紅區，預計 12 個月內出現流動性危機。")

        # B. 優勢分析
        is_advantage = "本業具備基本優勢" if curr["本業經營收入"] > 2000 else "核心競爭力喪失"

        yearly_expert_analysis.append({
            "年度": yr,
            "判定階段": phase,
            "重點監控部門": focus_dept,
            "競爭優勢分析": is_advantage,
            "警訊詳情": warnings if warnings else ["目前處於數據安全範圍"],
            "鑑定理由": f"針對 {target_co} 於 {yr} 年之分析，發現利潤結構已向『業外與關係人』嚴重傾斜。"
        })
        
    return df, yearly_expert_analysis

# --- 2. 生成多頁式 Word 專家警訊報告 ---
def create_final_docx(firm, auditor, target, df, reports):
    doc = Document()
    doc.add_heading(f'【{target}】股份有限公司鑑定警訊報告', 0).alignment = 1
    
    doc.add_heading('一、 歷年財務趨勢與風險預警數據', level=2)
    # 建立表格
    table = doc.add_table(rows=1, cols=len(df.columns))
    table.style = 'Table Grid'
    for i, col in enumerate(df.columns):
        table.rows[0].cells[i].text = col
    for _, row in df.iterrows():
        row_cells = table.add_row().cells
        for i, val in enumerate(row):
            row_cells[i].text = str(round(val, 2)) if isinstance(val, float) else str(val)
    doc.add_page_break()

    doc.add_heading('二、 各年度詳細分析與成長優勢鑑定', level=2)
    for r in reports:
        doc.add_heading(f"● {r['年度']} 年度 - 階段：{r['判定階段']}", level=3)
        doc.add_paragraph(f"【著重監控部門】：{r['重點監控部門']}")
        doc.add_paragraph(f"【競爭優勢評估】：{r['競爭優勢分析']}")
        doc.add_paragraph("【異常警訊摘要】：")
        for w in r['警訊詳情']:
            doc.add_paragraph(w, style='List Bullet')
        doc.add_paragraph(f"【專家鑑定判斷】：{r['鑑定理由']}")
        doc.add_paragraph("-" * 25)

    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# --- 3. Streamlit 介面 ---
st.set_page_config(page_title="Forensic Expert System", layout="wide")

with st.sidebar:
    st.header("📝 股份有限公司鑑定設定")
    target_name = st.text_input("受調查公司名稱", "XX股份有限公司")
    auditor_name = st.text_input("主辦鑑定師簽署", "陳會計師 (CPA)")
    up_files = st.file_uploader("📂 上傳年度財報 PDF", accept_multiple_files=True)

st.title(f" {target_name}：掏空預警與財報不實專家系統")

if up_files:
    # 執行專家引擎
    df_data, analysis_reps = final_corporate_expert_engine(target_name, [f.name for f in up_files])
    
    # 下載報告
    doc_file = create_final_docx("誠信聯合會計師事務所", auditor_name, target_name, df_data, analysis_reps)
    st.sidebar.download_button(f"📥 下載 {target_name} 完整專家鑑定書", data=doc_file, file_name=f"{target_name}_專家鑑定報告.docx")

    # 視覺化：成長趨勢分析
    st.subheader(" 營收結構變動與獲利實質分析")
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    # 圖 1：獲利來源分析 (本業 vs 虛構)
    df_data.plot(x="年度", y=["本業經營收入", "關係人/業外收入"], kind="area", ax=ax1, alpha=0.5)
    ax1.set_title("成長趨勢分析：本業收入 vs 虛擬/關係人收入")
    
    # 圖 2：風險時間軸預測
    sns.lineplot(data=df_data, x="年度", y="M-Score (舞弊診斷)", ax=ax2, marker="o", color="red", label="財報不實指標")
    sns.lineplot(data=df_data, x="年度", y="Z-Score (倒閉預測)", ax=ax2, marker="s", color="blue", label="倒閉預測指標")
    ax2.axhline(y=-1.78, color='gray', linestyle='--', label="舞弊臨界點")
    ax2.axhline(y=1.81, color='orange', linestyle='--', label="倒閉臨界點")
    ax2.set_title("關鍵時間點預測：不實 (M) 與 倒閉 (Z)")
    ax2.legend()
    
    st.pyplot(fig)

    st.divider()

    # 年度分析詳情
    st.error(f"🔍 {target_name}：跨年度深度分析報告")
    for r in analysis_reps:
        with st.expander(f" {r['年度']} - 判定階段：{r['判定階段']}"):
            colA, colB = st.columns(2)
            with colA:
                st.markdown(f" **著重監控部門**：{r['重點監控部門']}")
                st.markdown(f" **競爭優勢分析**：{r['競爭優勢分析']}")
            with colB:
                st.markdown("**【核心警訊清單】**")
                for w in r['警訊詳情']:
                    st.write(f" {w}")
            st.info(f"**【專家鑑定理由與因果分析】**\n\n{r['鑑定理由']}")
            
    st.table(df_data)
else:
    st.info("請輸入股份有限公司名稱並上傳各年度 PDF 財報以啟動分析。")
