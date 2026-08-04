import streamlit

import requests

st = streamlit
st.title("AI-知识助手")
import streamlit.runtime.scriptrunner as sr
ctx = sr.get_script_run_ctx()
st.write("会话ID:", ctx.session_id if ctx else "无")
if "token" in st.query_params:
  st.subheader("成功登录")
  st.session_state["token"] = st.query_params["token"]
  if st.button("退出"):
    st.session_state.clear()
else:
  select = st.selectbox("登录/注册",["登录","注册"])
  if select =="登录": 
    st.subheader("登录")
    username = st.text_input("用户名：",placeholder="请输入用户名")
    password = st.text_input("密码：",placeholder="请输入密码",type="password")
    if st.button("登录"):
      resp = requests.post(
        "http://localhost:8000/api/v1/auth/login",
        json={"username":username,"password":password}
      )
      if resp.status_code == 200:
        data = resp.json()
        st.session_state["token"] = data["access_token"]
        st.query_params["token"] = data["access_token"]
        # user = data["user"]
        st.success("登陆成功")
      else:
        st.error(resp.json().get("detail","登陆失败"))

  else:
    st.subheader("注册")
    username = st.text_input("用户名：",placeholder="请输入用户名")
    password = st.text_input("密码：",placeholder="请输入密码",type="password")
    if st.button("注册"):
      resp = requests.post(
        "http://localhost:8000/api/v1/auth/register",
        json={"username":username,"password":password}
      )
      if resp.status_code == 201:
        data = resp.json()
        st.session_state["token"] = data["access_token"]
        st.query_params["token"] = data["access_token"]
        user = data["user"]
        st.success("注册成功")
      else:
        st.error(resp.json().get("detail","注册失败"))