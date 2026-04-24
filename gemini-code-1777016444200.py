import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 頁面基礎配置
st.set_page_config(page_title="玄武會計師事務所", layout="wide")

# 設置圖表為深色風格
plt.style.use('dark_background')

# =====================================================
# 1. 強制視覺重構 (物理移除登入框樣式並注入深色背景)
# =====================================================
st.markdown(
    """
    <style>
    /* 強制全局背景為深色科技風漸變 */
    .stApp {
        background: linear-gradient(135deg, #05070a 0%, #0d1117 50%, #161b22 100%) !important;
        color: #ecf0f1 !important;
    }

    /* 隱藏所有登入介面可能留下的邊框 */
    [data-testid="stForm"], .stTextInput, .stSelectbox {
        border: none !important;
    }

    /* 金黃色標題與強調文字 */
    h1 {
        color: #f1c40f !important;
        font-weight: 800 !important;
        letter-spacing: 2px;
    }

    /* 科技感透明卡片 */
    .card {
        background-color: rgba(22, 27, 34, 0.8) !important;
        border: 1px solid rgba(241, 196, 15, 0.2) !important;
        border-radius: 12px;
        padding: 25px;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    
    /* 側邊欄深色處理 */
    section[data-testid="stSidebar"] {
        background-color: #010409 !important;
        border-right: 1px solid #30363d !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =====================================================
# 2. 側邊控制欄 (物理上已無登入判斷，直接渲染)
# =====================================================
with st.sidebar:
    st.markdown("<h2 style='color:#f1c40f;'>系統控制台</h2>", unsafe_allow_html=True)
    user_role = st.radio("模式切換", ["公司使用者", "會計師事務所"])
    st.divider()
    
    # 直接上傳區域
    files = st.file_uploader("批次上傳財報 PDF", type=["pdf"], accept_multiple_files=True)

# =====================================================
# 3. 主畫面顯示 (直接進入功能)
# =====================================================
st.title("玄武會計師事務所")
st.subheader("AI 四大財務 + 年度分析 + 查核整合系統 v64")

if files:
    st.markdown(f"### 正在執行：{user_role} 分析模式")
    
    # 模擬數據
    df = pd.DataFrame({
        "年度": ["2022", "2023", "2024"],
        "營收": [1000, 1200, 850],
        "純益": [100, 150, -50]
    })

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:#f1c40f;'>異常點分析</h4>", unsafe_allow_html=True)
        st.write("營收趨勢：2024年度下滑約 29%。")
        st.write("獲利狀況：本期淨損，獲利能力轉負。")
        
        if user_role == "會計師事務所":
            st.divider()
            st.markdown("<h4 style='color:#f1c40f;'>會計師查核建議 (ISA)</h4>", unsafe_allow_html=True)
            st.write("重點科目：應收帳款、存貨週轉、收入認列。")
            st.write("建議程序：執行函證程序並針對異常科目執行細部測試。")
        else:
            st.divider()
            st.markdown("<h4 style='color:#f1c40f;'>經營改善建議</h4>", unsafe_allow_html=True)
            st.write("策略方向：重新檢視變動成本，並規劃短期週轉資金。")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:#f1c40f;'>財務表現趨勢</h4>", unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(df["年度"], df["營收"], label="Revenue", color='#f1c40f', linewidth=2, marker='o')
        ax.plot(df["年度"], df["純益"], label="Profit", color='#e74c3c', linewidth=2, marker='s')
        ax.set_facecolor('none')
        ax.legend()
        st.pyplot(fig)
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    st.download_button("下載完整分析報告 PDF", data="DATA", file_name="analysis.pdf", use_container_width=True)

else:
    # 初始歡迎卡片
    st.markdown(
        """
        <div class='card' style='text-align: center; padding: 100px;'>
            <h2 style='color:#f1c40f;'>系統就緒</h2>
            <p>請於左側選單上傳財報 PDF，AI 將直接執行異常點分析與查核建議。</p>
        </div>
        """,
        unsafe_allow_html=True
    )
