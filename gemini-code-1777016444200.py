import streamlit as st
import pandas as pd
from datetime import datetime
from docx import Document
import io

# --- 1. 配置頁面 ---
st.set_page_config(page_title="專業鑑定工作站", layout="wide")

# --- 2. 鑑定模型數據邏輯 ---
def get_audit_logic(filename):
    # 這裡模擬您的 HLM/DID 分析結果
    return {
        "hlm": "顯著性 p < 0.01。階層線性模型顯示產業波動與企業盈餘管理具有高度結構性關聯。",
        "did": "雙重差分法分析顯示，在關鍵時點後，數據偏離正常值達 15.4%。",
        "m_score": "-1.38",
        "z_score": "1.21",
        "fraud_type": "營收提前認列與遞延資產減損之操縱",
        "ml_prob": "91.2%"
    }

# --- 3. 生成 Word 檔案的函數 ---
def make_docx(firm, auditor, filename, results):
    doc = Document()
    doc.add_heading(f'{firm} - 鑑定報告', 0)
    doc.add_paragraph(f"鑑定對象：{filename}")
    doc.add_paragraph(f"主辦鑑定師：{auditor}")
    doc.add_paragraph(f"報告生成時間：{datetime.now().strftime('%Y-%m-%d')}")
    
    doc.add_heading('一、 實證模型分析', level=1)
    doc.add_paragraph(f"HLM 分析結果：{results['hlm']}")
    doc.add_paragraph(f"DID 分析結果：{results['did']}")
    
    doc.add_heading('二、 風險指標', level=1)
    doc.add_paragraph(f"Beneish M-Score: {results['m_score']}")
    doc.add_paragraph(f"Altman Z-Score: {results['z_score']}")
    doc.add_paragraph(f"AI 舞弊預測機率: {results['ml_prob']}")
    
    # 轉為二進位流供下載
    target = io.BytesIO()
    doc.save(target)
    target.seek(0)
    return target

# --- 4. 介面呈現 ---
with st.sidebar:
    st.header("⚙️ 報告設定與匯出")
    firm = st.text_input("事務所名稱", "誠信聯合會計師事務所")
    auditor = st.text_input("主辦鑑定師", "陳大文 (CPA / CFE)")
    st.divider()
    
    # 【關鍵：多檔案上傳功能】
    uploaded_files = st.file_uploader(
        "📂 上傳 PDF 報表 (可多選)", 
        type=["pdf"], 
        accept_multiple_files=True  # 開啟多選
    )
    
    st.divider()
    st.info("提示：上傳後，下方會出現下載按鈕")

st.title("⚖️ 財務報表不實鑑定暨風險預測系統")

if uploaded_files:
    # 如果上傳了多個檔案，讓使用者選擇目前要看哪一個
    file_names = [f.name for f in uploaded_files]
    selected_file = st.selectbox("🎯 請選擇欲檢視的鑑定個案：", file_names)
    
    # 取得選中檔案的分析數據
    res = get_audit_logic(selected_file)
    
    # 在左側側邊欄產生下載按鈕
    docx_data = make_docx(firm, auditor, selected_file, res)
    
    with st.sidebar:
        st.download_button(
            label="📥 下載 Word 鑑定書",
            data=docx_data,
            file_name=f"鑑定報告_{selected_file}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        st.success(f"已準備好 {selected_file} 的報告")

    # 主畫面顯示專業報告 (HTML 格式)
    st.markdown(f"""
    <div style="border: 2px solid #000; padding: 40px; background-color: white; color: black; font-family: 'Microsoft JhengHei';">
        <div style="text-align: center; border-bottom: 4px solid #003366; padding-bottom: 10px;">
            <h1 style="color: #003366;">{firm}</h1>
            <h2 style="letter-spacing: 10px;">財務報表不實鑑定報告書</h2>
        </div>
        <p style="margin-top:20px;"><b>鑑定標的：</b>{selected_file}</p>
        <h3 style="background-color: #003366; color: white; padding: 5px;">一、 實證模型分析</h3>
        <p><b>HLM:</b> {res['hlm']}</p>
        <p><b>DID:</b> {res['did']}</p>
        <h3 style="background-color: #c0392b; color: white; padding: 5px;">二、 預測機率</h3>
        <p style="font-size: 20px; color: red;"><b>AI 預測舞弊機率：{res['ml_prob']}</b></p>
    </div>
    """, unsafe_allow_html=True)
    
else:
    st.warning("請先從左側上傳財報檔案。")
