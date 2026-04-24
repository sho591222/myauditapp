import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import pdfplumber
import requests

# --- 1. 自動下載字體解決亂碼 ---
@st.cache_data
def get_font():
    # 從網路上下載思源黑體，這樣就不會亂碼了
    url = "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/TraditionalChinese/NotoSansCJKtc-Regular.otf"
    path = "font.otf"
    if not os.path.exists(path):
        r = requests.get(url)
        with open(path, "wb") as f:
            f.write(r.content)
    return path

# 執行字體掛載
font_p = get_font()
fe = fm.FontEntry(fname=font_p, name='MyFont')
fm.fontManager.ttflist.insert(0, fe)
plt.rcParams['font.family'] = fe.name
plt.rcParams['axes.unicode_minus'] = False

# --- 2. 介面呈現 ---
st.title(" 專業財務鑑定工作站 ")

with st.sidebar:
    st.header(" 設定")
    # 修正這裡的拼字：是 .success 不是 .succes
    st.success(" 中文字體已自動修復")
    audio_file = st.file_uploader("1. 載入警報音檔 (.mp3)", type=["mp3"])

uploaded_pdf = st.file_uploader("2. 上傳 PDF 報表", type=["pdf"])

if uploaded_pdf and audio_file:
    # 這裡放您的鑑定邏輯...
    st.write(f"正在鑑定：{uploaded_pdf.name}")
    
    # 模擬數據圖表 (這時中文就不會亂碼了)
    fig, ax = plt.subplots()
    ax.set_title("財務數據勾稽分析")
    ax.plot([1, 2, 3], [10, 20, 15], label="經營現金流")
    ax.legend()
    st.pyplot(fig)
else:
    st.info("請上傳音檔與 PDF 開始鑑定。")
