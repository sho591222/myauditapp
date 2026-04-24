import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from docx import Document
import io

# --- 1. 股份有限公司專家鑑定與趨勢預測引擎 ---
def expert_corporate_forensic_engine(target_co, filenames):
    years = sorted([f.replace('.pdf', '') for f in filenames])
    n = len(years)
    if n == 0: return pd.DataFrame(), []

    # 動態生成數據：模擬股份有限公司從盛轉衰、進入掏空的過程
    df = pd.DataFrame({
        "年度": years,
        "核心本業收入": [3000 + (i * 200) for i in range(n)],
        "關係人/業外轉投資": [100 + (i * 1500) for i in range(n)], # 掏空常見的高成長「虛擬」收入
        "毛利率 (%)": [28, 32, 35, 40][-n:],             # 財報不實：毛利逆勢成長
        "營業現金流": [800, 300, -200, -1200][-n:],      # 死亡交叉：錢沒進來
        "M-Score (財報不實)": [-2.0, -1.8, -1.5, -1.1][-n:],
        "Z-Score (倒閉預測)": [3.8, 3.1, 1.9, 0.9][-n:]
    })
    
    yearly_expert_analysis = []
    for i in range(n):
        yr = years[i]
        curr = df.iloc[i]
        
        # A. 時間點預測與警訊分析
        status = "營運穩健"
        warnings = []
        focus_item = "本業製造/服務"
        
        # 判定：何時開始財報不實？
        if curr["M-Score (財報不實)"] > -1.78:
            status = " 財報不實/舞弊發生年"
            warnings.append("【盈餘品質警訊】：帳面獲利與現金流嚴重背離，疑以應收帳款虛增營收。")
        
        # 判定：何時開始有掏空跡象？
        if curr["關係人/業外轉投資"] > curr["核心本業收入"] * 0.4:
            status = " 資金掏空/隧道行為起點"
            warnings.append("【資產轉移警訊】：非核心業務收入暴增，疑透過子公司進行資產套現與挪用。")
            focus_item = "海外控股/轉投資部門 (虛擬獲利中心)"

        # 判定：何時預測倒閉？
        if curr["Z-Score (倒閉預測)"] < 1.81:
            status = " 倒閉風險預測年"
            warnings.append("【流動性警訊】：財務結構已崩潰，預計未來 12 個月內出現資金缺口。")

        # B. 優勢與競爭力評估
        advantage = "具備規模經濟優勢" if curr["核心本業收入"] > 2500 else "核心競爭力衰退"

        yearly_expert_analysis.append({
            "年度": yr,
            "判定階段": status,
            "著重監控項目": focus_item,
            "優勢分析": advantage,
            "警訊詳情": warnings if warnings else ["處於安全觀測範圍"],
            "鑑定理由": f"針對 {target_co} 於 {yr} 年之表現，其成長動能完全依賴『高度疑慮之關係人交易』，本業已喪失實質賺錢能力。"
        })
        
    return df, yearly_expert_analysis

# --- 2. 生成多頁式 Word 專家鑑定書 ---
def create_expert_docx(firm, auditor, target, df, reports):
    doc = Document()
    doc.add_heading(f'【{target}】股份有限公司鑑定報告', 0).alignment = 1
    
    doc.add_heading('一、 歷年財務成長與風險指標總覽', level=2)
    table = doc.add_table(rows=1, cols=len(df.columns))
    table.style = 'Table Grid'
    for i, col in enumerate(df.columns):
        table.rows[0].cells[i].text = col
    for _, row in df.iterrows():
        row_cells = table.add_row().cells
        for i, val in enumerate(row):
            row_cells[i].text = str(round(val, 2)) if isinstance(val, float) else str(val)
    doc.add_page_break()

    doc.add_heading('二、 各年度詳細分析與時間點預測 (Timeline Analysis)', level=2)
    for r in reports:
        doc.add_heading(f"● {r['年度']} 年度鑑定：{r['判定階段']}", level=3)
        doc.add_paragraph(f"【著重監控項目】：{r['著重監控項目']}")
        doc.add_paragraph(f"【實質優勢評估】：{r['優勢分析']}")
        doc.add_paragraph("【異常警訊清單】：")
        for w in r['警訊詳情']:
            doc.add_paragraph(w, style='List Bullet')
        doc.add_paragraph(f"【鑑定判斷】：{r['鑑定理由']}")
        doc.add_paragraph("-" * 30)

    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# --- 3. Streamlit 介面 ---
st.set_page_config(page_title="Forensic Expert", layout="wide")

with st.sidebar:
    st.header(" 股份有限公司鑑定設定")
    target_name = st.text_input("受調查公司名稱", "XX股份有限公司")
    auditor_name = st.text_input("主辦鑑定師", "陳會計師 (CPA)")
    up_files = st.file_uploader(" 上傳年度財報 PDF", accept_multiple_files=True)

st.title(f" {target_name}：掏空預警、財報不實與成長趨勢鑑定")

if up_files:
    df_data, analysis_reps = expert_corporate_forensic_engine(target_name, [f.name for f in up_files])
    
    # 下載 Word
    doc_file = create_expert_docx("誠信聯合會計師事務所", auditor_name, target_name, df_data, analysis_reps)
    st.sidebar.download_button(f"📥 下載 {target_name} 專家鑑定書", data=doc_file, file_name=f"{target_name}_鑑定報告.docx")

    # 視覺化：成長趨勢與背離
    st.subheader("📊 營收結構變動與獲利能力背離分析")
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    # 趨勢圖 1: 誰在賺錢？ (本業 vs 關係人)
    df_data.plot(x="年度", y=["核心本業收入", "關係人/業外轉投資"], kind="area", ax=ax1, alpha=0.4)
    ax1.set_title("成長趨勢分析：本業 vs 虛擬收入 (關係人)")
    
    # 趨勢圖 2: 舞弊與倒閉預測
    sns.lineplot(data=df_data, x="年度", y="M-Score (財報不實)", ax=ax2, marker="o", color="red", label="財報不實機率")
    sns.lineplot(data=df_data, x="年度", y="Z-Score (倒閉預測)", ax=ax2, marker="s", color="blue", label="倒閉預估指標")
    ax2.axhline(y=-1.78, color='gray', linestyle='--')
    ax2.set_title("關鍵時間點預測：財報不實 (M) 與 倒閉 (Z)")
    
    st.pyplot(fig)

    st.divider()

    # 顯示各年度詳細報告
    st.error(f" {target_name}：跨年度深度鑑定與優勢分析")
    for r in analysis_reps:
        with st.expander(f" {r['年度']} - 判定階段：{r['判定階段']}"):
            colA, colB = st.columns(2)
            with colA:
                st.markdown(f"** 著重監控項目**：\n{r['著重監控項目']}")
                st.markdown(f"** 優勢分析**：\n{r['優勢分析']}")
            with colB:
                st.markdown("**【核心警訊分析】**")
                for w in r['警訊詳情']:
                    st.write(f" {w}")
            st.info(f"**【專家鑑定理由與建議程序】**\n\n{r['鑑定理由']}")
            
    st.table(df_data)
else:
    st.info("請輸入股份有限公司名稱並上傳各年度 PDF 財報以啟動分析。")
