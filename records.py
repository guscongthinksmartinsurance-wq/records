import streamlit as st
import google.generativeai as genai
import os

# --- CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Hệ thống Đánh giá Sale - Team Công", layout="wide")
st.title("🛡️ Trợ lý Phân tích Tâm lý Hội thoại")
st.write("Giải pháp thực chiến dành riêng cho Sales Manager.")

# --- LẤY API KEY ---
# Ưu tiên lấy từ Secrets của Streamlit Cloud để bảo mật
google_api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")

with st.sidebar:
    st.header("Cấu hình hệ thống")
    if not google_api_key:
        google_api_key = st.text_input("Nhập Google API Key", type="password")
        st.info("Anh lấy Key tại: aistudio.google.com")
    else:
        st.success("✅ Đã kết nối Google AI")

# --- XỬ LÝ CHÍNH ---
if google_api_key:
    try:
        genai.configure(api_key=google_api_key)
        
        # Tự động dò tìm tên model khả dụng để tránh lỗi 404
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Ưu tiên chọn Flash cho nhanh và ổn định, nếu không có thì lấy Pro
        target_model = next((m for m in available_models if 'gemini-1.5-flash' in m), 
                            next((m for m in available_models if 'gemini-1.5-pro' in m), available_models[0]))
        
        model = genai.GenerativeModel(model_name=target_model)
        
        uploaded_file = st.file_uploader("Kéo thả file record của nhân viên vào đây (mp3, wav, m4a)", type=["mp3", "wav", "m4a"])

        if uploaded_file is not None:
            if st.button("Bắt đầu mổ xẻ"):
                try:
                    with st.spinner(f"Đang phân tích bằng {target_model.split('/')[-1]}..."):
                        # Đọc dữ liệu file âm thanh
                        audio_data = uploaded_file.read()
                        
                        prompt = """
                        Bạn là một chuyên gia tâm lý hành vi và Sales Manager lão luyện ngành bảo hiểm IUL. 
                        Hãy phân tích file ghi âm này với thái độ thẳng thắn, sâu sắc, không máy móc, không thảo mai.

                        YÊU CẦU PHÂN TÍCH THEO ĐÚNG 9 TIÊU CHÍ SAU:
                        1. Cốt truyện & Điểm mấu chốt (Gạch đầu dòng ngắn gọn).
                        2. Vấn đề thực sự của khách hàng (Insight ngầm, không phải điều họ nói lúc đầu).
                        3. Hiệu quả xử lý: Tư vấn viên có "chạm" đúng nỗi đau của khách không?
                        4. Mức độ giải quyết: (Chưa xong/Xong một phần/Triệt để/Có kế hoạch rõ ràng).
                        5. Độ "Người" & Đồng cảm: Có nói giọng máy móc, văn mẫu không? Có thực sự lắng nghe không?
                        6. Kỹ thuật chuyên môn: Phân tích tính logic và kiến thức IUL trong cuộc gọi.
                        7. Gót chân Achilles: Chỉ rõ điểm yếu và TẠI SAO (về mặt tâm lý) nhân viên lại mắc lỗi đó. Đưa ra mẫu câu "đời" hơn để khắc phục.
                        8. Lộ trình cải thiện: 3 việc cụ thể cần làm cho cuộc gọi sau.
                        9. Câu hỏi chiến lược: 1-2 câu hỏi để làm chủ hoàn toàn thế trận.
                        """
                        
                        # Gửi file và prompt cho Gemini
                        response = model.generate_content([
                            prompt,
                            {"mime_type": "audio/mpeg", "data": audio_data}
                        ])
                        
                        st.divider()
                        st.subheader("📊 Kết quả phân tích chi tiết")
                        st.markdown(response.text)
                        
                        # Nút tải báo cáo
                        st.download_button(
                            label="Tải báo cáo về máy",
                            data=response.text,
                            file_name=f"Bao_cao_{uploaded_file.name}.txt",
                            mime="text/plain"
                        )
                        
                except Exception as e:
                    st.error(f"Lỗi khi xử lý file: {e}")
                    
    except Exception as e:
        st.error(f"Lỗi cấu hình API: {e}")
else:
    st.warning("Anh vui lòng nhập API Key để bắt đầu nhé!")
