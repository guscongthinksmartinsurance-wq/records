import streamlit as st
import google.generativeai as genai
import os
import time

# --- CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="The Nexus | Behavioral Analysis", layout="wide")

# Đọc file CSS riêng (Giữ nguyên 100% cấu trúc gốc của anh)
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Inject thêm CSS bổ sung cho phần Form để Highlight tiêu đề và bo góc kiểu Zoom trên nền sáng mượt
st.markdown("""
<style>
    /* Ép toàn bộ màu nền hệ thống về tone xám trắng mịn đồng nhất */
    .main, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #F8F9FA !important;
    }
    
    /* Đồng bộ khối hộp trắng viền xám tinh tế cho cả 2 trang */
    .zoom-container-card {
        background-color: #FFFFFF !important;
        padding: 32px;
        border-radius: 16px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.03);
        margin-bottom: 24px;
    }
    
    /* Thẻ hiển thị bảng giá kết quả */
    .zoom-pricing-card {
        background-color: #FFFFFF !important;
        border-radius: 16px;
        padding: 28px;
        margin-bottom: 20px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.02);
        transition: all 0.3s ease;
    }
    .zoom-pricing-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 30px rgba(11, 92, 255, 0.08);
        border-color: #0B5CFF;
    }
    
    /* Gói Tối Ưu Khuyên Dùng */
    .recommended-card {
        border: 1.5px solid #0B5CFF !important;
        background: linear-gradient(180deg, #FFFFFF 0%, #F4F7FF 100%) !important;
    }
    
    /* HIGHLIGHT TIÊU ĐỀ KIỂU ZOOM CHUYÊN NGHIỆP */
    .zoom-highlight-header {
        color: #0B5CFF !important;
        font-size: 16px;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        background-color: #F4F7FF;
        padding: 8px 16px;
        border-radius: 8px;
        display: inline-block;
        margin-bottom: 20px;
        border-left: 4px solid #0B5CFF;
    }
    
    /* Tag nhỏ nhãn hiệu */
    .zoom-tag {
        background-color: #0B5CFF;
        color: white;
        font-size: 11px;
        font-weight: bold;
        padding: 4px 12px;
        border-radius: 20px;
        display: inline-block;
        margin-bottom: 12px;
        text-transform: uppercase;
    }
    
    /* Giá tiền hiển thị */
    .price-text {
        font-size: 38px;
        font-weight: 800;
        color: #0B5CFF;
        margin: 10px 0;
        font-family: 'Inter', sans-serif;
    }
    
    /* Chữ nhãn nhập liệu */
    .zoom-container-card label, .zoom-container-card p {
        color: #1E293B !important;
        font-weight: 500 !important;
    }
</style>
""", unsafe_allow_html=True)

# Giữ nguyên 100% logic hàm làm sạch báo cáo gốc của anh
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


# --- SIDEBAR: BẢNG ĐIỀU KHIỂN (Menu chọn tính năng tệp màu hệ thống) ---
with st.sidebar:
    st.title("⚙️ Điều khiển")
    
    # Menu chọn tính năng đặt trên Sidebar đầu tiên
    menu_selection = st.radio(
        "Lựa chọn tính năng",
        ["🎙️ PHÂN TÍCH CUỘC GỌI", "🎯 FORM KHẢO SÁT & BÁO GIÁ"],
        index=0
    )
    
    st.divider()
    
    # Giữ nguyên logic lấy API Key gốc của anh
    google_api_key = st.secrets.get("GOOGLE_API_KEY", "")
    if not google_api_key:
        google_api_key = st.text_input("Nhập Google API Key:", type="password")


