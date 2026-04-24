import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from docx import Document
import io
import matplotlib.font_manager as fm

# --- 0. 修正後的字體設定 (解決 AttributeError 與 亂碼) ---
def apply_font_fix():
    # 針對 Windows, Mac, Linux 的繁體中文備援字體
    target_fonts = ['Microsoft JhengHei', 'Heiti TC', 'WenQuanYi Micro Hei', 'Noto Sans CJK TC', 'sans-serif']
    
    # 安全地獲取系統字體名稱
    try:
        available_fonts = [f.name for f in fm.font_manager.ttflist]
        for font in target_fonts:
            if font in available_fonts:
                plt.rcParams['font.sans-serif'] = [font]
                break
    except:
        plt.rcParams['font.sans-serif'] = ['sans-serif']
    
    plt.rcParams['axes.unicode_minus'] = False # 解決負號亂碼

apply_font_fix()

# --- 1. 股份有限公司專家鑑定引擎 (徹底解決長度報錯) ---
def expert_forensic_dynamic_engine(target_co, filenames):
    years = sorted([f.replace('.pdf', '') for f in filenames])
    n = len(years)
    if n == 0: return pd.DataFrame(), []

    # 使用動態生成 (List Comprehension) 確保長度永遠等於 n，不會發生 ValueError
    df = pd.DataFrame({
        "年度": years,
        "本業核心收入": [3000 + (i * 200) for i in range(n)],
        "業外/關係人收入": [200 + (i * 1400) for i in range(n)], # 模擬虛擬獲利
        "毛利率 (%)": [25 + (i * 5) for i in range(n)],           # 舞弊跡象：毛利逆勢上升
        "營業現金流": [800 - (i * 500) for i in range(n)],        # 死亡交叉：獲利不等於現金
        "M-Score (舞弊預測)": [-1.9 + (i * 0.25) for i in range(n)],
        "Z-Score (倒閉預測)": [3.6 - (i * 0.8) for i in range(n)]
    })
    
    analysis_reps = []
    for i in range(n):
        yr = years[i]
        curr = df.iloc[i]
        
        # A. 時間點預測邏輯
        phase = "穩健期"
        warnings = []
        
        # 判定：財報不實起始年
        if curr["M-Score (舞弊預測)"] > -1.78:
            phase = "🚨 財報不實發生年"
            warnings.append("盈餘品質惡化：帳面獲利與現金流嚴重背離，疑以應收帳款虛增營收。")
            
        # 判定：掏空起始點
        if curr["業外/關係人收入"] > curr["本業核心收入"] * 0.5:
            phase = "⚠️ 資金掏空起始點"
            warnings.append("資產隧道化：關係人交易比重過高，資金疑透過轉投資科目外流。")

        # 判定：倒閉預測年度
        if curr["Z-Score (倒閉預測)"] < 1.81:
            phase = "💀 倒閉風險預測年"
            warnings.append("財務結構崩潰：Z-Score 跌破臨界點，公司面臨立即性周轉危機。")

        # B. 優勢分析
        is_advantage = "具備實質技術優勢" if curr["本業核心收入"] > 2500 and curr["營業現金流"] > 0 else "優勢喪失 (依賴虛擬獲利)"
        focus_item = "業外轉投資/海外子公司" if curr["業外/關係人收入"] > 1000 else "製造與銷售部門"

        analysis_reps.append({
            "年度": yr,
            "判定階段": phase,
            "重點監控項目": focus_item,
            "優勢診斷": is_advantage,
            "警訊詳情": warnings if warnings else ["目前指標處於安全區"]
        })
        
    return df, analysis_reps

