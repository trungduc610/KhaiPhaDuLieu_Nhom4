"""
Tiền xử lý dữ liệu: chuyển data_input format → data_output format (features cho model)
"""

import pandas as pd
import numpy as np

# Thứ tự features đúng theo data_output.csv (không có Attrition)
FEATURE_COLS = [
    'DailyRate', 'Education', 'EnvironmentSatisfaction', 'Gender',
    'HourlyRate', 'JobInvolvement', 'JobLevel', 'JobSatisfaction',
    'MonthlyIncome', 'MonthlyRate', 'NumCompaniesWorked', 'OverTime',
    'PercentSalaryHike', 'PerformanceRating', 'RelationshipSatisfaction',
    'StockOptionLevel', 'TotalWorkingYears', 'TrainingTimesLastYear',
    'WorkLifeBalance', 'YearsAtCompany', 'YearsInCurrentRole',
    'YearsSinceLastPromotion', 'YearsWithCurrManager',
    'BusinessTravel_Travel_Frequently', 'BusinessTravel_Travel_Rarely',
    'Department_Research & Development', 'Department_Sales',
    'EducationField_Life Sciences', 'EducationField_Marketing',
    'EducationField_Medical', 'EducationField_Other',
    'EducationField_Technical Degree',
    'JobRole_Human Resources', 'JobRole_Laboratory Technician',
    'JobRole_Manager', 'JobRole_Manufacturing Director',
    'JobRole_Research Director', 'JobRole_Research Scientist',
    'JobRole_Sales Executive', 'JobRole_Sales Representative',
    'MaritalStatus_Married', 'MaritalStatus_Single',
    'AgeGroup_31-40', 'AgeGroup_41-50', 'AgeGroup_51+',
    'DistanceGroup_Trung binh (5-15km)', 'DistanceGroup_Xa (>15km)'
]

# Tùy chọn các trường categorical
DEPT_OPTIONS = ['Human Resources', 'Research & Development', 'Sales']
JOBROLE_OPTIONS = [
    'Healthcare Representative', 'Human Resources', 'Laboratory Technician',
    'Manager', 'Manufacturing Director', 'Research Director',
    'Research Scientist', 'Sales Executive', 'Sales Representative'
]
EDUCATIONFIELD_OPTIONS = ['Human Resources', 'Life Sciences', 'Marketing', 'Medical', 'Other', 'Technical Degree']
BUSINESSTRAVEL_OPTIONS = ['Non-Travel', 'Travel_Rarely', 'Travel_Frequently']
MARITALSTATUS_OPTIONS = ['Single', 'Married', 'Divorced']
GENDER_OPTIONS = ['Male', 'Female']

# Nhãn hiển thị tiếng Việt
FIELD_LABELS = {
    'TenNhanVien': 'Tên nhân viên',
    'EmployeeNumber': 'Mã nhân viên',
    'Age': 'Tuổi',
    'Gender': 'Giới tính',
    'MaritalStatus': 'Tình trạng hôn nhân',
    'Department': 'Phòng ban',
    'JobRole': 'Chức vụ',
    'JobLevel': 'Cấp độ (1-5)',
    'Education': 'Trình độ (1-5)',
    'EducationField': 'Lĩnh vực học vấn',
    'BusinessTravel': 'Tần suất công tác',
    'OverTime': 'Làm thêm giờ',
    'MonthlyIncome': 'Thu nhập tháng ($)',
    'DailyRate': 'Lương ngày ($)',
    'HourlyRate': 'Lương giờ ($)',
    'MonthlyRate': 'Tỷ lệ tháng',
    'PercentSalaryHike': 'Tăng lương (%)',
    'StockOptionLevel': 'Mức cổ phiếu (0-3)',
    'JobSatisfaction': 'Hài lòng công việc (1-4)',
    'EnvironmentSatisfaction': 'Hài lòng môi trường (1-4)',
    'RelationshipSatisfaction': 'Hài lòng quan hệ (1-4)',
    'WorkLifeBalance': 'Cân bằng cuộc sống (1-4)',
    'JobInvolvement': 'Mức tham gia (1-4)',
    'PerformanceRating': 'Đánh giá hiệu suất (1-4)',
    'DistanceFromHome': 'Khoảng cách nhà (km)',
    'TotalWorkingYears': 'Tổng năm kinh nghiệm',
    'YearsAtCompany': 'Năm tại công ty',
    'YearsInCurrentRole': 'Năm ở vị trí hiện tại',
    'YearsSinceLastPromotion': 'Năm từ lần thăng chức gần nhất',
    'YearsWithCurrManager': 'Năm với quản lý hiện tại',
    'NumCompaniesWorked': 'Số công ty đã làm',
    'TrainingTimesLastYear': 'Số lần đào tạo năm qua',
}

