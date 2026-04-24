import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# 設定頁面資訊
st.set_page_config(page_title="玄武會計師事務所", layout="wide")

# =====================================================
# 🔐 登入邏輯 (比照截圖設計)
# =====================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("玄武會計師事務所")
    st.subheader("AI 四大財務 + 年度分析 + 查核整合系統 v64")
    
    with st.container():
        entry_type = st.selectbox("入口", ["登入", "註冊"])
        email = st.text_input("Email")
        password = st.text_input("密碼", type="password")
        
        if st.button("登入"):
            if email and password: # 這裡可加入實際驗證邏輯
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("請輸入帳號密碼")
    st.stop()

# =====================================================
# 📂 側邊欄設定
# =====================================================
with st.sidebar:
    st.title("系統控制台")
    role = st.radio("使用者權限", ["會計師事務所", "公司使用者"])
    st.divider()
    files = st.file_uploader("批次上傳財報 (PDF)", type=["pdf"], accept_multiple_files=True)
    if st.button("登出"):
        st.session_state.logged_in = False
        st.rerun()

# =====================================================
# 📊 資料處理與分析核心
# =====================================================
st.title("📊 審計及財務報表分析結果")

# 模擬資料 (建議未來接上 PDF 解析後的 Dataframe)
df = pd.DataFrame({
    "年度": ["2022", "2023", "2024"],
    "營收": [100, 120, 90],
    "獲利": [10, 15, -5],
    "負債": [80, 100, 130]
})

def perform_analysis(data, user_role):
    alerts = []
    risks = ["財報不實風險", "舞弊風險"]
    
    # 簡單邏輯判斷
    if data["獲利"].iloc[-1] < 0:
        alerts.append("⚠️ 偵測到本年度虧損")
    if data["負債"].iloc[-1] > data["負債"].iloc[-2]:
        alerts.append("⚠️ 負債比例持續上升")
        
    return alerts, risks

# =====================================================
# 🚀 渲染主介面
# =====================================================
if files:
    alerts, risks = perform_analysis(df, role)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📌 異常點與風險")
        for a in alerts:
            st.warning(a)
        for r in risks:
            st.error(r)
            
    with col2:
        st.subheader("📈 趨勢分析")
        fig, ax = plt.subplots()
        # 注意：若要顯示中文，需額外設定字體，此處先用英文 Label 避免亂碼
        ax.plot(df["年度"], df["營收"], marker='o', label="Revenue")
        ax.plot(df["年度"], df["獲利"], marker='s', label="Profit")
        ax.legend()
        st.pyplot(fig)

    st.divider()
    
    # 針對會計師顯示查核建議
    if role == "會計師事務所":
        st.subheader("🔎 會計師查核專區")
        st.info("建議查核科目：應收帳款、關係人交易、收入認列")
        st.write("建議程序：執行外部函證、收入切割測試 (Cut-off test)")

    # 下載按鈕
    st.download_button(
        label="📥 下載完整分析報告 (PDF)",
        data=b"Sample PDF Content", # 這裡應放入 generate_pdf 的回傳值
        file_name="audit_report.pdf",
        mime="application/pdf"
    )
else:
    st.info("請於左側上傳財務報表 PDF 檔案以開始分析。")
