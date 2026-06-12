"""
Trang 2: Quản lý Nhân viên — Xem, Thêm, Sửa, Xóa trong cùng màn hình.
"""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Nhân viên | HR Analytics", page_icon="👥", layout="wide")

from utils.styles import apply_styles, page_header, section_header
from utils.data_manager import (load_employees, save_employees, add_employee,
                                  update_employee, delete_employee, get_employee)
from utils.preprocessor import (DEPT_OPTIONS, JOBROLE_OPTIONS, EDUCATIONFIELD_OPTIONS,
                                  BUSINESSTRAVEL_OPTIONS, MARITALSTATUS_OPTIONS,
                                  GENDER_OPTIONS, FIELD_LABELS)

apply_styles()
page_header("👥 Quản lý Nhân viên",
            "Xem danh sách, tìm kiếm, thêm mới, chỉnh sửa và xóa nhân viên")

# ── Session state ─────────────────────────────────────────────
if 'nv_action' not in st.session_state:
    st.session_state.nv_action = None  # 'add' | 'edit' | None
if 'nv_edit_id' not in st.session_state:
    st.session_state.nv_edit_id = None


def render_employee_form(mode='add', existing=None):
    """Render form thêm/sửa nhân viên."""
    title = "✏️ Chỉnh sửa nhân viên" if mode == 'edit' else "➕ Thêm nhân viên mới"
    section_header(title)
    e = existing.to_dict() if existing is not None else {}

    with st.form(key=f'form_{mode}'):
        st.markdown("**Thông tin cơ bản**")
        c1, c2, c3 = st.columns(3)
        with c1:
            ten = st.text_input("Tên nhân viên *", value=str(e.get('TenNhanVien', '')))
            dept = st.selectbox("Phòng ban *", DEPT_OPTIONS,
                                 index=DEPT_OPTIONS.index(str(e.get('Department', DEPT_OPTIONS[0])))
                                 if str(e.get('Department','')) in DEPT_OPTIONS else 0)
            gender = st.selectbox("Giới tính", GENDER_OPTIONS,
                                   index=0 if str(e.get('Gender','Male')) == 'Male' else 1)
        with c2:
            jobrole = st.selectbox("Chức vụ *", JOBROLE_OPTIONS,
                                    index=JOBROLE_OPTIONS.index(str(e.get('JobRole', JOBROLE_OPTIONS[0])))
                                    if str(e.get('JobRole','')) in JOBROLE_OPTIONS else 0)
            marital = st.selectbox("Hôn nhân", MARITALSTATUS_OPTIONS,
                                    index=MARITALSTATUS_OPTIONS.index(str(e.get('MaritalStatus', 'Single')))
                                    if str(e.get('MaritalStatus','')) in MARITALSTATUS_OPTIONS else 0)
            age = st.number_input("Tuổi *", 18, 65, int(e.get('Age', 30)))
        with c3:
            ef = st.selectbox("Lĩnh vực học vấn", EDUCATIONFIELD_OPTIONS,
                               index=EDUCATIONFIELD_OPTIONS.index(str(e.get('EducationField', EDUCATIONFIELD_OPTIONS[0])))
                               if str(e.get('EducationField','')) in EDUCATIONFIELD_OPTIONS else 0)
            bt = st.selectbox("Tần suất công tác", BUSINESSTRAVEL_OPTIONS,
                               index=BUSINESSTRAVEL_OPTIONS.index(str(e.get('BusinessTravel', 'Travel_Rarely')))
                               if str(e.get('BusinessTravel','')) in BUSINESSTRAVEL_OPTIONS else 1)
            education = st.selectbox("Trình độ (1-5)", [1,2,3,4,5],
                                      index=int(e.get('Education', 3))-1)

        st.markdown("**Thu nhập & Tài chính**")
        c4, c5, c6 = st.columns(3)
        with c4:
            monthly_income = st.number_input("Thu nhập tháng ($)", 1000, 200000,
                                              int(e.get('MonthlyIncome', 5000)), step=100)
            daily_rate = st.number_input("Lương ngày ($)", 100, 1500,
                                          int(e.get('DailyRate', 800)), step=10)
        with c5:
            hourly_rate = st.number_input("Lương giờ ($)", 30, 150,
                                           int(e.get('HourlyRate', 65)), step=1)
            monthly_rate = st.number_input("Tỷ lệ tháng", 2000, 27000,
                                            int(e.get('MonthlyRate', 14000)), step=100)
        with c6:
            pct_hike = st.number_input("Tăng lương (%)", 11, 25, int(e.get('PercentSalaryHike', 14)))
            stock = st.selectbox("Mức cổ phiếu (0-3)", [0,1,2,3],
                                  index=int(e.get('StockOptionLevel', 1)))

        st.markdown("**Thâm niên & Công việc**")
        c7, c8, c9 = st.columns(3)
        with c7:
            overtime = st.selectbox("Làm thêm giờ", ['No', 'Yes'],
                                     index=0 if str(e.get('OverTime','No')) == 'No' else 1)
            job_level = st.selectbox("Cấp độ (1-5)", [1,2,3,4,5],
                                      index=int(e.get('JobLevel', 2))-1)
            total_yrs = st.number_input("Tổng năm kinh nghiệm", 0, 40,
                                         int(e.get('TotalWorkingYears', 8)))
        with c8:
            yrs_company = st.number_input("Năm tại công ty", 0, 40,
                                           int(e.get('YearsAtCompany', 4)))
            yrs_role = st.number_input("Năm ở vị trí hiện tại", 0, 20,
                                        int(e.get('YearsInCurrentRole', 2)))
            yrs_promo = st.number_input("Năm từ lần thăng chức gần nhất", 0, 15,
                                         int(e.get('YearsSinceLastPromotion', 1)))
        with c9:
            yrs_mgr = st.number_input("Năm với quản lý hiện tại", 0, 20,
                                       int(e.get('YearsWithCurrManager', 3)))
            num_comp = st.number_input("Số công ty đã làm", 0, 10,
                                        int(e.get('NumCompaniesWorked', 2)))
            training = st.number_input("Số lần đào tạo năm qua", 0, 6,
                                        int(e.get('TrainingTimesLastYear', 3)))

        st.markdown("**Mức độ hài lòng**")
        c10, c11, c12 = st.columns(3)
        with c10:
            job_sat = st.select_slider("Hài lòng công việc (1-4)", [1,2,3,4],
                                        value=int(e.get('JobSatisfaction', 3)))
            env_sat = st.select_slider("Hài lòng môi trường (1-4)", [1,2,3,4],
                                        value=int(e.get('EnvironmentSatisfaction', 3)))
        with c11:
            rel_sat = st.select_slider("Hài lòng quan hệ (1-4)", [1,2,3,4],
                                        value=int(e.get('RelationshipSatisfaction', 3)))
            wlb = st.select_slider("Cân bằng cuộc sống (1-4)", [1,2,3,4],
                                    value=int(e.get('WorkLifeBalance', 3)))
        with c12:
            job_inv = st.select_slider("Mức tham gia (1-4)", [1,2,3,4],
                                        value=int(e.get('JobInvolvement', 3)))
            perf = st.select_slider("Đánh giá hiệu suất (3-4)", [3,4],
                                     value=int(e.get('PerformanceRating', 3)))
            distance = st.number_input("Khoảng cách nhà (km)", 1, 30,
                                        int(e.get('DistanceFromHome', 5)))

        col_submit, col_cancel = st.columns([1, 4])
        with col_submit:
            submitted = st.form_submit_button(
                "💾 Lưu" if mode == 'edit' else "➕ Thêm mới",
                type="primary", use_container_width=True
            )
        with col_cancel:
            cancelled = st.form_submit_button("❌ Hủy", use_container_width=False)

    if cancelled:
        st.session_state.nv_action = None
        st.session_state.nv_edit_id = None
        st.rerun()

    if submitted:
        if not ten.strip():
            st.error("Vui lòng nhập tên nhân viên!")
            return

        data = dict(
            TenNhanVien=ten.strip(), Department=dept, JobRole=jobrole,
            Gender=gender, MaritalStatus=marital, Age=age,
            EducationField=ef, BusinessTravel=bt, Education=education,
            MonthlyIncome=monthly_income, DailyRate=daily_rate,
            HourlyRate=hourly_rate, MonthlyRate=monthly_rate,
            PercentSalaryHike=pct_hike, StockOptionLevel=stock,
            OverTime=overtime, JobLevel=job_level,
            TotalWorkingYears=total_yrs, YearsAtCompany=yrs_company,
            YearsInCurrentRole=yrs_role, YearsSinceLastPromotion=yrs_promo,
            YearsWithCurrManager=yrs_mgr, NumCompaniesWorked=num_comp,
            TrainingTimesLastYear=training, JobSatisfaction=job_sat,
            EnvironmentSatisfaction=env_sat, RelationshipSatisfaction=rel_sat,
            WorkLifeBalance=wlb, JobInvolvement=job_inv,
            PerformanceRating=perf, DistanceFromHome=distance,
        )

        if mode == 'edit':
            ok, msg = update_employee(st.session_state.nv_edit_id, data)
        else:
            ok, msg = add_employee(data)

        if ok:
            st.success(f"✅ {msg}")
            st.session_state.nv_action = None
            st.session_state.nv_edit_id = None
            st.cache_data.clear()
            st.rerun()
        else:
            st.error(f"❌ {msg}")


