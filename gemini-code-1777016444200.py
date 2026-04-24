import streamlit as st
import pandas as pd
from datetime import datetime
from docx import Document
import io

# --- 1. 配置頁面 ---
st.set_page_config(page_title="多年度財務鑑定系統", layout="wide")

# --- 2. 模擬多年度分析引擎 ---
def get_multi_year_analysis(filenames):
    # 這裡將多個檔案名稱轉為年度排序，並產生趨勢數據
    years = sorted([f.replace('.pdf', '') for f in filenames])
    
    # 建立趨勢表格數據
    trend_data = pd.DataFrame({
        "年度": years,
        "M-Score (舞弊值)": [-1.45, -1.38, -1.21][-len(years):],
        "Z-Score (破產值)": [2.10, 1.55, 1.21][-len(years):],
        "舞弊預測機率": ["65%", "82%", "91%"][-len(years):]
    })
    
    return {
        "trend_table": trend_data,
        "summary": f"經由 {len(filenames)} 個年度的 DID 因果鑑定顯示，標的公司之盈餘操縱行為自 {years[0]} 年起逐年惡化，且 Z-Score 呈現顯著下滑趨勢。",
        "suggestion": "建議針對跨年度之應收帳款週轉率與關聯方交易進行溯源查核。"
    }

# --- 3. 側邊欄 ---
with st.sidebar:
    st.header("🏢 鑑識中心")
    firm = st.text_input("事務所", "誠信聯合會計師事務所")
    auditor = st.text_input("鑑定師", "陳大文 (CPA)")
    st.divider()
    
    # 開啟多選功能
    uploaded_files = st.file_uploader("📂 上傳年度財報 (可多選 92.pdf, 93.pdf...)", type=["pdf"], accept_multiple_files=True)
    
    if uploaded_files:
        st.success(f"已讀取 {len(uploaded_files)} 份年度檔案")

# --- 4. 主畫面顯示 ---
st.title("⚖️ 多年度財務不實鑑定與趨勢預測")

if uploaded_files:
    file_names = [f.name for f in uploaded_files]
    analysis = get_multi_year_analysis(file_names)
    
    # 顯示多年度趨勢圖表 (避免 HTML 亂碼，改用 Streamlit 原生表格)
    st.subheader("📊 各年度關鍵數據對照表")
    st.table(analysis['trend_table'])

    # 專業鑑定報告預覽
    st.divider()
    
    # 使用 container 確保樣式穩定，避免亂碼
    with st.container():
        st.markdown(f"### {firm}")
        st.markdown(f"#### 綜合財務鑑定報告書 (年度：{', '.join([f.replace('.pdf','') for f in file_names])})")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info("💡 **跨年度總結**")
            st.write(analysis['summary'])
        with col2:
            st.warning("⚠️ **專家建議**")
            st.write(analysis['suggestion'])
            
    # 下載按鈕
    # (此處可串接之前給您的 Word 產生函數，將表格放入 Word)
    st.sidebar.button("📥 匯出年度對照 Word 報告")

else:
    st.info("請同時上傳多份年度財報 PDF（例如：92.pdf、93.pdf），系統將自動執行跨年度 DID 趨勢分析。")
