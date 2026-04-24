import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# 設定頁面配置
st.set_page_config(page_title="玄武會計師事務所", layout="wide")

# =====================================================
# 🚪 1. 入口（極簡）
# =====================================================
if "entered" not in st.session_state:
    st.session_state.entered = False

if not st.session_state.entered:
    st.title(" 玄武會計師事務所")
    st.subheader("AI 四大財報分析 查核整合系統")
    if st.button("進入系統", use_container_width=True):
        st.session_state.entered = True
        st.rerun()
    st.stop()

# =====================================================
# 📂 2. 上傳區 & 👥 3. 使用者類型
# =====================================================
with st.sidebar:
    st.title("⚙️ 系統選單")
    role = st.radio("請選擇身分：", ["🏢 公司使用者", "🏛️ 會計師事務所"])
    st.divider()
    files = st.file_uploader("上傳財報 PDF (可多選)", type=["pdf"], accept_multiple_files=True)
    if st.button("登出 / 返回首頁"):
        st.session_state.entered = False
        st.rerun()

# =====================================================
# 🧠 分析引擎邏輯
# =====================================================
# 模擬從 PDF 提取的資料
df_mock = pd.DataFrame({
    "年度": ["2022", "2023", "2024"],
    "營收": [1000, 1250, 950],
    "純益": [150, 180, -20],
    "負債比": ["45%", "48%", "62%"]
})

def get_analysis(role):
    # 共用分析
    common_alerts = ["⚠️ 2024年由盈轉虧，獲利能力大幅衰退。", "⚠️ 負債比例異常攀升，需注意償債壓力。"]
    risks = ["🚩 掏空風險：中", "🚩 舞弊風險：低", "🚩 財報不實風險：中"]
    
    if role == "🏛️ 會計師事務所":
        return {
            "alerts": common_alerts + ["⚠️ 存貨週轉率下降，疑似存貨呆滯。", "⚠️ 應收帳款回收天數異常拉長。"],
            "risks": risks,
            "focus": ["應收帳款 (AR)", "存貨 (Inventory)", "關係人交易", "收入認列 (Cut-off)"],
            "isa_advise": [
                "ISA 505：對重大客戶執行外部函證程序。",
                "ISA 501：參與年度實地存貨盤點，確保其存在性。",
                "ISA 240：針對收入認列執行分錄測試 (Journal Entry Testing)。"
            ]
        }
    else:
        return {
            "alerts": common_alerts,
            "risks": risks,
            "advise": ["建議優化財務結構，降低短期借款。", "強化內控制度，特別是採購與付款循環。"]
        }

# =====================================================
# 📊 4. 結果頁 (一頁式顯示)
# =====================================================
if files:
    st.title(f"📊 分析報告 - {role}")
    analysis = get_analysis(role)
    
    # --- 第一排：關鍵指標 ---
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("⚠️ 異常與風險分析")
        for alert in analysis["alerts"]:
            st.warning(alert)
        for risk in analysis["risks"]:
            st.error(risk)
            
    with col2:
        st.subheader("📈 營運趨勢圖")
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(df_mock["年度"], df_mock["營收"], label="Revenue", marker='o')
        ax.plot(df_mock["年度"], df_mock["純益"], label="Profit", marker='s')
        ax.legend()
        st.pyplot(fig)

    st.divider()

    # --- 第二排：專業建議 (根據身分變動) ---
    if role == " 會計師事務所":
        c1, c2 = st.columns(2)
        with c1:
            st.subheader(" 查核重點科目")
            st.write(analysis["focus"])
        with c2:
            st.subheader(" 查核建議 (ISA)")
            for item in analysis["isa_advise"]:
                st.info(item)
    else:
        st.subheader(" 改善建議")
        for item in analysis["advise"]:
            st.success(item)

    # --- 下載區 ---
    st.divider()
    st.download_button(
        label="📥 自動生成並下載完整分析報告 (
