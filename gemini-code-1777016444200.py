import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 1. 基礎頁面配置
st.set_page_config(page_title="玄武會計師事務所 | AI 財務查核", layout="wide")

# 2. 注入 EY 風格深色科技 CSS
st.markdown(
    """
    <style>
    /* 全局背景：深色漸變 (EY 風格) */
    .stApp {
        background: #000000 !important;
        background-image: 
            radial-gradient(circle at 20% 30%, rgba(255, 230, 0, 0.05) 0%, transparent 40%),
            radial-gradient(circle at 80% 70%, rgba(255, 230, 0, 0.05) 0%, transparent 40%) !important;
        color: #FFFFFF !important;
    }

    /* 標題與強調色 (安永黃) */
    h1, h2, h3, .highlight {
        color: #FFE600 !important;
        font-family: 'Segoe UI', Arial, sans-serif !important;
        font-weight: 700 !important;
    }

    /* 專業卡片佈局 */
    .data-card {
        background-color: rgba(28, 28, 28, 0.8) !important;
        border-left: 5px solid #FFE600 !important;
        border-radius: 4px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    }

    /* 側邊欄樣式 */
    [data-testid="stSidebar"] {
        background-color: #111111 !important;
        border-right: 1px solid #333333 !important;
    }

    /* 隱藏多餘 UI */
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

# =====================================================
# 3. 側邊欄控制 (PDF 檔案選擇與模式)
# =====================================================
with st.sidebar:
    st.markdown("<h2 class='highlight'>控制面板</h2>", unsafe_allow_html=True)
    user_role = st.radio("模式選擇", ["會計師事務所", "公司使用者"])
    st.divider()
    
    # 核心功能：多 PDF 檔案選擇
    uploaded_files = st.file_uploader("選擇 PDF 財務報表 (可多選)", type=["pdf"], accept_multiple_files=True)
    
    st.markdown("<br><br><p style='color:#666;'>版本：v64.2 Premium</p>", unsafe_allow_html=True)

# =====================================================
# 4. 主畫面：財務分析結果 (FR 關鍵指標與改善建議)
# =====================================================
st.markdown("<h1>玄武會計師事務所 <span style='font-size:18px; color:#666;'>AI 審計與顧問系統</span></h1>", unsafe_allow_html=True)

if uploaded_files:
    st.markdown(f"### 已選取檔案數量：{len(uploaded_files)} - 正在進行 {user_role} 專項分析")
    
    # 模擬 4 個 FR (Financial Report) 關鍵維度數據
    # 1. 獲利能力 2. 營運效率 3. 償債能力 4. 現金流量
    fr_data = pd.DataFrame({
        "指標項目": ["營收成長率", "淨利率", "負債比率", "流動比率"],
        "當前數值": ["-29.1%", "-5.8%", "62%", "115%"],
        "預警狀態": ["嚴重衰退", "轉盈為虧", "偏高", "需注意"]
    })

    col1, col2 = st.columns([1.2, 0.8])

    with col1:
        st.markdown("<h3 class='highlight'>FR 核心指標深度分析</h3>", unsafe_allow_html=True)
        
        # 指標 1: 損益與營收
        st.markdown("<div class='data-card'>", unsafe_allow_html=True)
        st.markdown("**1. 獲利性分析 (Profitability)**")
        st.write("2024 年度營收大幅下滑，主因為核心產品需求減弱。本期淨利轉負，需重新評估毛利結構。")
        st.markdown("<span style='color:#FFE600;'>改善建議：</span> 啟動成本管控計畫，檢視變動成本支出。", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # 指標 2: 資產負債結構
        st.markdown("<div class='data-card'>", unsafe_allow_html=True)
        st.markdown("**2. 償債能力分析 (Solvency)**")
        st.write("負債比率上升至 62%，長期償債壓力增加。流動比率略低於同業平均值 150%。")
        st.markdown("<span style='color:#FFE600;'>改善建議：</span> 優化債務結構，考慮將部分短期貸款轉為長期貸款。", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        if user_role == "會計師事務所":
            st.markdown("<div class='data-card'>", unsafe_allow_html=True)
            st.markdown("**3. 審計風險
