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
                    prompt = """
                    Bạn là một chuyên gia tâm lý hành vi và Sales Manager lão luyện ngành bảo hiểm IUL Mỹ. 
                    Phân tích file này với thái độ thẳng thắn, sâu sắc, không thảo mai. 
                    Sử dụng ngôn ngữ đời thường, gãy gọn.

                    YÊU CẦU ĐẶC BIỆT:
                    - TRÍCH DẪN TRỰC TIẾP: Chỉ rõ "Ở phút thứ X, nhân viên nói câu [A], đây là biểu hiện của sự [thiếu tự tin/thảo mai/máy móc]".
                    - KHẨU VỊ: Dùng thuật ngữ IUL (Index, Premium, Loan, Cash Value...) nhưng giải thích dưới góc độ tâm lý khách hàng lo sợ điều gì.

                    CẤU TRÚC PHÂN TÍCH 9 TIÊU CHÍ:
                    1. Cốt truyện & Điểm mấu chốt.
                    2. Insight ngầm: Khách lo gì thực sự?
                    3. Hiệu quả xử lý: Có "chạm" đúng nỗi đau không?
                    4. Trạng thái kết thúc: Triệt để hay chưa?
                    5. Độ "Người": Chỗ nào nói văn mẫu, máy móc?
                    6. Kỹ thuật chuyên môn IUL.
                    7. Gót chân Achilles: Lỗi tâm lý và mẫu câu "đời" hơn để thay thế.
                    8. Lộ trình cải thiện: 3 việc cụ thể.
                    9. Câu hỏi chiến lược: 1 câu hỏi để làm chủ thế trận.
                    """
                    
                    response = model.generate_content([prompt, {"mime_type": "audio/mpeg", "data": audio_data}])
                    time.sleep(1)
                    status.write("📝 Đang hoàn thiện báo cáo chi tiết...")
                    status.update(label="✅ Đã phân tích xong!", state="complete", expanded=False)

                # Hiển thị kết quả trong Card đã được CSS
                st.markdown(f'<div class="analysis-card">{response.text}</div>', unsafe_allow_True=True)
                
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
