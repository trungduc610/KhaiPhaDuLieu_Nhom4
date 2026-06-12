"""
Quản lý dữ liệu nhân viên (CRUD) - lưu trữ bằng CSV.
"""

import os
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_INPUT = os.path.join(BASE_DIR, 'du_lieu', 'data_input.csv')
EMPLOYEES_CSV = os.path.join(BASE_DIR, 'du_lieu', 'employees.csv')

# Các cột hiển thị (subset quan trọng)
DISPLAY_COLS = [
    'EmployeeNumber', 'TenNhanVien', 'Department', 'JobRole', 'JobLevel',
    'Age', 'Gender', 'MaritalStatus', 'MonthlyIncome', 'OverTime',
    'TotalWorkingYears', 'YearsAtCompany', 'Attrition'
]

# Các trường nhập liệu cho form thêm/sửa
FORM_COLS_REQUIRED = ['TenNhanVien', 'Department', 'JobRole', 'Age', 'Gender',
                       'MaritalStatus', 'Education', 'EducationField', 'BusinessTravel']
FORM_COLS_WORK = ['JobLevel', 'JobInvolvement', 'OverTime', 'TotalWorkingYears',
                   'YearsAtCompany', 'YearsInCurrentRole', 'YearsSinceLastPromotion',
                   'YearsWithCurrManager', 'NumCompaniesWorked', 'TrainingTimesLastYear']
FORM_COLS_INCOME = ['MonthlyIncome', 'DailyRate', 'HourlyRate', 'MonthlyRate',
                     'PercentSalaryHike', 'StockOptionLevel']
FORM_COLS_SATISFACTION = ['JobSatisfaction', 'EnvironmentSatisfaction',
                            'RelationshipSatisfaction', 'WorkLifeBalance', 'PerformanceRating', 'JobInvolvement']
FORM_COLS_OTHER = ['DistanceFromHome']


def _ensure_employees_csv():
    """Khởi tạo employees.csv từ data_input.csv nếu chưa tồn tại."""
    if not os.path.exists(EMPLOYEES_CSV):
        df = pd.read_csv(DATA_INPUT)
        # Thêm cột TenNhanVien
        df.insert(0, 'TenNhanVien', df['EmployeeNumber'].apply(lambda x: f'NV-{int(x):04d}'))
        # Giữ Attrition như thông tin thực tế (trước khi dự đoán)
        df.to_csv(EMPLOYEES_CSV, index=False)
    return EMPLOYEES_CSV


def load_employees():
    """Tải toàn bộ danh sách nhân viên."""
    _ensure_employees_csv()
    df = pd.read_csv(EMPLOYEES_CSV)
    if 'TenNhanVien' not in df.columns:
        df.insert(0, 'TenNhanVien', df['EmployeeNumber'].apply(lambda x: f'NV-{int(x):04d}'))
        df.to_csv(EMPLOYEES_CSV, index=False)
    return df


def save_employees(df):
    """Lưu toàn bộ DataFrame nhân viên."""
    _ensure_employees_csv()
    df.to_csv(EMPLOYEES_CSV, index=False)


def get_employee(emp_number):
    """Lấy thông tin 1 nhân viên theo EmployeeNumber."""
    df = load_employees()
    rows = df[df['EmployeeNumber'] == emp_number]
    return rows.iloc[0] if len(rows) > 0 else None


def add_employee(data: dict):
    """
    Thêm nhân viên mới. data là dict chứa các trường.
    Tự động sinh EmployeeNumber mới.
    Trả về (True, '') nếu thành công, (False, msg) nếu lỗi.
    """
    df = load_employees()
    new_id = int(df['EmployeeNumber'].max()) + 1 if len(df) > 0 else 1

    # Điền các trường mặc định từ data_input schema
    template = pd.read_csv(DATA_INPUT, nrows=1).iloc[0].to_dict()
    template.update(data)
    template['EmployeeNumber'] = new_id
    template['TenNhanVien'] = data.get('TenNhanVien', f'NV-{new_id:04d}')
    template['EmployeeCount'] = 1
    template['Over18'] = 'Y'
    template['StandardHours'] = 80

    new_row = pd.DataFrame([template])
    # Đảm bảo cùng cột
    for col in df.columns:
        if col not in new_row.columns:
            new_row[col] = 0
    new_row = new_row[df.columns]

    df = pd.concat([df, new_row], ignore_index=True)
    save_employees(df)
    return True, f'Đã thêm nhân viên {template["TenNhanVien"]} (ID: {new_id})'


def update_employee(emp_number, data: dict):
    """Cập nhật thông tin nhân viên theo EmployeeNumber."""
    df = load_employees()
    idx = df[df['EmployeeNumber'] == emp_number].index
    if len(idx) == 0:
        return False, 'Không tìm thấy nhân viên'
    for key, val in data.items():
        if key in df.columns:
            df.loc[idx[0], key] = val
    save_employees(df)
    return True, 'Cập nhật thành công'


