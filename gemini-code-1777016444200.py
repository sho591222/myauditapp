import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 1. 基礎配置：強制開啟寬螢幕模式與深色側邊欄
st.set_page_config(page_title="玄武會計師事務所", layout="wide")

# 2. 強制注入深色科技感背景 CSS (模仿安永官網風格)
# 這段 CSS 會強行覆蓋 Streamlit 的預設背景
st.markdown(
    """
    <style>
    /* 全局背景漸變 */
    .stApp {
        background: linear-gradient(180deg, #05070a 0%, #0d1117 100%) !important;
        color: #ecf0f1 !important;
    }

    /* 標題與字體：金黃色科技感 */
    h1, h2, h3, .stSubheader {
        color: #f1c40f !important;
        font-family: 'Segoe UI', sans-serif !important;
    }

    /* 內容區塊卡片化 */
    .card {
        background-color: rgba(22, 27, 34, 0.8) !important;
        border: 1px solid rgba(241, 196, 15, 0.2) !important;
        border-radius: 12px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
    }
    
    /* 側邊欄樣式修正 */
    [data-testid="stSidebar"] {
        background-color: #010409 !important;
        border-right: 1px solid #30363d !important;
    }

    /* 隱藏原生多餘 UI */
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

# =====================================================
# 3. 系統核心介面 (直接渲染，不設登入門檻)
# =====================================================

# 側邊控制欄
with st.sidebar:
    st.markdown("<h2 style='color:#f1c40f;'>系統控制台</h2>", unsafe_allow_html=True)
    # 使用者權限切換
    user_role = st.radio("當前模式", ["公司使用者", "會計師事務所"])
    st.divider()
    
    # 核心檔案上傳區域
    files = st.file_uploader("批次上傳財報 PDF", type=["pdf"], accept_multiple_files=True)
    
    st.markdown("<br><br><p style='color:#57606a; font-size:12px;'>玄武 AI 查核系統 v64.1</p>", unsafe_allow_html=True)

# 主標題區
st.title("玄武會計師事務所")
st.subheader("AI 四大財務分析 與 異常點查核整合系統")

# 4. 分析邏輯與結果呈現
if files:
    st.markdown(f"#### 正在執行分析：{user_role} 專屬模式")
    
    # 模擬提取的財務數據
    chart_data = pd.DataFrame({
        "年度": ["2022", "2023", "2024"],
        "營收": [1000, 1200, 850],
        "純益": [100, 150, -50]
    })

    # 左右分欄
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:#f1c40f;'>異常點分析結果</h4>", unsafe_allow_html=True)
        st.write("營收表現：2024年度下滑約 29.1%。")
        st.write("獲利狀況：本期由盈轉虧，淨利表現異常。")
        
        if user_role == "會計師事務所":
            st.divider()
            st.markdown("<h4 style='color:#f1c40f;'>會計師查核建議</h4>", unsafe_allow_html=True)
            st.write("重點科目：應收帳款、存貨週轉、收入認列。")
            st.write("建議程序：執行 ISA 505 外部函證並針對異常科目執行細部測試。")
        else:
            st.divider()
            st.markdown("<h4 style='color:#f1c40f;'>經營策略建議</h4>", unsafe_allow_html=True)
            st.write("策略方向：重新檢視變動成本結構，並規劃短期週轉資金。")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:#f1c40f;'>財務表現趨勢圖</h4>", unsafe_allow_html=True)
        # 繪製圖表
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(chart_data["年度"], chart_data["營收"], label="Revenue", color='#f1c40f', linewidth=2.5, marker='o')
        ax.plot(chart_data["年度"], chart_data["純益"], label="Profit", color='#e74c3c', linewidth=2.5, marker='s')
        ax.set_facecolor('none')
        ax.legend(facecolor='#0d1117', edgecolor='#f1c40f')
        st.pyplot(fig)
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    st.download_button("下載完整 AI 查核分析報告 (PDF)", data="DATA", file_name="audit_report.pdf", use_container_width=True)

else:
    # 啟動時顯示的預設卡片
    st.markdown(
        """
        <div class='card' style='text-align: center; padding: 100px 20px;'>
            <h2 style='color:#f1c40f;'>系統就緒</h2>
            <p style='color:#8b949e;'>請於左側控制面板上傳 PDF 財報，AI 將立即執行財務查核分析。</p>
            <p style='color:#57606a; font-size:13px;'>本系統已移除登入驗證，開啟即可直接使用。</p>
        </div>
        """,
        unsafe_allow_html=True
    )
