import streamlit as st
import google.generativeai as genai
import os

# --- CẤU HÌNH GOOGLE API ---
# Nếu anh đưa lên Streamlit Cloud thì dán Key vào Secrets, còn không thì nhập tay
google_api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")

st.set_page_config(page_title="Đánh giá Sale - Team Công (Gemini Edition)", layout="wide")
st.title("🛡️ Trợ lý Phân tích Sale - Google AI")

with st.sidebar:
    if not google_api_key:
        google_api_key = st.text_input("Nhập Google API Key", type="password")
    else:
        st.success("✅ Đã kết nối Google AI")

if google_api_key:
    genai.configure(api_key=google_api_key)
    
    uploaded_file = st.file_uploader("Kéo thả file record của nhân viên vào đây", type=["mp3", "wav", "m4a"])

    if uploaded_file is not None:
        if st.button("Bắt đầu mổ xẻ"):
            try:
                with st.spinner("Gemini đang nghe và phân tích..."):
                    # Khởi tạo model Gemini 1.5 Pro (rất mạnh về xử lý file âm thanh)
                    model = genai.GenerativeModel("gemini-1.5-pro")
                    
                    # Gemini có khả năng đọc trực tiếp file audio mà không cần qua Whisper
                    audio_data = uploaded_file.read()
                    
                    prompt = """
                    Bạn là một chuyên gia tâm lý hành vi và Sales Manager lão luyện ngành bảo hiểm IUL. 
                    Hãy phân tích file ghi âm này với thái độ thẳng thắn, sâu sắc, không máy móc.
                    
                    YÊU CẦU PHÂN TÍCH (9 TIÊU CHÍ):
                    (Dán bộ 9 tiêu chí của anh vào đây...)
                    """
                    
                    # Gửi file và prompt cho Gemini
                    response = model.generate_content([
                        prompt,
                        {"mime_type": "audio/mp3", "data": audio_data}
                    ])
                    
                    st.subheader("Kết quả phân tích từ Gemini 1.5 Pro")
                    st.markdown(response.text)
                    
            except Exception as e:
                st.error(f"Lỗi rồi anh ơi: {e}")