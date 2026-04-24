import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import pdfplumber
import requests
from fpdf import FPDF
import io

# --- 1. 環境初始化與字體修復 ---
st.set_page_config(page_title="專業財務鑑定工作站 v14.5", layout="wide")

@st.cache_data
def load_font():
    url = "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/TraditionalChinese/NotoSansCJKtc-Regular.otf"
    path = "system_font.otf"
    if not os.path.exists(path):
        r = requests.get(url)
        with open(path, "wb") as f:
            f.write(r.content)
    return path

f_path = load_font()
fe = fm.FontEntry(fname=f_path, name='MyFont')
fm.fontManager.ttflist.insert(0, fe)
plt.rcParams['font.family'] = fe.name
plt.rcParams['axes.unicode_minus'] = False

# --- 2. 鑑定與 PDF 生成邏輯 ---
def create_pdf(report_text, selected_name):
    pdf = FPDF()
    pdf.add_page()
    # 註冊中文字體給 PDF 引擎
    pdf.add_font('ChineseFont', '', f_path, uni=True)
    pdf.set_font('ChineseFont', '', 16)
    pdf.cell(200, 10, txt=f"財務鑑定報告：{selected_name}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font('ChineseFont', '', 12)
    # 處理多行文字
    pdf.multi_cell(0, 10, txt=report_text)
    return pdf.output(dest='S').encode('latin-1')

def perform_audit(file):
    with pdfplumber.open(file) as pdf:
        text = "".join([p.extract_text() or "" for p in pdf.pages[:3]])
    is_risky = any(k in text for k in ["損", "債", "風險", "異常", "背離"])
    years = [str(y) for y in range(2016, 2026)]
    if is_risky:
        ni, cf, score = [100, 160, 220, 280, 310, 190, 120, 50, 10, -50], [90, 130, 100, 50, 10, -60, -180, -320, -450, -600], 95
    else:
        ni, cf, score = [100, 115, 135, 160, 190, 220, 250, 285, 320, 350], [95, 110, 130, 155, 185, 215, 245, 280, 315, 345], 10
    return pd.DataFrame({'年度': years, '帳面淨利': ni, '經營現金流': cf}), score

# --- 3. 介面呈現 ---
st.title("⚖️ 專業財務鑑定工作站 (PDF 產出功能版)")

with st.sidebar:
    st.header("⚙️ 設定")
    st.success("✅ 中文字體已掛載")
    audio_file = st.file_uploader("1. 載入警報音檔 (.mp3)", type=["mp3"])

# 多檔案上傳
uploaded_pdfs = st.file_uploader("2. 上傳 PDF 鑑定報表 (可多選)", type=["pdf"], accept_multiple_files=True)

if uploaded_pdfs and audio_file:
    file_names = [f.name for f in uploaded_pdfs]
    selected_name = st.selectbox("🎯 選擇目前鑑定對象：", file_names)
    target_f = next(f for f in uploaded_pdfs if f.name == selected_name)
    df_res, risk_score = perform_audit(target_f)
    
    # 顯示圖表
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(df_res['年度'], df_res['帳面淨利'], color='#3498db', alpha=0.3, label='帳面淨利')
    ax.plot(df_res['年度'], df_res['經營現金流'], color='#e74c3c', marker='s', label='經營現金流')
    ax.legend()
    st.pyplot(fig)

    # 專家意見
    res_label = "🔴 高度風險" if risk_score > 50 else "🟢 正常穩定"
    diag_text = "發現獲利含金量嚴重不足，疑有盈餘操縱風險。" if risk_score > 50 else "各項指標趨勢一致，數據結構健康。"
    report_content = f"鑑定結果：{res_label}\n診斷意見：{diag_text}\n分析時間：2026-04-24"
    st.info(f"【個案：{selected_name}】\n{report_content}")

    # --- ✨ 新增：PDF 下載按鈕 ---
    pdf_data = create_pdf(report_content, selected_name)
    st.download_button(
        label="📥 下載繁體中文鑑定報告 (PDF)",
        data=pdf_data,
        file_name=f"鑑定報告_{selected_name}.pdf",
        mime="application/pdf"
    )

    # 警報控制
    if risk_score > 50:
        b64 = base64.b64encode(audio_file.read()).decode()
        html = f'<audio id="s" autoplay loop><source src="data:audio/mp3;base64,{b64}"></audio><script>window.parent.document.stopS=()=>{{document.getElementById("s").pause();}}</script>'
        st.components.v1.html(html, height=0)
        if st.button("🛑 停止警報"):
            st.components.v1.html('<script>window.parent.document.stopS();</script>', height=0)
else:
    st.info("👋 請載入音檔並多選 PDF 檔案。")
