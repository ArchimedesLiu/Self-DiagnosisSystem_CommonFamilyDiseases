import streamlit as st
import pymysql
import time
import hashlib
from PIL import Image
from loguru import logger
logger.info("This is log info!")
logger.warning("This is log warn!")
logger.error("This is log error!")
logger.debug("This is log debug!")
# Convert Pass into hash format
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()


# 连接MySQL数据库
def create_conn():
    return pymysql.connect(
        host='localhost',  # 主机名（或IP地址）
        port=3306,  # 端口号，默认为3306
        user='root',  # 用户名
        password='root',  # 密码
        database='Med',  # 数据库名
    )


# 创建用户表和个人信息表
def create_tables():
    conn = create_conn()
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS users (username VARCHAR(255) PRIMARY KEY, password VARCHAR(255), phone_number VARCHAR(20))")
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS user_info (username VARCHAR(255) PRIMARY KEY, gender VARCHAR(10), age INT, medical_history TEXT, medication TEXT, FOREIGN KEY (username) REFERENCES users(username))")
    conn.commit()
    conn.close()


# 注册用户
def register(username, password, phone_number):
    # 如果未有输入则返回false
    conn = create_conn()
    cursor = conn.cursor()
    # 如果用户已存在则提示用户已存在，请重新输
    cursor.execute("SELECT * FROM users WHERE username = %s", (username))
    if cursor.fetchone() is not None:
        conn.commit()
        conn.close()
        return False
    else:
        hash_password = make_hashes(password)
        cursor.execute("INSERT INTO users (username, password, phone_number) VALUES (%s, %s, %s)",
                       (username, hash_password, phone_number))
        # 插入该用户的信息
        cursor.execute(
            "INSERT INTO user_info (username, gender, age, medical_history, medication) VALUES (%s, %s, %s, %s, %s)",
            (username, None, None, None, None))
        conn.commit()
        conn.close()
        return True


# 修改密码
def change_password(username, phone_number, new_password):
    conn = create_conn()
    cursor = conn.cursor()
    # 若用户不存在则提示用户不存在，请重新输入
    cursor.execute("SELECT * FROM users WHERE username = %s", (username))
    if cursor.fetchone() is None:
        conn.commit()
        conn.close()
        return False
    else:
        new_hash_password = make_hashes(new_password)
        cursor.execute("UPDATE users SET password = %s WHERE phone_number = %s", (new_hash_password, phone_number))
        conn.commit()
        conn.close()
        return True


# 登录功能
def login(username, password):
    conn = create_conn()
    cursor = conn.cursor()
    hash_password = make_hashes(password)
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, hash_password))
    result = cursor.fetchone()
    conn.close()
    return result is not None


# 登录页面（入口页）
def login_page():
    st.set_page_config(page_title="Login", page_icon="🏥", initial_sidebar_state="collapsed")
    img1, img2, img3 = st.columns([0.4, 0.2, 0.4])
    with img2:
        with Image.open("./image/logo.png") as img:
            st.image(img, use_column_width=True)
    # 添加页面标题，并居中显示
    st.markdown('''
    <div style="text-align: center; font-size: 48px; font-weight: bold; color: #000000;">
    家庭常见病自诊系统
    </div>
    <br>
    ''', unsafe_allow_html=True)
    username = st.text_input("**用户名**")
    password = st.text_input("**密码**", type="password")
    if st.button("登录", use_container_width=True):
        if username == "" or password == "":
            st.error("🚨用户名或密码不能为空")
        else:
            if login(username, password):
                st.success("登录成功！")
                st.session_state.username = username
                time.sleep(0.5)
                # 跳转至多页聊天应用的主界面
                st.switch_page("pages/1_🗒️_用户信息.py")
            else:
                st.error("🚨用户名或密码错误")
    # 注册和找回密码的按钮或链接
    st.markdown('''
    **还没有账号？**
     [点击注册](?page=register)
     
    **忘记密码？**
    [点击找回密码](?page=change)
    ''', unsafe_allow_html=True)


# 注册页面
def register_page():
    st.set_page_config(page_title="注册", page_icon=":sparkles:", initial_sidebar_state="collapsed")
    st.markdown('''
    <div style="text-align: center; font-size: 48px; font-weight: bold; color: #000000;">
    注册
    </div>
    <br>
        ''', unsafe_allow_html=True)
    new_username = st.text_input("**用户名**")
    new_password = st.text_input("**密码**", type="password")
    new_phone = st.text_input("**手机号码**")
    if st.button("注册", use_container_width=True):
        if new_username == "" or new_password == "":
            st.error("🚨用户名或密码不能为空")
        elif new_phone == "":
            st.error("🚨手机号码不能为空")
        else:
            if register(new_username, new_password, new_phone):
                st.success("注册成功！请关闭页面进行登录")
            else:
                st.error("🚨用户名已存在，请重新输入")


# 修改密码界面
def change_password_page():
    st.set_page_config(page_title="忘记密码", page_icon=":sparkles:", initial_sidebar_state="collapsed")
    st.markdown('''
    <div style="text-align: center; font-size: 48px; font-weight: bold; color: #000000;">
    找回密码
    </div>
    <br>
        ''', unsafe_allow_html=True)
    forgot_username = st.text_input("**用户名**")
    forgot_phone_nember = st.text_input("**手机号码**")
    new_password = st.text_input("**新密码**", type="password")
    if st.button("确认", use_container_width=True):
        if change_password(forgot_username, forgot_phone_nember, new_password):
            st.success("密码已修改！请关闭页面进行登录")
        elif forgot_username == "":
            st.error("🚨手机号码下无用户，请检查后输入")
        else:
            st.error("🚨用户名不存在，请重新输入")


# Streamlit应用
def main():
    create_tables()
    # 根据URL查询参数决定显示哪个页面
    page = st.query_params.get('page')
    if page == 'register':
        register_page()
    elif page == 'change':
        change_password_page()
    else:
        login_page()  # 默认显示主页


if __name__ == "__main__":
    main()
