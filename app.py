import streamlit as st
import google.generativeai as genai

# إعدادات الواجهة والألوان
st.set_page_config(page_title="Ve-Chat", page_icon="🤖", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #131314; color: #e3e3e3; }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 Ve-Chat")

# جلب المفتاح المخبأ وكلمة السر بأمان من السيرفر
api_key = st.secrets["GEMINI_API_KEY"]
correct_password = st.secrets["MY_PASSWORD"]

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# القائمة الجانبية لإدخال كلمة المرور
user_password = st.sidebar.text_input("أدخل كلمة السر للدخول:", type="password")

if user_password == correct_password:
    st.sidebar.success("تم الدخول بنجاح!")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("اسأل Ve-Chat أي شيء..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            response = model.generate_content(prompt)
            st.markdown(response.text)
            
        st.session_state.messages.append({"role": "assistant", "content": response.text})

elif user_password:
    st.sidebar.error("كلمة السر غير صحيحة!")
else:
    st.info("👈 يرجى إدخال كلمة السر في القائمة الجانبية للبدء.")
