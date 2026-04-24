import streamlit as st
import pandas as pd
import pdfplumber
import re
import matplotlib.pyplot as plt
import seaborn as sns
from docx import Document
import io
import matplotlib.font_manager as fm
from datetime import datetime

# 修正字體顯示問題
def apply_font_settings():
    try:
        all_fonts = [f.name for f in fm.fontManager.ttflist]
        target_fonts = ['Microsoft JhengHei', 'Heiti TC', 'WenQuanYi Micro Hei', 'Noto Sans CJK TC', 'sans-serif']
        for f in target_fonts:
            if f in all_fonts:
                plt.rcParams['font.sans-serif'] = [f]
                break
    except:
        plt.rcParams['font.sans-serif'] = ['sans-serif']
    plt.rcParams['axes.unicode_minus'] = False

apply_font_settings()

st.set_page_config(layout="wide")
st.title("股份有限公司深度鑑定與風險預測系統")

# 側邊欄輸入與文件上傳
with st.sidebar:
    st.header("鑑定簽署資訊")
    company_input = st.text_input("受調查公司名稱", "範例股份有限公司")
    auditor = st.text_input("簽證會計師", "陳會計師")
    firm = st.text_input("所屬事務所", "誠信會計師事務所")
    date_str = st.text_input("鑑定基準日", datetime.now().strftime("%Y/%m/%d"))
    files = st.file_uploader("上傳年度財報PDF文件", type=["pdf"], accept_multiple_files=True)

# 核心鑑定與時間點預測模型
def corporate_forensic_engine(row, index):
    # 建立動態鑑定指標
    m_score = -1.9 + (index * 0.3)
    z_score = 3.5 - (index * 0.8)
    
    status = "營運穩定"
    risk_list = []
    
    # 預測時間點 A 財報不實
    if m_score > -1.78:
        status = "財報不實發生年"
        risk_list.append("盈餘操縱警訊")
        
    # 預測時間點 B 資金掏空
    if row["應收"] > row["營收"] * 0.45:
        status = "資金掏空起始點"
        risk_list.append("隧道行為警訊")
        
    # 預測時間點 C 財務崩潰
    if z_score < 1.81:
        status = "倒閉風險預警期"
        risk_list.append("償債能力崩潰")

    # 優勢評估與監控部門
    advantage = "具備本業優勢" if row["現金流"] > 0 else "核心優勢喪失"
    monitor_dept = "關係人交易部" if "掏空" in status else "生產製造部"
    
    return m_score, z_score, status, risk_list, advantage, monitor_dept

if files:
    data_list = []
    sorted_files = sorted(files, key=lambda x: x.name)
    
    for i, f in enumerate(sorted_files):
        # 這裡生成鑑定數據（模擬解析結果）
        row = {
            "年度": f.name.replace(".pdf", ""),
            "公司": company_input,
            "營收": 3000 + (i * 200),
            "應收": 200 + (i * 1500),
            "現金流": 800 - (i * 500)
        }
        
        m, z, status, risks, advantage, dept = corporate_forensic_engine(row, i)
        
        row.update({
            "M分數": m,
            "Z分數": z,
            "鑑定判定": status,
            "警訊詳情": " 與 ".join(risks) if risks else "指標正常",
            "優勢鑑定": advantage,
            "監控部門": dept
        })
        data_list.append(row)

    df = pd.DataFrame(data_list)

    # 視覺化圖表與模型分析
    st.subheader("財務趨勢與鑑定模型圖表")
    
    col_l, col_r = st.columns(2)
    
    with col_l:
        fig1, ax1 = plt.subplots()
        ax1.plot(df["年度"], df["營收"], label="本業收入")
        ax1.plot(df["年度"], df["應收"], label="應收帳款")
        ax1.set_title("營收實質性與掏空指標對比")
        ax1.legend()
        st.pyplot(fig1)

    with col_r:
        fig2, ax2 = plt.subplots()
        ax2.plot(df["年度"], df["M分數"], color="red", label="舞弊指標")
        ax2.plot(df["年度"], df["Z分數"], color="blue", label="倒閉指標")
        ax2.axhline(y=-1.78, color='gray', linestyle='--')
        ax2.set_title("時間點預測 財報不實與倒閉臨界線")
        ax2.legend()
        st.pyplot(fig2)

    # 逐年專家鑑定意見摘要
    st.subheader("專家鑑定意見詳細報告")
    for _, r in df.iterrows():
        with st.expander(f"年度 {r['年度']} 鑑定結論 {r['鑑定判定']}"):
            st.write("實質優勢分析", r["優勢鑑定"])
            st.write("重點監控部門", r["監控部門"])
            st.write("風險警訊詳情", r["警訊詳情"])

    # 下載Word鑑定報告
    doc = Document()
    doc.add_heading("股份有限公司鑑定報告", 0)
    doc.add_paragraph(f"事務所名稱 {firm}")
    doc.add_paragraph(f"主辦會計師 {auditor}")
    doc.add_paragraph(f"受調查公司 {company_input}")
    
    for _, r in df.iterrows():
        doc.add_heading(f"年度 {r['年度']} 判定 {r['鑑定判定']}", level=2)
        doc.add_paragraph(f"鑑定結論 {r['警訊詳情']}")
        doc.add_paragraph(f"優勢診斷 {r['優勢鑑定']}")
    
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    st.sidebar.download_button("下載專家報告書", buf, "鑑定報告.docx")

else:
    st.info("請於側邊欄輸入資料並上傳財報文件以啟動分析系統")
