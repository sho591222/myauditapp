import streamlit as st
import pandas as pd
from datetime import datetime
from docx import Document
import io

# --- 1. 配置頁面 ---
st.set_page_config(page_title="專業會計鑑定系統", layout="wide")

# --- 2. 動態分析引擎 (修正長度錯誤問題) ---
def get_audit_engine(filenames):
    # 取得上傳的年度清單並排序
    years = sorted([f.replace('.pdf', '') for f in filenames])
    n = len(years)
    
    # 動態產生模擬數據，確保長度與檔案數量完全一致
    # 這裡模擬隨年度惡化的數據
    m_scores = [-1.20 - (i * 0.1) for i in range(n)]
    z_scores = [2.5 - (i * 0.4) for i in range(n)]
    probs = [f"{60 + (i * 10)}%" for i in range(n)]
    
    trend_df = pd.DataFrame({
        "年度項目": years,
        "Beneish M-Score (舞弊偵測)": m_scores,
        "Altman Z-Score (破產預測)": z_scores,
        "AI 舞弊預測機率": probs
    })
    
    return {
        "df": trend_df,
        "health_status": "警告：標的公司速動比率逐年下降，且 Z-Score 已跌破 1.8 臨界值，財務狀況呈現『高度違約風險』。",
        "cpa_summary": f"經跨年度 ({', '.join(years)}) 綜合鑑定，標的公司存在明顯的盈餘操縱特徵，主要集中於應收帳款之異常增長與研發支出之資本化。其財務穩定性已瀕臨崩潰點。",
        "cpa_suggestions": [
            "建議融資銀行立即啟動債權保全程序。",
            "建議針對綠色貸款之專款專用情況執行實質性測試。",
            "應對其海外子公司的關聯交易執行專案審計。"
        ]
    }

# --- 3. Word 報告生成函數 ---
def make_report_docx(firm, auditor, data):
    doc = Document()
    doc.add_heading(firm, 0)
    doc.add_heading('財務報表鑑定暨風險預測報告書', level=1)
    
    doc.add_paragraph(f"主辦鑑定師：{auditor}")
    doc.add_paragraph(f"鑑定基準日：{datetime.now().strftime('%Y-%m-%d')}")
    
    doc.add_heading('一、 多年度關鍵財務指標對照', level=2)
    # 建立表格
    df = data['df']
    table = doc.add_table(rows=1, cols=len(df.columns))
    hdr_cells = table.rows[0].cells
    for i, col in enumerate(df.columns):
        hdr_cells[i].text = col
    for _, row in df.iterrows():
        row_cells = table.add_row().cells
        for i, val in enumerate(row):
            row_cells[i].text = str(val)
            
    doc.add_heading('二、 財務健康狀況與鑑定總結', level=2)
    doc.add_paragraph(data['health_status'])
    doc.add_paragraph(data['cpa_summary'])
    
    doc.add_heading('三、 專業專家建議', level=2)
    for s in data['cpa_suggestions']:
        doc.add_paragraph(s, style='List Number')
        
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# --- 4. Streamlit 介面設計 ---
with st.sidebar:
    st.header("🏢 鑑定控制台")
    firm = st.text_input("會計師事務所", "誠信聯合會計師事務所")
    auditor = st.text_input("負責鑑定師", "陳大文 (CPA / CFE)")
    st.divider()
    
    # 關鍵：開啟多選
    up_files = st.file_uploader("📂 上傳年度財報 PDF (可多選)", type=["pdf"], accept_multiple_files=True)
    st.divider()

st.title("⚖️ 跨年度財務不實鑑定與深度預測系統")

if up_files:
    # 執行分析
    f_names = [f.name for f in up_files]
    results = get_audit_engine(f_names)
    
    # 側邊欄下載按鈕
    doc_out = make_report_docx(firm, auditor, results)
    st.sidebar.download_button(
        label="📥 下載完整 Word 鑑定報告",
        data=doc_out,
        file_name=f"鑑定報告_多年度對照.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

    # 主介面呈現 (使用 st 原生元件避免 HTML 亂碼)
    st.subheader(f"📊 {firm} - 年度數據趨勢分析")
    st.dataframe(results['df'], use_container_width=True)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        st.error("🚨 **財務健康診斷**")
        st.write(results['health_status'])
        st.info("🧾 **會計師鑑定總結**")
        st.write(results['cpa_summary'])
        
    with col2:
        st.warning("💡 **專業行動建議**")
        for s in results['cpa_suggestions']:
            st.write(f"- {s}")

    st.success("✅ 分析完成。您可以在左側側邊欄點擊按鈕下載 Word 格式的鑑定報告。")

else:
    st.info("👋 歡迎使用！請於左側同時上傳多份 PDF 檔案（例如：92.pdf, 93.pdf）以啟動跨年度趨勢鑑定。")
