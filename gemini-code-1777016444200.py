import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 頁面基礎設定
st.set_page_config(page_title="玄武會計師事務所", layout="wide")

# =====================================================
# 1. 狀態管理
# =====================================================
if "entered" not in st.session_state:
    st.session_state.entered = False

# =====================================================
# 2. 登入入口 (已刪除 Email, 密碼, 選單)
# =====================================================
if not st.session_state.entered:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.title("玄武會計師事務所")
    st.subheader("AI 四大財務 + 年度分析 + 查核整合系統 v64")
    
    # 此處為畫面唯一按鈕，絕無其他輸入框
    if st.button("進入系統", use_container_width=True):
        st.session_state.entered = True
        st.rerun()
    
    # 強制停止，不載入後續任何功能
    st.stop()

# =====================================================
# 3. 系統主功能區 (點擊按鈕後才會進入)
# =====================================================

# 側邊欄：控制身分與上傳
with st.sidebar:
    st.title("控制中心")
    # 選擇使用者類型
    role = st.radio("選擇使用者類型", ["公司使用者", "會計師事務所"])
    st.divider()
    
    # 檔案上傳
    files = st.file_uploader("上傳財務報表 PDF", type=["pdf"], accept_multiple_files=True)
    
    if st.button("返回首頁"):
        st.session_state.entered = False
        st.rerun()

# 4. 結果頁面呈現
if files:
    st.title(f"分析報告 - {role}")
    
    # 模擬數據
    df = pd.DataFrame({
        "年度": ["2022", "2023", "2024"],
        "營收": [1000, 1250, 920],
        "獲利": [120, 180, -30]
    })

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("分析指標與異常點")
        st.write("1. 2024年度出現經營虧損")
        st.write("2. 營收較前一期大幅下滑")
        
        if role == "會計師事務所":
            st.divider()
            st.subheader("查核重點與建議 (ISA)")
            st.write("重點科目：應收帳款、存貨、收入認列")
            st.write("建議程序：執行函證程序與收入切截測試")
        else:
            st.divider()
            st.subheader("經營改善建議")
            st.write("建議優化財務結構，並加強現金流量控管")

    with col2:
        st.subheader("營運趨勢圖")
        fig, ax = plt.subplots()
        ax.plot(df["年度"], df["營收"], label="Revenue")
        ax.plot(df["年度"], df["獲利"], label="Profit")
        ax.legend()
        st.pyplot(fig)

    st.divider()
    st.download_button("下載 PDF 完整報告", data="REPORT_BINARY", file_name="audit_report.pdf")

else:
    st.info("系統已啟動。請於左側控制面板上傳財報 PDF 以進行 AI 查核分析。")
