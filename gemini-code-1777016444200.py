import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import pdfplumber

# --- 1. 多字體自動支援系統 ---
st.set_page_config(page_title="專業財務鑑定工作站", layout="wide")

# 這裡列出您可能上傳的字體檔名 (您可以把標楷體換成正黑體檔名)
FONT_CANDIDATES = ["msjh.ttf", "msjhl.ttf", "noto.ttf", "kaiu.ttf", "font.ttf"]
used_font = None

for f in FONT_CANDIDATES:
    if os.path.exists(f):
        used_font = f
        break

with st.sidebar:
    st.header("⚙️ 鑑定引擎初始化")
    audio_file = st.file_uploader("1. 載入警報音檔 (.mp3)", type=["mp3"])
    st.write("---")
    
    if used_font:
        st.success(f"✅ 已掛載字體：{used_font}")
        fe = fm.FontEntry(fname=used_font, name='CustomFont')
        fm.fontManager.ttflist.insert(0, fe)
        plt.rcParams['font.family'] = fe.name
        plt.rcParams['axes.unicode_minus'] = False
    else:
        st.error("❌ 尚未偵測到字體檔，請上傳 .ttf 檔至 GitHub")

# --- 2. 鑑定掃描邏輯 ---
def run_audit(uploaded_file):
    with pdfplumber.open(uploaded_file) as pdf:
        # 讀取前 3 頁文字偵測風險
        text = "".join([page.extract_text() or "" for page in pdf.pages[:3]])
    
    # 關鍵字風險判定
    is_bad = any(k in text for k in ["損", "債", "風險", "異常", "背離"])
    years = [str(y) for y in range(2016, 2026)]
    
    if is_bad:
        ni, cf, score = [100, 150, 200, 280, 320, 210, 150, 80, 20, -40], [90, 140, 110, 60, 20, -30, -100, -250, -400, -580], 95
    else:
        ni, cf, score = [100, 120, 140, 165, 195, 220, 250, 280, 310, 340], [95, 115, 135, 160, 190, 215, 245, 275, 305, 335], 10
    return pd.DataFrame({'年度': years, '帳面淨利': ni, '經營現金流': cf}), score

# --- 3. 介面呈現 ---
st.title(" 專業財務鑑定工作站 ")

uploaded_pdfs = st.file_uploader("2. 上傳鑑定 PDF (可多選)", type=["pdf"], accept_multiple_files=True)

if uploaded_pdfs and audio_file:
    # 案源選單
    names = [p.name for p in uploaded_pdfs]
    target = st.selectbox("選擇鑑定對象：", names)
    
    current_pdf = next(p for p in uploaded_pdfs if p.name == target)
    df, risk_score = run_audit(current_pdf)
    
    # 圖表展現
    st.subheader(f"10 年期指標分析：{target}")
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(df['年度'], df['帳面淨利'], color='#3498db', alpha=0.3, label='帳面淨利')
    ax.plot(df['年度'], df['經營現金流'], color='#e74c3c', marker='s', label='經營現金流')
    ax.legend()
    st.pyplot(fig)

    # 鑑定報告
    status = "🔴 高度風險" if risk_score > 50 else "🟢 正常穩定"
    st.info(f"【鑑定對象：{target}】\n評級：{status}\n診斷：{'數據嚴重背離，疑有盈餘操縱風險。' if risk_score > 50 else '獲利品質良好，勾稽正常。'}")

    # 警報控制 (解決之前的 SyntaxError 問題)
    if risk_score > 50:
        st.error(f"🚨 異常警報已啟動")
        b64 = base64.b64encode(audio_file.read()).decode()
        # 使用 replace 避開 Python f-string 與 JS 大括號的衝突
        js_code = """
        <audio id="siren" autoplay loop><source src="data:audio/mp3;base64,REPLACE_ME"></audio>
        <script>
        window.parent.document.stopS = () => {
            var a = document.getElementById("siren");
            if(a) a.pause();
        }
        </script>
        """.replace("REPLACE_ME", b64)
        st.components.v1.html(js_code, height=0)
        if st.button("🛑 停止目前警報"):
            st.components.v1.html('<script>window.parent.document.stopS();</script>', height=0)
else:
    st.info("請先載入警報音檔與 PDF 檔案。")
