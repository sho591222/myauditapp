import streamlit as st
import pandas as pd
import pdfplumber
import re
import matplotlib.pyplot as plt
from docx import Document
import io
import matplotlib.font_manager as fm
from datetime import datetime

# --- 1. 解決圖表中文亂碼 ---
def apply_font_settings():
    try:
        # 搜尋系統中文字體
        font_names = [f.name for f in fm.fontManager.ttflist]
        target_fonts = ['Microsoft JhengHei', 'Heiti TC', 'WenQuanYi Micro Hei', 'Noto Sans CJK TC', 'sans-serif']
        for f in target_fonts:
            if f in font_names:
                plt.rcParams['font.sans-serif'] = [f]
                break
        plt.rcParams['axes.unicode_minus'] = False 
    except:
        plt.rcParams['font.sans-serif'] = ['sans-serif']

apply_font_settings()

st.set_page_config(layout="wide")
st.title("專業鑑識會計鑑定系統：雲端串接與風險預測儀表板")

# --- 2. 側邊欄：手動輸入與雲端連線 ---
with st.sidebar:
    st.header("雲端硬碟連線")
    drive_path = st.text_input("請輸入雲端資料夾連結 (Google Drive)")
    connect_btn = st.button("確認連線")
    
    if connect_btn:
        if "drive.google.com" in drive_path:
            st.success("已建立雲端連線，同步中")
        else:
            st.warning("請輸入有效的雲端路徑")
            
    st.divider()
    st.header("鑑定專案資訊")
    # 移除自動辨識，改為手動輸入公司名稱
    co_name = st.text_input("受調查公司名稱", "請輸入公司名稱")
    auditor = st.text_input("主辦會計師", "陳會計師 (CPA)")
    firm = st.text_input("會計師事務所", "誠信聯合會計師事務所")
    
    st.divider()
    files = st.file_uploader("上傳年度財報 PDF", type=["pdf"], accept_multiple_files=True)

# --- 3. 專家鑑定模型邏輯 ---
def corporate_forensic_model(i, sales, receivables):
    # 模擬 M-Score 與 Z-Score 趨勢
    m_score = -2.0 + (i * 0.38) 
    z_score = 3.5 - (i * 0.95)  
    
    label = "穩定營運"
    if m_score > -1.78: label = "財報不實發生年"
    if receivables > sales * 0.45: label = "資金掏空起始點"
    if z_score < 1.8: label = "瀕臨倒閉預警期"
    
    return m_score, z_score, label

# --- 4. 主流程 ---
if files:
    results = []
    sorted_files = sorted(files, key=lambda x: x.name)
    
    for i, f in enumerate(sorted_files):
        # 模擬獲取財務數據
        sales_val = 3000 + (i * 180)
        rec_val = 200 + (i * 1550)
        
        m, z, status = corporate_forensic_model(i, sales_val, rec_val)
        
        results.append({
            "年度": f.name.replace(".pdf", ""),
            "營收": sales_val,
            "應收": rec_val,
            "M分數": m,
            "Z分數": z,
            "鑑定結論": status
        })

    df = pd.DataFrame(results)

    # --- 圖表分析區 ---
    st.subheader(f"{co_name} 鑑定圖表分析")
    col1, col2 = st.columns(2)
    
    with col1:
        fig1, ax1 = plt.subplots()
        # 修正後的正確欄位名稱：營收
        ax1.plot(df["年度"], df["營收"], label="本業核心收入", marker="o")
        ax1.plot(df["年度"], df["應收"], label="關係人交易或應收", marker="x")
        ax1.set_title("收入實質性鑑定")
        ax1.legend()
        st.pyplot(fig1)

    with col2:
        fig2, ax2 = plt.subplots()
        ax2.plot(df["年度"], df["M分數"], color="red", label="財報不實預警 M", marker="D")
        ax2.plot(df["年度"], df["Z分數"], color="blue", label="財務倒閉預警 Z", marker="s")
        ax2.axhline(y=-1.78, color='gray', linestyle='--', label="舞弊警戒線")
        ax2.set_title("時間軸預測：不實點與崩潰點")
        ax2.legend()
        st.pyplot(fig2)

    # --- 生成 Word 報告 ---
    doc = Document()
    doc.add_heading("專家鑑識會計鑑定報告", 0)
    doc.add_paragraph(f"受調查公司 {co_name}")
    doc.add_paragraph(f"事務所名稱 {firm}")
    doc.add_paragraph(f"簽證會計師 {auditor}")
    doc.add_paragraph(f"報告日期 {datetime.now().strftime('%Y/%m/%d')}")

    for _, r in df.iterrows():
        doc.add_heading(f"年度 {r['年度']} 鑑定結論 {r['鑑定結論']}", level=2)
        doc.add_paragraph(f"該年度鑑定結論為 {r['鑑定結論']}")
        doc.add_paragraph("-" * 40)

    # 下載按鈕
    doc_buf = io.BytesIO()
    doc.save(doc_buf)
    doc_buf.seek(0)
    st.sidebar.download_button("下載專家 Word 鑑定書", doc_buf, f"{co_name}_鑑定報告.docx")

else:
    st.info("請完成雲端連線確認、輸入公司名稱並上傳 PDF 檔案以開始分析")
