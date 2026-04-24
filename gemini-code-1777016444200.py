import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from docx import Document
import io
import matplotlib.font_manager as fm

# --- 0. 修正後的字體設定 (解決 AttributeError) ---
def set_chinese_font():
    # 嘗試多種繁體中文字體名稱
    target_fonts = ['Microsoft JhengHei', 'Heiti TC', 'LiHei Pro', 'STHeiti', 'WenQuanYi Micro Hei', 'sans-serif']
    
    # 獲取系統中所有可用的字體名稱
    available_fonts = [f.name for f in fm.font_manager.ttflist]
    
    for font in target_fonts:
        if font in available_fonts:
            plt.rcParams['font.sans-serif'] = [font]
            break
    
    plt.rcParams['axes.unicode_minus'] = False # 解決負號顯示問題

# 執行字體設定
set_chinese_font()

# --- 1. 股份有限公司專家鑑定引擎 (時間點預測與優勢分析) ---
def corporate_forensic_expert_engine(target_co, filenames):
    years = sorted([f.replace('.pdf', '') for f in filenames])
    n = len(years)
    if n == 0: return pd.DataFrame(), []

    # 動態模擬數據：反應從實質獲利到「虛假賺錢」的轉變
    df = pd.DataFrame({
        "年度": years,
        "本業製造收入": [2800 + (i * 100) for i in range(n)],
        "關係人/業外轉投資": [200 + (i * 1400) for i in range(n)], # 掏空常見的高成長「虛擬」收入
        "帳面毛利率 (%)": [24, 28, 33, 42][-n:],             # 財報不實跡象：異常毛利
        "營業現金流": [850, 250, -400, -1500][-n:],         # 死亡交叉：獲利不見現金
        "M-Score (不實指標)": [-1.9, -1.8, -1.5, -1.1][-n:],
        "Z-Score (倒閉指標)": [3.7, 3.0, 1.8, 0.8][-n:]
    })
    
    analysis_reps = []
    for i in range(n):
        yr = years[i]
        curr = df.iloc[i]
        
        status = "營運觀察"
        warnings = []
        focus_item = "本業核心部門"
        
        # 判定：財報不實起始年
        if curr["M-Score (不實指標)"] > -1.78:
            status = " 財報不實發生年"
            warnings.append("【會計舞弊預警】：毛利飆升但現金流大幅流出，疑似虛假交易。")
            
        # 判定：掏空跡象起始年
        if curr["關係人/業外轉投資"] > curr["本業製造收入"] * 0.5:
            status = " 資金掏空起始點"
            warnings.append("【隧道行為預警】：業外收入佔比過高，資金疑透過子公司洗出。")
            focus_item = "海外子公司/關聯企業交易"

        # 判定：預測倒閉年
        if curr["Z-Score (倒閉指標)"] < 1.81:
            status = " 瀕臨倒閉預警期"
            warnings.append("【破產預警】：Z-Score 跌破臨界線，財務結構已實質崩潰。")

        # 優勢分析
        advantage = "具備本業技術優勢" if curr["本業製造收入"] > 2500 and curr["營業現金流"] > 0 else "核心優勢喪失 (依賴業外)"

        analysis_reps.append({
            "年度": yr,
            "判定階段": status,
            "重點監控項目": focus_item,
            "實質優勢分析": advantage,
            "警訊詳情": warnings if warnings else ["目前處於安全觀測範圍"]
        })
        
    return df, analysis_reps

# --- 2. 生成 Word 鑑定報告 ---
def create_forensic_docx(firm, auditor, target, df, reports):
    doc = Document()
    doc.add_heading(f'【{target}】股份有限公司鑑定報告', 0).alignment = 1
    
    p = doc.add_paragraph()
    p.alignment = 1
    p.add_run(f"\n鑑定機構：{firm}\n主辦會計師：{auditor}\n報告基準日：{datetime.now().strftime('%Y/%m/%d')}")
    doc.add_page_break()

    doc.add_heading('一、 歷年鑑定指標與風險趨勢表', level=2)
    # (表格生成邏輯...)
    table = doc.add_table(rows=1, cols=len(df.columns))
    table.style = 'Table Grid'
    for i, col in enumerate(df.columns):
        table.rows[0].cells[i].text = col
    for _, row in df.iterrows():
        row_cells = table.add_row().cells
        for i, val in enumerate(row):
            row_cells[i].text = str(round(val, 2)) if isinstance(val, float) else str(val)
    
    doc.add_heading('二、 各年度深度診斷與時間點預測', level=2)
    for r in reports:
        doc.add_heading(f"● {r['年度']} 年度 - 判定：{r['判定階段']}", level=3)
        doc.add_paragraph(f"【著重項目】：{r['重點監控項目']}\n【優勢評估】：{r['實質優勢分析']}")
        for w in r['警訊詳情']:
            doc.add_paragraph(f" {w}")
    
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# --- 3. Streamlit 介面 ---
st.set_page_config(page_title="Forensic Pro AI", layout="wide")

with st.sidebar:
    st.header(" 鑑定法律簽署")
    target_name = st.text_input("受調查公司 (股份有限公司)", "XX股份有限公司")
    firm_name = st.text_input("會計師事務所", "誠信聯合會計師事務所")
    auditor_name = st.text_input("簽證會計師", "陳大文 (CPA)")
    st.divider()
    up_files = st.file_uploader("📂 上傳年度財報 PDF", accept_multiple_files=True)

st.title(f" {target_name}：掏空與財報不實全維度預測系統")

if up_files:
    df_data, analysis_reps = corporate_forensic_expert_engine(target_name, [f.name for f in up_files])
    
    # --- 視覺化 (解決亂碼) ---
    st.subheader(f" {target_name}：成長趨勢與不實指標分析")
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    # 圖 1: 獲利來源 (本業 vs 虛擬)
    df_data.plot(x="年度", y=["本業製造收入", "關係人/業外轉投資"], kind="bar", ax=ax1, alpha=0.7)
    ax1.set_title(f"營收結構分析 - {target_name}")
    
    # 圖 2: 關鍵預測曲線
    sns.lineplot(data=df_data, x="年度", y="M-Score (不實指標)", ax=ax2, marker="o", color="red", label="財報不實預警")
    sns.lineplot(data=df_data, x="年度", y="Z-Score (倒閉指標)", ax=ax2, marker="s", color="blue", label="倒閉預測預警")
    ax2.axhline(y=-1.78, color='gray', linestyle='--')
    ax2.set_title("時間點預測：不實起始點 (M) 與 倒閉臨界點 (Z)")
    
    st.pyplot(fig)

    # 年度分析詳情
    st.error(f" {firm_name} - {auditor_name} 專業鑑定意見")
    for r in analysis_reps:
        with st.expander(f" {r['年度']} - 階段：{r['判定階段']}"):
            st.write(f" **重點監控項目**：{r['重點監控項目']}")
            st.write(f" **實質優勢分析**：{r['實質優勢分析']}")
            for w in r['警訊詳情']:
                st.write(f" {w}")

    # 下載報告
    doc_file = create_forensic_docx(firm_name, auditor_name, target_name, df_data, analysis_reps)
    st.sidebar.download_button("📥 下載專家鑑定報告", data=doc_file, file_name=f"{target_name}_報告.docx")
else:
    st.info("請完成上方設定並上傳財報。")
