import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 頁面基礎設定
st.set_page_config(page_title="玄武會計師事務所", layout="wide")

# =====================================================
# 1. 核心邏輯：狀態控制
# =====================================================
# 使用 session_state 來追蹤使用者是否已經點擊進入
if "sys_active" not in st.session_state:
    st.session_state.sys_active = False

# =====================================================
# 2. 入口頁面（按鈕點擊前顯示）
# =====================================================
if not st.session_state.sys_active:
    # 這裡確保畫面上除了標題和按鈕，沒有任何 Email 或密碼輸入框
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.title("玄武會計師事務所")
    st.header("AI 四大財務 + 年度分析 + 查核整合系統 v64")
    st.write("點擊下方按鈕啟動系統")
    
    if st.button("進入系統", use_container_width=True):
        st.session_state.sys_active = True
        st.rerun()  # 重新整理頁面以切換顯示內容

    st.stop()  # 強制停止，不執行後續程式碼

# =====================================================
# 3. 系統內部頁面（按鈕點擊後才會執行到這裡）
# =====================================================

# 使用側邊欄處理身分切換與上傳，讓主畫面保持乾淨
with st.sidebar:
    st.title("系統選單")
    user_role = st.radio("使用者身份", ["公司使用者", "會計師事務所"])
    st.divider()
    
    # 多選 PDF 上傳
    uploaded_files = st.file_uploader("上傳財報 PDF", type=["pdf"], accept_multiple_files=True)
    
    st.divider()
    if st.button("退出系統"):
        st.session_state.sys_active = False
        st.rerun()

# =====================================================
# 4. 分析結果呈現
# =====================================================
if uploaded_files:
    st.title(f"財務分析報告 - {user_role}")
    
    # 模擬數據（實際運作時應接續 PDF 解析邏輯）
    data = pd.DataFrame({
        "年份": ["2022", "2023", "2024"],
        "營收": [1000, 1200, 850],
        "純益": [100, 150, -50]
    })

    # 分欄顯示結果
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("分析結果與異常點")
        st.write("1. 2024 年度營收大幅下滑約 29%。")
        st.write("2. 本年度淨利轉負，出現經營虧損。")
        st.write("3. 財務槓桿比例上升，需注意償債風險。")
        
        if user_role == "會計師事務所":
            st.divider()
            st.subheader("查核重點科目")
            st.write("- 收入認列時點測試 (Cut-off)")
            st.write("- 存貨跌價損失評估")
            st.write("- 關係人交易往來核對")
            
            st.subheader("查核建議")
            st.info("建議執行 ISA 505 外部函證程序，並針對本期異常虧損執行細部測試。")
        else:
            st.divider()
            st.subheader("改善建議")
            st.success("建議重新評估成本結構，並進行短期資金調度規劃。")

    with col2:
        st.subheader("趨勢分析圖表")
        fig, ax = plt.subplots()
        ax.plot(data["年份"], data["營收"], label="Revenue")
        ax.plot(data["年份"], data["純益"], label="Profit")
        ax.legend()
        st.pyplot(fig)

    st.divider()
    
    # 生成報告下載按鈕
    st.download_button(
        label="下載分析報告 (PDF)",
        data="PDF_CONTENT_PLACEHOLDER",
        file_name="financial_analysis.pdf"
    )
else:
    st.info("系統已就緒。請於左側控制面板上傳財報 PDF 檔案開始分析。")
