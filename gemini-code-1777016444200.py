import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 頁面基本設定
st.set_page_config(page_title="玄武會計師事務所", layout="wide")

# 1. 初始化進入狀態
if "is_entered" not in st.session_state:
    st.session_state.is_entered = False

# 2. 入口頁面（點擊進入系統前，只會執行這段區塊）
if not st.session_state.is_entered:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.title("玄武會計師事務所")
    st.header("AI 四大財務 + 年度分析 + 查核整合系統 v64")
    
    st.write("系統已準備就緒，請點擊按鈕進入分析介面")
    
    # 畫面上唯一的按鈕
    if st.button("進入系統", use_container_width=True):
        st.session_state.is_entered = True
        st.rerun()

    # 關鍵：強制停止，不讓後面的身分選擇或上傳框出現
    st.stop()

# =====================================================
# 3. 系統功能頁面（點擊按鈕後才會顯示）
# =====================================================

# 側邊欄：功能切換與檔案上傳
with st.sidebar:
    st.title("控制面板")
    role = st.radio("使用者身份", ["公司使用者", "會計師事務所"])
    st.divider()
    
    # PDF 上傳
    files = st.file_uploader("上傳財報 PDF", type=["pdf"], accept_multiple_files=True)
    
    st.divider()
    if st.button("返回首頁"):
        st.session_state.is_entered = False
        st.rerun()

# 4. 結果呈現區
if files:
    st.title(f"財務分析報告 - {role}")
    
    # 模擬分析數據
    df = pd.DataFrame({
        "年度": ["2022", "2023", "2024"],
        "營收": [1000, 1200, 850],
        "純益": [100, 150, -50]
    })

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("分析結果與異常點")
        st.write("1. 2024 年度營收下滑")
        st.write("2. 本期淨損，獲利能力轉弱")
        
        if role == "會計師事務所":
            st.divider()
            st.subheader("查核重點科目")
            st.write("應收帳款、存貨、關係人交易")
            st.subheader("ISA 查核建議")
            st.write("建議執行外部函證程序與收入切截測試")
        else:
            st.divider()
            st.subheader("經營建議")
            st.write("建議檢視成本結構，強化現金流管理")

    with col2:
        st.subheader("趨勢分析圖")
        fig, ax = plt.subplots()
        ax.plot(df["年度"], df["營收"], label="Revenue")
        ax.plot(df["年度"], df["純益"], label="Profit")
        ax.legend()
        st.pyplot(fig)

    st.divider()
    st.download_button("下載 PDF 完整報告", data="PDF_DATA", file_name="report.pdf")

else:
    st.info("請於左側控制面板上傳 PDF 檔案開始分析")