# =====================================================================
# CHẠY TÍNH NĂNG 1: PHÂN TÍCH CUỘC GỌI (BÊ NGUYÊN VĂN 100% CODE CŨ VÀ CẤU TRÚC MODEL GỐC)
# =====================================================================
if menu_selection == "🎙️ PHÂN TÍCH CUỘC GỌI":
    uploaded_file = st.file_uploader("Kéo thả hoặc chọn file ghi âm cuộc gọi (.mp3, .wav)", type=["mp3", "wav"])

    if uploaded_file:
        if not google_api_key:
            st.warning("⚠️ Vui lòng nhập Google API Key để tiếp tục phân tích.")
        else:
            try:
                genai.configure(api_key=google_api_key)
                
                # SỬA LỖI TẠI ĐÂY: Trả về chính xác 100% cấu trúc gọi model ban đầu của anh để tránh lỗi 404
                model = genai.GenerativeModel(model_name="gemini-1.5-pro")
                
                with st.status("🚀 Đang xử lý dữ liệu cuộc gọi...", expanded=True) as status:
                    audio_data = uploaded_file.read()
                    
                    status.write("🎧 Đang lắng nghe và nhận diện giọng nói...")
                    time.sleep(1)
                    status.write("🧠 Đang bóc tách tâm lý hành vi và lỗi sales...")
                    
                    prompt = """
                    Bạn là một chuyên gia huấn luyện kỹ năng Bán hàng (Sales Coach) gắt gao nhất, sở hữu tư duy phân tích tâm lý hành vi con người sâu sắc, đặc biệt nhạy bén với các dòng sản phẩm tài chính phức tạp như Bảo hiểm nhân thọ dòng IUL tại thị trường Mỹ. Nhiệm vụ của bạn là lắng nghe, mổ xẻ file ghi âm cuộc gọi tư vấn giữa nhân viên bảo hiểm (Sales) và khách hàng Việt Kiều, sau đó lập một bản báo cáo đánh giá cực kỳ chi tiết, sắc bén, không né tránh sai lầm và mang tính thực chiến cao.

                    Yêu cầu phân tích và xuất báo cáo đầy đủ theo đúng 9 mục sau đây (Không được gộp mục, không được bỏ sót mục nào):

                    1. TỔNG QUAN TÌNH HUỐNG & ĐỐI TƯỢNG: Phác họa rõ nét chân dung khách hàng (Ví dụ: Thợ nail, chủ tiệm, độ tuổi ước lượng, vùng bang cư trú, tâm lý lúc bắt máy) và bối cảnh diễn ra cuộc gọi.
                    
                    2. ĐIỂM CHẠM TÂM LÝ ĐẦU TIÊN (FIRST IMPRESSION): Đánh giá cách sales mở đầu cuộc gọi trong 15-30 giây đầu tiên. Có phá băng thành công không? Giọng điệu nói chuyện có 'đời', tự nhiên hằng ngày không hay bị dội do dùng văn viết máy móc, cứng nhắc?
                    
                    3. ĐÁNH GIÁ CHẤT LƯỢNG KHAI THÁC THÔNG TIN: Phân tích cách sales đặt câu hỏi để tìm hiểu nhu cầu của khách. Sales đã hỏi những câu hỏi khéo léo nào để nắm tình hình tài chính, cấu trúc gia đình (số con phụ thuộc, nhà cửa), và tình trạng sức khỏe? Những câu nào hỏi quá trực diện gây mất tự nhiên cần sửa đổi?
                    
                    4. LỖI THẢO MAI & ĂN HÙA (CRITICAL): Chỉ rõ những đoạn sales có hành vi khen ngợi giả tạo, thiếu chân thành để lấy lòng khách, hoặc đồng tình một cách vô điều kiện với những định kiến sai lầm của khách thay vì duy trì sự đúng đắn để đưa ra lời khuyên tài chính chuẩn xác.
                    
                    5. LỖI CỨNG NHẮC LÝ THUYẾT & AI-STYLE: Bóc tách những đoạn sales giải thích quyền lợi sản phẩm IUL (Cash Value, Cap, Floor, tính năng miễn thuế) một cách khô khan, mang tính dạy đời, nhồi nhét lý thuyết thay vì dùng văn nói tự nhiên, dễ hiểu giữa người với người.
                    
                    6. PHẢN BIỆN KHÁCH HÀNG (HANDLING OBJECTIONS): Khi khách đưa ra các từ chối hoặc lo ngại (Kinh tế khó khăn, vắng khách mùa đông, áp lực chi phí trả góp nhà xe), sales xử lý có thấu tình đạt lý không? Có áp dụng tâm lý học hành vi để giải tỏa nỗi sợ cho khách không?
                    
                    7. GÓT CHÂN ACHILLES & MẪU CÂU "ĐỔI ĐỜI": Tìm ra lỗi tâm lý hoặc kỹ thuật nặng nhất của sales khiến cuộc gọi thất bại. 
                       -> Chỉ dẫn: Giải thích tại sao nói như cũ là sai tâm lý. Đưa ra 2 phương án nói mới: Một phương án an toàn và một phương án "sát thủ" để nhân viên tập luyện.
                    
                    8. LỘ TRÌNH CẢI THIỆN: 3 việc cụ thể cần làm ngay.
                    
                    9. CÂU HỎI CHIẾN LƯỢC: 1 câu hỏi duy nhất để lật ngược thế trận.
                    """
                    
                    response = model.generate_content([prompt, {"mime_type": "audio/mpeg", "data": audio_data}])
                    time.sleep(1)
                    status.write("📝 Đang hoàn thiện báo cáo chi tiết...")
                    status.update(label="✅ Đã phân tích xong!", state="complete", expanded=False)

                # Hiển thị kết quả trong Card đã được CSS gốc định dạng
                st.markdown(f'<div class="analysis-card">{response.text}</div>', unsafe_allow_html=True)
                
                # Tải báo cáo gốc
                st.divider()
                st.download_button(
                    label="Tải báo cáo sạch 📥",
                    data=lam_sach_bao_cao(response.text),
                    file_name=f"Nexus_Analysis_{uploaded_file.name}.txt",
                    mime="text/plain"
                )
                    
            except Exception as e:
                st.error(f"Có lỗi xảy ra: {e}")


