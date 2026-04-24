import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from docx import Document
import io

# --- 1. 專家級掏空與倒閉預測引擎 ---
def forensic_prediction_engine(target_co, filenames):
    years = sorted([f.replace('.pdf', '') for f in filenames])
    n = len(years)
    
    # 動態模擬數據：模擬從正常到倒閉的過程
    # 這裡假設倒閉發生在最後一年，掏空跡象從中間年份開始
    df = pd.DataFrame({
        "年度": years,
        "帳面淨利": [500 + (i * 100) for i in range(n)],
        "營業現金流": [400, 100, -200, -800][-n:], # 現金流死魚眼背離
        "M-Score (舞弊)": [-1.9, -1.7, -1.4, -1.1][-n:], # 越往後舞弊機率越高
        "Z-Score (倒閉)": [3.5, 2.8, 1.9, 0.8][-n:],    # 越往後倒閉機率越高
        "關係人往來比率": [5, 15, 45, 85][-n:]          # 掏空資金流向
    })
    
    analysis_results = []
    for i in range(n):
        yr = years[i]
        curr = df.iloc[i]
        status = "正常"
        risk_notes = []
        
        # 判斷掏空起始跡象
        if curr["M-Score (舞弊)"] > -1.78 and curr["營業現金流"] < 0:
            status = "⚠️ 偵測到掏空/不實跡象"
            risk_notes.append("利潤與現金流死亡交叉：虛增營收嫌疑極大。")
        
        # 判斷倒閉預測
        if curr["Z-Score (倒閉)"] < 1.81:
            status = " 高風險倒閉預警"
            risk_notes.append("財務結構崩潰：Z-Score 進入破產紅色警戒區。")
            
        analysis_results.append({
            "年度": yr,
            "鑑定狀態": status,
            "風險點": risk_notes if risk_notes else ["數據尚在安全範圍"],
            "專家建議": "應針對該年度執行資產減損測試與關係人穿透查核。" if status != "正常" else "持續監控"
        })
        
    return df, analysis_results

# --- 2. Word 報告生成 (包含預測章節) ---
def create_prediction_docx(firm, auditor, target, df, analysis):
    doc = Document()
    doc.add_heading(f'【{target}】掏空跡象與倒閉年度預測報告', 0)
    
    doc.add_heading('一、 歷年鑑定數據對照表', level=2)
    # (表格代碼同前...)
    
    doc.add_heading('二、 年度風險診斷與倒閉預測', level=2)
    for res in analysis:
        doc.add_heading(f"● {res['年度']} 年度鑑定：{res['鑑定狀態']}", level=3)
        for note in res['風險點']:
            doc.add_paragraph(note, style='List Bullet')
        doc.add_paragraph(f"【查核理由】：本年度顯示之{res['鑑定狀態']}，係由多項背離指標觸發，具備鑑識會計上的實質風險。")
        
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# --- 3. Streamlit 介面 ---
st.set_page_config(page_title="Forensic Prediction Pro", layout="wide")

with st.sidebar:
    st.header(" 鑑定簽署")
    target_name = st.text_input("受調查公司", "XX企業")
    auditor = st.text_input("鑑定師", "陳會計師")
    up_files = st.file_uploader("上傳財報 PDF", accept_multiple_files=True)

st.title(f" {target_name}：掏空跡象偵測與倒閉預測系統")

if up_files:
    df_data, analysis_report = forensic_prediction_engine(target_name, [f.name for f in up_files])
    
    # 視覺化：倒閉預警線
    st.subheader(" 財務崩塌曲線 (Z-Score 倒閉預測)")
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.lineplot(data=df_data, x="年度", y="Z-Score (倒閉)", marker="s", color="red", label="倒閉預警指標 (Z)")
    plt.axhline(y=1.81, color='gray', linestyle='--', label="破產臨界線")
    plt.axhline(y=2.99, color='green', linestyle='--', label="財務安全線")
    plt.title(f"{target_name} 倒閉預測趨勢")
    plt.legend()
    st.pyplot(fig)

    # 年度分析顯示
    st.error(f" {target_name}：各年度深度鑑定報告")
    for res in analysis_report:
        with st.expander(f" {res['年度']} - 狀態：{res['鑑定狀態']}"):
            for p in res['風險點']:
                st.write(f" {p}")
            st.warning(f"**專家查核理由：**\n這是一個關鍵的年度變動點。在掏空案模型中，此時期的資產膨脹（透過關係人）與現金枯竭是判定『惡意掏空』的核心證據。")

    # 提供下載
    doc_file = create_prediction_docx("誠信事務所", auditor, target_name, df_data, analysis_report)
    st.sidebar.download_button("📥 下載專家鑑定報告", data=doc_file, file_name=f"{target_name}_鑑定報告.docx")
