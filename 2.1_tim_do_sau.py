import pandas as pd
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import GridSearchCV, train_test_split

print("BẮT ĐẦU TÌM KIẾM ĐỘ SÂU TỐI ƯU (GRID SEARCH)...")

# 1. Đọc dữ liệu đã xử lý
file_path = 'data_output.csv'
df = pd.read_csv(file_path)

X = df.drop(columns=['Attrition'])
y = df['Attrition']

# Chia dữ liệu thành tập Train và Test (80/20) để kiểm chứng cuối cùng
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 2. Thiết lập các tham số cần thử nghiệm (Grid)
# Chúng ta sẽ thử độ sâu từ 1 đến 20
param_grid = {
    'max_depth': range(1, 21),
    'min_samples_leaf': [1, 5, 10, 20], # Thử thêm ràng buộc số mẫu ở lá để tránh nhiễu
    'criterion': ['gini', 'entropy']
}

# 3. Khởi tạo Grid Search với Cross-Validation (cv=5 nghĩa là chia 5 phần để thử)
# scoring='f1' thường tốt hơn 'accuracy' cho bài toán nhân viên nghỉ việc (dữ liệu lệch)
grid_search = GridSearchCV(
    estimator=DecisionTreeClassifier(random_state=42),
    param_grid=param_grid,
    cv=5,
    scoring='f1', 
    verbose=1,
    n_jobs=-1 # Sử dụng toàn bộ nhân CPU để chạy nhanh hơn
)

# 4. Thực thi tìm kiếm
grid_search.fit(X_train, y_train)

# 5. Trích xuất kết quả
best_params = grid_search.best_params_
best_score = grid_search.best_score_

print("\n" + "="*50)
print(f"KẾT QUẢ TÌM KIẾM TỐI ƯU:")
print(f"- Độ sâu tốt nhất (max_depth): {best_params['max_depth']}")
print(f"- Số mẫu tối thiểu tại lá: {best_params['min_samples_leaf']}")
print(f"- Tiêu chí phân chia: {best_params['criterion']}")
print(f"- Điểm F1-score trung bình (CV): {best_score:.4f}")
print("="*50)

# --- PHẦN TRỰC QUAN HÓA: ĐỒ THỊ BIẾN THIÊN ĐỘ SÂU ---
results = pd.DataFrame(grid_search.cv_results_)
# Lọc ra các kết quả của tiêu chí Gini và min_samples_leaf=1 để vẽ đồ thị cho gọn
vis_data = results[(results['param_criterion'] == 'gini') & (results['param_min_samples_leaf'] == 1)]

plt.figure(figsize=(10, 6))
plt.plot(vis_data['param_max_depth'], vis_data['mean_test_score'], marker='o', linestyle='-', color='b')
plt.title('Mối liên hệ giữa Độ sâu của cây và Điểm F1 (Gini)')
plt.xlabel('Độ sâu (max_depth)')
plt.ylabel('F1-Score Trung bình')
plt.grid(True)
plt.axvline(x=best_params['max_depth'], color='r', linestyle='--', label='Độ sâu tối ưu')
plt.legend()
plt.show()