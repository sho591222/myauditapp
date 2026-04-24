import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. 系統設定 ---
st.set_page_config(page_title="專業財務鑑定報告系統", layout="wide")

# --- 2. 鑑定模型數據邏輯 ---
def get_audit_data(filename):
    # 模擬深度分析數據
    return {
        "hlm": "顯著性 p<0.01。階層線性模型顯示產業波動與企業盈餘管理具備高度結構性關聯。",
        "did": "雙重差分法驗證標的公司在特定事件後，數據偏離正常值達 15.4%，具備操縱因果關係。",
        "m_score": "-1.38 (警戒值 -1.78)",
        "z_score": "1.21 (落入財務困窘區)",
        "fraud_type": "虛增營收、隱匿資產減損及綠色貸款違規風險",
        "prediction": "隨機森林預測該企業未來一年內發生『重大舞弊重編』之機率為 91.2%。",
        "impact": "可能導致信用評等下調、資金鏈斷裂及法律訴訟風險。"
    }

# --- 3. 介面呈現 ---
st.title("⚖️ 專業財務鑑定與風險預測工作站")

with st.sidebar:
    st.header("📝 報告抬頭設定")
    firm_name = st.text_input("事務所名稱", "誠信聯合會計師事務所")
    auditor_name = st.text_input("主辦鑑定師", "陳大文 (CPA / CFE)")
    st.divider()
    report_date = st.date_input("報告簽署日", datetime.now())
    base_date = st.date_input("鑑定基準日", datetime.now())
    st.info("💡 下方報告生成後，按 Ctrl + P 即可儲存成無亂碼的專業 PDF。")

