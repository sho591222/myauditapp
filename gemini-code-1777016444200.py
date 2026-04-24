import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
from fpdf import FPDF
import io
import os

# --- 1. 軟體風格與繁體中文介面 ---
st.set_page_config(page_title="多案源財務鑑定工作站", layout="wide")
st.markdown("""
    <style>
    .report-card { background: #ffffff; padding: 25px; border-radius: 15px; border-left: 10px solid #273c75; box-shadow: 0 4px 12px rgba(0,0,0,0.1); color: #333; line-height: 1.8; }
    .stButton>button { background-color: #c0392b !important; color: white !important; font-weight: bold; width: 100%; height: 50px; border-radius: 10px; }
    .stSelectbox label { color: #273c75; font-weight: bold; font-size: 1.2em; }
    h1 { color: #273c75; text-align: center; border-bottom: 2px solid #273c75; padding-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 核心鑑定分析引擎 (模擬 10 年縱向數據) ---
def run_audit_engine(file_name):
    # 建立 2015-2024 年份
    years = [str(y) for y in range(2015, 2025)]
    
    # 模擬邏輯：根據檔名長度區分風險，讓您可以看到不同結果
    if len(file_name) % 2 == 0:
        ni = [150, 180, 210, 250, 280, 260, 180, 100, 40, -30]
        cf = [140, 170, 200, 230, 190, 100, 20, -80, -200, -400]
        score = 85
    else:
        ni = [100, 110, 130, 150, 170, 190, 210, 230, 250, 270]
        cf = [90, 105, 120, 145, 160, 185, 200, 225, 240, 265]
        score = 15
    
    df = pd.DataFrame({'年度': years, '帳面淨利': ni, '經營現金流': cf})
    return df, score

# --- 3. 解決 PDF 亂碼的生成函數 ---
def create_pdf_report(df, file_target, summary_text):
    # 使用 fpdf2 (或 FPDF) 支援 Unicode
    pdf = FPDF()
    pdf.add_page()
    
    font_path = "font.ttf"
    if os.path.exists(font_path):
        # 註冊中文字體，uni=True 是解決亂碼的關鍵
        pdf.add_font('ChineseFont', '', font_path, uni=True)
        pdf.set_font('ChineseFont', size=16)
    else:
        pdf.set_font("Arial", 'B', 16)

    # 寫入標題
    pdf.cell(200, 10, txt=f"財務鑑定專案報告: {file_target}", ln=True, align='C')
    pdf.ln(10)
    
    # 寫入內容 (將摘要文字逐行寫入)
    if os.path.exists(font_path):
        pdf.set_font('ChineseFont', size=12)
    else:
        pdf.set_font("Arial", size=10)
        
    for line in summary_text.split('\n'):
        # 移除特殊表情符號以防 PDF 編碼錯誤
        clean_line = line.replace('⭕', '[O]').replace('❌', '[X]').replace('⚠️', '[!]').replace('🔴', '').replace('🟢', '')
        pdf.multi_cell(0, 10, txt=clean_line)
    
    # 直接輸出 byte string，不手動進行 latin-1 編碼
    return pdf.output(dest='S')

# --- 4. 軟體主介面 ---
st.title("🛡️ 專業財務鑑定工作站 v12.5 (全能版)")

with st.sidebar:
    st.header("⚙️ 系統初始化")
    audio_file = st.file_uploader("1. 載入警報音檔 (.mp3)", type=["mp3"])
    st.write("---")
    if os.path.exists("font.ttf"):
        st.success("✅ 中文字體已就緒")
    else:
        st.error("⚠️ 缺少 font.ttf，PDF 將無法顯示中文")
    st.info("支援多檔案上傳，系統將自動進行 10 年期縱向數據分析。")

# 允許多選檔案
uploaded_files = st.file_uploader("2. 請選取多份 PDF 財報進行鑑定", type=["pdf"], accept_multiple_files=True)

if uploaded_files and audio_file:
    file_names = [f.name for f in uploaded_files]
    st.success(f"系統已載入 {len(file_names)} 個檔案。")
    
    # 下拉選單切換案源
    selected_file = st.selectbox("🎯 請選擇欲檢視的鑑定個案：", file_names)
    
    # 執行分析
    df_data, score = run_audit_engine(selected_file)
    
    # A. 視覺化趨勢圖表
    st.markdown(f"### 📊 10 年期財務走勢鑑定：{selected_file}")
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(df_data['年度'], df_data['帳面淨利'], label='帳面淨利 (Net Income)', marker='o', color='#2980b9', linewidth=2)
    ax.plot(df_data['年度'], df_data['經營現金流'], label='經營現金流 (Cash Flow)', marker='s', color='#c0392b', linewidth=2)
    ax.set_title(f"Trend Analysis - {selected_file}", fontsize=14)
    ax.set_xlabel("年度")
    ax.set_ylabel("金額 (萬元)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)

    # B. 文字鑑定報告區
    st.markdown("### 📝 鑑定專家綜整意見")
    risk_status = "🔴 高度風險 (異常背離)" if score > 50 else "🟢 穩定正常 (含金量高)"
    summary = f"""
    【鑑定對象：{selected_file}】
    
    一、 綜合判定：
    本案源經 2015-2024 數據勾稽，目前處於「{risk_status}」狀態。
    
    二、 重點稽核意見：
    1. 盈餘品質：{'經營現金流已連續數年低於淨利，存在顯著虛增獲利風險。' if score > 50 else '現金流轉化能力穩定，獲利真實性高。'}
    2. 債權風險：{'應收帳款成長率遠超營收成長，建議進行專案抽查。' if score > 50 else '應收帳款管理良善，無異常積壓。'}
    3. 建議處置：{'建議立即啟動專案查核，並暫緩相關授信或投資。' if score > 50 else '維持一般等級監控即可。'}
    """
    st.markdown(f'<div class="report-card">{summary.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)

    # C. 警報聲控制
    if score > 50:
        st.error(f"🚨 偵測到重大異常：{selected_file}")
        b64 = base64.b64encode(audio_file.read()).decode()
        st.components.v1.html(f"""
            <audio id="siren" autoplay loop><source src="data:audio/mp3;base64,{b64}"></audio>
            <script>window.parent.document.stopSiren = () => {{ document.getElementById("siren").pause(); }}</script>
        """, height=0)
        
        if st.button("🛑 停止警報聲"):
            st.components.v1.html('<script>window.parent.document.stopSiren();</script>', height=0)
            st.warning("警報已暫時停止。")

    # D. PDF 報告下載 (修正編碼報錯)
    st.write("---")
    try:
        pdf_data = create_pdf_report(df_data, selected_file, summary)
        st.download_button(
            label=f"📥 下載「{selected_file}」鑑定報告 (PDF)",
            data=pdf_data,
            file_name=f"鑑定報告_{selected_file}.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"PDF 生成時發生錯誤：{str(e)}")

else:
    st.warning("👋 歡迎使用！請先於左側載入音檔，再上傳 PDF 開始鑑定。")

st.markdown("---")
st.caption("AI 財務鑑定系統 | 支援多國語言介面與 10 年期縱向鑑定功能")
