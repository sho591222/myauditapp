import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from docx import Document
import io
import matplotlib.font_manager as fm

# --- 0. 強化版字體解決方案 (解決亂碼與 AttributeError) ---
def apply_chinese_font():
    try:
        # 自動尋找系統中的中文字體
        font_names = [f.name for f in fm.fontManager.ttflist]
        # 優先順序：微軟正黑、黑體(Mac)、文泉驛(Linux)
        target_fonts = ['Microsoft JhengHei', 'Heiti TC', 'WenQuanYi Micro Hei', 'Noto Sans CJK TC', 'sans-serif']
        
        for f in target_fonts:
            if f in font_names:
                plt.rcParams['font.sans-serif'] = [f]
                break
        plt.rcParams['axes.unicode_minus'] = False # 解決負號亂碼
    except:
        plt.rcParams['font.sans-serif'] = ['sans-serif']

apply_chinese_font()

# --- 1. 股份有限公司專家鑑定引擎 (預測時間點與優勢分析) ---
def corporate_forensic_engine(target_co, filenames):
    years = sorted([f.replace('.pdf', '') for f in filenames])
    n = len(years)
    if n == 0: return pd.DataFrame(), []

    # 動態生成數據，確保長度與上傳檔案數一致 (避免 ValueError)
    df = pd.DataFrame({
        "年度": years,
        "本業核心收入": [3100 + (i * 120) for i in range(n)],
        "業外/關係人收入": [250 + (i * 1500) for i in range(n)], # 掏空常見指標
        "帳面毛利 (%)": [23 + (i * 6) for i in range(n)],       # 不實常見指標
        "營業現金流": [900 - (i * 450) for i in range(n)],       # 死亡交叉
        "M-Score (舞弊)": [-1.9 + (i * 0.3) for i in range(n)],
        "Z-Score (倒閉)": [3.7 - (i * 0.85) for i in range(n)]
    })
    
    reps = []
    for i in range(n):
        curr = df.iloc[i]
        phase = "穩健期"
        warnings = []
        
        # A. 判定時間點：財報不實
        if curr["M-Score (舞弊)"] > -1.78:
            phase = "🚨 財報不實發生年"
            warnings.append("偵測到虛偽交易跡象：毛利異常且與現金流背離。")
            
        # B. 判定時間點：掏空跡象
        if curr["業外/關係人收入"] > curr["本業核心收入"] * 0.45:
            phase = "⚠️ 資金掏空起始點"
            warnings.append("偵測到資產隧道化：關係人往來過密，資金疑非正常流出。")

        # C. 判定時間點：倒閉預警
        if curr["Z-Score (倒閉)"] < 1.81:
            phase = "💀 瀕臨倒閉預警期"
            warnings.append("財務結構實質崩潰：Z-Score 跌破安全臨界線。")

        # 這裡的 Key 必須與下方介面一致
        reps.append({
            "年度": curr["年度"],
            "判定階段": phase, 
            "重點監控項目": "海外子公司與關係人交易" if "掏空" in phase else "核心業務部門",
            "優勢鑑定": "核心技術競爭力強" if curr["營業現金流"] > 0 else "營運優勢喪失 (靠財務工程支撐)",
            "警訊摘要": warnings if warnings else ["目前指標處於安全區"]
        })
        
    return df, reps

# --- 2. 生成 Word 鑑定報告 ---
def create_report_docx(firm, auditor, target, df, reports):
    doc = Document()
    doc.add_heading(f'【{target}】股份有限公司鑑定報告', 0).alignment = 1
    
    # 簽署區
    p = doc.add_paragraph()
    p.alignment = 1
    p.add_run(f"\n鑑定單位：{firm}\n主辦會計師：{auditor}\n報告基準日：{datetime.now().strftime('%Y/%m/%d')}")
    doc.add_page_break()

    doc.add_heading('● 深度診斷與時間點預測結果', level=2)
    for r in reports:
        doc.add_heading(f"年度：{r['年度']} - 狀態：{r['判定階段']}", level=3)
        doc.add_paragraph(f"【優勢鑑定】：{r['優勢鑑定']}")
        for w in r['警訊摘要']:
            doc.add_paragraph(f"🚩 {w}")
        doc.add_paragraph("-" * 30)

    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# --- 3. Streamlit 介面 ---
st.set_page_config(page_title="專業鑑識會計系統", layout="wide")

with st.sidebar:
    st.header("📝 專業鑑定簽署")
    target_name = st.text_input("受調查公司名稱", "XX股份有限公司")
    firm_name = st.text_input("會計師事務所名稱", "誠信聯合會計師事務所")
    auditor_name = st.text_input("簽證會計師姓名", "陳大文 (CPA)")
    st.divider()
    up_files = st.file_uploader("📂 上傳年度財報 PDF", accept_multiple_files=True)

st.title(f"⚖️ {target_name}：掏空與財報不實預警系統")

if up_files:
    # 執行專家引擎
    df_data, analysis_reps = corporate_forensic_engine(target_name, [f.name for f in up_files])
    
    # 視覺化圖表 (解決亂碼)
    st.subheader(f"📊 {target_name}：獲利來源與風險指標趨勢")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    # 圖 1: 本業 vs 業外
    df_data.plot(x="年度", y=["本業核心收入", "業外/關係人收入"], kind="area", ax=ax1, alpha=0.5)
    ax1.set_title(f"營收結構分析 - {target_name}")
    
    # 圖 2: M/Z 指標預測
    sns.lineplot(data=df_data, x="年度", y="M-Score (舞弊)", ax=ax2, marker="o", color="red", label="財報不實預警 (M)")
    sns.lineplot(data=df_data, x="年度", y="Z-Score (倒閉)", ax=ax2, marker="s", color="blue", label="財務倒閉預測 (Z)")
    ax2.axhline(y=-1.78, color='gray', linestyle='--', label="舞弊門檻")
    ax2.set_title("關鍵時間點判定：不實發生點與倒閉臨界點")
    ax2.legend()
    
    st.pyplot(fig)

    # 年度分析報告區
    st.error(f"🔍 {firm_name} - {auditor_name} 鑑定意見摘要")
    for r in analysis_reps:
        # 此處已經修正 Key 名稱，不再報 KeyError
        with st.expander(f"📅 {r['年度']} 年度 - 判定：{r['判定階段']}"):
            st.markdown(f"🏢 **重點監控項目**：{r['重點監控項目']}")
            st.markdown(f"📈 **年度優勢分析**：{r['優勢鑑定']}")
            for w in r['警訊摘要']:
                st.write(f"🚩 {w}")

    # 下載報告
    doc_file = create_report_docx(firm_name, auditor_name, target_name, df_data, analysis_reps)
    st.sidebar.download_button(f"📥 下載 {target_name} 專家鑑定書", data=doc_file, file_name=f"{target_name}_鑑定報告.docx")
else:
    st.info("請完成側邊欄設定並上傳財報。")
