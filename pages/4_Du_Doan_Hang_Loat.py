"""
Trang 4: Dự đoán hàng loạt / toàn bộ nhân viên.
"""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io

st.set_page_config(page_title="Dự đoán Hàng loạt | HR Analytics", page_icon="📈", layout="wide")

from utils.styles import apply_styles, page_header, section_header, metric_card
from utils.data_manager import load_employees
from utils.predictor import predict_batch
from utils.history_manager import add_history_batch
from utils.preprocessor import get_risk_level, DEPT_OPTIONS, JOBROLE_OPTIONS

apply_styles()
page_header("📈 Dự đoán Hàng loạt / Toàn bộ",
            "Chọn nhiều nhân viên hoặc toàn bộ, chạy dự đoán hàng loạt và xem thống kê")

PLOTLY_DARK = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#e2e8f0"),
    margin=dict(l=10, r=10, t=40, b=10),
)

df_all = load_employees()

# ── Bộ chọn phạm vi ──────────────────────────────────────────
section_header("1️⃣ Chọn phạm vi dự đoán")

tab_all, tab_filter, tab_select = st.tabs(["📌 Toàn bộ nhân viên", "🔽 Theo bộ lọc", "☑️ Chọn thủ công"])

selected_df = None

with tab_all:
    st.markdown(f"""
    <div class="info-box">
        Sẽ dự đoán toàn bộ <b>{len(df_all)}</b> nhân viên trong hệ thống.
    </div>
    """, unsafe_allow_html=True)
    if st.button("🚀 Chạy dự đoán toàn bộ", type="primary", key="btn_all"):
        selected_df = df_all.copy()

with tab_filter:
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        dept_f = st.selectbox("Phòng ban", ['Tất cả'] + DEPT_OPTIONS, key='batch_dept')
    with fc2:
        role_f = st.selectbox("Chức vụ", ['Tất cả'] + JOBROLE_OPTIONS, key='batch_role')
    with fc3:
        ot_f = st.selectbox("Làm thêm giờ", ['Tất cả', 'Yes', 'No'], key='batch_ot')

    filtered = df_all.copy()
    if dept_f != 'Tất cả': filtered = filtered[filtered['Department'] == dept_f]
    if role_f != 'Tất cả': filtered = filtered[filtered['JobRole'] == role_f]
    if ot_f != 'Tất cả':  filtered = filtered[filtered['OverTime'] == ot_f]

    st.caption(f"→ {len(filtered)} nhân viên phù hợp điều kiện lọc")
    if st.button(f"🚀 Chạy dự đoán ({len(filtered)} NV)", type="primary", key="btn_filter"):
        selected_df = filtered.copy()

with tab_select:
    emp_labels = df_all.apply(
        lambda r: f"{r['TenNhanVien']} (#{int(r['EmployeeNumber'])})", axis=1
    ).tolist()
    chosen = st.multiselect("Chọn nhân viên", emp_labels, max_selections=200,
                             placeholder="Tìm kiếm hoặc chọn nhân viên...")
    if chosen:
        chosen_ids = [emp_labels.index(c) for c in chosen]
        sel_preview = df_all.iloc[chosen_ids]
        st.caption(f"→ Đã chọn {len(chosen)} nhân viên")
        if st.button(f"🚀 Chạy dự đoán ({len(chosen)} NV)", type="primary", key="btn_select"):
            selected_df = sel_preview.copy()

# ── Thực hiện dự đoán ─────────────────────────────────────────
if selected_df is not None and len(selected_df) > 0:
    with st.spinner(f"⏳ Đang dự đoán {len(selected_df)} nhân viên..."):
        result_df = predict_batch(selected_df)
    st.session_state['batch_result'] = result_df
    st.success(f"✅ Hoàn tất dự đoán {len(result_df)} nhân viên!")

