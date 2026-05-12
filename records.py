import streamlit as st
import google.generativeai as genai
import os
import time

# --- CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="The Nexus | Behavioral Analysis", layout="wide")

# Đọc file CSS riêng
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def lam_sach_bao_cao(text_markdown):
    lines = text_markdown.split('\n')
    cleaned_lines = []
    for line in lines:
        if line.strip().startswith('###') or line.strip().startswith('##'):
            header_text = line.replace('#', '').strip().upper()
            cleaned_lines.append(f"\n{'='*55}\n MỤC: {header_text}\n{'='*55}\n")
        else:
            line_clean = line.replace('**', '')
            if line_clean.strip().startswith('* ') or line_clean.strip().startswith('- '):
                line_clean = "  • " + line_clean.strip()[2:]
            cleaned_lines.append(line_clean)
    return "\n".join(cleaned_lines)

# --- SIDEBAR: BẢNG ĐIỀU KHIỂN ---
with st.sidebar:
    st.title("⚙️ Điều khiển")
    google_api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        google_api_key = st.text_input("API Key", type="password")
    
    st.markdown("---")
    # Thông số độ gắt cho anh Công tùy chỉnh
    temp = st.slider("Độ 'Gắt' & Sáng tạo (Temperature)", 0.0, 1.0, 0.7, 0.1)
    st.caption("Thấp (0.0): Phân tích logic, thực tế. Cao (1.0): Rất gắt, xoáy sâu tâm lý.")
    
    st.markdown("---")
    st.info("Dòng IUL - National Life Group")

# --- XỬ LÝ CHÍNH ---
st.title("🎯 The Nexus: Phân tích Records")

if google_api_key:
    genai.configure(api_key=google_api_key)
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    target_model = next((m for m in available_models if 'gemini-1.5-flash' in m), available_models[0])
    
    # Áp dụng temperature vào cấu hình model
    generation_config = {"temperature": temp}
    model = genai.GenerativeModel(model_name=target_model, generation_config=generation_config)
    
    uploaded_file = st.file_uploader("Kéo thả file ghi âm vào đây", type=["mp3", "wav", "m4a"])

    if uploaded_file:
        if st.button("BẮT ĐẦU PHÂN TÍCH TÂM LÝ"):
            try:
                # Sử dụng st.status sinh động như anh yêu cầu
                with st.status("Hệ thống đang làm việc...", expanded=True) as status:
                    status.write("🎧 Đang nghe và chuyển hóa bản ghi...")
                    audio_data = uploaded_file.read()
                    time.sleep(1.5)
                    
                    status.write("🧠 Đang mổ xẻ tâm lý hành vi & logic IUL...")
                    prompt = f"""
                    Bạn là một chuyên gia tâm lý hành vi và Sales Manager lão luyện ngành bảo hiểm IUL Mỹ (National Life Group). 
                    Nhiệm vụ của bạn là phân tích file ghi âm với thái độ thẳng thắn, sâu sắc nhưng mang tính giáo dục cao. 
                    Đừng chỉ bắt bẽ, hãy chỉ dẫn để nhân viên nhìn ra "điểm mù" trong giao tiếp của họ.
                    
                    YÊU CẦU ĐẶC BIỆT:
                    - TRÍCH DẪN TRỰC TIẾP: Phải có thời gian (Phút:Giây) và câu nói cụ thể của nhân viên.
                    - KHẨU VỊ: Dùng thuật ngữ IUL chuyên nghiệp nhưng giải thích theo tâm lý học "đời thường".
                    - ĐỘ GẮT: Dựa trên mức Temperature {temp}, hãy đưa ra những nhận xét sắc bén tương ứng.
                    
                    CẤU TRÚC PHÂN TÍCH & CHỈ DẪN (9 TIÊU CHÍ):
                    
                    1. CỐT TRUYỆN & ĐIỂM MẤU CHỐT: Tóm tắt cực gọn diễn biến cuộc gọi.
                    
                    2. INSIGHT NGẦM & CHỈ DẪN TƯ DUY: Khách thực sự lo gì? 
                       -> Chỉ dẫn: Thay vì nghe bề nổi, hãy dạy nhân viên cách "ngửi" ra nỗi sợ thực sự của khách qua tông giọng hoặc từ ngữ họ dùng.
                    
                    3. HIỆU QUẢ "CHẠM" & CÁCH KẾT NỐI: Có đánh trúng nỗi đau không? 
                       -> Chỉ dẫn: Nếu chưa chạm, hãy chỉ cho nhân viên cách đặt câu hỏi gợi mở để khách tự nói ra vấn đề của họ thay vì mình tự suy đoán.
                    
                    4. TRẠNG THÁI KẾT THÚC & HƯỚNG GIẢI QUYẾT: Triệt để chưa? 
                       -> Chỉ dẫn: Nếu chưa xong, hãy hướng dẫn cách "đặt gạch" cho cuộc gọi tiếp theo để khách không cảm thấy bị làm phiền mà là đang được giúp đỡ.
                    
                    5. ĐỘ "NGƯỜI" vs VĂN MẪU: Trích dẫn đoạn nói như máy. 
                       -> Chỉ dẫn: Cách biến câu văn mẫu đó thành một lời tâm sự, chia sẻ đời thường để phá vỡ rào cản phòng thủ của khách.
                    
                    6. KỸ THUẬT IUL & CÁCH GIẢI THÍCH DỄ HIỂU: (Index, Premium, Cash Value...). 
                       -> Chỉ dẫn: Dạy nhân viên cách ví von các khái niệm IUL khô khan thành những hình ảnh gần gũi (ví dụ: Cash Value như cái kho dự trữ mùa đông).
                    
                    7. GÓT CHÂN ACHILLES & MẪU CÂU "ĐỔI ĐỜI": Lỗi tâm lý nặng nhất. 
                       -> Chỉ dẫn: Giải thích tại sao nói như cũ là sai tâm lý. Đưa ra 2 phương án nói mới: Một phương án an toàn và một phương án "sát thủ" để nhân viên tập luyện.
                    
                    8. LỘ TRÌNH CẢI THIỆN: 3 việc cụ thể cần làm ngay.
                    
                    9. CÂU HỎI CHIẾN LƯỢC: 1 câu hỏi duy nhất để lật ngược thế trận.
                    """
                    
                    response = model.generate_content([prompt, {"mime_type": "audio/mpeg", "data": audio_data}])
                    time.sleep(1)
                    status.write("📝 Đang hoàn thiện báo cáo chi tiết...")
                    status.update(label="✅ Đã phân tích xong!", state="complete", expanded=False)

                # Hiển thị kết quả trong Card đã được CSS
                st.markdown(f'<div class="analysis-card">{response.text}</div>', unsafe_allow_html=True)
                
                # Tải báo cáo
                st.divider()
                st.download_button(
                    label="Tải báo cáo sạch 📥",
                    data=lam_sach_bao_cao(response.text),
                    file_name=f"Nexus_Analysis_{uploaded_file.name}.txt",
                    mime="text/plain"
                )
                    
            except Exception as e:
                st.error(f"Lỗi: {e}")
else:
    st.warning("Anh nhập API Key ở Sidebar nhé!")
