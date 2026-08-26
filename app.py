import streamlit as st
import google.generativeai as genai
from PIL import Image

# ---------------------------------------------------------------------------
# إعدادات الصفحة الأساسية
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Ve Chat",
    page_icon="📁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------------------------
# تصميم واجهات CSS المخصص (خلفية سوداء، إزالة الحواف البيضاء، أزرار زرقاء)
# ---------------------------------------------------------------------------
st.markdown("""
    <style>
    /* خلفية التطبيق العامة باللون الأسود الداكن وإخفاء العناصر غير المرغوب فيها */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    [data-testid="stSidebar"] {
        background-color: #161b22;
        color: #ffffff;
    }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 100% !important;
    }

    /* تخصيص شريط الكتابة وإطار الإدخال وزر الإرسال ليصبح باللون الأزرق الفخم */
    [data-testid="stChatInput"] {
        border-color: #1f6feb !important;
        background-color: #161b22 !important;
        border-radius: 12px !important;
    }
    [data-testid="stChatInput"] textarea {
        color: #ffffff !important;
    }
    [data-testid="stChatInput"] button {
        background-color: #1f6feb !important;
        color: #ffffff !important;
        border-radius: 8px !important;
    }
    [data-testid="stChatInput"] button svg {
        fill: #ffffff !important;
    }

    /* تنسيق صندوق رسائل المستخدم والبوت */
    .stChatMessage {
        background-color: transparent !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# عنوان التطبيق الرئيسي (بدون شرطة)
# ---------------------------------------------------------------------------
st.title("📁 Ve Chat - المساعد الذكي والمتطور")

# ---------------------------------------------------------------------------
# الاتصال بمحرك الذكاء الاصطناعي (Gemini)
# ---------------------------------------------------------------------------
api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    st.error("⚠️ تنبيه: يرجى إضافة مفتاح GEMINI_API_KEY في إعدادات Secrets على منصة Streamlit.")
else:
    genai.configure(api_key=api_key)

# اختيار الموديل القادر على قراءة النصوص وتحليل الصور بكفاءة عالية
model = genai.GenerativeModel('gemini-1.5-flash')

# ---------------------------------------------------------------------------
# تهيئة الذاكرة وإدارة المحادثات المتعددة
# ---------------------------------------------------------------------------
if "chats" not in st.session_state:
    st.session_state.chats = {"المحادثة الرئيسية": []}

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "المحادثة الرئيسية"

# ---------------------------------------------------------------------------
# الشريط الجانبي (إدارة المحادثات، إنشاء محادثة جديدة، التنزيل)
# ---------------------------------------------------------------------------
st.sidebar.markdown("### 🗂️ لوحة تحكم المحادثات")

# خانة تسمية المحادثة الجديدة وزر الإنشاء
new_chat_name = st.sidebar.text_input("اسم المحادثة الجديدة:", placeholder="اكتب اسم المحادثة هنا...")
if st.sidebar.button("➕ إنشاء محادثة جديدة"):
    if new_chat_name and new_chat_name not in st.session_state.chats:
        st.session_state.chats[new_chat_name] = []
        st.session_state.current_chat = new_chat_name
        st.rerun()
    elif not new_chat_name:
        st.sidebar.warning("الرجاء كتابة اسم للمحادثة أولاً.")
    else:
        st.sidebar.warning("هذا الاسم موجود مسبقاً.")

st.sidebar.markdown("---")

# قائمة الانتقال بين المحادثات المحفوظة
chat_keys = list(st.session_state.chats.keys())
selected_chat = st.sidebar.selectbox(
    "📚 اختر المحادثة للانتقال إليها:",
    chat_keys,
    index=chat_keys.index(st.session_state.current_chat)
)

if selected_chat != st.session_state.current_chat:
    st.session_state.current_chat = selected_chat
    st.rerun()

st.sidebar.markdown("---")

# زر تحميل المحادثة الحالية كملف نصي على الجهاز
current_messages_list = st.session_state.chats[st.session_state.current_chat]
if current_messages_list:
    export_text = f"--- سجل محادثة: {st.session_state.current_chat} ---\n\n"
    for m in current_messages_list:
        speaker = "المستخدم" if m["role"] == "user" else "Ve Chat"
        export_text += f"[{speaker}]:\n{m['content']}\n\n" + "-"*40 + "\n\n"
    
    st.sidebar.download_button(
        label="💾 حفظ وتنزيل المحادثة الحالية",
        data=export_text,
        file_name=f"{st.session_state.current_chat}.txt",
        mime="text/plain"
    )

# ---------------------------------------------------------------------------
# عرض سجل الرسائل للمحادثة الحالية
# ---------------------------------------------------------------------------
for message in current_messages_list:
    with st.chat_message(message["role"]):
        if "image" in message and message["image"] is not None:
            st.image(message["image"], width=300)
        st.markdown(message["content"])

# ---------------------------------------------------------------------------
# صندوق الإدخال التفاعلي (يدعم النص ورفع الصور في نفس الوقت)
# ---------------------------------------------------------------------------
user_prompt = st.chat_input(
    f"اكتب رسالتك أو ارفع صورة في ({st.session_state.current_chat})...",
    accept_file=True,
    file_type=["jpg", "jpeg", "png"]
)

# ---------------------------------------------------------------------------
# معالجة المدخلات (النصوص والصور) وإرسالها للذكاء الاصطناعي
# ---------------------------------------------------------------------------
if user_prompt:
    text_content = user_prompt.text if hasattr(user_prompt, "text") else str(user_prompt)
    files_content = user_prompt.files if hasattr(user_prompt, "files") else []
    
    attached_image = None
    pil_image_obj = None

    if files_content:
        for file_obj in files_content:
            if file_obj.type and "image" in file_obj.type:
                attached_image = file_obj
                pil_image_obj = Image.open(file_obj)
                break

    if not text_content and attached_image:
        text_content = "قم بتحليل هذه الصورة واشرح ما فيها بالتفصيل."

    if text_content or attached_image:
        current_messages_list.append({
            "role": "user",
            "content": text_content,
            "image": pil_image_obj
        })

        with st.chat_message("user"):
            if pil_image_obj is not None:
                st.image(pil_image_obj, width=300)
            st.markdown(text_content)

        with st.chat_message("assistant"):
            with st.spinner("جاري التفكير وتحليل المدخلات..."):
                try:
                    if pil_image_obj is not None:
                        response = model.generate_content([pil_image_obj, text_content])
                        ai_reply = response.text
                    else:
                        formatted_history = []
                        for msg in current_messages_list[:-1]:
                            r_role = "user" if msg["role"] == "user" else "model"
                            formatted_history.append({"role": r_role, "parts": [msg["content"]]})
                        
                        chat_session = model.start_chat(history=formatted_history)
                        response = chat_session.send_message(text_content)
                        ai_reply = response.text

                    st.markdown(ai_reply)
                    
                    current_messages_list.append({
                        "role": "assistant",
                        "content": ai_reply,
                        "image": None
                    })
                    st.rerun()

                except Exception as err:
                    st.error(f"حدث خطأ أثناء الاتصال بالخادم: {err}")
