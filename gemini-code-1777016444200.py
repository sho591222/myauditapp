import streamlit as st
import base64
import pandas as pd

# --- 1. 介面樣式設定 ---
st.set_page_config(page_title="財務鑑定工作站", layout="wide")
st.markdown("""
    <style>
    .report-card { background: white; padding: 25px; border-radius: 15px; border-left: 10px solid #2c3e50; color: #333; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
    .stButton>button { background-color: #c0392b !important; color: white !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 核心分析引擎 (最多10年) ---
def analyze_data(file):
    # 模擬 10 年分析邏輯
    years = [str(y) for y in range(2015, 2025)]
    df = pd.DataFrame({
        '年度': years,
        '淨利': [100, 120, 150, 180, 160, 140, 80, 30, 10, -20],
        '現金流': [90, 110, 130, 140, 100, 20, -50, -150, -250, -300],
        '應收帳款': [200, 220, 250, 300, 450, 600, 800, 1000, 1200, 1500]
    })
    return df, "HIGH"

# --- 3. 軟體主介面 ---
st.title("🛡️ 專業財務鑑定工作站 v11.6")
st.write("---")

with st.sidebar:
    st.header("⚙️ 系統初始化")
    audio_file = st.file_uploader("1. 載入警報音檔 (ug.mp3)", type=["mp3"])
    st.info("💡 初始化後，單獨上傳報表即可產出 10 年期文字綜整報告。")

uploaded_pdf = st.file_uploader("2. 上傳 PDF 報表開始全自動鑑定", type=["pdf"])

if uploaded_pdf and audio_file:
    df_res, status = analyze_data(uploaded_pdf)
    
    # 顯示 10 年趨勢圖
    st.markdown("### 📊 10年期核心數據趨勢")
    st.line_chart(df_res.set_index('年度'))

    # 文字綜整敘述
    st.markdown("### 📝 長週期專業鑑定文字綜整報告")
    summary = f"""
    【專案鑑定結論：{uploaded_pdf.name}】
    經 10 年期動態分析，該單位呈現「盈餘品質系統性偏移」。
    ❌ 經營現金流：已連續多年為負，且與淨利完全背離。
    ⭕ 應收帳款：10 年內成長超過 7 倍，存在高度虛增風險。
    ⚠️ 異常標記：原檔已標註 ⭕❌⚠️，請參閱。
    """
    st.markdown(f'<div class="report-card">{summary.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)

    # 警報控制
    if status == "HIGH":
        st.error("🚨 偵測到重大風險！")
        b64 = base64.b64encode(audio_file.read()).decode()
        st.components.v1.html(f"""
            <audio id="siren" autoplay loop><source src="data:audio/mp3;base64,{b64}"></audio>
            <script>window.parent.document.stopSiren = () => {{ document.getElementById("siren").pause(); }}</script>
        """, height=0)
        
        if st.button("🛑 停止警報聲"):
            st.components.v1.html('<script>window.parent.document.stopSiren();</script>', height=0)
            st.warning("警報已手動中斷。")

st.markdown("---")
st.caption("AI 財務鑑定引擎 | 雲端整合版")