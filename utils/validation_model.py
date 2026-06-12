"""
Script đánh giá mô hình CART (Decision Tree) cho bài toán dự đoán nghỉ việc.
Chạy: python utils/validation_model.py

Kết quả được lưu vào thư mục danh_gia/:
  - bo_quy_tac.txt          : Bộ quy tắc của cây quyết định
  - do_quan_trong_thuoc_tinh.csv : Độ quan trọng của từng thuộc tính
  - classification_report.csv    : Bảng Classification Report
  - confusion_matrix.csv         : Bảng Confusion Matrix
"""

import os
import sys
import io
import pandas as pd
import numpy as np

# Fix encoding cho Windows console (cp1252 không hỗ trợ tiếng Việt)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
import joblib

# ── Đường dẫn ────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'du_lieu', 'data_output.csv')
MODEL_PATH = os.path.join(BASE_DIR, 'model', 'cart_model.pkl')
FEATURE_NAMES_PATH = os.path.join(BASE_DIR, 'model', 'feature_names.pkl')
OUTPUT_DIR = os.path.join(BASE_DIR, 'danh_gia')

# Tạo thư mục đầu ra nếu chưa tồn tại
os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_model():
    """Tải mô hình CART và danh sách tên feature đã lưu."""
    print(f"[1] Đang tải mô hình: {MODEL_PATH}")
    model = joblib.load(MODEL_PATH)
    feature_names = joblib.load(FEATURE_NAMES_PATH)
    print(f"    → Mô hình: DecisionTreeClassifier")
    print(f"    → Số lá: {model.get_n_leaves()}, Độ sâu: {model.get_depth()}")
    print(f"    → Số features: {len(feature_names)}")
    return model, feature_names


