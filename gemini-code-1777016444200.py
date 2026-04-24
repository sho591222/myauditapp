import streamlit as st
import sqlite3
import hashlib
import random
import string


# =========================
# DATABASE
# =========================

conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    email TEXT PRIMARY KEY,
    password TEXT
)
""")

conn.commit()


# =========================
# HASH
# =========================

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


# =========================
# EMAIL FORMAT CHECK
# =========================

def valid_email(email):
    return "@" in email and "." in email


# =========================
# REGISTER
# =========================

def register(email, pw):

    if not valid_email(email):
        return "email_error"

    try:
        c.execute(
            "INSERT INTO users VALUES (?,?)",
            (email, hash_pw(pw))
        )
        conn.commit()
        return "ok"

    except:
        return "exists"


# =========================
# LOGIN
# =========================

def login(email, pw):

    c.execute("SELECT password FROM users WHERE email=?", (email,))
    d = c.fetchone()

    if d and d[0] == hash_pw(pw):
        return True

    return False


# =========================
# RESET PASSWORD (SIMULATION)
# =========================

def reset_password(email):

    c.execute("SELECT email FROM users WHERE email=?", (email,))
    d = c.fetchone()

    if not d:
        return False, None

    new_pw = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

    c.execute(
        "UPDATE users SET password=? WHERE email=?",
        (hash_pw(new_pw), email)
    )
    conn.commit()

    return True, new_pw


# =========================
# SESSION
# =========================

if "auth" not in st.session_state:
    st.session_state.auth = False

if "page" not in st.session_state:
    st.session_state.page = "login"


# =========================
# UI
# =========================

st.title("玄武會計師事務所｜AI 財報系統 v32（Email SaaS）")


# =========================
# NAV
# =========================

st.sidebar.title("帳號系統")

if st.sidebar.button("註冊"):
    st.session_state.page = "register"

if st.sidebar.button("登入"):
    st.session_state.page = "login"

if st.sidebar.button("忘記密碼"):
    st.session_state.page = "reset"


# =========================
# REGISTER PAGE
# =========================

if st.session_state.page == "register":

    st.subheader("註冊（Email帳號）")

    email = st.text_input("Email")
    pw = st.text_input("密碼", type="password")

    if st.button("建立帳號"):

        result = register(email, pw)

        if result == "ok":
            st.success("註冊成功，請登入")

        elif result == "exists":
            st.error("Email 已存在")

        else:
            st.error("Email 格式錯誤")


# =========================
# LOGIN PAGE
# =========================

if st.session_state.page == "login":

    st.subheader("登入")

    email = st.text_input("Email")
    pw = st.text_input("密碼", type="password")

    if st.button("登入"):

        if login(email, pw):

            st.session_state.auth = True
            st.session_state.email = email

            st.success("登入成功")

        else:
            st.error("帳號或密碼錯誤")


# =========================
# RESET PASSWORD PAGE
# =========================

if st.session_state.page == "reset":

    st.subheader("忘記密碼")

    email = st.text_input("輸入Email")

    if st.button("寄送重設密碼"):

        ok, new_pw = reset_password(email)

        if ok:

            st.success("已重設密碼（模擬Email寄送）")
            st.info(f"新密碼：{new_pw}")

        else:
            st.error("Email不存在")


# =========================
# MAIN SYSTEM LOCK
# =========================

if not st.session_state.auth:

    st.warning("請先登入（Email帳號）")
    st.stop()


# =========================
# MAIN SYSTEM
# =========================

st.divider()

st.subheader("財報分析系統")

st.write("登入帳號：", st.session_state.email)


# =========================
# PDF UPLOAD (placeholder for next stage)
# =========================

st.file_uploader("上傳財報PDF", type="pdf", accept_multiple_files=True)


st.info("登入成功後才可進行財報分析（下一版會接上完整查核引擎）")
