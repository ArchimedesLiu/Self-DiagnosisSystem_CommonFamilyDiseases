# -- coding:utf-8 --
from langchain.llms import Tongyi
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import streamlit as st
from typing import List
from fuzzywuzzy import fuzz
import logging
import os
import time

os.environ["DASHSCOPE_API_KEY"] = "sk-458444fdb70c4e648ab713940b41eff0"

# 模糊匹配
def calculate_similarity(str1, str2):
    return fuzz.ratio(str1, str2)


class SafePromptTemplate:
    def __init__(self, template: str, input_variables: List[str]):
        self.template = template
        self.input_variables = input_variables

    def render(self, **kwargs):
        return self.template.format(**kwargs)


class PromptInformation:
    def __init__(self, age, sex, past_medical_history, previous_medications):
        self.age = age
        self.sex = sex
        self.past_medical_history = past_medical_history
        self.previous_medications = previous_medications

    def to_dict(self):
        return {
            "age": self.age,
            "sex": self.sex,
            "past_medical_history": self.past_medical_history,
            "previous_medications": self.previous_medications,
        }


def call_with_prompt(age: int, sex: str, past_medical_history: str, previous_medications: str, informations: str):
    """
    调用大模型回答
    :param age:
    :param sex:
    :param past_medical_history:
    :param previous_medications:
    :param informations:
    :return: answers
    """
    template = """你是一名十分专的业家庭常见病领域的医生，请你结合我的年龄、性别、既往病史、过往用药等基本信息和病症信息，对我进行诊断，给出专业的诊断结果，包括但不限于可能患有的病情、用药建议、饮食建议、生活建议、进一步医院就诊挂号科室的推荐等，如果我提供的病症信息不足，则对我进行病症的追问，直到我回答与没有其他症状相关的话语，然后再综合的为我提供诊断结果。
    我的基本信息如下：
    年龄：{age}；
    性别：{sex}；
    既往病史：{past_medical_history}；
    过往用药：{previous_medications};
    """
    try:
        prompt_information = PromptInformation(age, sex, past_medical_history, previous_medications)
        safe_prompt_information = SafePromptTemplate(template,
                                                     ["age", "sex", "past_medical_history", "previous_medications"])
        prompt = safe_prompt_information.render(**prompt_information.to_dict())
        user_template = prompt + "\n我的病症信息：{informations}。"
        user_prompt = PromptTemplate(template=user_template, input_variables=["informations"])
        # llm = Tongyi(model_name="qwen-72b-chat")
        llm = Tongyi(model_name="qwen-max")
        llm_chain = LLMChain(prompt=user_prompt, llm=llm)
        answers = llm_chain.run(informations)
        return answers
    except Exception as e:
        # 在实际应用中，可能需要根据具体的异常类型进行更细致的处理
        logging.error(f"🚨处理用户请求时发生错误: {str(e)}")  # 记录错误日志
        # 对可能的异常进行捕获和处理，提高程序的健壮性
        print(f"An error occurred: {str(e)}")


st.set_page_config(page_title="家庭常见病自诊系统", page_icon="🩺", initial_sidebar_state="auto")
# 展示image文件夹下的logo图片
st.markdown('''
<div style="text-align: center; font-size: 32px; font-weight: bold; color: #000000;">
🩺家庭常见病自诊系统🩺
</div>
<br>
<br>
    ''', unsafe_allow_html=True)

# 获取用户信息
if "user_info" not in st.session_state:
    st.write("\n")
    st.write("\n")
    with st.container(border=True, height=200):
        st.write("\n")
        st.write("\n")
        st.markdown("""<div style="text-align: center; font-family: 'Times New Roman', serif; font-size: 24px; 
        font-weight: bold; color: #000000;">⚠️请登录后进行自诊</div> 
        <br>""", unsafe_allow_html=True)
        if st.button("登录", use_container_width=True):
            st.switch_page("Login.py")
else:
    # 设置按钮点击清空聊天记录
    response = "你好呀！我是家庭常见病自诊小助手，将为您提供家庭常见病的诊断建议，请输入您的病症信息进行自诊。"
    with st.sidebar:
        if st.button("开始新对话", use_container_width=True):
            st.session_state.messages = []
            st.session_state.messages.append({"role": "assistant", "content": response})
        if st.button("退出登录", type="primary", use_container_width=True):
            del st.session_state.messages
            # 清除st.session_state中的username
            del st.session_state.user_info
            del st.session_state.username
            st.switch_page("Login.py")
    age = st.session_state.user_info['年龄'][0]
    sex = st.session_state.user_info['性别'][0]
    past_medical_history = st.session_state.user_info['既往病史'][0]
    previous_medications = st.session_state.user_info['过往用药'][0]
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({"role": "assistant", "content": response})
    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        if message["role"] == "assistant":
            with st.chat_message(message["role"], avatar="👨🏻‍⚕️"):
                st.markdown(message["content"])
        else:
            with st.chat_message(message["role"], avatar="😷️"):
                st.markdown(message["content"])
    # React to user input
    if user_input := st.chat_input("请输入你的病症信息"):
        sim_self = calculate_similarity(user_input, "你是谁")
        sim_do = calculate_similarity(user_input, "你可以干什么")
        sim_hello = calculate_similarity(user_input, "你好")
        if sim_self > 50 or sim_do > 30 or sim_hello > 50:
            st.chat_message("user", avatar="😷️").markdown(user_input)
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("assistant", avatar="👨🏻‍⚕️"):
                time.sleep(0.2)
                st.markdown(response)
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
        else:
            # Display user message in chat message container
            st.chat_message("user", avatar="😷️").markdown(user_input)
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.spinner("正在诊断中..."):
                response = call_with_prompt(age=age, sex=sex, past_medical_history=past_medical_history,
                                            previous_medications=previous_medications, informations=user_input)
            # Display assistant response in chat message container
            with st.chat_message("assistant", avatar="👨🏻‍⚕️"):
                st.markdown(response)
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