def load_and_prepare_data(feature_names):
    """Tải dữ liệu đã xử lý và chuẩn bị X, y."""
    print(f"\n[2] Đang tải dữ liệu: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    print(f"    → Kích thước: {df.shape}")

    # Target
    if df['Attrition'].dtype == object:
        y = (df['Attrition'].str.strip().str.lower() == 'yes').astype(int)
    else:
        y = df['Attrition'].astype(int)

    # Features
    X = df.drop(columns=['Attrition'])

    # Encode các cột object còn lại (nếu có)
    for col in X.columns:
        if X[col].dtype == object:
            X[col] = pd.factorize(X[col])[0]

    X = X.fillna(0)

    # Đảm bảo thứ tự cột khớp với lúc train
    X = X[feature_names]

    print(f"    → Phân phối Attrition: 0={int((y == 0).sum())}, 1={int((y == 1).sum())}")
    return X, y


def split_data(X, y):
    """Chia tập train/test giống hệt lúc huấn luyện (80/20, stratified, random_state=42)."""
    print("\n[3] Chia train/test (80/20, stratified, random_state=42)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"    → Train: {len(X_train)}, Test: {len(X_test)}")
    return X_train, X_test, y_train, y_test


# ═══════════════════════════════════════════════════════════════
#  CÁC HÀM XUẤT KẾT QUẢ ĐÁNH GIÁ
# ═══════════════════════════════════════════════════════════════

def export_decision_rules(model, feature_names):
    """
    Xuất bộ quy tắc (decision rules) của cây quyết định ra file txt.
    Sử dụng sklearn.tree.export_text để tạo biểu diễn dạng text.
    """
    print("\n[4] Xuất bộ quy tắc...")
    rules_text = export_text(
        model,
        feature_names=feature_names,
        show_weights=True,
        max_depth=100,
    )

    output_path = os.path.join(OUTPUT_DIR, 'bo_quy_tac.txt')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("  BỘ QUY TẮC CÂY QUYẾT ĐỊNH CART - DỰ ĐOÁN NGHỈ VIỆC\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Số lá (leaves): {model.get_n_leaves()}\n")
        f.write(f"Độ sâu cây (depth): {model.get_depth()}\n")
        f.write(f"Số features: {len(feature_names)}\n\n")
        f.write("-" * 70 + "\n")
        f.write("CHI TIẾT QUY TẮC:\n")
        f.write("-" * 70 + "\n\n")
        f.write(rules_text)

    print(f"    → Đã lưu: {output_path}")
    return output_path


def export_feature_importance(model, feature_names):
    """
    Xuất độ quan trọng của từng thuộc tính ra file CSV.
    Sắp xếp giảm dần theo mức độ quan trọng.
    """
    print("\n[5] Xuất độ quan trọng thuộc tính...")
    importance_df = pd.DataFrame({
        'Thu_tu': range(1, len(feature_names) + 1),
        'Thuoc_tinh': feature_names,
        'Do_quan_trong': model.feature_importances_,
    })

    # Sắp xếp giảm dần và đánh lại số thứ tự
    importance_df = importance_df.sort_values(
        'Do_quan_trong', ascending=False
    ).reset_index(drop=True)
    importance_df['Thu_tu'] = range(1, len(importance_df) + 1)

    output_path = os.path.join(OUTPUT_DIR, 'do_quan_trong_thuoc_tinh.csv')
    importance_df.to_csv(output_path, index=False, encoding='utf-8-sig')

    # In top 10
    print("    → Top 10 thuộc tính quan trọng nhất:")
    for _, row in importance_df.head(10).iterrows():
        bar = '█' * int(row['Do_quan_trong'] * 50)
        print(f"      {int(row['Thu_tu']):2d}. {row['Thuoc_tinh']:40s} "
              f"{row['Do_quan_trong']:.4f} {bar}")

    print(f"    → Đã lưu: {output_path}")
    return output_path


def export_classification_report(y_test, y_pred):
    """
    Xuất bảng Classification Report ra file CSV.
    Bao gồm precision, recall, f1-score, support cho từng lớp.
    """
    print("\n[6] Xuất Classification Report...")
    target_names = ['Khong nghi viec (0)', 'Nghi viec (1)']

    report_dict = classification_report(
        y_test, y_pred,
        target_names=target_names,
        output_dict=True,
        zero_division=0,
    )

    # Chuyển sang DataFrame
    report_df = pd.DataFrame(report_dict).T

    # Làm tròn giá trị
    report_df = report_df.round(4)

    # Đổi tên cột sang tiếng Việt
    report_df.columns = ['Precision', 'Recall', 'F1-Score', 'Support']

    # Chuyển support sang int (trừ dòng tổng hợp)
    report_df['Support'] = report_df['Support'].astype(int)

    # Thêm cột tên chỉ số
    report_df.insert(0, 'Chi_so', report_df.index)
    report_df = report_df.reset_index(drop=True)

    output_path = os.path.join(OUTPUT_DIR, 'classification_report.csv')
    report_df.to_csv(output_path, index=False, encoding='utf-8-sig')

    # In ra console
    print("    → Bảng Classification Report:")
    print(classification_report(
        y_test, y_pred,
        target_names=target_names,
        zero_division=0,
    ))

    print(f"    → Đã lưu: {output_path}")
    return output_path


def export_confusion_matrix(y_test, y_pred):
    """
    Xuất bảng Confusion Matrix ra file CSV.
    Hiển thị ma trận nhầm lẫn với nhãn dòng/cột rõ ràng.
    """
    print("\n[7] Xuất Confusion Matrix...")
    cm = confusion_matrix(y_test, y_pred)

    labels = ['Khong nghi viec (0)', 'Nghi viec (1)']

    cm_df = pd.DataFrame(
        cm,
        index=[f'Thuc_te: {label}' for label in labels],
        columns=[f'Du_doan: {label}' for label in labels],
    )

    # Thêm cột tổng
    cm_df['Tong'] = cm_df.sum(axis=1)

    # Thêm hàng tổng
    total_row = cm_df.sum(axis=0)
    total_row.name = 'Tong'
    cm_df = pd.concat([cm_df, total_row.to_frame().T])

    # Thêm cột chỉ số dòng
    cm_df.insert(0, 'Nhan', cm_df.index)
    cm_df = cm_df.reset_index(drop=True)

    output_path = os.path.join(OUTPUT_DIR, 'confusion_matrix.csv')
    cm_df.to_csv(output_path, index=False, encoding='utf-8-sig')

    # In ra console
    print("    → Confusion Matrix:")
    print(f"      {'':30s} {'Dự đoán: Không':>18s} {'Dự đoán: Nghỉ':>18s}")
    print(f"      {'Thực tế: Không nghỉ':30s} {cm[0][0]:>18d} {cm[0][1]:>18d}")
    print(f"      {'Thực tế: Nghỉ việc':30s} {cm[1][0]:>18d} {cm[1][1]:>18d}")

    acc = (cm[0][0] + cm[1][1]) / cm.sum()
    print(f"\n      Accuracy: {acc:.4f}")

    print(f"    → Đã lưu: {output_path}")
    return output_path


# ═══════════════════════════════════════════════════════════════
#  HÀM CHÍNH
# ═══════════════════════════════════════════════════════════════

def run_validation():
    """
    Chạy toàn bộ quy trình đánh giá mô hình CART.
    Trả về dictionary chứa đường dẫn các file kết quả.
    """
    print("=" * 60)
    print("  ĐÁNH GIÁ MÔ HÌNH CART - DỰ ĐOÁN NGHỈ VIỆC NHÂN VIÊN")
    print("=" * 60)

    # 1. Tải mô hình
    model, feature_names = load_model()

    # 2. Tải và chuẩn bị dữ liệu
    X, y = load_and_prepare_data(feature_names)

    # 3. Chia dữ liệu (cùng tham số với lúc train)
    X_train, X_test, y_train, y_test = split_data(X, y)

    # Dự đoán trên tập test
    y_pred = model.predict(X_test)

    # 4. Xuất bộ quy tắc
    rules_path = export_decision_rules(model, feature_names)

    # 5. Xuất độ quan trọng thuộc tính
    importance_path = export_feature_importance(model, feature_names)

    # 6. Xuất Classification Report
    report_path = export_classification_report(y_test, y_pred)

    # 7. Xuất Confusion Matrix
    cm_path = export_confusion_matrix(y_test, y_pred)

    # Tổng kết
    print("\n" + "=" * 60)
    print("  ✅ ĐÁNH GIÁ HOÀN TẤT!")
    print("=" * 60)
    print(f"\n  Các file kết quả đã lưu tại: {OUTPUT_DIR}/")
    print(f"    1. bo_quy_tac.txt")
    print(f"    2. do_quan_trong_thuoc_tinh.csv")
    print(f"    3. classification_report.csv")
    print(f"    4. confusion_matrix.csv")
    print("=" * 60)

    return {
        'bo_quy_tac': rules_path,
        'do_quan_trong_thuoc_tinh': importance_path,
        'classification_report': report_path,
        'confusion_matrix': cm_path,
    }


if __name__ == '__main__':
    run_validation()
