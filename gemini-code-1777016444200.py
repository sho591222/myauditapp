import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 頁面基礎配置
st.set_page_config(page_title="玄武會計師事務所", layout="wide")

# 設定圖表為深色風格
plt.style.use('dark_background')

# =====================================================
# 1. 視覺風格設定 (深色科技背景)
# =====================================================
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0d1117;
        background-image:
            linear-gradient(rgba(13, 17, 23, 0.9), rgba(13, 17, 23, 0.9)),
            radial-gradient(at 100% 0%, #2e2e2e 0px, transparent 50%),
            radial-gradient(at 0% 100%, #1a1a1a 0px, transparent 50%);
        color: #ecf0f1;
    }

    /* 標題與文字顏色 */
    h1, h2, h3, .stSubheader {
        color: #f1c40f !important;
    }

    /* 卡片區塊 */
    .card {
        background-color: rgba(26, 32, 44, 0.8);
        border: 1px solid #2d3748;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    /* 側邊欄樣式修正 */
    section[data-testid="stSidebar"] {
        background-color: #161b22 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =====================================================
# 2. 側邊控制欄 (直接顯示)
# =====================================================
with st.sidebar:
    st.title("系統控制台")
    user_role = st.radio("使用者權限", ["公司使用者", "會計師事務所"])
    st.divider()
    
    # 檔案上傳
    files = st.file_uploader("批次上傳財報 PDF", type=["pdf"], accept_multiple_files=True)

# =====================================================
# 3. 主畫面顯示
# =====================================================
st.title("玄武會計師事務所")
st.subheader("AI 四大財務 + 年度分析 + 查核整合系統 v64")

if files:
    st.markdown(f"### 當前分析對象：{user_role}", unsafe_allow_html=True)
    
    # 模擬數據
    df = pd.DataFrame({
        "年度": ["2022", "2023", "2024"],
        "營收": [1000, 1200, 850],
        "純益": [100, 150, -50]
    })

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.write("分析結果與異常點")
        st.write("- 2024 年度營收下滑約 29%")
        st.write("- 本期由盈轉虧，淨利表現異常")
        
        if user_role == "會計師事務所":
            st.divider()
            st.write("查核重點：應收帳款認列、存貨跌價損失")
            st.write("建議程序：執行 ISA 505 函證測試")
        else:
            st.divider()
            st.write("經營改善建議：檢視成本結構，優化現金流管理")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        fig, ax = plt.subplots()
        ax.plot(df["年度"], df["營收"], label="Revenue", color='#f1c40f')
        ax.plot(df["年度"], df["純益"], label="Profit", color='#e74c3c')
        ax.legend()
        st.pyplot(fig)
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    st.download_button("下載完整分析報告 PDF", data="DATA", file_name="analysis.pdf")

else:
    st.markdown("<div class='card'>系統已就緒。請在左側上傳 PDF 檔案以開始 AI 查核與財務分析。</div>", unsafe_allow_html=True)