# =====================================================================
# CHẠY TÍNH NĂNG 2: FORM KHẢO SÁT & BÁO GIÁ THÔNG MINH (ZOOM UNIFIED STYLE)
# =====================================================================
elif menu_selection == "🎯 FORM KHẢO SÁT & BÁO GIÁ":
    st.markdown("<h2 style='color:#1E293B; font-size:26px; font-weight:700; margin-bottom:5px;'>Khảo Sát Khách Hàng Nail & Báo Giá IUL</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748B; font-size:14px; margin-bottom:25px;'>Hệ thống tự động phân tích sức khỏe bệnh lý và dòng tiền tài chính thực tế để gợi ý mức phí tối ưu.</p>", unsafe_allow_html=True)
    
    col_input, col_result = st.columns([1, 1], gap="large")
    
    with col_input:
        st.markdown('<div class="zoom-container-card">', unsafe_allow_html=True)
        
        st.markdown('<div class="zoom-highlight-header">1. Thông Tin Khách Hàng</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            gender = st.selectbox("Giới tính", ["Nữ", "Nam"])
        with c2:
            age = st.number_input("Tuổi hiện tại", min_value=1, max_value=100, value=35)
            
        st.markdown("<hr style='border:0; border-top:1px solid #E2E8F0; margin:24px 0;'>", unsafe_allow_html=True)
        
        st.markdown('<div class="zoom-highlight-header">2. Tình Trạng Sức Khỏe</div>', unsafe_allow_html=True)
        lung_habit = st.radio("Thói quen lá phổi", ["Không hút thuốc", "Có hút thuốc, vape, hoặc cần"], horizontal=True)
        health_status = st.selectbox(
            "Tình trạng bệnh lý hiện tại",
            [
                "Khỏe mạnh hoàn toàn / Bệnh lý cực nhẹ (Cao máu nhẹ, huyết áp nhẹ, men gan cao nhẹ, tiền tiểu đường, viêm gan B không hoạt động/không dùng thuốc)",
                "Có bệnh lý nền rõ ràng (Tiểu đường, Combo tiểu đường + mỡ máu/cao máu, bướu tuyến giáp lành, sỏi thận, sỏi mật)",
                "Bệnh lý nặng (Tim bẩm sinh, suy tim, suy thận, từng điều trị ung thư, đột quỵ, từng phẫu thuật nội tạng...)"
            ]
        )
        
        st.markdown("<hr style='border:0; border-top:1px solid #E2E8F0; margin:24px 0;'>", unsafe_allow_html=True)
        
        st.markdown('<div class="zoom-highlight-header">3. Dòng Tiền & Đời Sống tại Mỹ</div>', unsafe_allow_html=True)
        c3, c4 = st.columns(2)
        with c3:
            time_in_us = st.selectbox("Thời gian định cư ở Mỹ", ["Trên 3 năm", "Dưới 3 năm"])
        with c4:
            job_title = st.selectbox("Vị trí công việc", ["Thợ nail ăn chia 6/4", "Manager", "Chủ tiệm"])
            
        num_chairs = "Không áp dụng"
        if job_title in ["Manager", "Chủ tiệm"]:
            num_chairs = st.selectbox("Quy mô số ghế của tiệm", ["3-5 ghế", "6-8 ghế", "Trên 10 ghế"])
            
        c5, c6 = st.columns(2)
        with c5:
            marital_status = st.selectbox("Tình trạng hôn nhân", ["Đã kết hôn", "Độc thân"])
        with c6:
            num_children = st.selectbox("Số lượng con cái phụ thuộc", ["1", "2", "3", "4", "Chưa có con"])
            
        c7, c8 = st.columns(2)
        with c7:
            home_status = st.selectbox("Tình trạng nhà cửa tại Mỹ", ["Đã mua trả góp (Mortgage)", "Đang mướn nhà (Rent)"])
        with c8:
            retire_plan = st.selectbox("Dự kiến thời gian cày còn lại trước khi nghỉ hưu", ["10 - 20 năm nữa", "Trên 20 năm nữa", "Dưới 10 năm nữa"])
            
        st.markdown('</div>', unsafe_allow_html=True)

    with col_result:
        # --- LOGIC THẨM ĐỊNH RATING SỨC KHỎE ---
        rating_result = "Standard NTBC"
        if lung_habit == "Có hút thuốc, vape, hoặc cần":
            rating_result = "Standard TBC"
        else:
            if "Có bệnh lý nền rõ ràng" in health_status:
                rating_result = "Express Standard Non-Tobacco 1 (EX1)"
            elif "Bệnh lý nặng" in health_status:
                rating_result = "Express Standard Non-Tobacco 2 (EX2)"
                
        # --- LOGIC ĐỊNH HƯỚNG DÒNG TIỀN PHÍ ĐÓNG ---
        suggested_premium = 300
        if job_title == "Thợ nail ăn chia 6/4":
            suggested_premium = 180 if num_children in ["3", "4"] else 250
        elif job_title == "Manager":
            suggested_premium = 400
        elif job_title == "Chủ tiệm":
            if num_chairs == "3-5 ghế": suggested_premium = 450
            elif num_chairs == "6-8 ghế": suggested_premium = 700
            elif num_chairs == "Trên 10 ghế": suggested_premium = 1200
                
        if home_status == "Đang mướn nhà (Rent)" or time_in_us == "Dưới 3 năm":
            suggested_premium = int(suggested_premium * 0.85)
            
        calculated_face_amount = suggested_premium * 700  
        backup_premium = int(suggested_premium * 0.5)
        backup_face_amount = int(calculated_face_amount * 0.5)

        # --- HIỂN THỊ KẾT QUẢ CARD THEO PHONG CÁCH ZOOM ---
        st.markdown("<h3 style='color:#1E293B; font-size:16px; font-weight:700; margin-bottom:15px;'>KẾT QUẢ PHÂN TÍCH BIỂU PHÍ KHUYẾN NGHỊ</h3>", unsafe_allow_html=True)
        st.info(f"📋 **Rating Thẩm Định Định Hướng:** Hệ thống định hướng chạy bảng giá chuyên ngành **{rating_result}**")
        
        # Thẻ Gói Tối Ưu
        st.markdown(f"""
        <div class="zoom-pricing-card recommended-card">
            <div class="zoom-tag">✨ GÓI TỐI ƯU (RECOMMENDED)</div>
            <div class="price-text">${suggested_premium:,} <span style="font-size:14px; color:#64748B; font-weight:normal;">/ tháng</span></div>
            <div class="price-subtext" style="color:#1E293B;">${calculated_face_amount:,} Mệnh Giá Bảo Vệ</div>
            <div class="zoom-bullet">🔹 Thiết kế: Maximum Cash Value (Tích lũy tài sản hưu trí an toàn)</div>
            <div class="zoom-bullet">🔹 Tối ưu dòng tiền thặng dư để làm chỗ trú ẩn thuế hợp pháp cuối năm</div>
            <div class="zoom-bullet">🔹 Tiến trình đóng phí phù hợp trọn vẹn với quỹ thời gian cày cuốc {retire_plan} còn lại</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Thẻ Gói Dự Phòng
        st.markdown(f"""
        <div class="zoom-pricing-card">
            <div class="zoom-tag" style="background-color:#E2E8F0; color:#64748B;">GÓI DỰ PHÒNG CHỮA CHÁY</div>
            <div class="price-text" style="color:#64748B;">${backup_premium:,} <span style="font-size:14px; color:#64748B; font-weight:normal;">/ tháng</span></div>
            <div class="price-subtext" style="color:#1E293B;">${backup_face_amount:,} Mệnh Giá Bảo Vệ</div>
            <div class="zoom-bullet">🔸 Điểm tựa rút lui an toàn khi tiệm vắng khách hoặc bước vào mùa đông lạnh</div>
            <div class="zoom-bullet">🔸 Đảm bảo duy trì trọn vẹn quyền lợi bảo vệ thu nhập cho người phụ thuộc</div>
        </div>
        """, unsafe_allow_html=True)
