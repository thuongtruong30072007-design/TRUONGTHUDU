import streamlit as st

import pandas as pd

# 1. Cấu hình trang Streamlit
st.set_page_config(
    page_title="Công Cụ Rửa Tiền Của Bùi Đình Thương Trường",
    page_icon="💰",
    layout="wide"
)

# 2. Bảng biểu lãi suất tham chiếu theo kỳ hạn (%/năm)
INTEREST_RATES_BY_TERM = {
    1: 3.0,   # 1 tháng
    2: 3.0,   # 2 tháng
    3: 3.4,   # 3 tháng
    6: 4.5,   # 6 tháng
    9: 4.5,   # 9 tháng
    12: 5.2,  # 12 tháng
    18: 5.5,  # 18 tháng
    24: 5.7,  # 24 tháng
    36: 5.8,  # 36 tháng
    60: 6.0   # 60 tháng trở lên
}

def get_suggested_rate(term_months):
    """Hàm tìm lãi suất tương ứng với kỳ hạn"""
    matched_rate = 3.0
    for term, rate in sorted(INTEREST_RATES_BY_TERM.items()):
        if term_months >= term:
            matched_rate = rate
    return matched_rate

# Hiển thị Logo (Nếu có)
try:
    st.image("logo.jpg.jpg", width=150)
except Exception:
    pass

# Tiêu đề ứng dụng
st.title("💰 Công Cụ Tính Tiền Lãi Tiết Kiệm Tự Động")
st.write("Chỉ cần chọn **Số tiền gửi** và **Kỳ hạn**, hệ thống sẽ tự động áp dụng lãi suất và tính toán ngay lập tức!")

st.divider()

# Tạo 2 cột: Cột nhập liệu (bên trái) - Cột kết quả (bên phải)
col_input, col_result = st.columns([1, 1.2], gap="large")

with col_input:
    st.subheader("📥 Thông Tin Tiền Gửi")
    
    # 1. Nhập Số tiền gửi
    principal = st.number_input(
        "Số tiền gửi (VND):",
        min_value=1_000_000,
        max_value=100_000_000_000,
        value=100_000_000,
        step=10_000_000,
        format="%d"
    )
    st.caption(f"👉 **Số tiền:** {principal:,.0f} VND")

    # 2. Nhập Kỳ hạn gửi
    months = st.number_input(
        "Kỳ hạn gửi (Tháng):",
        min_value=1,
        max_value=120,
        value=12,
        step=1
    )

    # 3. Chọn Hình thức nhận lãi
    payment_method = st.selectbox(
        "Hình thức nhận lãi:",
        options=["Cuối kỳ", "Hàng tháng", "Hàng quý"]
    )

    # Tự động lấy lãi suất theo kỳ hạn
    interest_rate = get_suggested_rate(months)
    st.info(f"💡 **Mức lãi suất tự động áp dụng ({months} tháng):** `{interest_rate}%/năm`")

# ---------------- LOGIC TÍNH TOÁN TỰ ĐỘNG ----------------
r = interest_rate / 100

if payment_method == "Cuối kỳ":
    total_interest = principal * r * (months / 12)
    periodic_interest = total_interest
    period_label = "Tiền lãi nhận cuối kỳ"
    num_periods = 1

elif payment_method == "Hàng tháng":
    periodic_interest = principal * (r / 12)
    total_interest = periodic_interest * months
    period_label = "Tiền lãi nhận hàng tháng"
    num_periods = months

elif payment_method == "Hàng quý":
    periodic_interest = principal * (r / 4)
    num_periods = months / 3
    total_interest = periodic_interest * num_periods
    period_label = "Tiền lãi nhận hàng quý"

total_amount = principal + total_interest

# ---------------- HIỂN THỊ KẾT QUẢ TỨC THÌ ----------------
with col_result:
    st.subheader("📊 Kết Quả Tính Toán Tức Thì")

    # Hiển thị số liệu nổi bật bằng Card
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
        for m in range(1, months + 1):
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
