import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# 設定頁面基礎配置
st.set_page_config(page_title="玄武會計師事務所", layout="wide")

# =====================================================
# 🚪 1. 入口（極簡單按鈕）
# =====================================================
if "entered" not in st.session_state:
    st.session_state.entered = False

if not st.session_state.entered:
    # 這裡顯示您截圖中的標題，但移除所有輸入框
    st.markdown("<br><br>", unsafe_allow_html=True) # 增加間距
    st.title("玄武會計師事務所")
    st.subheader("AI 四大財務 + 年度分析 + 查核整合系統 v64")
    
    st.info("歡迎使用 AI 審計整合系統，請點擊下方按鈕開始。")
    
    # 唯一的進入按鈕
    if st.button("進入系統", use_container_width=True):
        st.session_state.entered = True
        st.rerun()
    st.stop()

# =====================================================
# 📂 2. 上傳與身分選擇 (進入後顯示)
# =====================================================
with st.sidebar:
    st.title("🛠️ 操作面板")
    
    # 👥 3. 使用者類型切換
    role = st.radio("選擇您的身分：", ["🏢 公司使用者", "🏛️ 會計師事務所"])
    
    st.divider()
    
    # 檔案上傳
    uploaded_files = st.file_uploader("上傳財報 PDF (可多選)", type=["pdf"], accept_multiple_files=True)
    
    if st.button("登出 / 返回首頁"):
        st.session_state.entered = False
        st.rerun()

# =====================================================
# 📊 4. 結果頁（一頁式分析）
# =====================================================
if uploaded_files:
    st.header(f"📊 財務分析報告 - {role}")
    
    # 這裡模擬分析數據 (實際開發時會解析 PDF)
    mock_data = pd.DataFrame({
        "年度": ["2022", "2023", "2024"],
        "營收": [1000, 1250, 950],
        "純益": [150, 180, -20]
    })

    # 分欄顯示
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("⚠️ 異常點與風險分析")
        st.warning("● 2024年淨利轉負，獲利能力顯著衰退。")
        st.warning("● 負債比率較去年同期上升 15%。")
        st.error("🚩 潛在舞弊/掏空風險評估：中高")
        
        if role == "🏛️ 會計師事務所":
            st.subheader("📌 查核重點科目")
            st.write("* 應收帳款認列時點 (Cut-off)")
            st.write("* 存貨跌價損失準備")
            st.write("* 關係人資金往來測試")
    
    with col2:
        st.subheader("📈 營運趨勢")
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(mock_data["年度"], mock_data["營收"], label="Revenue", marker='o')
        ax.plot(mock_data["年度"], mock_data["純益"], label="Profit", marker='s')
        ax.legend()
        st.pyplot(fig)

    st.divider()

    # 查核建議
    if role == "🏛️ 會計師事務所":
        st.subheader("💡 查核建議 (ISA 規範)")
        st.info("建議執行 ISA 505 外部函證，並針對異常收入執行分錄測試 (Journal Entry Testing)。")
    else:
        st.subheader("💡 改善建議")
        st.success("建議強化內部控制循環，並審核資金調度計畫以應對虧損風險。")

    # 5. 自動生成報告下載
    st.download_button(
        label="📥 下載完整 PDF 分析報告",
        data="PDF_Binary_Data", # 這裡放入 reportlab 生成的內容
        file_name="Audit_Report.pdf",
        mime="application/pdf"
    )

else:
    st.info("請於左側面板上傳 PDF 檔案開始 AI 自動查核分析。")
