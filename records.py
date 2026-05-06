import streamlit as st
import google.generativeai as genai
import os

# --- CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="The Nexus", layout="wide")
st.title("Phân tích Tâm lý Hội thoại")

# --- BỘ LỌC CHỮ DÀNH CHO FILE BÁO CÁO TẢI VỀ ---
def lam_sach_bao_cao(text_markdown):
    # Tách từng dòng để xử lý định dạng
    lines = text_markdown.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Nếu là dòng tiêu đề lớn (bắt đầu bằng ### hoặc ##)
        if line.strip().startswith('###') or line.strip().startswith('##'):
            header_text = line.replace('###', '').replace('##', '').strip()
            # Loại bỏ các dấu bôi đậm nếu có trong tiêu đề
            header_text = header_text.replace('**', '').replace('*', '')
            
            # Tạo block tiêu đề cực kỳ rõ ràng, dễ nhìn
            cleaned_lines.append("\n" + "="*55)
            cleaned_lines.append(f" MỤC: {header_text.upper()}")
            cleaned_lines.append("="*55 + "\n")
        else:
            # Xóa bỏ các ký tự bôi đậm dòng ** của markdown rối mắt
            line_clean = line.replace('**', '')
            # Đổi các dấu gạch đầu dòng của AI thành dấu chấm tròn cho thoáng
            if line_clean.strip().startswith('* ') or line_clean.strip().startswith('- '):
                line_clean = "  • " + line_clean.strip()[2:]
            cleaned_lines.append(line_clean)
            
    return "\n".join(cleaned_lines)

# --- LẤY API KEY ---
# Ưu tiên lấy từ Secrets của Streamlit Cloud để bảo mật
google_api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")

with st.sidebar:
    st.header("Cấu Hình")
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
            if st.button("Bắt đầu"):
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
                        st.subheader("📊 Kết quả phân tích")
                        st.markdown(response.text)

                        
                        bao_cao_sach = lam_sach_bao_cao(response.text)
                        
                        # Nút tải báo cáo đã được làm sạch trực quan
                        st.download_button(
                            label="Tải báo cáo sạch về máy 📥",
                            data=bao_cao_sach,
                            file_name=f"Bao_cao_sach_{uploaded_file.name}.txt",
                            mime="text/plain"
                        )
                        
                except Exception as e:
                    st.error(f"Lỗi khi xử lý file: {e}")
                    
    except Exception as e:
        st.error(f"Lỗi cấu hình API: {e}")
else:
    st.warning("Anh vui lòng nhập API Key để bắt đầu nhé!")
