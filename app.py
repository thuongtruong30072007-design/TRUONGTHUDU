import streamlit as st
import pandas as pd

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="Công Cụ Rửa Tiền của Bùi Đình Thương Trường",
    page_icon="💰",
    layout="wide"
)

# Tiêu đề ứng dụng
st.title("💰 Công Cụ Rửa Tiền của Bùi Đình Thương Trường")
st.write("Nhập thông số tiền gửi bên dưới để tính toán chính xác tiền lãi nhận được theo các hình thức nhận lãi khác nhau.")

st.divider()

# Tạo 2 cột cho phần nhập liệu và phần kết quả
col_input, col_result = st.columns([1, 1.2], gap="large")

with col_input:
    st.subheader("📥 Thông Tin Tiền Gửi")
    
    # 1. Số tiền gửi
    principal = st.number_input(
        "Số tiền gửi (VND):",
        min_value=1_000_000,
        max_value=100_000_000_000,
        value=100_000_000,
        step=10_000_000,
        format="%d"
    )
    st.caption(f"👉 **Số tiền bằng chữ:** {principal:,.0f} VND")

    # 2. Kỳ hạn gửi
    months = st.number_input(
        "Kỳ hạn gửi (Tháng):",
        min_value=1,
        max_value=120,
        value=12,
        step=1
    )

    # 3. Lãi suất
    interest_rate = st.number_input(
        "Lãi suất (%/năm):",
        min_value=0.1,
        max_value=30.0,
        value=6.5,
        step=0.1,
        format="%.2f"
    )

    # 4. Hình thức nhận lãi
    payment_method = st.selectbox(
        "Hình thức nhận lãi:",
        options=["Cuối kỳ", "Hàng tháng", "Hàng quý"]
    )

    # Nút bấm tính toán
    calculate_btn = st.button("🧮 Tính Tiền Lãi", type="primary", use_container_width=True)

# Xử lý logic tính toán
r = interest_rate / 100

if payment_method == "Cuối kỳ":
    # Lãi cuối kỳ = Số tiền * Lãi suất năm * (Số tháng / 12)
    total_interest = principal * r * (months / 12)
    periodic_interest = total_interest
    period_label = "Tiền lãi nhận cuối kỳ"
    num_periods = 1

elif payment_method == "Hàng tháng":
    # Lãi hàng tháng = Số tiền * (Lãi suất năm / 12)
    periodic_interest = principal * (r / 12)
    total_interest = periodic_interest * months
    period_label = "Tiền lãi nhận hàng tháng"
    num_periods = months

elif payment_method == "Hàng quý":
    # Lãi hàng quý = Số tiền * (Lãi suất năm / 4)
    periodic_interest = principal * (r / 4)
    # Tố kỳ hạn theo quý (mỗi quý = 3 tháng)
    num_periods = months / 3
    total_interest = periodic_interest * num_periods
    period_label = "Tiền lãi nhận hàng quý"

total_amount = principal + total_interest

with col_result:
    st.subheader("📊 Kết Quả Tính Toán")

    # Hiển thị kết quả tóm tắt bằng Metric Cards
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        st.metric(
            label="Tổng tiền gốc & lãi",
            value=f"{total_amount:,.0f} VND"
        )
        st.metric(
            label="Tổng tiền lãi thu được",
            value=f"{total_interest:,.0f} VND"
        )

    with m_col2:
        st.metric(
            label=period_label,
            value=f"{periodic_interest:,.0f} VND"
        )
        st.metric(
            label="Số lần nhận lãi",
            value=f"{num_periods:.1f}".rstrip('0').rstrip('.') + " lần"
        )

    st.divider()

    # Bảng lịch trình nhận lãi chi tiết
    st.write("📅 **Lịch Trình Nhận Lãi Chi Tiết:**")
    
    schedule_data = []
    
    if payment_method == "Cuối kỳ":
        schedule_data.append({
            "Kỳ nhận lãi": f"Tháng thứ {months} (Cuối kỳ)",
            "Tiền lãi (VND)": total_interest,
            "Tiền gốc (VND)": principal,
            "Tổng nhận (VND)": total_amount
        })
    elif payment_method == "Hàng tháng":
        accumulated_interest = 0
        for m in range(1, months + 1):
            accumulated_interest += periodic_interest
            is_last = (m == months)
            p_payout = principal if is_last else 0
            schedule_data.append({
                "Kỳ nhận lãi": f"Tháng {m}",
                "Tiền lãi (VND)": periodic_interest,
                "Tiền gốc (VND)": p_payout,
                "Tổng nhận (VND)": periodic_interest + p_payout
            })
    elif payment_method == "Hàng quý":
        total_quarters = int(months // 3)
        remaining_months = months % 3
        
        for q in range(1, total_quarters + 1):
            is_last = (q == total_quarters and remaining_months == 0)
            p_payout = principal if is_last else 0
            schedule_data.append({
                "Kỳ nhận lãi": f"Quý {q} (Tháng {q*3})",
                "Tiền lãi (VND)": periodic_interest,
                "Tiền gốc (VND)": p_payout,
                "Tổng nhận (VND)": periodic_interest + p_payout
            })
            
        # Tính phần dư tháng lẻ nếu kỳ hạn không chia hết cho 3
        if remaining_months > 0:
            extra_interest = principal * r * (remaining_months / 12)
            schedule_data.append({
                "Kỳ nhận lãi": f"Tháng lẻ cuối ({remaining_months} tháng)",
                "Tiền lãi (VND)": extra_interest,
                "Tiền gốc (VND)": principal,
                "Tổng nhận (VND)": extra_interest + principal
            })

    df = pd.DataFrame(schedule_data)
    st.dataframe(
        df.style.format({
            "Tiền lãi (VND)": "{:,.0f}",
            "Tiền gốc (VND)": "{:,.0f}",
            "Tổng nhận (VND)": "{:,.0f}"
        }),
        use_container_width=True,
        hide_index=True
    )
