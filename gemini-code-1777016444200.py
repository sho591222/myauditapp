import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 設定頁面配置
st.set_page_config(page_title="玄武會計師事務所", layout="wide")

# =====================================================
# 1. 系統進入狀態控制
# =====================================================
# 使用 session_state 確保按下按鈕後畫面會切換
if "sys_active" not in st.session_state:
    st.session_state.sys_active = False

# =====================================================
# 2. 單一按鈕入口頁面 (點擊按鈕前顯示)
# =====================================================
if not st.session_state.sys_active:
    # 這裡絕對不會出現 Email 或密碼輸入框
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.title("玄武會計師事務所")
    st.subheader("AI 四大財務 + 年度分析 + 查核整合系統 v64")
    st.write("點擊下方按鈕啟動系統進行分析")
    
    if st.button("進入系統", use_container_width=True):
        st.session_state.sys_active = True
        st.rerun()

    # 關鍵：這裡會停止執行後續程式碼，確保主功能頁面不會提前出現
    st.stop()

# =====================================================
# 3. 內部主功能頁面 (點擊按鈕後顯示)
# =====================================================

# 使用側邊欄來放置設定選項
with st.sidebar:
    st.title("系統選單")
    user_type = st.radio("選擇使用者類型", ["公司使用者", "會計師事務所"])
    st.divider()
    
    # 檔案上傳
    files = st.file_uploader("上傳財務報表 PDF", type=["pdf"], accept_multiple_files=True)
    
    st.divider()
    if st.button("返回首頁"):
        st.session_state.sys_active = False
        st.rerun()

# 4. 分析結果顯示區
if files:
    st.header(f"財務分析報告 - {user_type}")
    
    # 模擬數據供視覺化呈現
    chart_data = pd.DataFrame({
        "年度": ["2022", "2023", "2024"],
        "營收": [1000, 1250, 920],
        "純益": [120, 180, -30]
    })

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("分析結果與異常點")
        st.write("1. 2024 年度營收出現顯著衰退。")
        st.write("2. 本期淨損，需注意獲利能力風險。")
        
        if user_type == "會計師事務所":
            st.divider()
            st.subheader("查核重點科目")
            st.write("應收帳款、存貨週轉、關係人資金往來。")
            st.subheader("查核建議")
            st.write("建議執行 ISA 505 外部函證並針對異常科目執行細部測試。")
        else:
            st.divider()
            st.subheader("改善建議")
            st.write("建議檢視成本管控機制，並優化營運資金調度。")

    with col2:
        st.subheader("營運趨勢圖")
        fig, ax = plt.subplots()
        ax.plot(chart_data["年度"], chart_data["營收"], label="Revenue")
        ax.plot(chart_data["年度"], chart_data["純益"], label="Profit")
        ax.legend()
        st.pyplot(fig)

    st.divider()
    st.download_button("下載 PDF 完整報告", data="REPORT_CONTENT", file_name="analysis_report.pdf")

else:
    st.info("系統已就緒。請於左側控制面板上傳財報 PDF 以開始分析。")