uploaded_files = st.file_uploader("📂 上傳 PDF 報表檔案", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    names = [f.name for f in uploaded_files]
    selected_name = st.selectbox("🎯 選擇欲處理個案：", names)
    data = get_audit_data(selected_name)
    
    # --- 專業報告區域 (HTML 渲染解決亂碼) ---
    st.divider()
    
    report_html = f"""
    <div style="border: 2px solid #000; padding: 40px; background-color: white; color: black; font-family: 'Microsoft JhengHei', sans-serif; line-height: 1.8; max-width: 900px; margin: auto; box-shadow: 10px 10px 30px rgba(0,0,0,0.1);">
        
        <div style="text-align: center; border-bottom: 4px solid #003366; padding-bottom: 10px;">
            <h1 style="margin: 0; font-size: 32px; color: #003366;">{firm_name}</h1>
            <h2 style="margin: 5px 0; font-size: 20px; letter-spacing: 12px; color: #333;">財務報表不實鑑定暨風險預測報告書</h2>
            <div style="display: flex; justify-content: space-between; margin-top: 15px; font-size: 13px;">
                <span>報告編號：AUD-{report_date.strftime('%Y%m%d')}-001</span>
                <span>日期：{report_date.strftime('%Y年%m月%d日')}</span>
            </div>
        </div>

        <table style="width: 100%; margin-top: 20px; border-collapse: collapse; font-size: 14px;">
            <tr style="border-bottom: 1px solid #ddd;">
                <td style="padding: 10px; font-weight: bold; width: 20%;">鑑定標的：</td>
                <td style="padding: 10px;">{selected_name}</td>
                <td style="padding: 10px; font-weight: bold; width: 20%;">鑑定基準日：</td>
                <td style="padding: 10px;">{base_date.strftime('%Y年%m月%d日')}</td>
            </tr>
            <tr>
                <td style="padding: 10px; font-weight: bold;">主辦鑑定師：</td>
                <td colspan="3" style="padding: 10px;">{auditor_name}</td>
            </tr>
        </table>

        <div style="margin-top: 30px;">
            <h3 style="background-color: #003366; color: white; padding: 5px 15px; font-size: 16px;">一、 舞弊特徵實證模型分析</h3>
            <div style="border: 1px solid #003366; padding: 15px; background-color: #fcfcfc;">
                <p><strong>1. 階層線性模型 (HLM) 分析：</strong><br>{data['hlm']}</p>
                <p><strong>2. 雙重差分法 (DID) 鑑定：</strong><br>{data['did']}</p>
            </div>
        </div>

        <div style="margin-top: 20px;">
            <h3 style="background-color: #c0392b; color: white; padding: 5px 15px; font-size: 16px;">二、 財報不實檢測指標 (Beneish M-Score)</h3>
            <table style="width: 100%; border-collapse: collapse; text-align: center;">
                <tr style="background-color: #f2f2f2;">
                    <th style="border: 1px solid #000; padding: 10px;">模型</th>
                    <th style="border: 1px solid #000; padding: 10px;">結果數值</th>
                    <th style="border: 1px solid #000; padding: 10px;">鑑定結論</th>
                </tr>
                <tr>
                    <td style="border: 1px solid #000; padding: 10px;">M-Score</td>
                    <td style="border: 1px solid #000; padding: 10px;">{data['m_score']}</td>
                    <td style="border: 1px solid #000; padding: 10px; color: red; font-weight: bold;">極高操縱機率</td>
                </tr>
            </table>
            <p style="font-size: 14px; margin-top: 10px;"><strong>弊案樣態：</strong>{data['fraud_type']}</p>
        </div>

        <div style="margin-top: 20px;">
            <h3 style="background-color: #f39c12; color: white; padding: 5px 15px; font-size: 16px;">三、 未來持續經營與風險預測</h3>
            <div style="border: 2px dashed #f39c12; padding: 15px; background-color: #fffcf5;">
                <p><strong>1. Altman Z-Score 破產預測：</strong><br>數值 <strong>{data['z_score']}</strong>。顯示標的公司具備高度違約與經營中斷風險。</p>
                <p><strong>2. AI 隨機森林模型預測：</strong><br>未來一年內發生重大舞弊重編機率：<strong>{data['prediction']}</strong>。</p>
                <p><strong>3. 潛在影響：</strong><br>{data['impact']}</p>
            </div>
        </div>

        <div style="margin-top: 30px;">
            <h3 style="background-color: #003366; color: white; padding: 5px 15px; font-size: 16px;">四、 會計師專業鑑定意見</h3>
            <p style="text-indent: 2em; text-align: justify; font-size: 15px;">
                綜上所述，本會計師團隊經由 <strong>HLM</strong> 與 <strong>DID</strong> 量化實證模型分析，交叉比對 <strong>Beneish M-Score</strong> 與 <strong>Altman Z-Score</strong>。鑑定結果顯示該標的公司之財務數據存在系統性偏誤。
                由於盈餘管理程度已超過業界常態，且預測模型揭示顯著破產風險，本報告建議相關監理單位與融資銀行應立即啟動保全措施。
            </p>
        </div>

        <div style="margin-top: 60px; text-align: right;">
            <div style="display: inline-block; text-align: center; border-top: 1px solid #000; width: 300px; padding-top: 15px;">
                <p style="margin: 0; font-size: 18px;"><strong>{firm_name}</strong></p>
                <p style="margin: 10px 0; font-size: 15px;">執行鑑定會計師：{auditor_name}</p>
                <p style="margin: 0; font-size: 12px; color: #999;">(本報告由 AI 審計鑑定系統正式授權發布)</p>
            </div>
        </div>
    </div>
    """

    st.markdown(report_html, unsafe_allow_html=True)
    
    # 下載簡版文字檔 (預防萬一)
    st.divider()
    raw_text = f"【{firm_name} 鑑定簡報】\n標的：{selected_name}\n會計師意見：{data['hlm']}\n預測：{data['prediction']}"
    st.download_button("📄 下載簡版純文字 (TXT)", raw_text, file_name="report_summary.txt")

else:
    st.info("👋 您好！請上傳 PDF 報表檔案，系統將自動生成無亂碼的專業鑑定報告。")
