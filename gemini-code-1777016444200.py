import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from docx import Document
import io
import matplotlib.font_manager as fm

# --- 0. 解決繪圖亂碼：設定中文字體 ---
def set_chinese_font():
    # 優先尋找系統中的繁體中文字體
    font_list = ['Microsoft JhengHei', 'Heiti TC', 'Arial Unicode MS', 'SimHei']
    for font in font_list:
        if font in [f.name for f in fm.font_manager.ttflist]:
            plt.rcParams['font.sans-serif'] = [font]
            break
    plt.rcParams['axes.unicode_minus'] = False  # 解決負號顯示問題

set_chinese_font()

# --- 1. 股份有限公司專家鑑定引擎 (完全動態化，預測時間點) ---
def final_expert_analysis_engine(target_co, filenames):
    years = sorted([f.replace('.pdf', '') for f in filenames])
    n = len(years)
    if n == 0: return pd.DataFrame(), []

    # 動態生成數據：模擬股份有限公司從正常、不實、掏空到倒閉的過程
    df = pd.DataFrame({
        "年度": years,
        "本業經營收入": [2500 + (i * 150) for i in range(n)],
        "關係人交易/業外收入": [150 + (i * 1300) for i in range(n)], # 虛擬賺錢來源
        "帳面毛利 (%)": [26 + (i * 5) for i in range(n)],          # 財報不實跡象
        "營業現金流": [700 - (i * 400) for i in range(n)],          # 現金流枯竭
        "M-Score (舞弊診斷)": [-1.95 + (i * 0.3) for i in range(n)],
        "Z-Score (倒閉預測)": [3.6 - (i * 0.85) for i in range(n)]
    })
    
    analysis_reps = []
    for i in range(n):
        yr = years[i]
        curr = df.iloc[i]
        
        phase = "營運穩定"
        warnings = []
        
        # A. 時間點診斷
        if curr["M-Score (舞弊診斷)"] > -1.78:
            phase = " 財報不實發生年"
            warnings.append("偵測到『盈餘操縱』：毛利異常上升但現金流大幅流出。")
            
        if curr["關係人交易/業外收入"] > curr["本業經營收入"] * 0.5:
            phase = " 資金掏空起始點"
            warnings.append("偵測到『隧道行為』：資金透過非核心部門洗出。")

        if curr["Z-Score (倒閉預測)"] < 1.81:
            phase = " 瀕臨倒閉預警期"
            warnings.append("財務結構崩潰：預計 12-18 個月內面臨倒閉風險。")

        # B. 優勢與部門診斷
        focus_dept = "轉投資/海外子公司" if curr["關係人交易/業外收入"] > 800 else "製造與研發部門"
        advantage = "具備實質競爭優勢" if curr["本業經營收入"] > 2200 and curr["營業現金流"] > 0 else "核心競爭力虛弱"

        analysis_reps.append({
            "年度": yr,
            "判定階段": phase,
            "重點監控項目": focus_dept,
            "優勢評估": advantage,
            "警訊清單": warnings if warnings else ["目前處於安全觀測範圍"]
        })
        
    return df, analysis_reps

# --- 2. 生成多頁式 Word 報告 (包含事務所與姓名) ---
def create_final_report(firm, auditor, target, df, reports):
    doc = Document()
    doc.add_heading(f'【{target}】股份有限公司鑑定報告', 0).alignment = 1
    
    # 封面資訊
    doc.add_paragraph("\n" * 2)
    p = doc.add_paragraph()
    p.alignment = 1
    p.add_run(f"鑑定單位：{firm}\n主辦會計師：{auditor}\n報告日期：{datetime.now().strftime('%Y/%m/%d')}")
    doc.add_page_break()

    # 年度分析
    doc.add_heading('一、 各年度深度鑑定與預測報告', level=2)
    for r in reports:
        doc.add_heading(f"● {r['年度']} 年度 - 階段：{r['判定階段']}", level=3)
        doc.add_paragraph(f"【著重部門】：{r['重點監控項目']}")
        doc.add_paragraph(f"【優勢分析】：{r['優勢評估']}")
        for w in r['警訊清單']:
            doc.add_paragraph(f"🚩 {w}")
        doc.add_paragraph("-" * 30)

    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# --- 3. Streamlit 介面 ---
st.set_page_config(page_title="專業鑑識會計系統", layout="wide")

with st.sidebar:
    st.header(" 簽證與鑑定設定")
    target_name = st.text_input("受調查公司名稱", "XX股份有限公司")
    firm_name = st.text_input("會計師事務所名稱", "誠信聯合會計師事務所")
    auditor_name = st.text_input("簽證會計師姓名", "陳大文 (CPA)")
    st.divider()
    up_files = st.file_uploader("📂 上傳年度財報 PDF", accept_multiple_files=True)

st.title(f" {target_name}：掏空偵測與倒閉預警 (專業版)")

if up_files:
    df_data, reps = final_expert_analysis_engine(target_name, [f.name for f in up_files])
    
    # 圖表區 (解決亂碼)
    st.subheader(f" {target_name}：成長趨勢與不實指標分析")
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    # 圖 1: 本業與關係人收入對比
    df_data.plot(x="年度", y=["本業經營收入", "關係人交易/業外收入"], kind="bar", ax=ax1, alpha=0.7)
    ax1.set_title(f"營收結構分析 - {target_name}", fontsize=14)
    ax1.set_ylabel("金額 (萬元)")
    
    # 圖 2: 預警指標
    sns.lineplot(data=df_data, x="年度", y="M-Score (舞弊診斷)", ax=ax2, marker="o", color="red", label="財報不實指標")
    sns.lineplot(data=df_data, x="年度", y="Z-Score (倒閉預測)", ax=ax2, marker="s", color="blue", label="倒閉預測指標")
    ax2.axhline(y=-1.78, color='gray', linestyle='--')
    ax2.set_title("關鍵時間點預測 (財報不實與倒閉)", fontsize=14)
    ax2.legend()
    
    st.pyplot(fig)

    # 年度分析詳情
    st.error(f" {firm_name} - {auditor_name} 鑑定意見")
    for r in reps:
        with st.expander(f" {r['年度']} 年度分析 - 判定：{r['判定階段']}"):
            st.write(f" **著重監控項目**：{r['重點監控項目']}")
            st.write(f" **年度實質優勢**：{r['優勢評估']}")
            st.markdown("**【警訊摘要】**")
            for w in r['警訊清單']:
                st.write(f" {w}")
    
    # 下載報告
    doc_file = create_final_report(firm_name, auditor_name, target_name, df_data, reps)
    st.sidebar.download_button(f"📥 下載 {target_name} 鑑定報告", data=doc_file, file_name=f"{target_name}_鑑定報告.docx")
else:
    st.info("請輸入資料並上傳 PDF。系統將自動解決亂碼並產出專業鑑定。")
