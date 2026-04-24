import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from fpdf import FPDF
import io
import os
import pdfplumber

# --- 1. 介面與風格優化 ---
st.set_page_config(page_title="專業財務鑑定工作站 | 旗艦版", layout="wide")
st.markdown("""
    <style>
    .report-card { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-left: 8px solid #1e3799; line-height: 1.8; }
    .stButton>button { border-radius: 20px; background: #c0392b !important; color: white !important; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 細緻化：PDF 深度掃描 ---
def sophisticated_pdf_scan(uploaded_file):
    with pdfplumber.open(uploaded_file) as pdf:
        text = "".join([page.extract_text() or "" for page in pdf.pages[:3]])
    
    # 搜尋敏感字眼
    risk_keywords = ["減損", "損失", "負債", "流動性", "不確定", "背離"]
    found_risks = [k for k in risk_keywords if k in text]
    
    years = [str(y) for y in range(2015, 2025)]
    # 若偵測到敏感字，模擬數據會顯現風險
    if found_risks:
        ni = [100, 120, 150, 180, 200, 180, 150, 100, 40, -20]
        cf = [90, 110, 130, 100, 80, 30, 10, -60, -180, -350]
        score = 88
    else:
        ni = [100, 110, 125, 140, 160, 180, 200, 220, 245, 270]
        cf = [95, 105, 120, 135, 150, 175, 195, 215, 235, 260]
        score = 15
    return pd.DataFrame({'年度': years, '帳面淨利': ni, '經營現金流': cf}), score, found_risks

# --- 3. 細緻化：圖表標記功能 ---
def plot_financial_chart(df, title, font_p):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(df['年度'], df['帳面淨利'], color='#3498db', alpha=0.3, label='帳面淨利')
    ax.plot(df['年度'], df['帳面淨利'], color='#2980b9', marker='o', linewidth=2)
    ax.plot(df['年度'], df['經營現金流'], color='#e74c3c', marker='s', linewidth=3, label='經營現金流')
    
    if font_p:
        ax.set_title(f"長週期趨勢分析: {title}", fontproperties=font_p, fontsize=15)
        ax.set_ylabel("金額 (萬元)", fontproperties=font_p)
        ax.legend(prop=font_p)
    else:
        ax.set_title(f"Financial Trend: {title}")
        ax.legend()
    return fig

# --- 4. 軟體主介面 ---
st.title("⚖️ 專業財務鑑定工作站 v12.9")

with st.sidebar:
    st.header("⚙️ 引擎設定")
    audio_file = st.file_uploader("1. 載入警報音檔 (.mp3)", type=["mp3"])
    st.write("---")
    font_exists = os.path.exists("font.ttf")
    if font_exists:
        st.success("✅ 字體已載入：PDF 功能正常")
        my_font = fm.FontProperties(fname="font.ttf")
    else:
        st.error("❌ 缺少 font.ttf：將出現亂碼")
        my_font = None

uploaded_files = st.file_uploader("2. 上傳 PDF 鑑定對象 (支援多選)", type=["pdf"], accept_multiple_files=True)

if uploaded_files and audio_file:
    file_names = [f.name for f in uploaded_files]
    selected = st.selectbox("🎯 切換個案：", file_names)
    
    # 取得當前檔案並分析
    target_file = next(f for f in uploaded_files if f.name == selected)
    df_data, score, risks = sophisticated_pdf_scan(target_file)
    
    # 顯示圖表
    st.pyplot(plot_financial_chart(df_data, selected, my_font))
    
    # 顯示診斷報告
    risk_label = "🔴 高度風險 (背離異常)" if score > 50 else "🟢 正常穩定"
    risk_msg = f"偵測到關鍵字：{', '.join(risks)}" if risks else "未見明顯負面詞彙"
    
    summary = f"""
    【個案鑑定：{selected}】
    一、 質量評級：{risk_label}
    二、 深度診斷：
    1. 盈餘勾稽：{'經營現金流嚴重萎縮，帳面利潤疑有水分。' if score > 50 else '現金轉化效率良好，獲利結構扎實。'}
    2. 文本特徵：{risk_msg}。
    三、 專家建議：
    {'建議啟動專案實地查核。' if score > 50 else '維持一般監控。'}
    """
    st.markdown(f'<div class="report-card">{summary.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)

    # 警報修復版 (解決語法錯誤)
    if score > 50:
        st.error(f"🚨 異常警報：{selected}")
        b64_audio = base64.b64encode(audio_file.read()).decode()
        # 這裡改用格式化避開 JS 大括號衝突
        js_code = """
        <audio id="siren" autoplay loop><source src="data:audio/mp3;base64,{0}"></audio>
        <script>
        window.parent.document.stopSiren = function() {{
            var a = document.getElementById("siren");
            if(a) a.pause();
        }}
        </script>
        """.format(b64_audio)
        st.components.v1.html(js_code, height=0)
        
        if st.button("🛑 停止目前個案警報"):
            st.components.v1.html('<script>window.parent.document.stopSiren();</script>', height=0)

else:
    st.info("👋 您好！請依序載入音檔與 PDF 財報。")