# ── Hiển thị kết quả ─────────────────────────────────────────
if 'batch_result' in st.session_state:
    result_df = st.session_state['batch_result']

    n_total = len(result_df)
    n_high   = (result_df['MucRuiRo'] == 'Cao').sum()
    n_medium = (result_df['MucRuiRo'] == 'Trung bình').sum()
    n_low    = (result_df['MucRuiRo'] == 'Thấp').sum()
    n_quit   = (result_df['NhanNhan'] == 'Nghỉ việc').sum()

    st.markdown("---")
    section_header("2️⃣ Thống kê kết quả")

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: metric_card("👥", f"{n_total:,}", "Tổng dự đoán")
    with c2: metric_card("🔴", f"{n_high:,}", "Nguy cơ Cao", "#ef4444")
    with c3: metric_card("🟡", f"{n_medium:,}", "Nguy cơ TB", "#f59e0b")
    with c4: metric_card("🟢", f"{n_low:,}", "Nguy cơ Thấp", "#10b981")
    with c5: metric_card("📉", f"{n_quit:,}", "Dự đoán Nghỉ")

    st.markdown("<br>", unsafe_allow_html=True)

    # Biểu đồ
    col_p, col_b = st.columns(2)

    with col_p:
        section_header("Phân bố mức rủi ro")
        pie_data = pd.DataFrame({
            'Mức': ['Cao (>70%)', 'Trung bình (40-70%)', 'Thấp (<40%)'],
            'Số lượng': [n_high, n_medium, n_low]
        })
        fig_pie = px.pie(pie_data, values='Số lượng', names='Mức', hole=0.5,
                          color='Mức', color_discrete_map={
                              'Cao (>70%)': '#ef4444',
                              'Trung bình (40-70%)': '#f59e0b',
                              'Thấp (<40%)': '#10b981'})
        fig_pie.update_traces(textinfo='percent+label', textposition='outside')
        fig_pie.update_layout(**PLOTLY_DARK, height=280, showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_b:
        section_header("Top 10 nhân viên nguy cơ cao nhất")
        top10 = result_df.nlargest(10, 'XacSuatNghiViec')[['TenNhanVien', 'XacSuatNghiViec']].copy()
        top10['XacSuatNghiViec'] = top10['XacSuatNghiViec'] * 100
        fig_bar = px.bar(top10, x='XacSuatNghiViec', y='TenNhanVien', orientation='h',
                          color='XacSuatNghiViec',
                          color_continuous_scale=['#f59e0b', '#ef4444'],
                          labels={'XacSuatNghiViec': 'Xác suất (%)', 'TenNhanVien': ''},
                          text='XacSuatNghiViec')
        fig_bar.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_bar.update_layout(**PLOTLY_DARK, height=280, coloraxis_showscale=False,
                               yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_bar, use_container_width=True)

    # ── Bảng kết quả đầy đủ ───────────────────────────────────
    section_header("3️⃣ Kết quả chi tiết")

    # Tô màu theo mức rủi ro
    show_cols = ['EmployeeNumber', 'TenNhanVien', 'Department', 'JobRole',
                 'MonthlyIncome', 'OverTime', 'XacSuatNghiViec', 'NhanNhan', 'MucRuiRo']
    show_cols = [c for c in show_cols if c in result_df.columns]
    display = result_df[show_cols].copy()
    display['XacSuatNghiViec'] = (display['XacSuatNghiViec'] * 100).round(1)
    display = display.sort_values('XacSuatNghiViec', ascending=False).reset_index(drop=True)
    display.columns = [
        {'EmployeeNumber': 'Mã NV', 'TenNhanVien': 'Tên NV', 'Department': 'Phòng ban',
         'JobRole': 'Chức vụ', 'MonthlyIncome': 'Thu nhập ($)', 'OverTime': 'OT',
         'XacSuatNghiViec': 'Xác suất (%)', 'NhanNhan': 'Dự đoán', 'MucRuiRo': 'Mức rủi ro'}.get(c, c)
        for c in show_cols
    ]

    st.dataframe(
        display, use_container_width=True, hide_index=True, height=400,
        column_config={
            'Xác suất (%)': st.column_config.ProgressColumn(
                'Xác suất (%)', min_value=0, max_value=100, format="%.1f%%"
            ),
        }
    )

    # ── Lưu & Export ──────────────────────────────────────────
    col_save, col_exp1, col_exp2 = st.columns(3)
    with col_save:
        if st.button("💾 Lưu toàn bộ vào lịch sử", type="primary", use_container_width=True):
            records = []
            for _, row in result_df.iterrows():
                records.append({
                    'LoaiDuDoan': 'Hàng loạt',
                    'EmployeeNumber': int(row.get('EmployeeNumber', 0)),
                    'TenNhanVien': str(row.get('TenNhanVien', '')),
                    'XacSuat': float(row.get('XacSuatNghiViec', 0)),
                    'KetQua': str(row.get('NhanNhan', '')),
                    'MucRuiRo': str(row.get('MucRuiRo', '')),
                })
            n = add_history_batch(records)
            st.success(f"✅ Đã lưu {n} bản ghi vào lịch sử!")

    with col_exp1:
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
            result_df.to_excel(writer, index=False, sheet_name='KetQuaDuDoan')
        st.download_button(
            "📥 Tải Excel", data=buf.getvalue(),
            file_name="ket_qua_du_doan.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    with col_exp2:
        csv_data = result_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            "📄 Tải CSV", data=csv_data,
            file_name="ket_qua_du_doan.csv",
            mime="text/csv",
            use_container_width=True
        )
else:
    st.markdown("""
    <div class="info-box" style="text-align:center; padding:2rem; margin-top:1rem;">
        👆 Chọn phạm vi dự đoán ở trên và nhấn <b>🚀 Chạy dự đoán</b>
    </div>
    """, unsafe_allow_html=True)
