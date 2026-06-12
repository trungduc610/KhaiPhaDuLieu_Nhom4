"""
app.py - Trang chủ / Landing page của ứng dụng HR Analytics.
"""

import os
import sys
import streamlit as st

# Thêm thư mục gốc vào sys.path để import utils
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(
    page_title="HR Analytics — Dự đoán Nghỉ việc",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.styles import apply_styles

apply_styles()

# ── Sidebar info ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0;">
        <div style="font-size:2.5rem">👥</div>
        <div style="font-size:1.1rem; font-weight:700; color:#a5b4fc;">HR Analytics</div>
        <div style="font-size:0.75rem; color:#64748b; margin-top:0.2rem;">Dự đoán Nghỉ việc Nhân viên</div>
    </div>
    <hr style="border-color:rgba(99,102,241,0.2); margin: 0.5rem 0 1rem;">
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:0.78rem; color:#64748b; padding: 0 0.5rem;">
    <b style="color:#a5b4fc;">Mô hình:</b> CART (Decision Tree)<br>
    <b style="color:#a5b4fc;">Đồ án:</b> Khai phá Dữ liệu<br>
    <b style="color:#a5b4fc;">Đề tài:</b> Phân tích nguyên nhân nhân viên nghỉ việc
    </div>
    """, unsafe_allow_html=True)

# ── Hero section ─────────────────────────────────────────────
st.markdown("""
<div style="
    background: linear-gradient(135deg, rgba(99,102,241,0.2) 0%, rgba(6,182,212,0.1) 100%);
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 20px;
    padding: 3rem 2rem;
    text-align: center;
    margin-bottom: 2rem;
">
    <div style="font-size:3rem; margin-bottom:0.5rem;">🏢</div>
    <h1 style="
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #a5b4fc, #67e8f9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 0 0.5rem;
    ">HR Analytics — Dự đoán Nghỉ việc</h1>
    <p style="color:#94a3b8; font-size:1rem; max-width:600px; margin:0 auto;">
        Hệ thống phân tích và dự đoán nguy cơ nghỉ việc của nhân viên
        sử dụng mô hình <strong style="color:#a5b4fc;">CART (Decision Tree)</strong>,
        hỗ trợ nhà quản lý đưa ra quyết định giữ chân nhân tài.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Feature cards ─────────────────────────────────────────────
features = [
    ("📊", "Dashboard", "Tổng quan tình trạng nhân sự, biểu đồ phân tích và cảnh báo nguy cơ"),
    ("👥", "Quản lý Nhân viên", "Xem, thêm, sửa, xóa thông tin nhân viên trong hệ thống"),
    ("🔍", "Dự đoán 1 Nhân viên", "Phân tích nguy cơ và giải thích nguyên nhân qua cây CART"),
    ("📈", "Dự đoán Hàng loạt", "Chạy mô hình cho nhiều nhân viên cùng lúc"),
    ("🔄", "What-if Analysis", "Mô phỏng kịch bản: điều gì xảy ra nếu thay đổi thông tin?"),
    ("📋", "Lịch sử Dự đoán", "Tra cứu và quản lý kết quả dự đoán đã lưu"),
    ("📁", "Import / Export", "Nhập dữ liệu từ Excel, xuất báo cáo kết quả"),
]

cols_row1 = st.columns(4)
cols_row2 = st.columns(3)
all_cols = cols_row1 + cols_row2

for i, (icon, title, desc) in enumerate(features):
    with all_cols[i]:
        st.markdown(f"""
        <div class="metric-card" style="text-align:left; padding:1.2rem;">
            <div style="font-size:1.8rem; margin-bottom:0.5rem;">{icon}</div>
            <div style="font-weight:700; color:#e2e8f0; font-size:0.95rem; margin-bottom:0.3rem;">{title}</div>
            <div style="color:#64748b; font-size:0.78rem; line-height:1.4;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

# ── Quick stats ───────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)

try:
    import pandas as pd
    from utils.data_manager import load_employees
    df_emp = load_employees()
    n_total = len(df_emp)

    # Kiểm tra model
    model_trained = os.path.exists(os.path.join(
        os.path.dirname(__file__), 'model', 'cart_model.pkl'
    ))

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("👤 Tổng nhân viên", f"{n_total:,}")
    with c2:
        st.metric("🤖 Trạng thái Model", "✅ Đã train" if model_trained else "❌ Chưa train")
    with c3:
        if 'Attrition' in df_emp.columns:
            n_yes = (df_emp['Attrition'].str.lower() == 'yes').sum()
            st.metric("📉 Đã nghỉ việc (thực tế)", f"{n_yes} ({n_yes/n_total:.1%})")

    if not model_trained:
        st.warning("⚠️ **Model chưa được train!** Hãy chạy lệnh bên dưới trước khi sử dụng.")
        st.code("python model/train_model.py", language="bash")

except Exception as e:
    st.info("ℹ️ Hệ thống sẵn sàng. Chọn trang từ sidebar để bắt đầu.")

st.markdown("""
<div style="text-align:center; color:#374151; font-size:0.75rem; margin-top:2rem;">
    Đồ án Khai phá Dữ liệu • Dự đoán nguy cơ và phân tích nguyên nhân nhân viên nghỉ việc
</div>
""", unsafe_allow_html=True)
