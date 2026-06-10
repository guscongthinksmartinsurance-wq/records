import streamlit as st
import google.generativeai as genai
import os
import time

# --- CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="The Nexus | Bound By Trust", layout="wide")

# Đọc file CSS riêng (Giữ nguyên 100% cấu trúc gốc của anh)
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Inject thêm CSS bổ sung cho phần Form - Tối ưu hiển thị đa chế độ (Light/Dark Mode)
st.markdown("""
<style>
    /* 1. KHỐI HỘP HAI BÊN: Tự động dùng màu nền bề mặt hệ thống (Card Background) */
    .zoom-container-card {
        background-color: var(--background-color) !important;
        padding: 32px;
        border-radius: 16px;
        border: 1px solid var(--text-color);
        opacity: 0.95;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.03);
        margin-bottom: 24px;
    }
    
    /* Thẻ hiển thị bảng giá kết quả bên phải */
    .zoom-pricing-card {
        background-color: var(--background-color) !important;
        border-radius: 16px;
        padding: 28px;
        margin-bottom: 20px;
        border: 1px solid var(--text-color);
        opacity: 0.95;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.02);
        transition: all 0.3s ease;
    }
    .zoom-pricing-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 30px rgba(11, 92, 255, 0.15);
        border-color: #0B5CFF !important;
    }
    
    /* Gói Tối Ưu Khuyên Dùng - Giữ viền xanh đặc trưng của Zoom */
    .recommended-card {
        border: 2px solid #0B5CFF !important;
    }
    
    /* 2. HIGHLIGHT TIÊU ĐỀ KIỂU ZOOM CHUYÊN NGHIỆP */
    .zoom-highlight-header {
        color: #0B5CFF !important; /* Luôn giữ màu xanh thương hiệu Zoom */
        font-size: 16px;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        background-color: rgba(11, 92, 255, 0.1) !important; /* Nền xanh nhạt trong suốt, tự thích ứng nền tối */
        padding: 8px 16px;
        border-radius: 8px;
        display: inline-block;
        margin-bottom: 20px;
        border-left: 4px solid #0B5CFF;
    }
    
    /* Tag nhỏ nhãn hiệu */
    .zoom-tag {
        background-color: #0B5CFF;
        color: white !important;
        font-size: 11px;
        font-weight: bold;
        padding: 4px 12px;
        border-radius: 20px;
        display: inline-block;
        margin-bottom: 12px;
        text-transform: uppercase;
    }
    
    /* Giá tiền hiển thị to rõ nổi bật */
    .price-text {
        font-size: 38px;
        font-weight: 800;
        color: #0B5CFF !important; /* Màu xanh gốc của Zoom */
        margin: 10px 0;
        font-family: 'Inter', sans-serif;
    }
    
    /* 3. ĐỒNG BỘ CHỮ: Ép dùng biến chữ hệ thống, tự động trắng khi nền đen, đen khi nền trắng */
    .zoom-container-card label, 
    .zoom-container-card p, 
    .zoom-container-card span,
    .price-subtext,
    .zoom-bullet {
        color: var(--text-color) !important; 
        font-weight: 500 !important;
    }
    
    /* Làm mịn khoảng cách dòng lựa chọn của Radio */
    div[data-testid="stRadio"] > div {
        gap: 10px;
    }

    /* Đường gạch ngang chia dòng tự động ăn theo màu chữ mờ */
    .zoom-container-card hr {
        border: 0;
        border-top: 1px solid var(--text-color) !important;
        opacity: 0.2;
        margin: 24px 0 !important;
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
        ["PHÂN TÍCH CUỘC GỌI", "FORM KHẢO SÁT & BÁO GIÁ"],
        index=0
    )
    
    st.divider()
    
    # Giữ nguyên logic lấy API Key gốc của anh
    google_api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        google_api_key = st.text_input("API Key", type="password")
    
    st.markdown("---")
    # Thông số độ gắt cho anh Công tùy chỉnh
    temp = st.slider("Độ 'Gắt' & Sáng tạo (Temperature)", 0.0, 1.0, 0.7, 0.1)
    st.caption("Thấp (0.0): Phân tích logic, thực tế. Cao (1.0): Rất gắt, xoáy sâu tâm lý.")
    
    st.markdown("---")
    st.info("Dòng IUL - National Life Group")

# =====================================================================
# CHẠY TÍNH NĂNG 1: PHÂN TÍCH CUỘC GỌI (BÊ NGUYÊN VĂN 100% CODE CŨ VÀ CẤU TRÚC MODEL GỐC)
# =====================================================================
if menu_selection == "PHÂN TÍCH CUỘC GỌI":
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


# =====================================================================
# CHẠY TÍNH NĂNG 2: FORM KHẢO SÁT & GỢI Ý BÁO GIÁ CHIẾN LƯỢC CỦA ANH CONG
# =====================================================================
elif menu_selection == "FORM KHẢO SÁT & BÁO GIÁ":
    st.markdown("<h2 style='color:#1E293B; font-size:26px; font-weight:700; margin-bottom:5px;'>Khảo Sát Khách Hàng Nail & Báo Giá IUL</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748B; font-size:14px; margin-bottom:25px;'>Hệ thống gợi ý tầm giá định hướng chiến lược giúp sales mở lời đàm phán dòng tiền phù hợp với chân dung khách hàng.</p>", unsafe_allow_html=True)
    
    col_input, col_result = st.columns([1, 1], gap="large")
    
    with col_input:
        st.markdown('<div class="zoom-container-card">', unsafe_allow_html=True)
        
        st.markdown('<div class="zoom-highlight-header">1. Thông Tin Khách Hàng</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            gender = st.selectbox("Giới tính", ["Nữ", "Nam"])
        with c2:
            age = st.number_input("Tuổi hiện tại", min_value=0, max_value=100, value=35)
            
        st.markdown("<hr>", unsafe_allow_html=True)
        
        st.markdown('<div class="zoom-highlight-header">2. Tình Trạng Sức Khỏe</div>', unsafe_allow_html=True)
        lung_habit = st.radio("Thói quen lá phổi", ["Không hút thuốc", "Có hút thuốc, vape, hoặc cần"], horizontal=True)
        
        health_status = st.radio(
            "Tình trạng bệnh lý hiện tại",
            [
                "Khỏe mạnh hoàn toàn / Bệnh lý cực nhẹ (Cao máu nhẹ, huyết áp nhẹ, men gan cao nhẹ, tiền tiểu đường, viêm gan B không hoạt động)",
                "Có bệnh lý nền rõ ràng (Tiểu đường, Combo tiểu đường + mỡ máu/cao máu, bướu tuyến giáp lành, sỏi thận, sỏi mật)",
                "Bệnh lý nặng (Tim bẩm sinh, suy tim, suy thận, từng điều trị ung thư, đột quỵ, từng phẫu thuật nội tạng...)"
            ]
        )
        
        st.markdown("<hr>", unsafe_allow_html=True)
        
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
        # --- BƯỚC 1: XÁC ĐỊNH MỨC GIÁ GỐC THEO PHÂN KHÚC TUỔI CHUẨN ---
        base_low, base_high = 150, 200  # Mặc định dưới 35 tuổi
        
        if 36 <= age <= 50:
            base_low, base_high = 200, 400
        elif 51 <= age <= 65:
            base_low, base_high = 300, 500
        elif age > 65:
            base_low, base_high = 500, 800  # Phân khúc lão niên

        # --- BƯỚC 2: TRA ĐỊNH HƯỚNG RATING VÀ TỰ ĐỘNG CỘNG PHẠT SỨC KHỎE SÒNG PHẲNG ---
        rating_result = "Standard NTBC"
        risk_multiplier = 1.0  # Hệ số giữ nguyên cho nhóm khỏe mạnh
        
        if lung_habit == "Có hút thuốc, vape, hoặc cần":
            rating_result = "Standard TBC"
            risk_multiplier = 1.20  # Nhóm có khói tăng phạt 20%
        else:
            if "Có bệnh lý nền rõ ràng" in health_status:
                rating_result = "Express Standard Non-Tobacco 1 (EX1)"
                risk_multiplier = 1.15  # Nhóm bệnh lý nền EX1 tăng phạt 15% (An toàn về giá)
            elif "Bệnh lý nặng" in health_status:
                rating_result = "Express Standard Non-Tobacco 2 (EX2)"
                risk_multiplier = 1.35  # Nhóm bệnh lý nặng EX2 tăng phạt 35%

        # Áp trọng số sức khỏe vào tầm giá gốc
        suggested_low = int(base_low * risk_multiplier)
        suggested_high = int(base_high * risk_multiplier)

        # --- BƯỚC 3: CO GIÃN THEO CHÂN DUNG DÒNG TIỀN NGHỀ NGHIỆP CỦA KHÁCH ---
        # Nếu khách là đại gia ngành nail (Chủ tiệm lớn), đẩy cao định hướng để tư vấn trú ẩn thuế hợp pháp
        if job_title == "Chủ tiệm" and num_chairs == "Trên 10 ghế":
            suggested_low = int(suggested_low * 1.5)
            suggested_high = int(suggested_high * 1.8)
        # Nếu khách gánh nặng tài chính cao (Thợ nail đông con, đang mướn nhà), ghìm nhẹ về mức an toàn cận dưới
        elif job_title == "Thợ nail ăn chia 6/4" and (num_children in ["3", "4"] or home_status == "Đang mướn nhà (Rent)"):
            suggested_high = int(suggested_high * 0.85)

        # Đóng gói số liệu cuối cùng cho hai Thẻ báo giá chiến lược
        optimal_premium = int((suggested_low + suggested_high) / 2)
        backup_premium = int(suggested_low)

        # --- HIỂN THỊ KẾT QUẢ ĐỊNH HƯỚNG ---
        st.markdown("<h3 style='color:#1E293B; font-size:16px; font-weight:700; margin-bottom:15px;'>KẾT QUẢ ĐỊNH HƯỚNG TẦM GIÁ CHIẾN LƯỢC</h3>", unsafe_allow_html=True)
        st.info(f"📋 **Định hướng chạy bảng minh họa hãng:** Chạy cho khách ở Tab nhóm: **{rating_result}**")
        
        # Thẻ Gói Tối ưu
        st.markdown(f"""
        <div class="zoom-pricing-card recommended-card">
            <div class="zoom-tag">✨ TẦM GIÁ TỐI ƯU (RECOMMENDED)</div>
            <div class="price-text">${optimal_premium:,} <span style="font-size:14px; color:#94A3B8; font-weight:normal;">/ tháng</span></div>
            <div class="price-subtext">Khung thương lượng đề xuất: ${suggested_low:,} - ${suggested_high:,} / tháng</div>
            <div class="zoom-bullet">🔹 Định hướng thiết kế: Tập trung tối đa vào nuôi dòng tiền tích lũy (Maximum Cash Value) làm quỹ hưu trí tương lai cho khách.</div>
            <div class="zoom-bullet">🔹 Định hướng kịch bản: {"Khai thác bài toán trú ẩn, giảm nghĩa vụ quyết toán thuế cuối năm cho chủ doanh nghiệp." if job_title == 'Chủ tiệm' else 'Tạo chỗ trú ẩn an toàn cho dòng tiền thặng dư, tăng tốc lãi kép miễn thuế.'}</div>
            <div class="zoom-bullet">🔹 Tiến trình đóng phí phù hợp trọn vẹn với quỹ thời gian cày cuốc {retire_plan} còn lại của khách tại Mỹ.</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Thẻ Gói Dự phòng
        st.markdown(f"""
        <div class="zoom-pricing-card">
            <div class="zoom-tag" style="background-color:#232936; color:#94A3B8;">PHƯƠNG ÁN DỰ PHÒNG CHỮA CHÁY</div>
            <div class="price-text" style="color:#94A3B8;">${backup_premium:,} <span style="font-size:14px; color:#94A3B8; font-weight:normal;">/ tháng</span></div>
            <div class="zoom-bullet">🔸 Sử dụng làm phương án lùi binh khi khách hàng lo ngại áp lực kinh tế sụt giảm, tiệm vắng khách mùa đông lạnh hoặc lo gánh nặng trả góp nhà xe.</div>
            <div class="zoom-bullet">🔸 Kịch bản xử lý từ chối: Hướng dẫn khách chốt ở mức an toàn này trước để kích hoạt trọn vẹn quyền lợi bảo vệ thu nhập cốt lõi cho gia đình, mùa hè đông khách có tiền thặng dư thì đóng bù thêm vào nuôi Cash Value sau nhờ tính linh hoạt của IUL.</div>
        </div>
        """, unsafe_allow_html=True)
