import streamlit as st
import google.generativeai as genai

# إعدادات الواجهة
st.set_page_config(page_title="Ve-Chat", page_icon="🤖", layout="wide")

# تحسين مظهر الواجهة بالكامل
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

st.title("🤖 Ve-Chat")

# جلب البيانات من Secrets
api_key = st.secrets.get("GEMINI_API_KEY", "")
correct_password = st.secrets.get("MY_PASSWORD", "")

genai.configure(api_key=api_key)

# استخدام الموديل المستقر الحديث
model = genai.GenerativeModel('gemini-3.6-flash')

# القائمة الجانبية
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
            try:
                response = model.generate_content(prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"حدث خطأ في الاتصال: {e}")

elif user_password:
    st.sidebar.error("كلمة السر غير صحيحة!")
else:
    st.info("👈 يرجى إدخال كلمة السر في القائمة الجانبية للبدء.")
        # === كود حفظ المحادثة المضاف ===
    if st.session_state.messages:
        chat_text = "--- سجل محادثة Ve-Chat ---\n\n"
        for msg in st.session_state.messages:
            role = "المستخدم" if msg["role"] == "user" else "Ve-Chat"
            chat_text += f"[{role}]:\n{msg['content']}\n\n" + "-"*40 + "\n\n"
        
        st.sidebar.markdown("---")
        st.sidebar.download_button(
            label="💾 حفظ المحادثة (تنزيل ملف)",
            data=chat_text,
            file_name="محادثة_Ve_Chat.txt",
            mime="text/plain"
        )
            # أسطر إدارة المحادثات الجديدة
    if "chats" not in st.session_state:
        st.session_state.chats = {"محادثة رئيسية": []}
    if "current_chat" not in st.session_state:
        st.session_state.current_chat = "محادثة رئيسية"

    new_chat_title = st.sidebar.text_input("اسم محادثة جديدة:")
    if st.sidebar.button("➕ إنشاء محادثة جديدة"):
        if new_chat_title and new_chat_title not in st.session_state.chats:
            st.session_state.chats[new_chat_title] = []
            st.session_state.current_chat = new_chat_title
            st.rerun()

    chat_names_list = list(st.session_state.chats.keys())
    selected_chat = st.sidebar.selectbox("📚 اختر المحادثة:", chat_names_list, index=chat_names_list.index(st.session_state.current_chat))
    if selected_chat != st.session_state.current_chat:
        st.session_state.current_chat = selected_chat
        st.rerun()

    # أسطر زر حفظ المحادثة الحالية
    if st.session_state.chats[st.session_state.current_chat]:
        chat_text = f"--- سجل محادثة: {st.session_state.current_chat} ---\n\n"
        for msg in st.session_state.chats[st.session_state.current_chat]:
            role = "المستخدم" if msg["role"] == "user" else "Ve-Chat"
            chat_text += f"[{role}]:\n{msg['content']}\n\n" + "-"*40 + "\n\n"
        
        st.sidebar.markdown("---")
        st.sidebar.download_button(
            label="💾 تحميل المحادثة الحالية",
            data=chat_text,
            file_name=f"{st.session_state.current_chat}.txt",
            mime="text/plain"
        )
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #161b22; }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    </style>
""", unsafe_allow_html=True)