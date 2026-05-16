import pandas as pd
from sklearn.tree import DecisionTreeClassifier
import joblib

print("Đang khởi tạo quá trình xây dựng mô hình CART...")
# 1. Đọc dữ liệu đầu vào. Dữ liệu đã qua bước tiền xử lý
file_path = './du_lieu/data_output.csv'
try:
    df = pd.read_csv(file_path)
except FileNotFoundError:
    print(f"Lỗi: Không tìm thấy file {file_path}. Vui lòng chạy lại bước xử lý dữ liệu.")
    exit()

# 2. Phân tách đặc trưng (X) và biến mục tiêu (y)
target_column = 'Attrition'

if target_column not in df.columns:
    print(f"Lỗi: Không tìm thấy cột mục tiêu '{target_column}' trong dữ liệu.")
    exit()

X = df.drop(columns=[target_column])
y = df[target_column]

# 3. Khởi tạo và Huấn luyện mô hình CART (DecisionTreeClassifier)
cart_model = DecisionTreeClassifier(criterion='gini', random_state=42, max_depth=4)

print("Đang huấn luyện mô hình cây quyết định đầy đủ...")
cart_model.fit(X, y)

# 4. Lưu mô hình ra file
output_model_file = './thong_so_mo_hinh/cart_decision_tree_model.joblib'
joblib.dump(cart_model, output_model_file)

print(f"\nThành công! Đã lưu mô hình CART vào file: {output_model_file}")