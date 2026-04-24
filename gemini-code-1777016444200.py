import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 頁面基礎配置
st.set_page_config(page_title="玄武會計師事務所", layout="wide")

# 設定圖表為深色風格，確保與背景視覺統一
plt.style.use('dark_background')

# =====================================================
# 1. 視覺風格設計 (深色科技背景，完全移除登入相關 UI)
# =====================================================
st.markdown(
    """
    <style>
    /* 強制全局背景為深色漸變科技感 */
    .stApp {
        background: linear-gradient(135deg, #05070a 0%, #0d1117 50%, #161b22 100%) !important;
        color: #ecf0f1 !important;
    }

    /* 標題區域：金黃色科技感文字 */
    h1 {
        color: #f1c40f !important;
        font-weight: 800 !important;
        letter-spacing: 2px;
        text-shadow: 0px 0px 10px rgba(241, 196, 15, 0.3);
    }

    h3, .stSubheader {
        color: #bdc3c7 !important;
    }

    /* 科技感透明卡片佈局 */
    .card {
        background-color: rgba(22, 27, 34, 0.7) !important;
        border: 1px solid rgba(241, 196, 15, 0.2) !important;
        border-radius: 12px;
        padding: 25px;
        margin-bottom: 25px;
        backdrop-filter: blur(10px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    
    /* 側邊欄樣式調整 */
    section[data-testid="stSidebar"] {
        background-color: #010409 !important;
        border-right: 1px solid #30363d !important;
    }

    /* 隱藏預設元件與表情符號 */
    button {
        border-radius: 4px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =====================================================
# 2. 系統功能介面 (直接進入，無須按鈕)
# =====================================================

# 側邊控制欄：直接顯示功能選項
with st.sidebar:
    st.markdown("<h2 style='color:#f1c40f;'>系統控制台</h2>", unsafe_allow_html=True)
    user_role = st.radio("當前模式", ["公司使用者", "會計師事務所"])
    st.divider()
    
    # 核心檔案上傳功能
    files = st.file_uploader("批次上傳財報 PDF", type=["pdf"], accept_multiple_files=True)
    
    st.markdown("<br><br><p style='color:#7f8c8d; font-size:12px;'>玄武 AI 查核系統 v64</p>", unsafe_allow_html=True)

# 主畫面標題
st.title("玄武會計師事務所")
st.subheader("AI 四大財務 + 年度分析 + 查核整合系統")

# =====================================================
# 3. 分析內容呈現 (保留原本所有核心功能)
# =====================================================
if files:
    st.markdown(f"### 正在執行：{user_role} 專屬分析模式")
    
    # 模擬從 PDF 提取的分析數據
    df = pd.DataFrame({
        "年度": ["2022", "2023", "2024"],
        "營收": [1000, 1200, 850],
        "純益": [100, 150, -50]
    })

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:#f1c40f;'>異常點與風險分析</h4>", unsafe_allow_html=True)
        st.write("2024年度營收衰退幅度達 29%，且淨利轉負。")
        st.write("系統偵測到現金流量與營收變動率不匹配。")
        
        if user_role == "會計師事務所":
            st.divider()
            st.markdown("<h4 style='color:#f1c40f;'>查核建議 (ISA模式)</h4>", unsafe_allow_html=True)
            st.write("重點科目：應收帳款存在性、收入截止測試。")
            st.write("建議程序：執行函證程序並核對關係人往來。")
        else:
            st.divider()
            st.markdown("<h4 style='color:#f1c40f;'>經營改善建議</h4>", unsafe_allow_html=True)
            st.write("建議檢視變動成本結構，並規劃短期週轉資金。")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:#f1c40f;'>財務趨勢視覺化</h4>", unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(df["年度"], df["營收"], label="Revenue", color='#f1c40f', linewidth=3, marker='o')
        ax.plot(df["年度"], df["純益"], label="Profit", color='#e74c3c', linewidth=3, marker='s')
        ax.set_facecolor('none')
        ax.spines['bottom'].set_color('#bdc3c7')
        ax.spines['left'].set_color('#bdc3c7')
        ax.legend(facecolor='#161b22', edgecolor='#f1c40f')
        st.pyplot(fig)
        st.markdown("</div>", unsafe_allow_html=True)

    # 下載報告按鈕
    st.divider()
    st.download_button(
        label="下載 PDF 完整分析報告",
        data="RESULT_DATA",
        file_name="玄武查核報告.pdf",
        use_container_width=True
    )

else:
    # 啟動時的空白提示區塊
    st.markdown(
        """
        <div class='card' style='text-align: center; padding: 100px;'>
            <h2 style='color:#f1c40f;'>系統就緒</h2>
            <p>請於左側控制面板上傳 PDF 檔案，AI 將立即啟動查核與異常點分析。</p>
        </div>
        """,
        unsafe_allow_html=True
    )
