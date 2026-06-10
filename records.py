import streamlit as st
import google.generativeai as genai
import os
import time

# --- 1. CẤU HÌNH GIAO DIỆN TỔNG THỂ (ZOOM UNIFIED STYLE) ---
st.set_page_config(page_title="The Nexus | Behavioral Analysis", layout="wide")

# Inject CSS đồng bộ toàn bộ website trên nền xám trắng mịn cao cấp
st.markdown("""
<style>
    /* Ép toàn bộ màu nền hệ thống về tone xám trắng mịn cao cấp */
    .main, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #F8F9FA !important;
    }
    
    /* Đồng bộ giao diện Sidebar */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0 !important;
    }
    
    /* Thiết kế khối hộp (Panel/Card) đồng nhất cho cả 2 tính năng */
    .zoom-container-card {
        background-color: #FFFFFF !important;
        padding: 32px;
        border-radius: 16px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.03);
        margin-bottom: 24px;
    }
    
    /* Hiệu ứng mượt mà khi di chuột qua các thẻ báo giá */
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
    
    /* Thẻ được khuyên dùng đặc biệt (Gói Tối Ưu) */
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
    
    /* Tag nhãn nhỏ bên trong card */
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
    
    /* Font số tiền lớn rõ nét màu xanh Zoom */
    .price-text {
        font-size: 38px;
        font-weight: 800;
        color: #0B5CFF;
        margin: 10px 0;
        font-family: 'Inter', sans-serif;
    }
    
    /* Font chữ nhãn nhập liệu */
    label, p, .stRadio > label {
        color: #1E293B !important;
        font-weight: 500 !important;
    }
    
    /* Đường gạch ngang tinh tế */
    hr {
        border: 0;
        border-top: 1px solid #E2E8F0 !important;
        margin: 24px 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Đọc file CSS gốc của anh để giữ nguyên định dạng cũ (.analysis-card)
if os.path.exists("style.css"):
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Giữ nguyên 100% logic làm sạch báo cáo cũ
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


# --- 2. SIDEBAR ĐIỀU HƯỚNG TẬP TRUNG TỆP MÀU APPS ---
with st.sidebar:
    st.title("⚙️ ĐIỀU KHIỂN")
    
    # Menu chuyển trang nằm gọn bên Sidebar
    menu_selection = st.radio(
        "Lựa chọn tính năng",
        ["🎙️ PHÂN TÍCH CUỘC GỌI", "🎯 FORM KHẢO SÁT & BÁO GIÁ"],
        index=0
    )
    
    st.divider()
    google_api_key = st.secrets.get("GOOGLE_API_KEY", "")
    if not google_api_key:
        google_api_key = st.text_input("Nhập Google API Key:", type="password")


# =====================================================================
# MỤC 1: PHÂN TÍCH CUỘC GỌI (GIỮ NGUYÊN TUYỆT ĐỐI TOÀN BỘ LOGIC GỐC)
# =====================================================================
if menu_selection == "🎙️ PHÂN TÍCH CUỘC GỌI":
    st.markdown("<h2 style='color:#1E293B; font-size:26px; font-weight:700; margin-bottom:20px;'>Hệ Thống Phân Tích Tâm Lý Hành Vi Cuộc Gọi</h2>", unsafe_allow_html=True)
    
    st.markdown('<div class="zoom-container-card">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Kéo thả hoặc chọn file ghi âm cuộc gọi (.mp3, .wav)", type=["mp3", "wav"])
    st.markdown('</div>', unsafe_allow_html=True)
    
    if uploaded_file:
        if not google_api_key:
            st.warning("⚠️ Vui lòng nhập Google API Key để tiếp tục phân tích.")
        else:
            try:
                genai.configure(api_key=google_api_key)
                model = genai.GenerativeModel("gemini-1.5-pro")
                
                with st.status("🚀 Đang xử lý dữ liệu cuộc gọi...", expanded=True) as status:
                    audio_data = uploaded_file.read()
                    
                    status.write("🎧 Đang lắng nghe và nhận diện giọng nói...")
                    time.sleep(1)
                    status.write("🧠 Đang bóc tách tâm lý hành vi và lỗi sales...")
                    
                    prompt = """
                    Bạn là một chuyên gia huấn luyện kỹ năng Bán hàng (Sales Coach) gắt gao nhất, sở hữu tư duy phân tích tâm lý hành vi con người sâu sắc, đặc biệt nhạy bén với các dòng sản phẩm tài chính phức tạp như Bảo hiểm nhân thọ dòng IUL tại thị trường Mỹ. 
                    Nhiệm vụ của bạn là lắng nghe, mổ xẻ file ghi âm cuộc gọi tư vấn giữa nhân viên bảo hiểm (Sales) và khách hàng Việt Kiều, sau đó lập một bản báo cáo đánh giá cực kỳ chi tiết, sắc bén, không né tránh sai lầm và mang tính thực chiến cao.

                    Yêu cầu phân tích và xuất báo cáo đầy đủ theo đúng 9 mục sau đây (Không được gộp mục, không được bỏ sót mục nào):

                    1. TỔNG QUAN TÌNH HUỐNG & ĐỐI TƯỢNG: Phác họa rõ nét chân dung khách hàng (Thợ nail, chủ tiệm, tuổi tác, vùng bang, tâm lý lúc bắt máy) và bối cảnh cuộc gọi.
                    
                    2. ĐIỂM CHẠM TÂM LÝ ĐẦU TIÊN (FIRST IMPRESSION): Đánh giá 15-30 giây đầu tiên. Sales có phá băng thành công không? Giọng điệu có đời, tự nhiên không hay bị dội và mang văn viết máy móc?
                    
                    3. ĐÁNH GIÁ CHẤT LƯỢNG KHAI THÁC THÔNG TIN: Sales đã hỏi những câu hỏi khéo léo nào để nắm tình hình tài chính, gia đình (số con, nhà cửa, thời gian ở Mỹ) và sức khỏe của khách? Những câu nào hỏi quá trực diện gây mất tự nhiên?
                    
                    4. LỖI THẢO MAI & ĂN HÙA (CRITICAL): Chỉ rõ những đoạn sales khen khách một cách giả tạo, thiếu chân thành, hoặc đồng tình vô điều kiện với định kiến sai lầm của khách thay vì duy trì sự đúng đắn để cho lời khuyên.
                    
                    5. LỖI CỨNG NHẮC LÝ THUYẾT & AI-STYLE: Bóc tách những đoạn sales giải thích thuật ngữ bảo hiểm (IUL, Cash Value, Cap, Floor, Tax-free) một cách khô khan, mang tính dạy đời, nhồi nhét lý thuyết cứng thay vì dùng văn nói hằng ngày.
                    
                    6. PHẢN BIỆN KHÁCH HÀNG (HANDLING OBJECTIONS): Khi khách đưa ra từ chối (Lo ngại kinh tế khó khăn, vắng khách mùa đông, sợ đứt gánh giữa chừng), sales xử lý có thấu tình đạt lý không? Có dùng tâm lý học hành vi để xoay chuyển không?
                    
                    7. GÓT CHÂN ACHILLES & MẪU CÂU "ĐỔI ĐỜI": Lỗi tâm lý nặng nhất của sales trong cuộc gọi này là gì? Giải thích tại sao cách nói cũ sai tâm lý. Đưa ra 2 phương án nói mới: Một phương án an toàn và một phương án "sát thủ" để nhân viên tập luyện.
                    
                    8. LỘ TRÌNH CẢI THIỆN: 3 việc cụ thể, thực tế sales cần sửa đổi và thực hành ngay lập tức sau cuộc gọi này.
                    
                    9. CÂU HỎI CHIẾN LƯỢC: Đưa ra 1 câu hỏi duy nhất mang tính điều hướng tâm lý cao để sales có thể dùng lật ngược thế trận hoặc chốt deal thành công với tệp khách hàng này.
                    """
                    
                    response = model.generate_content([prompt, {"mime_type": "audio/mpeg", "data": audio_data}])
                    time.sleep(1)
                    status.write("📝 Đang hoàn thiện báo cáo chi tiết...")
                    status.update(label="✅ Đã phân tích xong!", state="complete", expanded=False)

                # Hiển thị kết quả đúng định dạng cũ
                st.markdown(f'<div class="analysis-card">{response.text}</div>', unsafe_allow_html=True)
                
                # Tải báo cáo cũ
                st.divider()
                st.download_button(
                    label="Tải báo cáo sạch 📥",
                    data=lam_sach_bao_cao(response.text),
                    file_name=f"Nexus_Analysis_{uploaded_file.name}.txt",
                    mime="text/plain"
                )
                    
            except Exception as e:
                st.error(f"Có lỗi xảy ra trong quá trình phân tích: {e}")


# =====================================================================
# MỤC 2: FORM KHẢO SÁT & BÁO GIÁ THÔNG MINH (TRỌN VẸN LOGIC THỰC CHIẾN)
# =====================================================================
elif menu_selection == "🎯 FORM KHẢO SÁT & BÁO GIÁ":
    st.markdown("<h2 style='color:#1E293B; font-size:26px; font-weight:700; margin-bottom:5px;'>Khảo Sát Khách Hàng Nail & Báo Giá IUL</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748B; font-size:14px; margin-bottom:25px;'>Hệ thống tự động phân tích sức khỏe bệnh lý và dòng tiền tài chính thực tế để gợi ý mức phí tối ưu.</p>", unsafe_allow_html=True)
    
    # Thiết kế bố cục hai cột cân bằng thị giác (Tỷ lệ 5:5)
    col_input, col_result = st.columns([1, 1], gap="large")
    
    with col_input:
        st.markdown('<div class="zoom-container-card">', unsafe_allow_html=True)
        
        # Cụm 1: Thông tin khách hàng cơ bản
        st.markdown('<div class="zoom-highlight-header">1. Thông Tin Khách Hàng</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            gender = st.selectbox("Giới tính", ["Nữ", "Nam"])
        with c2:
            age = st.number_input("Tuổi hiện tại", min_value=1, max_value=100, value=35)
            
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Cụm 2: Thẩm định sức khỏe & bệnh lý chi tiết
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
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Cụm 3: Khảo sát dòng tiền công việc & đời sống tại Mỹ
        st.markdown('<div class="zoom-highlight-header">3. Dòng Tiền & Đời Sống tại Mỹ</div>', unsafe_allow_html=True)
        c3, c4 = st.columns(2)
        with c3:
            time_in_us = st.selectbox("Thời gian định cư ở Mỹ", ["Trên 3 năm", "Dưới 3 năm"])
        with c4:
            job_title = st.selectbox("Vị trí công việc", ["Thợ nail ăn chia 6/4", "Manager", "Chủ tiệm"])
            
        # Biến số quy mô số ghế của tiệm
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
        # --- LOGIC 1: ĐỊNH HƯỚNG TAB RATING THEO CHUẨN UNDERWRITING CỦA ANH ---
        rating_result = "Standard NTBC"
        if lung_habit == "Có hút thuốc, vape, hoặc cần":
            rating_result = "Standard TBC"  # Hút thuốc, vape, cần map thẳng nhóm hút thuốc
        else:
            if "Có bệnh lý nền rõ ràng" in health_status:
                rating_result = "Express Standard Non-Tobacco 1 (EX1)"  # Bệnh nền rõ ràng, tiểu đường, sỏi...
            elif "Bệnh lý nặng" in health_status:
                rating_result = "Express Standard Non-Tobacco 2 (EX2)"  # Các ca nặng tim mạch, ung thư, suy thận...
                
        # --- LOGIC 2: CHẤM ĐIỂM DÒNG TIỀN & XUẤT TARGET PREMIUM ---
        suggested_premium = 300  # Mức sàn mặc định cơ bản
        
        if job_title == "Thợ nail ăn chia 6/4":
            if num_children in ["3", "4"]:
                suggested_premium = 180  # Con đông, chi phí sinh hoạt cao, thiết kế gói nhỏ vừa sức
            else:
                suggested_premium = 250  # Thợ nail bình thường, ít con gánh nặng ít hơn
        elif job_title == "Manager":
            suggested_premium = 400      # Cấp quản lý, thu nhập ổn định khá
        elif job_title == "Chủ tiệm":
            if num_chairs == "3-5 ghế":
                suggested_premium = 450  # Chủ tiệm quy mô nhỏ
            elif num_chairs == "6-8 ghế":
                suggested_premium = 700  # Chủ tiệm quy mô vừa, dòng tiền mạnh, lo ngại bài toán thuế
            elif num_chairs == "Trên 10 ghế":
                suggested_premium = 1200 # Chủ tiệm lớn, đại gia ngành nail, dòng tiền thặng dư rất cao
                
        # Tinh chỉnh chiết khấu an toàn dòng tiền theo thời gian ở Mỹ và tình trạng nhà cửa
        if home_status == "Đang mướn nhà (Rent)" or time_in_us == "Dưới 3 năm":
            suggested_premium = int(suggested_premium * 0.85)  # Chiết khấu giảm 15% dòng tiền để tránh đứt gánh
            
        # Giả lập tính toán mệnh giá (Sau này kết nối trực tiếp vào sheet gsheet để quét đúng dòng/tuổi)
        calculated_face_amount = suggested_premium * 700  
        backup_premium = int(suggested_premium * 0.5)
        backup_face_amount = int(calculated_face_amount * 0.5)

        # --- HIỂN THỊ CỘT BIỂU PHÍ KẾT QUẢ TỆP MÀU XÁM TRẮNG TÍNH TẾ ---
        st.markdown("<h3 style='color:#1E293B; font-size:16px; font-weight:700; margin-bottom:15px;'>KẾT QUẢ PHÂN TÍCH BIỂU PHÍ KHUYẾN NGHỊ</h3>", unsafe_allow_html=True)
        st.info(f"📋 **Rating Thẩm Định Định Hướng:** Hệ thống khuyến nghị chạy bảng minh họa ở Tab: **{rating_result}**")
        
        # Thẻ 1: Gói Tối Ưu (Recommended Card)
        st.markdown(f"""
        <div class="zoom-pricing-card recommended-card">
            <div class="zoom-tag">✨ GÓI TỐI ƯU (RECOMMENDED)</div>
            <div class="price-text">${suggested_premium:,} <span style="font-size:14px; color:#64748B; font-weight:normal;">/ tháng</span></div>
            <div class="price-subtext" style="color:#1E293B;">${calculated_face_amount:,} Mệnh Giá Bảo Vệ</div>
            <div class="zoom-bullet">🔹 Thiết kế: Tối ưu tích lũy dòng tiền (Maximum Cash Value) làm quỹ hưu trí tương lai.</div>
            <div class="zoom-bullet">🔹 Tận dụng tốt dòng tiền thặng dư để làm chỗ trú ẩn, né nghĩa vụ thuế cá nhân/doanh nghiệp hợp pháp cuối năm.</div>
            <div class="zoom-bullet">🔹 Tiến trình đóng phí phù hợp trọn vẹn với quỹ thời gian cày cuốc {retire_plan} còn lại của khách.</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Thẻ 2: Gói Dự Phòng (Flex Card)
        st.markdown(f"""
        <div class="zoom-pricing-card">
            <div class="zoom-tag" style="background-color:#E2E8F0; color:#64748B;">GÓI DỰ PHÒNG CHỮA CHÁY</div>
            <div class="price-text" style="color:#64748B;">${backup_premium:,} <span style="font-size:14px; color:#64748B; font-weight:normal;">/ tháng</span></div>
            <div class="price-subtext" style="color:#1E293B;">${backup_face_amount:,} Mệnh Giá Bảo Vệ</div>
            <div class="zoom-bullet">🔸 Sử dụng làm phương án lùi binh khi khách hàng lo ngại áp lực tài chính, sụt giảm doanh thu vào mùa đông tiệm vắng.</div>
            <div class="zoom-bullet">🔸 Đảm bảo duy trì trọn vẹn quyền lợi bảo vệ thu nhập cốt lõi cho gia đình và {num_children if num_children != 'Chưa có con' else 'người'} phụ thuộc.</div>
            <div class="zoom-bullet">🔸 Kịch bản xử lý từ chối: Hướng dẫn khách đóng mức phí này trước, mùa hè đông khách có tiền đóng bù thêm vào sau để nuôi Cash Value nhờ tính linh hoạt của IUL.</div>
        </div>
        """, unsafe_allow_html=True)
