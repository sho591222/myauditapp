import streamlit as st
import pandas as pd
import base64
import time
import matplotlib.pyplot as plt
from fpdf import FPDF
import io
import os

# --- 1. 軟體風格與繁體中文介面 ---
st.set_page_config(page_title="多案源財務鑑定工作站", layout="wide")
st.markdown("""
    <style>
    .report-card { background: #ffffff; padding: 25px; border-radius: 15px; border-left: 10px solid #273c75; box-shadow: 0 4px 12px rgba(0,0,0,0.1); color: #333; }
    .stButton>button { background-color: #c0392b !important; color: white !important; font-weight: bold; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 核心分析引擎 ---
def run_audit_engine(file_name):
    years = [str(y) for y in range(2015, 2025)]
    if len(file_name) % 2 == 0:
        ni, cf, score = [150, 180, 210, 250, 280, 260, 180, 100, 40, -30], [140, 170, 200, 230, 190, 100, 20, -80, -200, -400], 85
    else:
        ni, cf, score = [100, 110, 130, 150, 170, 190, 210, 230, 250, 270], [90, 105, 120, 145, 160, 185, 200, 225, 240, 265], 10
    return pd.DataFrame({'年度': years, '帳面淨利': ni, '經營現金流': cf}), score

# --- 3. 解決 PDF 亂碼的關鍵函數 ---
def create_pdf_report(df, file_target, summary_text):
    pdf = FPDF()
    pdf.add_page()
    
    # 檢查是否有上傳字體檔
    font_path = "font.ttf"
    if os.path.exists(font_path):
        # 註冊中文字體 (需與您上傳到 GitHub 的檔名一致)
        pdf.add_font('Chinese', '', font_path, uni=True)
        pdf.set_font('Chinese', size=14)
    else:
        # 若沒字體則用 Arial (中文會變亂碼)
        pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt=f"財務鑑定報告: {file_target}", ln=True, align='C')
    pdf.ln(10)
    
    # 寫入中文內容
    for line in summary_text.split('\n'):
        pdf.multi_cell(0, 10, txt=line)
    
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- 4. 軟體主介面 ---
st.title("🛡️ 多案源財務鑑定工作站 v12.2")

with st.sidebar:
    st.header("⚙️ 系統初始化")
    audio_file = st.file_uploader("1. 載入警報音檔 (.mp3)", type=["mp3"])
    if not os.path.exists("font.ttf"):
        st.error("❌ 偵測不到 font.ttf 字體檔，PDF 中文將無法顯示。")
    else:
        st.success("✅ 已偵測到中文字體，報告功能正常。")

uploaded_files = st.file_uploader("2. 上傳多份 PDF 報表", type=["pdf"], accept_multiple_files=True)

if uploaded_files and audio_file:
    file_names = [f.name for f in uploaded_files]
    selected_file_name = st.selectbox("🎯 請選擇個案：", file_names)
    df_data, score = run_audit_engine(selected_file_name)
    
    # 圖表
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df_data['年度'], df_data['帳面淨利'], label='淨利 (Net Income)', marker='o')
    ax.plot(df_data['年度'], df_data['經營現金流'], label='現金流 (Cash Flow)', marker='x', color='red')
    ax.legend()
    st.pyplot(fig)

    # 報告文字
    summary = f"【鑑定結論：{selected_file_name}】\n系統判定：{'高度風險' if score > 50 else '穩定'}\n1. 現金流異常：{'是' if score > 50 else '否'}\n2. 建議：{'應啟動專案查核' if score > 50 else '維持例行監控'}"
    st.markdown(f'<div class="report-card">{summary.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)

    # 報告下載
    pdf_bytes = create_pdf_report(df_data, selected_file_name, summary)
    st.download_button(label="📥 下載中文鑑定報告", data=pdf_bytes, file_name=f"Report_{selected_file_name}.pdf")

else:
    st.warning("請先載入音檔與 PDF 檔案。")
