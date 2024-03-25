from Login import create_conn
import pandas as pd
import streamlit as st



def click_button():
    st.session_state.clicked = True


# 定义函数来获取用户信息
def get_user_info(username):
    conn = create_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_info WHERE username=%s", (username,))
    df = pd.DataFrame(cursor.fetchall())
    df.columns = ["用户名", "性别", "年龄", "既往病史", "过往用药"]
    st.session_state.user_info = df
    conn.close()
    return df
#
# 定义函数来更新用户信息
def update_user_info(username, gender, age, medical_history, medication):
    conn = create_conn()
    c = conn.cursor()
    c.execute("UPDATE user_info SET gender = %s, age = %s, medical_history = %s, medication = %s WHERE username = %s", (gender, age, medical_history, medication, username))
    conn.commit()
    conn.close()


st.set_page_config(page_title="用户信息", page_icon="ℹ", initial_sidebar_state="auto")
# 使用streamlit创建界面
st.markdown('''
<div style="text-align: center; font-size: 48px; font-weight: bold; color: #000000;">
用户信息
</div>
<br>
    ''', unsafe_allow_html=True)

# 获取用户信息
if "username" not in st.session_state:
    st.write("\n")
    st.write("\n")
    with st.container(border=True, height=200):
        st.write("\n")
        st.write("\n")
        st.markdown("""<div style="text-align: center; font-family: 'Times New Roman', serif; font-size: 24px; 
        font-weight: bold; color: #000000;">⚠️请登录后查看个人信息</div> 
        <br>""", unsafe_allow_html=True)
        if st.button("登录", use_container_width=True):
            st.switch_page("Login.py")
else:
    user_info = get_user_info(st.session_state.username)
    st.markdown(f"<div style='font-family: \"Microsoft YaHei\"; line-height: 2;"
                f"text-align: center; font-size: 1rem; font-weight: bold;'>🚨请先完善信息后进行自诊🚨</div>",unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(f"<div style='font-family: \"Microsoft YaHei\"; line-height: 2;"
                    f"text-align: start; font-size: 1.2rem; font-weight: bold;'>年龄：{user_info['年龄'][0]}岁</div>",
                    unsafe_allow_html=True)
        st.markdown(f"<div style='font-family: \"Microsoft YaHei\"; line-height: 2;"
                    f"text-align: start; font-size: 1.2rem; font-weight: bold;'>性别：{user_info['性别'][0]}</div>",
                    unsafe_allow_html=True)
        st.markdown(f"<div style='font-family: \"Microsoft YaHei\"; line-height: 2;"
                    f"text-align: start; font-size: 1.2rem; font-weight: bold;'>既往病史：{user_info['既往病史'][0]}</div>",
                    unsafe_allow_html=True)
        st.markdown(f"<div style='font-family: \"Microsoft YaHei\"; line-height: 2;"
                    f"text-align: start; font-size: 1.2rem; font-weight: bold;'>过往用药：{user_info['过往用药'][0]}</div>",
                    unsafe_allow_html=True)
        st.markdown(f"</b>", unsafe_allow_html=True)
    # 添加一个修改按钮
    if "clicked" not in st.session_state:
        st.session_state.clicked = False
    st.button("修改信息", on_click=click_button, use_container_width=True)
    if st.session_state.clicked:
        st.write("请在下方输入修改后的信息：")
        with st.container(border=True):
            new_age = st.text_input("年龄")
            new_gender = st.text_input("性别")
            new_medical_history = st.text_input("既往病史")
            new_medication = st.text_input("过往用药")
            col1, col2 = st.columns(2)
            with col2:
                if st.button("提交修改", use_container_width=True):
                    user_info['年龄'][0] = new_age
                    user_info['性别'][0] = new_gender
                    user_info['既往病史'][0] = new_medical_history
                    user_info['过往用药'][0] = new_medication
                    st.session_state.user_info = user_info
                    st.success("信息已更新")
                    st.session_state.clicked = False
                    update_user_info(user_info['用户名'][0], user_info['性别'][0], user_info['年龄'][0], user_info['既往病史'][0], user_info['过往用药'][0])
                    # 刷新页面
                    st.rerun()
            with col1:
                if st.button("取消修改", use_container_width=True):
                    st.session_state.clicked = False
                    st.rerun()
    if st.button("🩺前往自诊🩺", use_container_width=True):
        if user_info['性别'][0] and user_info['年龄'][0] and user_info['既往病史'][0] and user_info['过往用药'][0]:
            st.switch_page("/pages/2_🩺_自诊.py")
        else:
            st.error("🚨请完善所有信息后进行自诊🚨")
    # 在侧边栏增加退出登录的按钮
    with st.sidebar.container():
        if st.button("退出登录", type="primary", use_container_width=True):
            st.session_state.clicked = False
            del st.session_state.messages
            # 清除st.session_state中的username
            del st.session_state.username
            del st.session_state.user_info
            st.switch_page("Login.py")








