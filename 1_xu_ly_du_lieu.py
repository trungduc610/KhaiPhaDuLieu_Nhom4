import pandas as pd
from sklearn.preprocessing import LabelEncoder

# --- 1. LÀM SẠCH DỮ LIỆU ---
file_path = './du_lieu/data_input.csv'
try:
    df = pd.read_csv(file_path)
except FileNotFoundError:
    print(f"Lỗi: Không tìm thấy file {file_path}. Vui lòng kiểm tra lại đường dẫn.")
    exit()

# Xử lý giá trị thiếu và trùng lặp
df.dropna(inplace=True)
df.drop_duplicates(inplace=True)

# Xóa các cột rác (cardinality cao hoặc không có giá trị phân loại)
cols_to_drop = ['EmployeeCount', 'Over18', 'StandardHours', 'EmployeeNumber']
df.drop(columns=[col for col in cols_to_drop if col in df.columns], inplace=True)

# Làm sạch khoảng trắng thừa trong các cột chữ
object_cols = df.select_dtypes(include=['object']).columns
for col in object_cols:
    df[col] = df[col].str.strip()

# Kiểm tra tính logic nghiệp vụ
df = df[df['Age'] >= 18]

# --- 2. PHÂN GIỎ DỮ LIỆU (BINNING) ---
# Phân giỏ độ tuổi
age_bins = [17, 30, 40, 50, 100]
age_labels = ['18-30', '31-40', '41-50', '51+']
df['AgeGroup'] = pd.cut(df['Age'], bins=age_bins, labels=age_labels)

# Phân giỏ khoảng cách đi làm
dist_bins = [-1, 5, 15, 50]
dist_labels = ['Gan (<5km)', 'Trung binh (5-15km)', 'Xa (>15km)']
df['DistanceGroup'] = pd.cut(df['DistanceFromHome'], bins=dist_bins, labels=dist_labels)

# Bỏ các cột số gốc sau khi đã phân giỏ
df.drop(columns=['Age', 'DistanceFromHome'], inplace=True)

# --- 3. MÃ HOÁ DỮ LIỆU ---
# 3.1. Label Encoding (Cho biến mục tiêu và biến có 2 giá trị)
label_encoder = LabelEncoder()
cot_label = ['Attrition', 'Gender', 'OverTime']

for col in cot_label:
    if col in df.columns:
        df[col] = label_encoder.fit_transform(df[col])

# 3.2. One-Hot Encoding (Cho các biến phân loại nhiều giá trị)
cat_cols = ['BusinessTravel', 'Department', 'EducationField', 'JobRole', 'MaritalStatus', 'AgeGroup', 'DistanceGroup']
cat_cols_exist = [col for col in cat_cols if col in df.columns]

# drop_first=True giúp tránh bẫy biến giả (dummy variable trap)
df = pd.get_dummies(df, columns=cat_cols_exist, drop_first=True, dtype=int)

# --- 4. KIỂM TRA VÀ XUẤT FILE ---
# Đảm bảo không còn dữ liệu object/category (CART trong sklearn chỉ nhận số)
non_numeric = df.select_dtypes(exclude=['int32', 'int64', 'float32', 'float64']).columns

print("\n--- KẾT QUẢ XỬ LÝ ---")
if len(non_numeric) > 0:
    print(f"CẢNH BÁO: Vẫn còn biến chưa được chuyển sang số: {list(non_numeric)}")
else:
    print("Dữ liệu đã được mã hóa")

print(f"- Số lượng dòng sẵn sàng huấn luyện: {df.shape[0]}")
print(f"- Số lượng cột đặc trưng (features): {df.shape[1]}")

# Xuất ra file duy nhất
output_filename = './du_lieu/data_output.csv'
df.to_csv(output_filename, index=False)
print(f"\nĐã lưu tập dữ liệu hoàn chỉnh vào: {output_filename}")