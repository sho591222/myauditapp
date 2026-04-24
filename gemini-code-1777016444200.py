import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 頁面基礎配置
st.set_page_config(page_title="玄武會計師事務所", layout="wide")

# 設定圖表為深色風格
plt.style.use('dark_background')

# =====================================================
# 1. 視覺風格設定 (強制覆蓋背景與移除所有登入元件)
# =====================================================
st.markdown(
    """
    <style>
    /* 強制全局背景為深色科技風 */
    .stApp {
        background-color: #0d1117 !important;
        background-image: 
            radial-gradient(at 0% 0%, rgba(241, 196, 15, 0.05) 0px, transparent 50%),
            radial-gradient(at 100% 100%, rgba(241, 196, 15, 0.05) 0px, transparent 50%) !important;
        color: #ecf0f1 !important;
    }

    /* 隱藏所有可能殘留的登入相關元件邊框 */
    [data-testid="stForm"] {
        border: none !important;
    }

    /* 標題與金黃色科技感文字 */
    h1, h2, h3, .stSubheader {
        color: #f1c40f !important;
        font-family: 'Segoe UI', sans-serif;
    }

    /* 科技感卡片區塊 */
    .card {
        background-color: rgba(22, 27, 34, 0.8) !important;
        border: 1px solid #30363d !important;
        border-radius: 8px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    /* 側邊欄樣式修正 */
    section[data-testid="stSidebar"] {
        background-color: #010409 !important;
        border-right: 1px solid #30363d !important;
    }

    /* 移除所有表情符號按鈕樣式 */
    button {
        border-radius: 4px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =====================================================
# 2. 直接顯示系統主介面 (移除進入按鈕，直接進入)
# =====================================================

# 側邊控制欄
with st.sidebar:
    st.title("系統控制台")
    user_role = st.radio("使用者權限", ["公司使用者", "會計師事務所"])
    st.divider()
    
    # 直接上傳區域
    files = st.file_uploader("批次上傳財報 PDF", type=["pdf"], accept_multiple_files=True)

# 主標題
st.title("玄武會計師事務所")
st.subheader("AI 四大財務 + 年度分析 + 查核整合系統 v64")

# =====================================================
# 3. 分析結果呈現
# =====================================================
if files:
    st.markdown(f"### 當前分析對象：{user_role}")
    
    # 模擬數據
    df = pd.DataFrame({
        "年度": ["2022", "2023", "2024"],
        "營收": [1000, 1200, 850],
        "純益": [100, 150, -50]
    })

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("#### 分析結果與異常點")
        st.write("營收趨勢：2024 年度營收下滑約 29%")
        st.write("獲利狀況：本期由盈轉虧，淨利表現異常")
        
        if user_role == "會計師事務所":
            st.divider()
            st.markdown("#### 查核重點 (會計師專用)")
            st.write("重點科目：應收帳款認列、存貨跌價損失")
            st.write("建議程序：執行 ISA 505 函證測試")
        else:
            st.divider()
            st.markdown("#### 經營改善建議")
            st.write("財務策略：檢視成本結構，優化現金流管理")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("#### 財務趨勢圖表")
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(df["年度"], df["營收"], label="Revenue", color='#f1c40f', linewidth=2)
        ax.plot(df["年度"], df["純益"], label="Profit", color='#e74c3c', linewidth=2)
        ax.set_facecolor('#161b22')
        ax.legend()
        st.pyplot(fig)
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    st.download_button("下載完整分析報告 PDF", data="DATA", file_name="analysis.pdf", use_container_width=True)

else:
    # 初始狀態提示
    st.markdown("""
        <div class='card'>
            系統已就緒。請在左側選單上傳財報 PDF 檔案，AI 將自動執行財務風險查核與異常點分析。
        </div>
    """, unsafe_allow_html=True)
