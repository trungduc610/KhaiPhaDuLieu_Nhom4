"""
Trang 6: Lịch sử Dự đoán — Xem, lọc và xóa lịch sử.
"""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from datetime import date, timedelta
import io

st.set_page_config(page_title="Lịch sử | HR Analytics", page_icon="📋", layout="wide")

from utils.styles import apply_styles, page_header, section_header
from utils.history_manager import load_history, filter_history, delete_history_records

apply_styles()
page_header("📋 Lịch sử Dự đoán",
            "Tra cứu, xem chi tiết và quản lý các kết quả dự đoán đã lưu")

# ── Bộ lọc ───────────────────────────────────────────────────
section_header("🔽 Bộ lọc")
fc1, fc2, fc3, fc4, fc5 = st.columns([2, 2, 2, 2, 1])
with fc1:
    date_from = st.date_input("Từ ngày", value=date.today() - timedelta(days=30))
with fc2:
    date_to = st.date_input("Đến ngày", value=date.today())
with fc3:
    emp_search = st.text_input("Mã / Tên nhân viên", placeholder="Tìm kiếm...")
with fc4:
    loai_options = ['Tất cả', 'Đơn lẻ', 'Hàng loạt', 'What-if']
    loai_filter = st.selectbox("Loại dự đoán", loai_options)
with fc5:
    st.markdown("<br>", unsafe_allow_html=True)
    clear_filter = st.button("🔄 Đặt lại", use_container_width=True)

if clear_filter:
    date_from = date.today() - timedelta(days=30)
    date_to = date.today()
    emp_search = ''
    loai_filter = 'Tất cả'

df_hist = filter_history(
    date_from=date_from,
    date_to=date_to,
    emp_number=emp_search if emp_search else None,
    loai=loai_filter
)

# ── Thống kê nhanh ────────────────────────────────────────────
all_hist = load_history()
col_s1, col_s2, col_s3, col_s4 = st.columns(4)
with col_s1:
    st.metric("📌 Tổng bản ghi", len(all_hist))
with col_s2:
    st.metric("🔍 Kết quả lọc", len(df_hist))
with col_s3:
    n_quit = (df_hist['KetQua'] == 'Nghỉ việc').sum() if len(df_hist) > 0 else 0
    st.metric("📉 Dự đoán Nghỉ việc", n_quit)
with col_s4:
    n_high = (df_hist['MucRuiRo'] == 'Cao').sum() if len(df_hist) > 0 else 0
    st.metric("🔴 Nguy cơ cao", n_high)

st.markdown("---")

if len(df_hist) == 0:
    st.markdown("""
    <div class="info-box" style="text-align:center; padding:2rem;">
        📭 Chưa có lịch sử dự đoán nào phù hợp điều kiện lọc.
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Danh sách lịch sử ─────────────────────────────────────────
section_header(f"📜 Lịch sử ({len(df_hist)} bản ghi)")

# Hiển thị bảng
display_cols = ['ID', 'ThoiGian', 'LoaiDuDoan', 'EmployeeNumber',
                'TenNhanVien', 'XacSuat', 'KetQua', 'MucRuiRo']
display_cols = [c for c in display_cols if c in df_hist.columns]
display = df_hist[display_cols].copy()
if 'XacSuat' in display.columns:
    display['XacSuat'] = (display['XacSuat'] * 100).round(1).astype(str) + '%'

display.columns = [
    {'ID': 'ID', 'ThoiGian': 'Thời gian', 'LoaiDuDoan': 'Loại',
     'EmployeeNumber': 'Mã NV', 'TenNhanVien': 'Tên NV',
     'XacSuat': 'Xác suất', 'KetQua': 'Kết quả', 'MucRuiRo': 'Mức rủi ro'}.get(c, c)
    for c in display_cols
]

# Multiselect xóa
st.dataframe(display, use_container_width=True, hide_index=True, height=350,
             column_config={
                 'ID': st.column_config.NumberColumn('ID', width='small'),
                 'Xác suất': st.column_config.TextColumn('Xác suất', width='small'),
             })

# ── Xem chi tiết bản ghi ─────────────────────────────────────
section_header("🔎 Xem chi tiết")
if len(df_hist) > 0:
    id_options = df_hist['ID'].tolist()
    sel_id = st.selectbox("Chọn bản ghi (ID)", id_options)
    detail = df_hist[df_hist['ID'] == sel_id].iloc[0]

    with st.expander(f"📄 Chi tiết bản ghi #{sel_id}", expanded=True):
        d1, d2 = st.columns(2)
        with d1:
            st.markdown(f"**Thời gian:** {detail.get('ThoiGian','')}")
            st.markdown(f"**Loại dự đoán:** {detail.get('LoaiDuDoan','')}")
            st.markdown(f"**Nhân viên:** {detail.get('TenNhanVien','')} (#{detail.get('EmployeeNumber','')})")
        with d2:
            xac_suat = float(detail.get('XacSuat', 0)) * 100
            risk_color = '#ef4444' if detail.get('MucRuiRo') == 'Cao' else \
                         '#f59e0b' if detail.get('MucRuiRo') == 'Trung bình' else '#10b981'
            st.markdown(f"**Kết quả:** {detail.get('KetQua','')}")
            st.markdown(f"**Xác suất:** <span style='color:{risk_color};font-weight:700'>{xac_suat:.1f}%</span>", unsafe_allow_html=True)
            st.markdown(f"**Mức rủi ro:** {detail.get('MucRuiRo','')}")
        if detail.get('GhiChu'):
            st.markdown(f"**Ghi chú / Nguyên nhân:**")
            st.code(str(detail.get('GhiChu', '')), language=None)

# ── Xóa bản ghi ──────────────────────────────────────────────
section_header("🗑️ Xóa lịch sử")
col_x1, col_x2, col_x3 = st.columns([3, 2, 2])
with col_x1:
    ids_to_delete = st.multiselect("Chọn ID cần xóa", id_options)
with col_x2:
    st.markdown("<br>", unsafe_allow_html=True)
    if ids_to_delete and st.button(f"🗑️ Xóa {len(ids_to_delete)} bản ghi", type="primary", use_container_width=True):
        delete_history_records(ids_to_delete)
        st.success(f"✅ Đã xóa {len(ids_to_delete)} bản ghi!")
        st.rerun()
with col_x3:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑️ Xóa tất cả kết quả lọc", use_container_width=True):
        st.session_state['confirm_clear'] = True

if st.session_state.get('confirm_clear'):
    st.warning(f"⚠️ Xóa toàn bộ {len(df_hist)} bản ghi trong kết quả lọc?")
    cc1, cc2 = st.columns(2)
    with cc1:
        if st.button("✅ Xác nhận xóa", type="primary"):
            delete_history_records(df_hist['ID'].tolist())
            st.session_state['confirm_clear'] = False
            st.success("✅ Đã xóa!")
            st.rerun()
    with cc2:
        if st.button("❌ Hủy"):
            st.session_state['confirm_clear'] = False

# ── Export lịch sử ────────────────────────────────────────────
section_header("📥 Xuất lịch sử")
col_e1, col_e2 = st.columns(2)
with col_e1:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
        df_hist.to_excel(writer, index=False, sheet_name='LichSu')
    st.download_button(
        "📥 Tải lịch sử (Excel)", data=buf.getvalue(),
        file_name="lich_su_du_doan.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
with col_e2:
    csv_data = df_hist.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        "📄 Tải lịch sử (CSV)", data=csv_data,
        file_name="lich_su_du_doan.csv",
        mime="text/csv",
        use_container_width=True
    )
