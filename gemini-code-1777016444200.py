import streamlit as st
import sqlite3
import hashlib
import pandas as pd


# =========================
# DATABASE INIT
# =========================

conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT,
    role TEXT
)
""")

conn.commit()


# =========================
# PASSWORD HASH
# =========================

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


# =========================
# REGISTER
# =========================

def register_user(username, password, role):

    try:
        c.execute(
            "INSERT INTO users VALUES (?, ?, ?)",
            (username, hash_pw(password), role)
        )
        conn.commit()
        return True

    except:
        return False


# =========================
# LOGIN
# =========================

def login_user(username, password):

    c.execute("SELECT password, role FROM users WHERE username=?", (username,))
    result = c.fetchone()

    if result:

        db_pw, role = result

        if db_pw == hash_pw(password):
            return True, role

    return False, None


# =========================
# UI START
# =========================

st.title("玄武會計師事務所｜系統 v24（登入+註冊版）")


# =========================
# SIDEBAR AUTH MODE
# =========================

mode = st.sidebar.radio("選擇功能", ["登入", "註冊"])


# =========================
# REGISTER PAGE
# =========================

if mode == "註冊":

    st.subheader("建立帳號")

    new_user = st.text_input("帳號")
    new_pw = st.text_input("密碼", type="password")
    role = st.selectbox("角色", ["公司", "事務所"])

    if st.button("註冊"):

        if register_user(new_user, new_pw, role):
            st.success("註冊成功")
        else:
            st.error("帳號已存在")


# =========================
# LOGIN PAGE
# =========================

if mode == "登入":

    st.subheader("登入系統")

    username = st.text_input("帳號")
    password = st.text_input("密碼", type="password")

    if st.button("登入"):

        ok, role = login_user(username, password)

        if ok:

            st.session_state["login"] = True
            st.session_state["role"] = role
            st.success(f"登入成功：{role}")

        else:
            st.error("帳號或密碼錯誤")


# =========================
# AFTER LOGIN (你的原系統入口)
# =========================

if "login" in st.session_state and st.session_state["login"]:

    st.divider()

    st.subheader("財報分析系統已啟動")

    st.write("目前角色：", st.session_state["role"])


    # 這裡之後你可以直接接：
    # 👉 PDF分析系統
    # 👉 圖表
    # 👉 查核引擎
