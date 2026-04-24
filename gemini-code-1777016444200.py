import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 頁面基礎配置 - 務必放在程式碼最上方
st.set_page_config(page_title="玄武會計師事務所", layout="wide")

# 設定圖表為深色風格以配合背景
plt.style.use('dark_background')

# =====================================================
# 1. 視覺風格設定 (強制覆蓋為深色科技風 / 無表情符號)
# =====================================================
st.markdown(
    """
    <style>
    /* 強制全局背景為深色科技感 */
    .stApp {
        background: linear-gradient(135deg, #05070a 0%, #0d1117 50%, #161b22 100%) !important;
        color: #ecf0f1 !important;
    }

    /* 標題區域：金黃色強調色 */
    h1 {
        color: #f1c40f !important;
        font-weight: 800 !important;
        letter-spacing: 2px;
    }

    .stSubheader, h3 {
        color: #bdc3c7 !important;
    }

    /* 科技感透明卡片 */
    .report-card {
        background-color: rgba(22, 27, 34, 0.8) !important;
        border: 1px solid rgba(241, 196, 15, 0.3) !important;
        border-radius: 12px;
        padding: 25px;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    
    /* 側邊欄樣式 */
    section[data-testid="stSidebar"] {
        background-color: #010409 !important;
        border-right: 1px solid #30363d !important;
    }

    /* 隱藏多餘元件 */
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

# =====================================================
# 2. 系統功能介面 (物理移除所有登入邏輯，直接顯示)
# =====================================================

# 側邊控制面板
with st.sidebar:
    st.markdown("<h2 style='color:#f1c40f;'>系統控制台</h2>", unsafe_allow_html=True)
    # 使用者權限切換
    user_role = st.radio("當前模式", ["公司使用者", "會計師事務所"])
    st.divider()
    
    # 核心檔案上傳功能 (啟動後直接可用)
    files = st.file_uploader("批次上傳財報 PDF", type=["pdf"], accept_multiple_files=True)
    
    st.markdown("<br><br><p style='color:#57606a; font-size:12px;'>玄武 AI 查核系統 v64</p>", unsafe_allow_html=True)

# 主畫面標題
st.title("玄武會計師事務所")
st.subheader("AI 四大財務分析 與 異常點查核整合系統")

# =====================================================
# 3. 內容呈現區
# =====================================================
if files:
    st.markdown(f"#### 執行狀態：{user_role} 專屬分析模式")
    
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
        st.write("2024年度營收衰退幅度達 29.1%，且本期淨利由盈轉虧。")
        st.write("系統偵測到現金流量與營收變動率存在顯著不匹配。")
        
        if user_role == "會計師事務所":
            st.divider()
            st.markdown("<h4 style='color:#f1c40f;'>查核建議 (ISA 模式)</h4>", unsafe_allow_html=True)
            st.write("1. 針對收入認列時點執行截止
