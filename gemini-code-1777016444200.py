import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import pdfplumber
import requests
from fpdf import FPDF
from datetime import datetime

# --- 1. 核心字體修復（徹底解決亂碼） ---
st.set_page_config(page_title="專業財務鑑定系統", layout="wide")

@st.cache_data
def get_font():
    # 下載 Google 思源黑體，這是解決 PDF 與網頁亂碼的唯一解法
    url = "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/TraditionalChinese/NotoSansCJKtc-Regular.otf"
    path = "font_fixed.otf"
    if not os.path.exists(path):
        r = requests.get(url)
        with open(path, "wb") as f:
            f.write(r.content)
    return path

f_path = get_font()
fe = fm.FontEntry(fname=f_path, name='StandardFont')
fm.fontManager.ttflist.insert(0, fe)
plt.rcParams['font.family'] = fe.name
plt.rcParams['axes.unicode_minus'] = False

# --- 2. 專業事務所報告 PDF 工廠 ---
def generate_pro_report(firm_name, auditor_name, selected_file, conclusion, score):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('Chinese', '', f_path)
    
    # --- 頁首：事務所抬頭 ---
    pdf.set_font('Chinese', '', 20)
    pdf.set_text_color(0, 51, 102) # 深藍色，展現權威感
    pdf.cell(0, 15, txt=firm_name, ln=True, align='C')
    pdf.set_font('Chinese', '', 14)
    pdf.cell(0, 10, txt="AI 智慧財務鑑定報告書", ln=True, align='C')
    pdf.line(10, 35, 200, 35) # 專業橫線
    pdf.ln(10)
    
    # --- 基本資訊 ---
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Chinese', '', 11)
    pdf.cell(100, 10, txt=f"報告編號：AUD-{datetime.now().strftime('%Y%m%d%H%M')}")
    pdf.cell(0, 10, txt=f"日期：{datetime.now().strftime('%Y/%m/%d')}", ln=True, align='R')
    pdf.cell(0, 10, txt=f"鑑定對象：{selected_file}", ln=True)
    pdf.cell(0, 10, txt=f"鑑定會計師：{auditor_name}", ln=True)
    pdf.ln(5)
    
    # --- 鑑定結論框 ---
    pdf.set_fill_color(240, 240, 240) # 灰色底色
    pdf.set_font('Chinese', '', 13)
    pdf.cell(0, 10, txt="【一、鑑定結論】", ln=True, fill=True)
    pdf.set_font('Chinese', '', 12)
    pdf.multi_cell(0, 10, txt=conclusion)
    pdf.ln(5)
    
    # --- 指標評分 ---
    pdf.set_font('Chinese', '', 13)
    pdf.cell(0, 10, txt="【二、風險評級數據】", ln=True, fill=True)
    pdf.set_font('Chinese', '', 12)
    risk_level = "高風險" if score > 50 else "穩定"
    pdf.cell(0, 10, txt=f"綜合風險評估：{risk_level} (評分：{score} / 100)", ln=True)
    pdf.ln(20)
    
    # --- 頁尾：簽章區 ---
    pdf.cell(130) # 移到右側
    pdf.cell(0, 10, txt=firm_name, ln=True, align='C')
    pdf.cell(130)
    pdf.cell(0, 10, txt="(此報告由系統電子簽章發布)", ln=True, align='C')
    
    return pdf.output()

# --- 3. 介面與邏輯 ---
st.title("⚖️ 專業鑑定報告生成系統")

with st.sidebar:
    st.header("📝 報告抬頭設定")
    user_firm = st.text_input("事務所名稱", "德勤會計師事務所 (範例)")
    user_auditor = st.text_input("負責人/會計師", "陳大文 鑑定師")
    st.info("設定將自動套用於 PDF 報告標題與簽章處。")

uploaded_files = st.file_uploader("📂 上傳待鑑定財報 PDF", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    # 選擇目前要處理的檔案
    names = [f.name for f in uploaded_files]
    target_name = st.selectbox("請選擇欲產生報告之檔案：", names)
    target_file = next(f for f in uploaded_files if f.name == target_name)
    
    # 模擬鑑定引擎 (實際可加入您的 pdfplumber 邏輯)
    risk_val = 85 # 假設為高風險
    conclusion_text = f"經本系統對「{target_name}」之財務報表進行勾稽比對，發現其經營活動現金流量長期顯著低於帳面淨利，且文本分析顯示具備顯著風險訊號，建議進行實地查核以規避虛增盈餘之風險。"
    
    # 圖表呈現
    st.subheader("📊 財務數據勾稽分析圖")
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot([2023, 2024, 2025], [100, 150, 30], marker='o', label="經營現金流")
    ax.bar([2023, 2024, 2025], [110, 160, 200], alpha=0.3, label="帳面淨利")
    ax.legend()
    st.pyplot(fig)
    
    # 下載區
    st.divider()
    st.markdown(f"### 📄 產生正式鑑定報告 ({user_firm})")
    
    try:
        report_pdf = generate_pro_report(user_firm, user_auditor, target_name, conclusion_text, risk_val)
        
        st.download_button(
            label=f"📥 下載正式 PDF 鑑定報告",
            data=report_pdf,
            file_name=f"{user_firm}_鑑定報告_{target_name}.pdf",
            mime="application/pdf"
        )
        st.success("PDF 報告已生成，且已套用專業排版與事務所字樣。")
    except Exception as e:
        st.error(f"報告生成錯誤：{e}")

else:
    st.info("請上傳 PDF 財報以開始生成專業報告。")