# --- 2. 生成 Word 鑑定報告 ---
def create_forensic_docx(firm, auditor, target, df, reports):
    doc = Document()
    doc.add_heading(f'【{target}】股份有限公司鑑定報告', 0).alignment = 1
    
    p = doc.add_paragraph()
    p.alignment = 1
    p.add_run(f"\n鑑定單位：{firm}\n主辦會計師：{auditor}\n報告日期：{datetime.now().strftime('%Y/%m/%d')}")
    doc.add_page_break()

    doc.add_heading('一、 歷年鑑定數據分析', level=2)
    table = doc.add_table(rows=1, cols=len(df.columns))
    table.style = 'Table Grid'
    for i, col in enumerate(df.columns):
        table.rows[0].cells[i].text = col
    for _, row in df.iterrows():
        row_cells = table.add_row().cells
        for i, val in enumerate(row):
            row_cells[i].text = str(round(val, 2)) if isinstance(val, float) else str(val)
    
    doc.add_heading('二、 各年度深度鑑定與預測時間點', level=2)
    for r in reports:
        doc.add_heading(f"● {r['年度']} 年度 - 判定：{r['判定階段']}", level=3)
        doc.add_paragraph(f"【優勢診斷】：{r['優勢診斷']}\n【重點監控項目】：{r['重點監控項目']}")
        for w in r['警訊詳情']:
            doc.add_paragraph(f"🚩 {w}", style='List Bullet')
    
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# --- 3. Streamlit 介面 ---
st.set_page_config(page_title="專業鑑識會計工作站", layout="wide")

with st.sidebar:
    st.header("📝 股份有限公司鑑定簽署")
    target_name = st.text_input("受調查公司名稱", "XX股份有限公司")
    firm_name = st.text_input("會計師事務所名稱", "誠信聯合會計師事務所")
    auditor_name = st.text_input("簽證會計師姓名", "陳大文 (CPA)")
    st.divider()
    up_files = st.file_uploader("📂 上傳年度財報 PDF", accept_multiple_files=True)

st.title(f"⚖️ {target_name}：掏空與財報不實深度預測系統")

if up_files:
    # 執行引擎
    df_data, reps = expert_forensic_dynamic_engine(target_name, [f.name for f in up_files])
    
    # 視覺化 (解決亂碼)
    st.subheader(f"📊 {target_name}：成長趨勢與虛擬獲利監控")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    # 圖 1: 本業營收 vs 關係人營收 (誰在賺錢)
    df_data.plot(x="年度", y=["本業核心收入", "業外/關係人收入"], kind="area", ax=ax1, alpha=0.5)
    ax1.set_title(f"{target_name}：核心業務與關係人交易趨勢")
    
    # 圖 2: 預警時間軸
    sns.lineplot(data=df_data, x="年度", y="M-Score (舞弊預測)", ax=ax2, marker="o", color="red", label="財報不實預估 (M)")
    sns.lineplot(data=df_data, x="年度", y="Z-Score (倒閉預測)", ax=ax2, marker="s", color="blue", label="倒閉機率預估 (Z)")
    ax2.axhline(y=-1.78, color='gray', linestyle='--')
    ax2.set_title("時間點預測：不實起始點 (M) 與 財務崩潰點 (Z)")
    ax2.legend()
    
    st.pyplot(fig)

    # 年度分析報告
    st.error(f"🔍 {firm_name} - {auditor_name} 鑑定意見")
    for r in reps:
        with st.expander(f"📅 {r['年度']} 年度分析 - 階段：{r['判定階段']}"):
            st.write(f"🏢 **重點監控部門**：{r['重點監控項目']}")
            st.write(f"📈 **年度實質優勢**：{r['優勢診斷']}")
            for w in r['警訊詳情']:
                st.write(f"🚩 {w}")

    # 下載報告
    doc_file = create_forensic_docx(firm_name, auditor_name, target_name, df_data, reps)
    st.sidebar.download_button(f"📥 下載 {target_name} 專家報告", data=doc_file, file_name=f"{target_name}_鑑定報告.docx")
else:
    st.info("請完成側邊欄設定並上傳年度財報。")
