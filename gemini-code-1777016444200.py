import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# 設定頁面配置
st.set_page_config(page_title="玄武會計師事務所", layout="wide")

# =====================================================
# 1. 入口（單一按鈕模式）
# =====================================================
if "entered" not in st.session_state:
    st.session_state.entered = False

if not st.session_state.entered:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.title("玄武會計師事務所")
    st.subheader("AI 四大財務 + 年度分析 + 查核整合系統 v64")
    
    # 唯一的進入按鈕，不包含任何登入欄位
    if st.button("進入系統", use_container_width=True):
        st.session_state.entered = True
        st.rerun()
    st.stop()

# =====================================================
# 2. 內部功能區（進入後顯示）
# =====================================================
with st.sidebar:
    st.title("控制面板")
    # 使用者類型選擇
    role = st.radio("使用者權限", ["公司使用者", "會計師事務所"])
    st.divider()
    # 檔案上傳
    files = st.file_uploader("上傳財務報表 PDF", type=["pdf"], accept_multiple_files=True)
    
    if st.button("返回首頁"):
        st.session_state.entered = False
        st.rerun()

# =====================================================
# 3. 結果顯示區
# =====================================================
if files:
    st.header(f"分析報告 - {role}")
    
    # 模擬數據
    df = pd.DataFrame({
        "年度": ["2022", "2023", "2024"],
        "營收": [1000, 1250, 950],
        "純益": [150, 180, -20]
    })

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("異常與風險分析")
        st.write("2024年度獲利由盈轉虧")
        st.write("負債比率異常上升")
        
        if role == "會計師事務所":
            st.subheader("查核重點科目")
            st.write("應收帳款、存貨、關係人交易、收入認列")

    with col2:
        st.subheader("趨勢圖表")
        fig, ax = plt.subplots()
        ax.plot(df["年度"], df["營收"], label="Revenue")
        ax.plot(df["年度"], df["純益"], label="Profit")
        ax.legend()
        st.pyplot(fig)

    st.divider()

    # 專業建議
    if role == "會計師事務所":
        st.subheader("查核建議 (ISA)")
        st.write("建議執行函證程序與收入切割測試")
    else:
        st.subheader("改善建議")
        st.write("建議優化財務結構並強化內部控制")

    # 生成下載按鈕
    st.download_button(
        label="下載 PDF 分析報告",
        data="PDF_CONTENT",
        file_name="report.pdf"
    )
else:
    st.write("請於左側選單上傳 PDF 檔案以進行分析")