# ── Bộ lọc & tìm kiếm ────────────────────────────────────────
df = load_employees()

with st.container():
    fc1, fc2, fc3, fc4, fc5 = st.columns([3, 2, 2, 2, 1])
    with fc1:
        search = st.text_input("🔍 Tìm kiếm (tên, mã NV)", placeholder="Nhập tên hoặc mã...")
    with fc2:
        dept_filter = st.selectbox("Phòng ban", ['Tất cả'] + DEPT_OPTIONS)
    with fc3:
        role_filter = st.selectbox("Chức vụ", ['Tất cả'] + JOBROLE_OPTIONS)
    with fc4:
        ot_filter = st.selectbox("Làm thêm giờ", ['Tất cả', 'Yes', 'No'])
    with fc5:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Thêm mới", type="primary", use_container_width=True):
            st.session_state.nv_action = 'add'
            st.session_state.nv_edit_id = None

# Áp dụng filter
filtered = df.copy()
if search:
    mask = (
        filtered['TenNhanVien'].astype(str).str.contains(search, case=False, na=False) |
        filtered['EmployeeNumber'].astype(str).str.contains(search, na=False)
    )
    filtered = filtered[mask]
if dept_filter != 'Tất cả':
    filtered = filtered[filtered['Department'] == dept_filter]
