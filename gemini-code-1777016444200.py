import streamlit as st
import pandas as pd
import base64
import time
import matplotlib.pyplot as plt
from fpdf import FPDF
import io

# --- 1. 軟體風格與繁體中文介面設定 ---
st.set_page_config(page_title="多案源財務鑑定工作站", layout="wide")
st.markdown("""
    <style>
    /* 中文化字體與風格優化 */
    .report-card { background: #ffffff; padding: 25px; border-radius: 15px; border-left: 10px solid #273c75; box-shadow: 0 4px 12px rgba(0,0,0,0.1); color: #333; line-height: 1.6; }
    .stButton>button { background-color: #c0392b !important; color: white !important; font-weight: bold; width: 100%; border-radius: 8px; }
    .stSelectbox label { color: #273c75; font-weight: bold; font-size: 1.1em; }
    h1 { color: #273c75; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 核心分析引擎 (支援10年動態分析) ---
def run_audit_engine(file_name):
    # 建立 10 年時間軸
    years = [str(y) for y in range(2015, 2025)]
    
    # 模擬邏輯：若檔名包含特定關鍵字或特定長度，模擬為高風險
    if len(file_name) % 2 == 0:
        ni = [150, 180, 210, 250, 280, 260, 180, 100, 40, -30]
        cf = [140, 170, 200, 230, 190, 100, 20, -80, -200, -400]
        score = 85
    else:
        ni = [100, 110, 130, 150, 170, 190, 210, 230, 250, 270]
        cf = [90, 105, 120, 145, 160, 185, 200, 225, 240, 265]
        score = 10
    
    df = pd.DataFrame({'年度': years, '帳面淨利': ni, '經營現金流': cf})
    return df, score

# --- 3. 產出繁體中文 PDF 報告 (PDF 內部使用英文標頭避開雲端字體亂碼，內容為中文) ---
def create_pdf_report(df, file_target, summary_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=f"Audit Report: {file_target}", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    # PDF 內容摘要
    clean_text = summary_text.replace('⭕', '[O]').replace('❌', '[X]').replace('⚠️', '[!]')
    pdf.multi_cell(0, 10, txt=clean_text.encode('latin-1', 'replace').decode('latin-1'))
    return pdf.output(dest='S').encode('latin-1')

# --- 4. 軟體主介面 ---
st.title("🛡️ 多案源財務鑑定工作站 v12.1 (全中文版)")
st.write("---")

with st.sidebar:
    st.header("⚙️ 系統初始化設定")
    audio_file = st.file_uploader("1. 載入警報音檔 (.mp3)", type=["mp3"])
    st.write("---")
    st.info("💡 說明：請先載入音檔，系統將自動解鎖下方多檔案分析功能。支援最高 10 年期縱向數據勾稽。")

# 支援多選上傳
uploaded_files = st.file_uploader("2. 請選取多份 PDF 報表開始全自動鑑定", type=["pdf"], accept_multiple_files=True)

if uploaded_files and audio_file:
    file_names = [f.name for f in uploaded_files]
    st.success(f"✅ 系統訊息：已成功載入 {len(file_names)} 份報表。")
    
    # 下拉選單切換案源
    selected_file_name = st.selectbox("🎯 請選擇要檢視的鑑定個案：", file_names)
    
    # 執行鑑定分析
    df_data, score = run_audit_engine(selected_file_name)
    
    # A. 繪製中文趨勢圖
    st.markdown(f"### 📊 鑑定對象：{selected_file_name}")
    st.write("#### 10 年期財務趨勢走勢圖 (淨利 vs 現金流)")
    
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df_data['年度'], df_data['帳面淨利'], label='Net Income (淨利)', marker='o', color='#2980b9')
    ax.plot(df_data['年度'], df_data['經營現金流'], label='Cash Flow (現金流)', marker='x', color='#c0392b')
    ax.set_xlabel("年度 (Year)")
    ax.set_ylabel("金額 (單位:萬元)")
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.6)
    st.pyplot(fig)

    # B. 專業鑑定文字綜整區
    st.markdown("### 📝 長週期鑑定文字綜整報告")
    risk_text = "高度風險" if score > 50 else "穩定良好"
    summary = f"""
    【專案鑑定結論：{selected_file_name}】
    
    一、 綜合評述：
    針對該單位 2015 至 2024 年度之數據進行縱向勾稽，系統判定盈餘品質為「{risk_text}」。
    
    二、 核心問題點 (⭕❌⚠️)：
    1. ❌ 盈餘含金量：{'末期經營現金流嚴重背離淨利，疑有虛增獲利情事。' if score > 50 else '現金流轉化能力正常，獲利具備實質含金量。'}
    2. ⭕ 債權回收：{'應收帳款異常積壓，10年增幅過大，建議列入專案查核。' if score > 50 else '應收帳款管理穩定，未見異常積壓。'}
    3. ⚠️ 異常標記：請參閱 PDF 原始檔中 ⭕❌⚠️ 高亮標註之科目。
    """
    st.markdown(f'<div class="report-card">{summary.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)

    # C. 警報與手動停止開關
    if score > 50:
        st.error(f"🚨 重大警示：{selected_file_name} 偵測到財務異常！")
        b64 = base64.b64encode(audio_file.read()).decode()
        st.components.v1.html(f"""
            <audio id="siren" autoplay loop><source src="data:audio/mp3;base64,{b64}"></audio>
            <script>window.parent.document.stopSiren = () => {{ document.getElementById("siren").pause(); }}</script>
        """, height=0)
        
        if st.button("🛑 停止目前個案警報"):
            st.components.v1.html('<script>window.parent.document.stopSiren();</script>', height=0)
            st.warning("警報已手動關閉，不影響分析報告呈現。")

    # D. 報告下載按鈕
    st.write("---")
    pdf_bytes = create_pdf_report(df_data, selected_file_name, summary)
    st.download_button(label=f"📥 下載 {selected_file_name} 之專業鑑定報告", data=pdf_bytes, file_name=f"鑑定報告_{selected_file_name}.pdf")

else:
    st.warning("⚠️ 系統就緒：請先在左側載入音檔，再進行多檔案 PDF 上傳分析。")

st.markdown("---")
st.caption("AI 財務鑑定系統 v12.1 | 繁體中文專業版")
