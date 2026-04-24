import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 頁面基礎配置 - 務必放在第一行
st.set_page_config(page_title="玄武會計師事務所", layout="wide", initial_sidebar_state="expanded")

# 設定圖表深色風格
plt.style.use('dark_background')

# =====================================================
# 1. 強制重構視覺樣式 (仿 EY 深色科技風 / 無表情符號)
# =====================================================
st.markdown(
    """
    <style>
    /* 強制修改背景顏色與漸變 */
    .stApp {
        background: linear-gradient(135deg, #05070a 0%, #0d1117 50%, #161b22 100%) !important;
        color: #ecf0f1 !important;
    }

    /* 隱藏 Streamlit 原生頂部元件與裝飾 */
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* 側邊欄深色處理 */
    section[data-testid="stSidebar"] {
        background-color: #010409 !important;
        border-right: 1px solid #30363d !important;
        width: 300px !important;
    }

    /* 標題：科技金 */
    h1 {
        color: #f1c40f !important;
        font-weight: 800 !important;
        font-family: 'Segoe UI', sans-serif !important;
        padding-top: 0px !important;
    }

    /* 科技感卡片 */
    .report-card {
        background-color: rgba(22, 27, 34, 0.8) !important;
        border: 1px solid rgba(241, 196, 15, 0.3) !important;
        border-radius: 10px;
        padding: 25px;
        margin-top: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
    }
    
    /* 移除所有輸入框邊框 */
    .stTextInput, .stSelectbox, .stFileUploader {
        border: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =====================================================
# 2. 直接進入主程式 (完全移除登入/按鈕邏輯)
# =====================================================

# 側邊欄：功能選單
with st.sidebar:
    st.markdown("<h2 style='color:#f1c40f;'>控制面板</h2>", unsafe_allow_html=True)
    user_role = st.radio("模式選擇", ["公司使用者", "會計師事務所"])
    st.divider()
    
    # 檔案上傳 (啟動即顯示)
    files = st.file_uploader("批次上傳財報 PDF", type=["pdf"], accept_multiple_files=True)
    st.markdown("<p style='color:#57606a; font-size:12px; margin-top:50px;'>系統版本：v64.0.1</p>", unsafe_allow_html=True)

# 主畫面標題
st.title("玄武會計師事務所")
st.markdown("<p style='color:#bdc3c7; font-size:18px;'>AI 四大財務分析 與 異常點查核整合系統</p>", unsafe_allow_html=True)

# =====================================================
# 3. 內容顯示區
# =====================================================
if files:
    st.markdown(f"#### 執行狀態：{user_role} 數據分析中")
    
    # 模擬分析數據
    df = pd.DataFrame({
        "年度": ["2022", "2023", "2024"],
        "營收": [1000, 1200, 850],
        "純益": [100, 150, -50]
    })

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='report-card'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:#f1c40f;'>異常點分析結果</h4>", unsafe_allow_html=True)
        st.write("營收表現：2024年度大幅下滑，跌幅達 29.1%。")
        st.write("損益分析：本期由盈轉虧，毛利結構需進一步查核。")
        
        if user_role == "會計師事務所":
            st.divider()
            st.markdown("<h4 style='color:#f1c40f;'>查核建議 (ISA)</h4>", unsafe_allow_html=True)
            st.write("1. 針對收入認列執行截止測試。")
            st.write("2. 應收帳款函證應包含所有異常往來客戶。")
        else:
            st.divider()
            st.markdown("<h4 style='color:#f1c40f;'>經營策略建議</h4>", unsafe_allow_html=True)
            st.write("1. 評估變動成本管控，優化營運現金流。")
            st.write("2. 針對虧損部門進行損益平衡分析。")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='report-card'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:#f1c40f;'>財務趨勢視覺化</h4>", unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(df["年度"], df["營收"], label="Revenue", color='#f1c40f', linewidth=2.5, marker='o')
        ax.plot(df["年度"], df["純益"], label="Profit", color='#e74c3c', linewidth=2.5, marker='s')
        ax.set_facecolor('none')
        ax.legend(facecolor='#0d1117', edgecolor='#f1c40f')
        st.pyplot(fig)
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    st.download_button("下載完整 AI 查核報告 (PDF)", data="REPORT_BINARY", file_name="analysis_report.pdf", use_container_width=True)

else:
    # 預設首頁卡片
    st.markdown(
        """
        <div class='report-card' style='text-align: center; padding: 80px 20px;'>
            <h2 style='color:#f1c40f;'>系統就緒</h2>
            <p style='color:#8b949e;'>請從左側控制面板上傳 PDF 財報，AI 將立即執行財務查核分析。</p>
            <p style='color:#57606a; font-size:13px;'>本系統支援四大財務報表解析、異常點自動標記與 ISA 查核程序建議。</p>
        </div>
        """,
        unsafe_allow_html=True
    )