def delete_employee(emp_number):
    """Xóa nhân viên theo EmployeeNumber."""
    df = load_employees()
    before = len(df)
    df = df[df['EmployeeNumber'] != emp_number]
    if len(df) == before:
        return False, 'Không tìm thấy nhân viên'
    save_employees(df)
    return True, 'Xóa thành công'


def delete_employees_bulk(emp_numbers: list):
    """Xóa nhiều nhân viên."""
    df = load_employees()
    df = df[~df['EmployeeNumber'].isin(emp_numbers)]
    save_employees(df)
    return True, f'Đã xóa {len(emp_numbers)} nhân viên'


def import_employees_from_df(new_df: pd.DataFrame):
    """
    Import nhân viên từ DataFrame mới.
    Không ghi đè dữ liệu cũ, thêm vào cuối.
    Trả về (success, message, n_added, n_error).
    """
    df = load_employees()
    existing_ids = set(df['EmployeeNumber'].tolist())

    errors = []
    added = []

    for idx, row in new_df.iterrows():
        try:
            # Kiểm tra trùng EmployeeNumber
            emp_num = row.get('EmployeeNumber', None)
            if emp_num and int(emp_num) in existing_ids:
                errors.append(f'Hàng {idx+2}: EmployeeNumber {emp_num} đã tồn tại')
                continue

            # Sinh ID mới nếu không có
            if not emp_num or pd.isna(emp_num):
                max_id = int(df['EmployeeNumber'].max()) if len(df) > 0 else 0
                emp_num = max_id + len(added) + 1

            row_dict = row.to_dict()
            row_dict['EmployeeNumber'] = int(emp_num)
            if 'TenNhanVien' not in row_dict or pd.isna(row_dict.get('TenNhanVien')):
                row_dict['TenNhanVien'] = f'NV-{int(emp_num):04d}'
            row_dict['EmployeeCount'] = 1
            row_dict['Over18'] = 'Y'
            row_dict['StandardHours'] = 80

            added.append(row_dict)
            existing_ids.add(int(emp_num))

        except Exception as e:
            errors.append(f'Hàng {idx+2}: {str(e)}')

    if added:
        added_df = pd.DataFrame(added)
        for col in df.columns:
            if col not in added_df.columns:
                added_df[col] = None
        added_df = added_df[[c for c in df.columns if c in added_df.columns]]
        df = pd.concat([df, added_df], ignore_index=True)
        save_employees(df)

    msg = f'Thêm thành công {len(added)} nhân viên.'
    if errors:
        msg += f' {len(errors)} lỗi: ' + '; '.join(errors[:3])

    return len(added) > 0, msg, len(added), len(errors)


def get_employee_display_name(row):
    """Tên hiển thị của nhân viên."""
    name = str(row.get('TenNhanVien', ''))
    num = row.get('EmployeeNumber', '')
    return f"{name} (#{int(num)})" if name and str(name) != 'nan' else f"NV-{int(num):04d}"


def get_template_excel():
    """Tạo file Excel mẫu để download."""
    import io
    cols = [
        'TenNhanVien', 'Department', 'JobRole', 'Age', 'Gender', 'MaritalStatus',
        'Education', 'EducationField', 'BusinessTravel', 'OverTime',
        'MonthlyIncome', 'DailyRate', 'HourlyRate', 'MonthlyRate',
        'PercentSalaryHike', 'StockOptionLevel', 'JobLevel', 'JobInvolvement',
        'JobSatisfaction', 'EnvironmentSatisfaction', 'RelationshipSatisfaction',
        'WorkLifeBalance', 'PerformanceRating', 'DistanceFromHome',
        'TotalWorkingYears', 'YearsAtCompany', 'YearsInCurrentRole',
        'YearsSinceLastPromotion', 'YearsWithCurrManager',
        'NumCompaniesWorked', 'TrainingTimesLastYear'
    ]
    sample = {
        'TenNhanVien': 'Nguyễn Văn A', 'Department': 'Research & Development',
        'JobRole': 'Research Scientist', 'Age': 30, 'Gender': 'Male',
        'MaritalStatus': 'Single', 'Education': 3, 'EducationField': 'Life Sciences',
        'BusinessTravel': 'Travel_Rarely', 'OverTime': 'No',
        'MonthlyIncome': 5000, 'DailyRate': 800, 'HourlyRate': 60,
        'MonthlyRate': 15000, 'PercentSalaryHike': 12, 'StockOptionLevel': 1,
        'JobLevel': 2, 'JobInvolvement': 3, 'JobSatisfaction': 3,
        'EnvironmentSatisfaction': 3, 'RelationshipSatisfaction': 3,
        'WorkLifeBalance': 3, 'PerformanceRating': 3, 'DistanceFromHome': 5,
        'TotalWorkingYears': 8, 'YearsAtCompany': 4, 'YearsInCurrentRole': 2,
        'YearsSinceLastPromotion': 1, 'YearsWithCurrManager': 2,
        'NumCompaniesWorked': 2, 'TrainingTimesLastYear': 3
    }
    df_template = pd.DataFrame([{c: sample.get(c, '') for c in cols}])
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
        df_template.to_excel(writer, index=False, sheet_name='NhanVien')
    buf.seek(0)
    return buf.read()
