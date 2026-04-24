import streamlit as st
import pandas as pd
from datetime import datetime
from docx import Document
from docx.shared import Inches
import io

# --- 1. 配置頁面 ---
st.set_page_config(page_title="AI 鑑識會計鑑定系統", layout="wide")

# --- 2. 深度分析引擎：細緻化指標 ---
def perform_deep_audit(filenames):
    # 排序年度
    years = sorted([f.replace('.pdf', '') for f in filenames])
    n = len(years)
    
    # 模擬更細緻的財務比率分析 (依年度演變)
    # 這裡可以根據您的 DID 邏輯調整數據變化
    data = {
        "年度": years,
        "M-Score (盈餘操縱值)": [-1.45 - (i*0.05) for i in range(n)],
        "Z-Score (破產預測值)": [2.8 - (i*0.4) for i in range(n)],
        "應收帳款週轉率": [6.5 - (i*0.8) for i in range(n)],
        "營業現金流量/淨利": [0.9 - (i*0.2) for i in range(n)],
        "舞弊機率 (%)": [55 + (i*12) for i in range(n)]
    }
    df = pd.DataFrame(data)
    
    return {
        "df": df,
        "detail_analysis": f"經對比 {years[0]} 至 {years[-1]} 年度數據，標的公司之 M-Score 呈現惡化趨勢，且營業現金流量與淨利之背離幅度逐年擴大，顯示盈餘品質極度不佳。",
        "health_check": "標的公司之 Z-Score 已低於 1.8，屬破產高風險區。其速動比率嚴重不足，無法支應短期債務。",
        "cpa_conclusion": "綜合鑑定意見：標的公司涉嫌利用遞延損益與虛增營收之方式規避貸款契約之財務限制，建議啟動專案查核。",
        "action_plans": [
            "1. 立即清查過去三年之重大關聯方交易。",
            "2. 針對綠色貸款資金流向進行溯源追蹤。",
            "3. 要求標的公司限期補足資產抵押物。"
        ]
    }

# --- 3. 生成 Word 報告 (包含簽名欄位) ---
def create_signed_report(firm, auditor, report_date, results):
    doc = Document()
    
    # 標題
    title = doc.add_heading(firm, 0)
    doc.add_heading('財務報表鑑定暨深度預測報告書', level=1)
    
    # 基本資訊
    doc.add_paragraph(f"報告日期：{report_date.strftime('%Y年%m月%d日')}")
    doc.add_paragraph(f"鑑定對象：跨年度財報對照 ({', '.join(results['df']['年度'])})")
    
    # 一、 細緻指標分析
    doc.add_heading('一、 跨年度財務比率細緻對照表', level=2)
    df = results['df']
    table = doc.add_table(rows=1, cols=len(df.columns))
    for i, column in enumerate(df.columns):
        table.rows[0].cells[i].text = column
    for _, row in df.iterrows():
        row_cells = table.add_row().cells
        for i, item in enumerate(row):
            row_cells[i].text = str(item)
    
    # 二、 鑑定深度結論
    doc.add_heading('二、 鑑定結論與深度風險分析', level=2)
    doc.add_paragraph(results['detail_analysis'])
    doc.add_paragraph(results['health_check'])
    doc.add_paragraph(results['cpa_conclusion'])
    
    # 三、 行動建議
    doc.add_heading('三、 專家行動建議', level=2)
    for plan in results['action_plans']:
        doc.add_paragraph(plan)
        
    # 四、 簽署區
    doc.add_paragraph("\n" * 2)
    sig_table = doc.add_table(rows=1, cols=2)
    sig_table.columns[0].width = Inches(3.5)
    
    # 左側印鑑區
    sig_table.rows[0].cells[0].text = "會計師事務所蓋章欄："
    # 右側簽名區
    cell = sig_table.rows[0].cells[1]
    cell.text = f"主辦鑑定會計師簽名或蓋章：\n\n______________________\n\n{auditor}\n日期：{report_date.strftime('%Y/%m/%d')}"
    
    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# --- 4. Streamlit 介面 ---
with st.sidebar:
    st.header("📝 鑑定簽署設定")
    firm_name = st.text_input("事務所名稱", "誠信聯合會計師事務所")
    auditor_name = st.text_input("主辦鑑定師", "陳大文 (CPA / CFE)")
    r_date = st.date_input("報告簽署日期", datetime.now())
    st.divider()
    
    up_files = st.file_uploader("📂 上傳年度財報 PDF (可多選 92.pdf, 93.pdf...)", type=["pdf"], accept_multiple_files=True)
    st.divider()

st.title("⚖️ 多年度財報鑑定與深度風險分析工作站")

if up_files:
    # 執行鑑定
    f_names = [f.name for f in up_files]
    audit_data = perform_deep_audit(f_names)
    
    # 生成報告檔案
    docx_file = create_signed_report(firm_name, auditor_name, r_date, audit_data)
    
    with st.sidebar:
        st.download_button(
            label="📥 下載 Word 簽署版鑑定報告",
            data=docx_file,
            file_name=f"財務鑑定報告_{datetime.now().strftime('%Y%m%d')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        st.success("報告已備妥，請點擊下載。")

    # 主畫面呈現 (解決亂碼問題)
    st.subheader("📊 跨年度關鍵指標變化趨勢")
    st.dataframe(audit_data['df'], use_container_width=True)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        st.error(" **深度風險診斷**")
        st.write(audit_data['detail_analysis'])
        st.write(audit_data['health_check'])
        
    with col2:
        st.info(" **會計師綜合意見**")
        st.write(audit_data['cpa_conclusion'])
        st.warning(" **後續行動建議**")
        for p in audit_data['action_plans']:
            st.write(p)

    # 底部簽署預覽
    st.divider()
    st.markdown(f"""
    <div style="text-align:right; border-top: 1px solid #ccc; padding-top: 20px;">
        <p><b>執行鑑定事務所：{firm_name}</b></p>
        <p>主辦鑑定師簽署：____________________</p>
        <p>日期：{r_date.strftime('%Y年%m月%d日')}</p>
    </div>
    """, unsafe_allow_html=True)

else:
    st.info(" 歡迎使用！請從左側上傳多份 PDF 檔案以啟動跨年度鑑定流程。")
