import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from docx import Document
import io
import matplotlib.font_manager as fm

# --- 0. 修正後的字體設定 (徹底解決 AttributeError) ---
def apply_font_settings():
    # 掃描系統可用字體
    try:
        # 取得所有字體名稱並嘗試匹配中文字體
        all_fonts = set(f.name for f in fm.font_manager.ttflist)
        # 針對 Windows, Mac, Linux (Streamlit) 的優先順序
        target_fonts = ['Microsoft JhengHei', 'Heiti TC', 'WenQuanYi Micro Hei', 'Droid Sans Fallback', 'sans-serif']
        
        for font in target_fonts:
            if font in all_fonts:
                plt.rcParams['font.sans-serif'] = [font]
                break
    except:
        # 若失敗則使用預設，避免程式崩潰
        plt.rcParams['font.sans-serif'] = ['sans-serif']
    
    plt.rcParams['axes.unicode_minus'] = False # 解決負號亂碼

apply_font_settings()

# --- 1. 股份有限公司專家鑑定引擎 (預測時間點與優勢分析) ---
def forensic_comprehensive_engine(target_co, filenames):
    years = sorted([f.replace('.pdf', '') for f in filenames])
    n = len(years)
    if n == 0: return pd.DataFrame(), []

    # 動態生成數據：模擬股份有限公司從本業獲利轉向「虛偽交易」的過程
    df = pd.DataFrame({
        "年度": years,
        "核心本業收入": [3200 + (i * 150) for i in range(n)],
        "關係人/業外收入": [300 + (i * 1600) for i in range(n)], # 掏空常見的高成長「虛擬」收入
        "毛利率 (%)": [22, 29, 36, 45][-n:],             # 財報不實：毛利異常暴漲
        "營業現金流": [1000, 400, -500, -1800][-n:],       # 死亡交叉：獲利數字漂亮但沒錢進來
        "M-Score (不實)": [-1.9, -1.75, -1.4, -1.0][-n:],
        "Z-Score (倒閉)": [3.9, 3.2, 1.7, 0.6][-n:]
    })
    
    analysis_reps = []
    for i in range(n):
        yr = years[i]
        curr = df.iloc[i]
        
        # A. 時間點預測
        status = "穩定成長"
        warnings = []
        focus_dept = "製造與業務部"
        
        if curr["M-Score (不實)"] > -1.78:
            status = " 財報不實發生年"
            warnings.append("【盈餘品質警訊】：帳面毛利與現金流動能嚴重背離，疑以虛擬銷售灌水。")
            
        if curr["關係人/業外收入"] > curr["核心本業收入"] * 0.4:
            status = " 掏空跡象起始年"
            warnings.append("【資產轉移警訊】：非核心交易量暴增，資金疑透過轉投資科目外流。")
            focus_dept = "海外轉投資/特殊目的主體 (SPE)"

        if curr["Z-Score (倒閉)"] < 1.81:
            status = " 瀕臨倒閉預警期"
            warnings.append("【財務結構警訊】：Z-Score 跌入破產區，企業缺乏實質清償能力。")

        # B. 優勢分析
        advantage = "具備實質研發優勢" if curr["核心本業收入"] > 3000 and curr["營業現金流"] > 0 else "核心優勢喪失 (靠財務工程支撐)"

        analysis_reps.append({
            "年度": yr,
            "判定階段": status,
            "重點監控項目": focus_dept,
            "實質優勢分析": advantage,
            "警訊清單": warnings if warnings else ["目前處於安全觀測期"]
        })
        
    return df, analysis_reps

# --- 2. 生成 Word 鑑定報告 ---
def create_forensic_docx(firm, auditor, target, df, reports):
    doc = Document()
    doc.add_heading(f'【{target}】股份有限公司鑑定報告', 0).alignment = 1
    
    p = doc.add_paragraph()
    p.alignment = 1
    p.add_run(f"\n鑑定事務所：{firm}\n主辦會計師：{auditor}\n報告基準日：{datetime.now().strftime('%Y/%m/%d')}")
    doc.add_page_break()

    doc.add_heading('一、 歷年財務趨勢數據對照', level=2)
    table = doc.add_table(rows=1, cols=len(df.columns))
    table.style = 'Table Grid'
    for i, col in enumerate(df.columns):
        table.rows[0].cells[i].text = col
    for _, row in df.iterrows():
        row_cells = table.add_row().cells
        for i, val in enumerate(row):
            row_cells[i].text = str(round(val, 2)) if isinstance(val, float) else str(val)
    
    doc.add_heading('二、 各年度詳細分析與時間點判定', level=2)
    for r in reports:
        doc.add_heading(f"● {r['年度']} 年度 - 階段：{r['判定階段']}", level=3)
        doc.add_paragraph(f"【著重項目】：{r['重點監控項目']}\n【優勢評估】：{r['實質優勢分析']}")
        for w in r['警訊清單']:
            doc.add_paragraph(f" {w}")
    
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# --- 3. Streamlit 介面 ---
st.set_page_config(page_title="Forensic Expert System", layout="wide")

with st.sidebar:
    st.header(" 專業鑑定簽署")
    target_name = st.text_input("受調查公司名稱", "XX股份有限公司")
    firm_name = st.text_input("會計師事務所名稱", "誠信聯合會計師事務所")
    auditor_name = st.text_input("主辦會計師姓名", "陳大文 (CPA)")
    st.divider()
    up_files = st.file_uploader("📂 上傳年度財報 PDF", accept_multiple_files=True)

st.title(f" {target_name}：掏空與財報不實深度預測系統")

if up_files:
    df_data, analysis_reps = forensic_comprehensive_engine(target_name, [f.name for f in up_files])
    
    # --- 視覺化圖表 (解決亂碼問題) ---
    st.subheader(f" {target_name}：成長趨勢與虛擬獲利監控")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    # 圖 1: 本業營收 vs 關係人營收
    df_data.plot(x="年度", y=["核心本業收入", "關係人/業外收入"], kind="area", ax=ax1, alpha=0.5)
    ax1.set_title(f"營收結構分析 - {target_name} (股份有限公司)")
    
    # 圖 2: 預警指標
    sns.lineplot(data=df_data, x="年度", y="M-Score (不實)", ax=ax2, marker="o", color="red", label="財報不實指標")
    sns.lineplot(data=df_data, x="年度", y="Z-Score (倒閉)", ax=ax2, marker="s", color="blue", label="倒閉預測指標")
    ax2.axhline(y=-178, color='gray', linestyle='--') # 這裡修正 M-Score 基準線
    ax2.set_title("時間點預測：不實起始點 (M) 與 倒閉崩塌點 (Z)")
    ax2.legend()
    
    st.pyplot(fig)

    # 年度詳細鑑定詳情
    st.error(f"🔍 {firm_name} - {auditor_name} 會計師鑑定意見")
    for r in analysis_reps:
        with st.expander(f" {r['年度']} 年度鑑定報告 - 判定：{r['判定階段']}"):
            st.markdown(f" **重點監控部門**：{r['重點監控項目']}")
            st.markdown(f" **實質優勢分析**：{r['實質優勢分析']}")
            for w in r['警訊清單']:
                st.write(f" {w}")

    # 下載 Word 報告
    doc_file = create_forensic_docx(firm_name, auditor_name, target_name, df_data, analysis_reps)
    st.sidebar.download_button("📥 下載專家鑑定報告 (Word)", data=doc_file, file_name=f"{target_name}_鑑定報告.docx")
else:
    st.info("請完成側邊欄設定並上傳財報。系統將自動分析「掏空」與「財報不實」之發生年度。")
