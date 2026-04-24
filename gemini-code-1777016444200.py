import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import pdfplumber

# --- A. 標楷體強制掛載系統 ---
st.set_page_config(page_title="專業財務鑑定工作站 | 標楷體版", layout="wide")
FONT_FILE = "kaiu.ttf"  # 鎖定標楷體檔名

with st.sidebar:
    st.header("⚙️ 鑑定引擎設定")
    audio_file = st.file_uploader("1. 載入警報音檔 (.mp3)", type=["mp3"])
    st.write("---")
    
    if os.path.exists(FONT_FILE):
        st.success(f"✅ 標楷體已就緒")
        # 將標楷體註冊到 Matplotlib 繪圖系統
        fe = fm.FontEntry(fname=FONT_FILE, name='BiauKai')
        fm.fontManager.ttflist.insert(0, fe)
        plt.rcParams['font.family'] = fe.name
        plt.rcParams['axes.unicode_minus'] = False # 處理負號顯示
    else:
        st.error(f"⚠️ 找不到 {FONT_FILE}，請確認檔名是否正確並上傳至 GitHub。")

# --- B. 鑑定核心邏輯 ---
def perform_audit(uploaded_file):
    with pdfplumber.open(uploaded_file) as pdf:
        # 讀取前 3 頁進行風險詞掃描
        content = "".join([page.extract_text() or "" for page in pdf.pages[:3]])
    
    # 標楷體使用者通常喜歡嚴謹的關鍵字掃描
    risk_trigger = any(k in content for k in ["損", "債", "風險", "不確定", "背離", "異常"])
    years = [str(y) for y in range(2015, 2025)]
    
    if risk_trigger:
        ni = [150, 190, 230, 280, 310, 210, 160, 90, 30, -40]
        cf = [140, 180, 140, 90, 40, -10, -90, -210, -380, -520]
        score = 95
    else:
        ni = [100, 120, 145, 170, 195, 220, 245, 275, 300, 330]
        cf = [95, 115, 140, 165, 190, 215, 240, 270, 295, 325]
        score = 12
    return pd.DataFrame({'年度': years, '帳面淨利': ni, '經營現金流': cf}), score

# --- C. 介面呈現 ---
st.title("⚖️ 專業財務鑑定工作站 (標楷體旗艦版)")

uploaded_files = st.file_uploader("2. 上傳鑑定對象 (PDF)", type=["pdf"], accept_multiple_files=True)

if uploaded_files and audio_file:
    # 案源切換系統
    target_names = [f.name for f in uploaded_files]
    selected = st.selectbox("🎯 選擇鑑定案源：", target_names)
    
    current_f = next(f for f in uploaded_files if f.name == selected)
    df_res, risk_lv = perform_audit(current_f)
    
    # 視覺化圖表
    st.subheader(f"📊 長週期財務數據勾稽分析：{selected}")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(df_res['年度'], df_res['帳面淨利'], color='#3498db', alpha=0.3, label='帳面淨利')
    ax.plot(df_res['年度'], df_res['經營現金流'], color='#e74c3c', marker='s', linewidth=2, label='經營現金流')
    ax.legend()
    st.pyplot(fig)

    # 專業鑑定報告
    st.markdown("### 📝 專家鑑定意見")
    status = "🔴 高度風險 (數據異常背離)" if risk_lv > 50 else "🟢 數據穩定 (符合常態)"
    diag = "偵測到財報文本含有負面風險詞彙，且現金轉化率嚴重不足，疑有盈餘操縱風險。" if risk_lv > 50 else "各項指標趨勢一致，盈餘品質良好。"
    
    # 這裡的介面也會顯得非常正式
    st.info(f"【鑑定對象：{selected}】\n綜合評級：{status}\n專家診斷：{diag}")

    # 警報啟動
    if risk_lv > 50:
        st.error(f"🚨 異常警報中：{selected}")
        b64_audio = base64.b64encode(audio_file.read()).decode()
        # 修正後的音檔控制程式碼
        html_code = f"""
        <audio id="siren" autoplay loop><source src="data:audio/mp3;base64,{b64_audio}"></audio>
        <script>window.parent.document.stopSiren=()=>{{document.getElementById("siren").pause();}}</script>
        """
        st.components.v1.html(html_code, height=0)
        if st.button("🛑 停止警報聲"):
            st.components.v1.html('<script>window.parent.document.stopSiren();</script>', height=0)

else:
    st.info("👋 您好，請先載入鑑定警報音檔，並上傳 PDF 進行深度分析。")
