"""
Trang 7: Import / Export dữ liệu nhân viên và kết quả dự đoán.
"""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Import / Export | HR Analytics", page_icon="📁", layout="wide")

from utils.styles import apply_styles, page_header, section_header
from utils.data_manager import load_employees, get_template_excel, import_employees_from_df
from utils.history_manager import load_history
from utils.preprocessor import DEPT_OPTIONS, JOBROLE_OPTIONS

apply_styles()
page_header("📁 Import / Export",
            "Nhập dữ liệu từ Excel, tải file mẫu, xuất danh sách nhân viên và lịch sử")

# ── Tabs ─────────────────────────────────────────────────────
tab_import, tab_export = st.tabs(["📤 Import dữ liệu", "📥 Export dữ liệu"])

# ════════════════════════════════════════════════════════════
# TAB IMPORT
# ════════════════════════════════════════════════════════════
with tab_import:

    col_tmpl, col_up = st.columns([1, 2])

    with col_tmpl:
        section_header("1️⃣ Tải file mẫu")
        st.markdown("""
        <div class="info-box">
            Tải file Excel mẫu có đầy đủ cột cần thiết.
            Điền thông tin nhân viên vào file này rồi import lại.
        </div>
        """, unsafe_allow_html=True)

        tmpl_bytes = get_template_excel()
        st.download_button(
            "📥 Tải file mẫu (.xlsx)",
            data=tmpl_bytes,
            file_name="mau_nhan_vien.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type="primary"
        )

        st.markdown("**Các cột bắt buộc:**")
        required_cols = [
            'TenNhanVien', 'Department', 'JobRole', 'Age', 'Gender',
            'MaritalStatus', 'OverTime', 'MonthlyIncome'
        ]
        for c in required_cols:
            st.markdown(f"• `{c}`")

        st.markdown("**Lưu ý:**")
        st.markdown("""
        - Không cần cột `EmployeeNumber` (tự sinh)
        - Có thể để trống cột không bắt buộc
        - Không ghi đè dữ liệu cũ
        """)

    with col_up:
        section_header("2️⃣ Upload và Import")

        uploaded = st.file_uploader(
            "Chọn file Excel (.xlsx) hoặc CSV (.csv)",
            type=['xlsx', 'xls', 'csv'],
            help="File phải có cùng định dạng với file mẫu"
        )

        if uploaded is not None:
            try:
                if uploaded.name.endswith('.csv'):
                    import_df = pd.read_csv(uploaded)
                else:
                    import_df = pd.read_excel(uploaded)

                st.success(f"✅ Đọc file thành công: **{len(import_df)} hàng**, **{len(import_df.columns)} cột**")

                # Kiểm tra cột
                required = {'TenNhanVien', 'Department', 'JobRole', 'Age', 'Gender', 'MaritalStatus'}
                missing = required - set(import_df.columns)
                if missing:
                    st.error(f"❌ Thiếu các cột bắt buộc: {', '.join(missing)}")
                else:
                    # Preview
                    section_header("Preview dữ liệu (10 hàng đầu)")
                    st.dataframe(import_df.head(10), use_container_width=True, hide_index=True)

                    # Kiểm tra dữ liệu
                    issues = []
                    if import_df['Age'].isna().any():
                        issues.append("⚠️ Có hàng thiếu cột Age")
                    if import_df['MonthlyIncome'].isna().any() if 'MonthlyIncome' in import_df.columns else False:
                        issues.append("⚠️ Có hàng thiếu MonthlyIncome")
                    invalid_dept = import_df[~import_df['Department'].isin(DEPT_OPTIONS + [None])]
                    if len(invalid_dept) > 0:
                        issues.append(f"⚠️ {len(invalid_dept)} hàng có Department không hợp lệ")

                    if issues:
                        for issue in issues:
                            st.warning(issue)
                        st.markdown("""
                        <div class="warning-box">
                            Các cảnh báo trên không ngăn import, nhưng hãy kiểm tra lại dữ liệu.
                        </div>
                        """, unsafe_allow_html=True)

                    # Nút import
                    if st.button("⬆️ Xác nhận Import dữ liệu", type="primary", use_container_width=True):
                        with st.spinner("Đang import..."):
                            ok, msg, n_added, n_err = import_employees_from_df(import_df)
                        if ok:
                            st.success(f"✅ {msg}")
                            st.balloons()
                            st.cache_data.clear()
                        else:
                            st.error(f"❌ {msg}")

            except Exception as e:
                st.error(f"❌ Lỗi đọc file: {e}")

# ════════════════════════════════════════════════════════════
# TAB EXPORT
# ════════════════════════════════════════════════════════════
with tab_export:

    section_header("Xuất dữ liệu")

    df_emp = load_employees()
    df_hist = load_history()

    # Lọc trước khi export
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        exp_dept = st.selectbox("Lọc phòng ban (để export)", ['Tất cả'] + DEPT_OPTIONS)
    with col_f2:
        exp_type = st.selectbox("Loại dữ liệu xuất", [
            "Danh sách nhân viên",
            "Lịch sử dự đoán",
            "Tất cả (nhiều sheet Excel)",
        ])

    if exp_dept != 'Tất cả' and 'Department' in df_emp.columns:
        df_emp_filtered = df_emp[df_emp['Department'] == exp_dept]
    else:
        df_emp_filtered = df_emp

    st.caption(f"→ {len(df_emp_filtered)} nhân viên sẽ được xuất")

    # Export buttons
    col_e1, col_e2, col_e3 = st.columns(3)

    def make_excel_single(df, sheet_name):
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name=sheet_name)
        return buf.getvalue()

    def make_excel_multi():
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
            df_emp_filtered.to_excel(writer, index=False, sheet_name='NhanVien')
            df_hist.to_excel(writer, index=False, sheet_name='LichSuDuDoan')
        return buf.getvalue()

    with col_e1:
        section_header("Excel (.xlsx)")
        if exp_type == "Danh sách nhân viên":
            data = make_excel_single(df_emp_filtered, 'NhanVien')
            fname = "nhan_vien.xlsx"
        elif exp_type == "Lịch sử dự đoán":
            data = make_excel_single(df_hist, 'LichSu')
            fname = "lich_su.xlsx"
        else:
            data = make_excel_multi()
            fname = "hr_analytics_export.xlsx"

        st.download_button(
            "📥 Tải Excel",
            data=data,
            file_name=fname,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type="primary"
        )

    with col_e2:
        section_header("CSV (.csv)")
        if exp_type == "Danh sách nhân viên":
            csv_data = df_emp_filtered.to_csv(index=False).encode('utf-8-sig')
            fname_csv = "nhan_vien.csv"
        elif exp_type == "Lịch sử dự đoán":
            csv_data = df_hist.to_csv(index=False).encode('utf-8-sig')
            fname_csv = "lich_su.csv"
        else:
            csv_data = df_emp_filtered.to_csv(index=False).encode('utf-8-sig')
            fname_csv = "nhan_vien.csv"

        st.download_button(
            "📄 Tải CSV",
            data=csv_data,
            file_name=fname_csv,
            mime="text/csv",
            use_container_width=True
        )

    with col_e3:
        section_header("Thống kê")
        st.metric("👥 Nhân viên trong hệ thống", len(df_emp))
        st.metric("📋 Bản ghi lịch sử", len(df_hist))
        if 'Department' in df_emp.columns:
            dept_counts = df_emp['Department'].value_counts()
            for dept, cnt in dept_counts.items():
                st.markdown(f"• **{dept}**: {cnt} người")
