import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. 基本設定 ---
st.set_page_config(page_title="專業財務鑑定系統", layout="wide")

# --- 2. 模擬鑑定邏輯 ---
def run_audit(filename):
    # 這裡可以放您的 pdfplumber 邏輯
    # 暫時用模擬數據
    score = 85
    conclusion = f"經本系統鑑定，個案「{filename}」之現金流量與盈餘品質存在嚴重背離。建議詳查期末調整分錄。"
    return score, conclusion

# --- 3. 介面呈現 ---
st.title("⚖️ 專業財務鑑定報告生成系統")

# 側邊欄設定
with st.sidebar:
    st.header("📝 報告抬頭設定")
    firm_name = st.text_input("事務所名稱", "德勤會計師事務所")
    auditor_name = st.text_input("負責會計師", "陳大文")
    report_date = st.date_input("報告日期", datetime.now())
    st.divider()
    st.info("💡 提示：鑑定完成後，直接對著下方報告按右鍵『列印』並選擇『另存為 PDF』即可產出完美文件。")

# 檔案上傳 (多選)
uploaded_files = st.file_uploader("📂 上傳 PDF 財報", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    # 選擇檔案
    file_names = [f.name for f in uploaded_files]
    selected_name = st.selectbox("🎯 選擇鑑定個案：", file_names)
    
    # 執行鑑定
    risk_score, risk_desc = run_audit(selected_name)
    
    # --- 專業報告呈現區 (HTML/CSS 模擬正式文件) ---
    st.divider()
    
    # 使用 HTML 建立一個像正式信紙的框框
    report_html = f"""
    <div style="border: 2px solid #333; padding: 40px; background-color: white; color: black; font-family: 'Microsoft JhengHei', sans-serif; line-height: 1.6;">
        <div style="text-align: center;">
            <h1 style="margin: 0; color: #003366;">{firm_name}</h1>
            <p style="letter-spacing: 5px; font-weight: bold;">AI 智慧財務鑑定報告書</p>
            <hr style="border: 1px solid #003366;">
        </div>
        
        <table style="width: 100%; margin-top: 20px; font-size: 14px;">
            <tr>
                <td><strong>報告編號：</strong> AUD-{datetime.now().strftime('%Y%m%d%H%M')}</td>
                <td style="text-align: right;"><strong>日期：</strong> {report_date}</td>
            </tr>
            <tr>
                <td><strong>鑑定對象：</strong> {selected_name}</td>
                <td style="text-align: right;"><strong>負責人：</strong> {auditor_name}</td>
            </tr>
        </table>
        
        <div style="margin-top: 30px; background-color: #f9f9f9; padding: 15px; border-left: 5px solid #003366;">
            <h3 style="margin-top: 0;">一、 鑑定結論</h3>
            <p>{risk_desc}</p>
        </div>
        
        <div style="margin-top: 20px;">
            <h3>二、 風險評估結果</h3>
            <p>綜合風險評分：<strong>{risk_score} / 100</strong></p>
            <p>風險等級：<span style="color: red; font-weight: bold;">{'高度風險' if risk_score > 50 else '正常穩定'}</span></p>
        </div>
        
        <div style="margin-top: 50px; text-align: right;">
            <p style="margin-bottom: 50px;">鑑定人簽章：____________________</p>
            <p><strong>{firm_name}</strong></p>
            <p style="font-size: 12px; color: #666;">（本報告由系統自動生成，具備電子存證效力）</p>
        </div>
    </div>
    """
    
    # 在網頁上顯示這份報告
    st.markdown(report_html, unsafe_allow_html=True)
    
    # 提供一個簡單的 TXT 下載 (純文字，絕對不會亂碼)
    raw_text = f"【{firm_name} 鑑定報告】\n對象：{selected_name}\n結論：{risk_desc}\n評分：{risk_score}"
    st.download_button("📄 下載簡版文字檔 (TXT)", data=raw_text, file_name="report.txt")

else:
    st.info("👋 您好！請上傳 PDF 檔案，我將為您生成正式的事務所鑑定報告。")