if role_filter != 'Tất cả':
    filtered = filtered[filtered['JobRole'] == role_filter]
if ot_filter != 'Tất cả':
    filtered = filtered[filtered['OverTime'] == ot_filter]

st.caption(f"Hiển thị **{len(filtered)}** / {len(df)} nhân viên")

# ── Form thêm/sửa ─────────────────────────────────────────────
if st.session_state.nv_action == 'add':
    render_employee_form(mode='add')
    st.markdown("---")
elif st.session_state.nv_action == 'edit' and st.session_state.nv_edit_id:
    existing_row = get_employee(st.session_state.nv_edit_id)
    if existing_row is not None:
        render_employee_form(mode='edit', existing=existing_row)
    st.markdown("---")

# ── Danh sách nhân viên ───────────────────────────────────────
section_header("📋 Danh sách nhân viên")

SHOW_COLS = ['EmployeeNumber', 'TenNhanVien', 'Department', 'JobRole', 'JobLevel',
             'Age', 'Gender', 'OverTime', 'MonthlyIncome',
             'TotalWorkingYears', 'YearsAtCompany', 'Attrition']
SHOW_COLS = [c for c in SHOW_COLS if c in filtered.columns]
RENAME = {
    'EmployeeNumber': 'Mã NV', 'TenNhanVien': 'Tên NV',
    'Department': 'Phòng ban', 'JobRole': 'Chức vụ',
    'JobLevel': 'Cấp', 'Age': 'Tuổi', 'Gender': 'GT',
    'OverTime': 'OT', 'MonthlyIncome': 'Thu nhập ($)',
    'TotalWorkingYears': 'Năm KN', 'YearsAtCompany': 'Năm CT',
    'Attrition': 'Thực tế'
}

display_df = filtered[SHOW_COLS].rename(columns=RENAME).reset_index(drop=True)
st.dataframe(display_df, use_container_width=True, hide_index=True, height=400)

# ── Sửa / Xóa ────────────────────────────────────────────────
section_header("⚙️ Thao tác")
col_sel, col_edit, col_del = st.columns([3, 1, 1])
with col_sel:
    emp_options = filtered.apply(
        lambda r: f"{r['TenNhanVien']} (#{int(r['EmployeeNumber'])})", axis=1
    ).tolist()
    if emp_options:
        selected_label = st.selectbox("Chọn nhân viên", emp_options, key='nv_select')
        sel_idx = emp_options.index(selected_label)
        sel_emp_num = int(filtered.iloc[sel_idx]['EmployeeNumber'])
    else:
        st.info("Không có nhân viên nào phù hợp.")
        sel_emp_num = None

with col_edit:
    st.markdown("<br>", unsafe_allow_html=True)
    if sel_emp_num and st.button("✏️ Sửa", use_container_width=True):
        st.session_state.nv_action = 'edit'
        st.session_state.nv_edit_id = sel_emp_num
        st.rerun()

with col_del:
    st.markdown("<br>", unsafe_allow_html=True)
    if sel_emp_num and st.button("🗑️ Xóa", use_container_width=True):
        st.session_state[f'confirm_delete_{sel_emp_num}'] = True

# Xác nhận xóa
if sel_emp_num and st.session_state.get(f'confirm_delete_{sel_emp_num}'):
    st.warning(f"⚠️ Bạn có chắc muốn xóa nhân viên #{sel_emp_num}?")
    cc1, cc2 = st.columns(2)
    with cc1:
        if st.button("✅ Xác nhận xóa", type="primary"):
            ok, msg = delete_employee(sel_emp_num)
            st.session_state[f'confirm_delete_{sel_emp_num}'] = False
            st.cache_data.clear()
            st.success(f"✅ {msg}")
            st.rerun()
    with cc2:
        if st.button("❌ Hủy"):
            st.session_state[f'confirm_delete_{sel_emp_num}'] = False
            st.rerun()
