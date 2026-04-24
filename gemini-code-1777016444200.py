import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# 1. 設置頁面基礎配置，layout 設為 wide 以獲得更好的視覺效果
st.set_page_config(page_title="玄武會計師事務所", layout="wide")

# 在程式碼最開始設置全局圖表風格為深色
plt.style.use('dark_background')

# 2. 自定義 CSS 模擬深色科技數據背景
# 我們使用 CSS 漸變和一個抽象的數據點圖案來模擬類似圖片的深色數據流背景
st.markdown(
    """
    <style>
    /* 全局深色主題 */
    .stApp {
        background-color: #0d1117;
        background-image:
            linear-gradient(rgba(13, 17, 23, 0.9), rgba(13, 17, 23, 0.9)),
            radial-gradient(at 100% 0%, #2e2e2e 0px, transparent 50%),
            radial-gradient(at 0% 100%, #1a1a1a 0px, transparent 50%),
            radial-gradient(at 10% 10%, rgba(241, 196, 15, 0.1) 0px, transparent 20%),
            radial-gradient(at 90% 90%, rgba(241, 196, 15, 0.1) 0px, transparent 20%);
        color: #ecf0f1;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* 文字顏色調整 */
    h1, h2, h3, h4, h5, h6, .stSubheader, .stCaption {
        color: #ecf0f1 !important;
    }

    /* 強調色（黃色） */
    .highlight {
        color: #f1c40f;
    }

    /* 入口按鈕美化 - 科技感發光邊框 */
    .stButton>button {
        background-color: transparent !important;
        color: #f1c40f !important;
        border: 2px solid #f1c40f !important;
        border-radius: 5px !important;
        padding: 15px 30px !important;
        font-size: 20px !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        cursor: pointer !important;
        position: relative;
        overflow: hidden;
        width: 100%;
        margin-top: 30px;
    }

    .stButton>button:hover {
        background-color: rgba(241, 196, 15, 0.1) !important;
        border-color: #f39c12 !important;
        box-shadow: 0 0 20px rgba(241, 196, 15, 0.7) !important;
    }

    /* 內部介面卡片佈局 */
    .card {
        background-color: rgba(26, 32, 44, 0.8) !important;
        border: 1px solid #2d3748 !important;
        border-radius: 10px !important;
        padding: 25px !important;
        margin-bottom: 25px !important;
        box-shadow: 0 8px 12px rgba(0, 0, 0, 0.4) !important;
    }

    /* 側邊欄樣式 */
    .css-1d391kg {
        background-color: #161b22 !important;
        border-right: 1px solid #21262d !important;
    }

    /* 通知樣式 */
    .stAlert {
        border-radius: 5px !important;
    }
    .stWarning {
        background-color: rgba(243, 156, 18, 0.1) !important;
        border: 1px solid #f39c12 !important;
        color: #ecf0f1 !important;
    }
    .stError {
        background-color: rgba(231, 76, 60, 0.1) !important;
        border: 1px solid #e74c3c !important;
        color: #ecf0f1 !important;
    }
    .stInfo {
        background-color: rgba(52, 152, 219, 0.1) !important;
        border: 1px solid #3498db !important;
        color: #ecf0f1 !important;
    }
    .stSuccess {
        background-color: rgba(46, 204, 113, 0.1) !important;
        border: 1px solid #2ecc71 !important;
        color: #ecf0f1 !important;
    }

    /* 圖表容器樣式 */
    .plot-container {
        background-color: transparent !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 3. 核心邏輯：狀態控制
if "sys_active" not in st.session_state:
    st.session_state.sys_active = False

# 4. 入口頁面（按鈕點擊前顯示）
if not st.session_state.sys_active:
    # 這裡確保畫面上除了標題和按鈕，沒有任何 Email 或密碼輸入框
    st.markdown("<br><br><br><br><br><br><br><br>", unsafe_allow_html=True)
    st.title("玄武會計師事務所")
    st.header("AI 四大財務 + 年度分析 + 查核整合系統 v64")
    st.markdown("<p style='text-align: center; color: #7f8c8d;'>點擊下方按鈕啟動系統進行分析</p>", unsafe_allow_html=True)
    
    # 居中按鈕
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("進入系統"):
            st.session_state.sys_active = True
            st.rerun()

    st.stop()  # 強制停止後續代碼載入

# =====================================================
# 5. 系統內部頁面（按鈕點擊後才會執行到這裡）
# =====================================================

# 側邊控制欄
with st.sidebar:
    st.title("系統控制")
    user_role = st.radio("使用者類型", ["公司使用者", "會計師事務所"])
    st.divider()
    
    # 多選 PDF 上傳
    uploaded_files = st.file_uploader("上傳財報 PDF (可多選)", type=["pdf"], accept_multiple_files=True)
    
    st.divider()
    if st.button("退出系統"):
        st.session_state.sys_active = False
        st.rerun()

# 6. 分析結果呈現（一頁式顯示）
if uploaded_files:
    st.title(f"財務分析結果 - <span class='highlight'>{user_role}</span>", unsafe_allow_html=True)
    
    # 模擬數據（實際運作時應解析 PDF）
    data = pd.DataFrame({
        "年份": ["2022", "2023", "2024"],
        "營收": [1000, 1200, 850],
        "純益": [100, 150, -50],
        "存貨週轉": [4.2, 4.0, 3.1]
    })

    # 分欄顯示結果，並放入 CSS 卡片中
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("分析結果與異常點")
        st.warning("1. 2024 年度營收出現顯著下滑 (約 29%)。")
        st.warning("2. 本期淨損，獲利能力轉負。")
        if data["存貨週轉"].iloc[-1] < data["存貨週轉"].iloc[-2]:
            st.warning("3. 存貨週轉率下降，存在呆滯風險。")
        
        if user_role == "會計師事務所":
            st.divider()
            st.subheader("查核重點與建議 (ISA)")
            st.markdown("<p style='color: #bdc3c7;'>重點科目：應收帳款、存貨、收入認列</p>", unsafe_allow_html=True)
            st.info("建議程序：執行外部函證程序與收入切截測試。")
        else:
            st.divider()
            st.subheader("經營改善建議")
            st.success("建議重新檢視成本結構，優化現金流管理。")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("營運趨勢圖表")
        
        # 建立圖表，使用深色風格和強調色（黃色）
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(data["年份"], data["營收"], label="Revenue", color='#f1c40f', linewidth=2)
        ax.plot(data["年份"], data["純益"], label="Profit", color='#f39c12', linewidth=2, linestyle='--')
        # 存貨週轉線
        ax.plot(data["年份"], data["存貨週轉"] * 200, label="Inventory Turnover (x200)", color='#bdc3c7', linewidth=1, linestyle=':')
        
        ax.set_title("Financial Performance Trend", color='#ecf0f1')
        ax.set_xlabel("Year", color='#ecf0f1')
        ax.set_ylabel("Value (Million USD)", color='#ecf0f1')
        
        # 自定義刻度顏色
        ax.tick_params(colors='#bdc3c7')
        
        # 自定義圖例
        ax.legend(facecolor='#161b22', edgecolor='#21262d', loc='upper right')
        
        # 移除頂部和右側邊框
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#2d3748')
        ax.spines['bottom'].set_color('#2d3748')
        
        st.pyplot(fig)
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    
    # 生成報告下載按鈕美化
    col_dl1, col_dl2 = st.columns([1, 1])
    with col_dl1:
        st.info("分析已完成，可下載完整 PDF 報告。")
    with col_dl2:
        st.download_button(
            label="📥 下載完整 PDF 報告",
            data="PDF_CONTENT_PLACEHOLDER",  # 這裡應為報告二進位數據
            file_name="financial_analysis.pdf",
            mime="application/pdf",
            use_container_width=True
        )
else:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.info("系統已就緒。請於左側控制面板上傳財報 PDF 檔案開始 AI 查核分析。")
    st.markdown("</div>", unsafe_allow_html=True)
