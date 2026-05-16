import pandas as pd
import joblib
import matplotlib.pyplot as plt
from sklearn.tree import plot_tree, export_text
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

print("BẮT ĐẦU QUÁ TRÌNH TRÍCH XUẤT VÀ ĐÁNH GIÁ MÔ HÌNH...")

# 1. Đọc dữ liệu đầu vào và khởi tạo biến
# Dùng lại file dữ liệu đã xử lý để làm đầu vào cho việc dự báo và lấy tên cột
file_data = './du_lieu/data_output.csv'
df = pd.read_csv(file_data)

target_column = 'Attrition'
X = df.drop(columns=[target_column])
y_true = df[target_column]
feature_names = X.columns.tolist()

# 2. Load mô hình từ file joblib
file_model = './thong_so_mo_hinh/cart_decision_tree_model.joblib'
cart_model = joblib.load(file_model)
print(f"Đã load thành công mô hình từ: {file_model}\n")


# --- TẠO FILE 1: ẢNH CẤU TRÚC CÂY (.png) ---
print("1. Đang xuất file ảnh cấu trúc cây...")
plt.figure(figsize=(25, 15)) # Tăng kích thước ảnh để nhìn rõ hơn
# Lưu ý: max_depth=3 chỉ để giới hạn số tầng vẽ ra cho dễ nhìn. 
# Cây đầy đủ có thể rất khổng lồ và làm mờ ảnh chữ. Bạn có thể xóa max_depth=3 để vẽ toàn bộ.
plot_tree(cart_model, feature_names=feature_names, 
          class_names=['Stay', 'Leave'], filled=True, rounded=True, 
          fontsize=10, max_depth=4)
plt.title("Cấu Trúc Cây Quyết Định (Hiển thị tối đa 3 tầng đầu)")
plt.savefig('./danh_gia/1_cau_truc_cay.png', dpi=300, bbox_inches='tight')


# --- TẠO FILE 2: BỘ QUY TẮC QUYẾT ĐỊNH (.txt) ---
print("2. Đang xuất file bộ quy tắc quyết định...")
tree_rules = export_text(cart_model, feature_names=feature_names)
with open('./danh_gia/2_bo_quy_tac.txt', 'w', encoding='utf-8') as f:
    f.write("BỘ QUY TẮC LOGIC CỦA CÂY QUYẾT ĐỊNH\n")
    f.write("="*50 + "\n")
    f.write(tree_rules)


# --- TẠO FILE 3: KẾT QUẢ DỰ BÁO PHÂN LOẠI (.csv) ---
print("3. Đang xuất file kết quả dự báo...")
y_pred = cart_model.predict(X)
df_results = df.copy()
df_results['Predicted_Attrition'] = y_pred
# Thêm một cột để dễ dàng xem mô hình đoán đúng hay sai
df_results['Is_Correct'] = df_results[target_column] == df_results['Predicted_Attrition']
df_results.to_csv('./danh_gia/3_ket_qua_du_bao.csv', index=False)


# --- TẠO FILE 4: ĐỘ QUAN TRỌNG CỦA THUỘC TÍNH (.csv) ---
print("4. Đang xuất file độ quan trọng của thuộc tính...")
importances = cart_model.feature_importances_
df_importance = pd.DataFrame({
    'Thuoc_Tinh': feature_names,
    'Do_Quan_Trong': importances
})
# Sắp xếp từ quan trọng nhất đến ít quan trọng nhất
df_importance = df_importance.sort_values(by='Do_Quan_Trong', ascending=False)
df_importance.to_csv('./danh_gia/4_do_quan_trong_thuoc_tinh.csv', index=False)


# --- TẠO FILE 5: TỔNG HỢP CÁC THÔNG SỐ ĐÁNH GIÁ (.txt) ---
print("5. Đang xuất file báo cáo thông số đánh giá...")
accuracy = accuracy_score(y_true, y_pred)
report = classification_report(y_true, y_pred, target_names=['Stay (0)', 'Leave (1)'])
conf_matrix = confusion_matrix(y_true, y_pred)

with open('./danh_gia/5_thong_so_danh_gia.txt', 'w', encoding='utf-8') as f:
    f.write("BÁO CÁO ĐÁNH GIÁ HIỆU SUẤT MÔ HÌNH\n")
    f.write("="*50 + "\n\n")
    f.write(f"Độ chính xác tổng thể (Accuracy): {accuracy * 100:.2f}%\n\n")
    
    f.write("1. BẢNG BÁO CÁO CHI TIẾT (Classification Report):\n")
    f.write("-" * 50 + "\n")
    f.write(report)
    f.write("\n\n")
    
    f.write("2. MA TRẬN NHẦM LẪN (Confusion Matrix):\n")
    f.write("-" * 50 + "\n")
    f.write(f"                 Dự đoán Stay(0) | Dự đoán Leave(1)\n")
    f.write(f"Thực tế Stay(0) | {conf_matrix[0][0]:<15} | {conf_matrix[0][1]}\n")
    f.write(f"Thực tế Leave(1)| {conf_matrix[1][0]:<15} | {conf_matrix[1][1]}\n")
    f.write("\n(Giải thích Ma trận: Trục ngang là kết quả dự báo, Trục dọc là dữ liệu thực tế)")

print("\nHOÀN TẤT! Toàn bộ 5 file đã được lưu trong cùng thư mục chạy mã.")