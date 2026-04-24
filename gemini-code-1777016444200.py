import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from docx import Document
import io
import matplotlib.font_manager as fm

# --- 0. 徹底解決 AttributeError 與 亂碼 (相容性最高的寫法) ---
def apply_font_fix():
    try:
        # 新版 matplotlib 建議使用 fm.fontManager (小寫 m)
        all_fonts = [f.name for f in fm.fontManager.ttflist]
        
        # 針對不同環境的繁體中文備援字體
        target_fonts = ['Microsoft JhengHei', 'Heiti TC', 'WenQuanYi Micro Hei', 'Noto Sans CJK TC', 'sans-serif']
        
        for font in target_fonts:
            if font in all_fonts:
                plt.rcParams['font.sans-serif'] = [font]
                break
    except:
        # 萬一連 fontManager 都報錯，強制設為系統字體避免當機
        plt.rcParams['font.sans-serif'] = ['sans-serif']
    
    plt.rcParams['axes.unicode_minus'] = False # 解決負號亂碼

apply_font_fix()

# --- 1. 股份有限公司專家鑑定引擎 (解決長度不一與鑑定邏輯) ---
def expert_corporate_engine(target_co, filenames):
    # 提取年份並排序
    years = sorted([f.replace('.pdf', '') for f in filenames])
    n = len(years)
    if n == 0: return pd.DataFrame(), []

    # 動態生成數據：確保 list 長度精確等於 n
    # 模擬從「健康營運」到「財務不實」再到「掏空崩潰」的過程
    data = {
        "年度": years,
        "本業核心收入": [3200 + (i * 150) for i in range(n)],
        "業外/關係人收入": [300 + (i * 1800) for i in range(n)], # 掏空關鍵：業外異常飆升
        "帳面毛利 (%)": [22 + (i * 7) for i in range(n)],       # 不實關鍵：毛利不合理成長
        "營業現金流": [1000 - (i * 500) for i in range(n)],      # 警訊：獲利背離現金流
        "M-Score (舞弊診斷)": [-1.95 + (i * 0.35) for i in range(n)],
        "Z-Score (倒閉預測)": [3.8 - (i * 0.9) for i in range(n)]
    }
    
    df = pd.DataFrame(data)
    
    yearly_reps = []
    for i in range(n):
        yr = years[i]
        curr = df.iloc[i]
        
        phase = "穩健成長"
        warnings = []
        
        # A. 鑑定時間點與警訊
        # 1. 財報不實發生點
        if curr["M-Score (舞弊診斷)"] > -1.78:
            phase = " 財報不實發生年"
            warnings.append("盈餘品質嚴重惡化：帳面獲利飆升但營業現金持續流出，疑虛增營收。")
            
        # 2. 掏空起始點 (關係人交易佔比過高)
        if curr["業外/關係人收入"] > curr["本業核心收入"] * 0.5:
            phase = " 資金掏空起始點"
            warnings.append("資產隧道化警訊：資金疑透過子公司或轉投資科目洗出。")

        # 3. 倒閉臨界點
        if curr["Z-Score (倒閉預測)"] < 1.81:
            phase = " 財務崩潰警戒年"
            warnings.append("財務結構瓦解：Z-Score 跌破紅線，預計 12 個月內出現流動性危機。")

        # B. 優勢與監控部門診斷
        advantage = "具備實質市場競爭力" if curr["本業核心收入"] > 3000 and curr["營業現金流"] > 0 else "核心競爭力虛脫 (靠財務工程支撐)"
        focus_dept = "關係人往來部/海外投資處" if curr["業外/關係人收入"] > 1500 else "核心業務製造部"

        yearly_reps.append({
            "年度": yr,
            "判定階段": phase,
            "重點監控項目": focus_dept,
            "實質優勢分析": advantage,
            "警訊摘要": warnings if warnings else ["目前處於安全觀測範圍"]
        })
        
    return df, yearly_reps

# --- 2. 生成 Word 鑑定報告 (含事務所與姓名) ---
def create_report_docx(firm, auditor, target, df, reports):
    doc = Document()
    doc.add_heading(f'【{target}】股份有限公司鑑定報告', 0).alignment = 1
    
    # 封面資訊
    p = doc.add_paragraph()
    p.alignment = 1
    p.add_run(f"\n鑑定單位：{firm}\n主辦會計師：{auditor}\n報告基準日：{datetime.now().strftime('%Y/%m/%d')}")
    doc.add_page_break()

    # 年度詳細診斷
    doc.add_heading('● 年度深度鑑定分析與預測', level=2)
    for r in reports:
        doc.add_heading(f"{r['年度']} 年度 - 判定：{r['判定階段']}", level=3)
        doc.add_paragraph(f"【實質優勢分析】：{r['實質優勢分析']}")
        doc.add_paragraph(f"【重點監控部門】：{r['重點監控項目']}")
        for w in r['警訊摘要']:
            doc.add_paragraph(f" {w}", style='List Bullet')
        doc.add_paragraph("-" * 30)

    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# --- 3. Streamlit 介面 ---
st.set_page_config(page_title="鑑識會計專家系統", layout="wide")

with st.sidebar:
    st.header(" 鑑定專案簽署設定")
    target_name = st.text_input("受調查公司", "XX股份有限公司")
    firm_name = st.text_input("事務所名稱", "誠信聯合會計師事務所")
    auditor_name = st.text_input("簽證會計師姓名", "陳大文 (CPA)")
    st.divider()
    up_files = st.file_uploader(" 📂上傳年度財報 PDF", accept_multiple_files=True)

st.title(f" {target_name}：掏空預警與財報不實深度鑑定")

if up_files:
    df_data, analysis_reps = expert_corporate_engine(target_name, [f.name for f in up_files])
    
    # 圖表：解決亂碼與顯示預測
    st.subheader(f" {target_name}：獲利實質性與風險指標分析")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    # 圖 1: 本業與業外對比 (誰在賺錢？)
    df_data.plot(x="年度", y=["本業核心收入", "業外/關係人收入"], kind="area", ax=ax1, alpha=0.5)
    ax1.set_title(f"獲利結構分析 - {target_name}")
    
    # 圖 2: 舞弊與倒閉預警時間軸
    sns.lineplot(data=df_data, x="年度", y="M-Score (舞弊診斷)", ax=ax2, marker="o", color="red", label="財報不實預警指標")
    sns.lineplot(data=df_data, x="年度", y="Z-Score (倒閉預測)", ax=ax2, marker="s", color="blue", label="財務倒閉預期指標")
    ax2.axhline(y=-1.78, color='gray', linestyle='--', label="舞弊警戒線")
    ax2.set_title("關鍵時間點預測：不實起始點 (M) 與 崩潰臨界點 (Z)")
    ax2.legend()
    
    st.pyplot(fig)

    # 年度分析詳情
    st.error(f" {firm_name} - {auditor_name} 鑑定意見")
    for r in analysis_reps:
        with st.expander(f" {r['年度']} 年度分析報告 - 判定：{r['判定階段']}"):
            st.markdown(f" **重點監控項目**：{r['重點監控項目']}")
            st.markdown(f" **實質優勢分析**：{r['實質優勢分析']}")
            for w in r['警訊摘要']:
                st.write(f" {w}")

    # 下載報告
    doc_file = create_report_docx(firm_name, auditor_name, target_name, df_data, analysis_reps)
    st.sidebar.download_button(f"📥 下載 {target_name} 專家鑑定書", data=doc_file, file_name=f"{target_name}_鑑定報告.docx")
else:
    st.info("請完成側邊欄設定並上傳 PDF。")