# Nhãn tiếng Việt cho features trong model (để giải thích)
FEATURE_LABELS = {
    'DailyRate': 'Lương ngày',
    'Education': 'Trình độ học vấn',
    'EnvironmentSatisfaction': 'Hài lòng môi trường',
    'Gender': 'Giới tính (Nam=1)',
    'HourlyRate': 'Lương giờ',
    'JobInvolvement': 'Mức tham gia CV',
    'JobLevel': 'Cấp độ công việc',
    'JobSatisfaction': 'Hài lòng công việc',
    'MonthlyIncome': 'Thu nhập tháng',
    'MonthlyRate': 'Tỷ lệ tháng',
    'NumCompaniesWorked': 'Số công ty đã làm',
    'OverTime': 'Làm thêm giờ',
    'PercentSalaryHike': 'Tăng lương %',
    'PerformanceRating': 'Đánh giá hiệu suất',
    'RelationshipSatisfaction': 'Hài lòng quan hệ',
    'StockOptionLevel': 'Mức cổ phiếu',
    'TotalWorkingYears': 'Tổng năm kinh nghiệm',
    'TrainingTimesLastYear': 'Số lần đào tạo',
    'WorkLifeBalance': 'Cân bằng cuộc sống',
    'YearsAtCompany': 'Năm tại công ty',
    'YearsInCurrentRole': 'Năm ở vị trí hiện tại',
    'YearsSinceLastPromotion': 'Năm từ thăng chức gần nhất',
    'YearsWithCurrManager': 'Năm với quản lý hiện tại',
    'BusinessTravel_Travel_Frequently': 'Công tác: Thường xuyên',
    'BusinessTravel_Travel_Rarely': 'Công tác: Thỉnh thoảng',
    'Department_Research & Development': 'Phòng ban: R&D',
    'Department_Sales': 'Phòng ban: Sales',
    'EducationField_Life Sciences': 'Ngành: Khoa học sự sống',
    'EducationField_Marketing': 'Ngành: Marketing',
    'EducationField_Medical': 'Ngành: Y tế',
    'EducationField_Other': 'Ngành: Khác',
    'EducationField_Technical Degree': 'Ngành: Kỹ thuật',
    'JobRole_Human Resources': 'Vị trí: Nhân sự',
    'JobRole_Laboratory Technician': 'Vị trí: KTV Phòng thí nghiệm',
    'JobRole_Manager': 'Vị trí: Quản lý',
    'JobRole_Manufacturing Director': 'Vị trí: GĐ Sản xuất',
    'JobRole_Research Director': 'Vị trí: GĐ Nghiên cứu',
    'JobRole_Research Scientist': 'Vị trí: Nhà khoa học',
    'JobRole_Sales Executive': 'Vị trí: Giám đốc Sales',
    'JobRole_Sales Representative': 'Vị trí: Nhân viên Sales',
    'MaritalStatus_Married': 'Hôn nhân: Đã kết hôn',
    'MaritalStatus_Single': 'Hôn nhân: Độc thân',
    'AgeGroup_31-40': 'Nhóm tuổi: 31-40',
    'AgeGroup_41-50': 'Nhóm tuổi: 41-50',
    'AgeGroup_51+': 'Nhóm tuổi: 51+',
    'DistanceGroup_Trung binh (5-15km)': 'Khoảng cách: Trung bình (5-15km)',
    'DistanceGroup_Xa (>15km)': 'Khoảng cách: Xa (>15km)',
}


