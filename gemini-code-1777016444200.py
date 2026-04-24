import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from docx import Document
from docx.shared import Pt, Inches
import io

# --- 1. 專家級頁面配置 ---
st.set_page_config(page_title="CPA 鑑識審計工作站", layout="wide")

# --- 2. 專家鑑定引擎：深度科目分析 ---
def expert_audit_engine(filenames):
    years = sorted([f.replace('.pdf', '') for f in filenames])
    n = len(years)
    
    # 模擬年度對照數據
    df = pd.DataFrame({
        "年度": years,
        "M-Score (舞弊偵測)": [-1.45 - (i*0.1) for i in range(n)],
        "Z-Score (財務壓力)": [2.8 - (i*0.6) for i in range(n)],
        "AR 週轉天數": [45 + (i*20) for i in range(n)],
        "營運現金流量比": [0.85 - (i*0.2) for i in range(n)]
    })
    
    # 專家查核清單建議
    audit_focus = [
        {"科目": "應收帳款 (AR)", "風險": "週轉天數異常拉長", "查核點": "執行外部詢證函，確認是否存在虛假銷售或年底放寬信用條件(Window Dressing)。"},
        {"科目": "存貨 (Inventory)", "風險": "跌價損失提列不足", "查核點": "針對綠色貸款資助之設備執行實地盤點，確認資產真實存在且無損壞。"},
        {"科目": "其他應付款", "風險": "關聯方資助隱匿", "查核點": "穿透查核資金最終流向，防範透過該科目進行盈餘操縱或洗錢。"},
        {"科目": "研究發展支出", "風險": "支出資本化異常", "查核點": "核對技術藍圖與專案進度，確認不具備商業價值的研發是否被違規列為資產。"}
    ]
    
    return df, audit_focus

# --- 3. 一頁式 Word 報告生成 ---
def make_expert_docx(firm, auditor, date_obj, df, focus):
    doc = Document()
    
    # 事務所抬頭
    header = doc.add_heading(firm, 0)
    header.alignment = 1
    
    # 報告基本資訊
    p = doc.add_paragraph()
    p.add_run(f"鑑定基準：{', '.join(df['年度'])} | 報告日期：{date_obj.strftime('%Y/%m/%d')}").italic = True
    p.alignment = 1

    doc.add_heading('一、 跨年度關鍵指標鑑定', level=1)
    t = doc.add_table(rows=1, cols=len(df.columns))
    t.style = 'Table Grid'
    for i, col in enumerate(df.columns):
        t.rows[0].cells[i].text = col
    for _, row in df.iterrows():
        row_cells = table_row = t.add_row().cells
        for i, val in enumerate(row):
            row_cells[i].text = str(val)

    doc.add_heading('二、 專家專項查核建議 (Forensic Focus)', level=1)
    for item in focus:
        p = doc.add_paragraph()
        p.add_run(f"【{item['科目']}】").bold = True
        p.add_run(f" 查核重點：{item['查核點']}")

    # 簽署區塊
    doc.add_paragraph("\n" * 2)
    sig_table = doc.add_table(rows=1, cols=2)
    sig_table.rows[0].cells[0].text = "事務所印鑑欄：\n\n\n(Seal)"
    sig_table.rows[0].cells[1].text = f"執行鑑定會計師簽署：\n\n__________________\n{auditor}\n{date_obj.strftime('%Y/%m/%d')}"
    
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# --- 4. Streamlit 介面 ---
with st.sidebar:
    st.header(" 專家簽署設定")
    firm = st.text_input("事務所名稱", "誠信聯合會計師事務所")
    auditor = st.text_input("執業會計師", "陳大文 (CPA / CFE)")
    r_date = st.date_input("簽署日期", datetime.now())
    st.divider()
    files = st.file_uploader(" 上傳年度財報 PDF", type=["pdf"], accept_multiple_files=True)

st.title(" 專家級鑑識會計鑑定系統")

if files:
    df_result, focus_list = expert_audit_engine([f.name for f in files])
    
    # 下載按鈕
    docx_stream = make_expert_docx(firm, auditor, r_date, df_result, focus_list)
    st.sidebar.download_button("📥 下載一頁式簽署報告", data=docx_stream, file_name="鑑定報告_專家簽署版.docx")

    # 網頁呈現
    st.subheader(" 鑑定數據趨勢對照")
    st.dataframe(df_result, use_container_width=True)
    
    st.divider()
    
    # 深度分析與簽章
    col1, col2 = st.columns([3, 2])
    with col1:
        st.error(" **重點會計科目查核清單**")
        for item in focus_list:
            with st.expander(f" {item['科目']} - {item['風險']}"):
                st.write(f"**查核動作建議：** {item['查核點']}")
    
    with col2:
        st.warning(" **一頁式簽章預覽**")
        st.markdown(f"""
        <div style="border: 1px solid #000; padding: 15px; background: white; color: black; font-family: 'Microsoft JhengHei';">
            <h5 style="text-align:center;">{firm}</h5>
            <p style="font-size: 12px;">負責鑑定師：{auditor}</p>
            <p style="font-size: 12px;">日期：{r_date}</p>
            <div style="margin-top:20px; border-top:1px dashed #ccc; padding-top:10px;">
                <p style="text-align:center; font-size: 14px; color: #666;">（此處於 Word 下載後蓋章）</p>
                <div style="height:50px;"></div>
                <p style="text-align:right;">____________________<br>簽署人代碼：CPA-CFE-001</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

else:
    st.info("請從側邊欄上傳多份 PDF 檔案以啟動專家鑑定模式。")