def _safe_float(val, default=0.0):
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def preprocess_employee_row(row):
    """
    Chuyển đổi 1 hàng data_input (dict/Series) sang vector features cho model.
    Trả về dict với đúng thứ tự FEATURE_COLS.
    """
    if hasattr(row, 'to_dict'):
        row = row.to_dict()

    result = {}

    # Numeric features trực tiếp
    direct_cols = [
        'DailyRate', 'Education', 'EnvironmentSatisfaction',
        'HourlyRate', 'JobInvolvement', 'JobLevel', 'JobSatisfaction',
        'MonthlyIncome', 'MonthlyRate', 'NumCompaniesWorked',
        'PercentSalaryHike', 'PerformanceRating', 'RelationshipSatisfaction',
        'StockOptionLevel', 'TotalWorkingYears', 'TrainingTimesLastYear',
        'WorkLifeBalance', 'YearsAtCompany', 'YearsInCurrentRole',
        'YearsSinceLastPromotion', 'YearsWithCurrManager'
    ]
    for col in direct_cols:
        result[col] = _safe_float(row.get(col, 0))

    # Gender: Male=1, Female=0
    gender_val = str(row.get('Gender', '')).strip().lower()
    result['Gender'] = 1 if gender_val in ['male', 'nam', '1'] else 0

    # OverTime: Yes=1, No=0
    ot_val = str(row.get('OverTime', '')).strip().lower()
    result['OverTime'] = 1 if ot_val in ['yes', 'có', '1'] else 0

    # BusinessTravel
    bt = str(row.get('BusinessTravel', '')).strip()
    result['BusinessTravel_Travel_Frequently'] = 1 if bt == 'Travel_Frequently' else 0
    result['BusinessTravel_Travel_Rarely'] = 1 if bt == 'Travel_Rarely' else 0

    # Department
    dept = str(row.get('Department', '')).strip()
    result['Department_Research & Development'] = 1 if dept == 'Research & Development' else 0
    result['Department_Sales'] = 1 if dept == 'Sales' else 0

    # EducationField
    ef = str(row.get('EducationField', '')).strip()
    result['EducationField_Life Sciences'] = 1 if ef == 'Life Sciences' else 0
    result['EducationField_Marketing'] = 1 if ef == 'Marketing' else 0
    result['EducationField_Medical'] = 1 if ef == 'Medical' else 0
    result['EducationField_Other'] = 1 if ef == 'Other' else 0
    result['EducationField_Technical Degree'] = 1 if ef == 'Technical Degree' else 0

    # JobRole
    jr = str(row.get('JobRole', '')).strip()
    result['JobRole_Human Resources'] = 1 if jr == 'Human Resources' else 0
    result['JobRole_Laboratory Technician'] = 1 if jr == 'Laboratory Technician' else 0
    result['JobRole_Manager'] = 1 if jr == 'Manager' else 0
    result['JobRole_Manufacturing Director'] = 1 if jr == 'Manufacturing Director' else 0
    result['JobRole_Research Director'] = 1 if jr == 'Research Director' else 0
    result['JobRole_Research Scientist'] = 1 if jr == 'Research Scientist' else 0
    result['JobRole_Sales Executive'] = 1 if jr == 'Sales Executive' else 0
    result['JobRole_Sales Representative'] = 1 if jr == 'Sales Representative' else 0

    # MaritalStatus
    ms = str(row.get('MaritalStatus', '')).strip()
    result['MaritalStatus_Married'] = 1 if ms == 'Married' else 0
    result['MaritalStatus_Single'] = 1 if ms == 'Single' else 0

    # AgeGroup
    age = int(_safe_float(row.get('Age', 0)))
    result['AgeGroup_31-40'] = 1 if 31 <= age <= 40 else 0
    result['AgeGroup_41-50'] = 1 if 41 <= age <= 50 else 0
    result['AgeGroup_51+'] = 1 if age >= 51 else 0

    # DistanceGroup
    dist = _safe_float(row.get('DistanceFromHome', 0))
    result['DistanceGroup_Trung binh (5-15km)'] = 1 if 5 <= dist <= 15 else 0
    result['DistanceGroup_Xa (>15km)'] = 1 if dist > 15 else 0

    # Trả về đúng thứ tự
    return {col: result.get(col, 0) for col in FEATURE_COLS}


def preprocess_dataframe(df):
    """Chuyển đổi DataFrame data_input sang DataFrame features cho model."""
    rows = [preprocess_employee_row(row) for _, row in df.iterrows()]
    return pd.DataFrame(rows, columns=FEATURE_COLS)


def get_risk_level(prob):
    """Phân loại mức rủi ro theo xác suất nghỉ việc."""
    if prob >= 0.70:
        return 'Cao', '#ef4444'
    elif prob >= 0.40:
        return 'Trung bình', '#f59e0b'
    else:
        return 'Thấp', '#10b981'
