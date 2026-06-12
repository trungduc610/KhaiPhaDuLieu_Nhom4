"""
Script train mô hình CART (Decision Tree) cho bài toán dự đoán nghỉ việc.
Chạy: python model/train_model.py
"""

import os
import sys
import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (accuracy_score, classification_report,
                              confusion_matrix, roc_auc_score)
import joblib

# Đường dẫn
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'du_lieu', 'data_output.csv')
MODEL_DIR = os.path.dirname(os.path.abspath(__file__))

print("=" * 60)
print("  TRAIN MÔ HÌNH CART - DỰ ĐOÁN NGHỈ VIỆC NHÂN VIÊN")
print("=" * 60)

# ── 1. Load dữ liệu ─────────────────────────────────────────
print(f"\n[1] Đang tải dữ liệu: {DATA_PATH}")
df = pd.read_csv(DATA_PATH)
print(f"    → Kích thước: {df.shape}")
print(f"    → Phân phối Attrition:\n{df['Attrition'].value_counts()}")

# ── 2. Chuẩn bị features & target ───────────────────────────
print("\n[2] Chuẩn bị dữ liệu...")

# Target: Attrition
if df['Attrition'].dtype == object:
    y = (df['Attrition'].str.strip().str.lower() == 'yes').astype(int)
else:
    y = df['Attrition'].astype(int)

# Features: tất cả cột trừ Attrition
X = df.drop(columns=['Attrition'])
feature_names = list(X.columns)

# Xử lý các cột object còn lại (nếu có)
for col in X.columns:
    if X[col].dtype == object:
        print(f"    → Encode cột: {col}")
        X[col] = pd.factorize(X[col])[0]

X = X.fillna(0)

print(f"    → Số features: {len(feature_names)}")
print(f"    → Tỷ lệ nghỉ việc: {y.mean():.2%}")

# ── 3. Train/Test split ──────────────────────────────────────
print("\n[3] Chia train/test (80/20, stratified)...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f"    → Train: {len(X_train)}, Test: {len(X_test)}")

# ── 4. Train CART ────────────────────────────────────────────
print("\n[4] Training Decision Tree (CART)...")
model = DecisionTreeClassifier(
    criterion='gini',
    max_depth=8,
    min_samples_split=15,
    min_samples_leaf=8,
    max_features=None,
    class_weight='balanced',
    random_state=42
)
model.fit(X_train, y_train)
print(f"    → Số lá: {model.get_n_leaves()}")
print(f"    → Độ sâu thực: {model.get_depth()}")

# ── 5. Đánh giá ─────────────────────────────────────────────
print("\n[5] Đánh giá mô hình...")
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]

acc = accuracy_score(y_test, y_pred)
auc = roc_auc_score(y_test, y_prob)
cv_scores = cross_val_score(model, X, y, cv=5, scoring='roc_auc')

print(f"    → Accuracy: {acc:.4f}")
print(f"    → ROC-AUC:  {auc:.4f}")
print(f"    → CV AUC (5-fold): {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
print("\n    Classification Report:")
print(classification_report(y_test, y_pred,
                             target_names=['Không nghỉ', 'Nghỉ việc']))

# Top features
print("    Top 10 features quan trọng nhất:")
importance_df = pd.DataFrame({
    'Feature': feature_names,
    'Importance': model.feature_importances_
}).sort_values('Importance', ascending=False).head(10)
for _, row in importance_df.iterrows():
    bar = '█' * int(row['Importance'] * 50)
    print(f"    {row['Feature']:45s} {row['Importance']:.4f} {bar}")

# ── 6. Lưu model ─────────────────────────────────────────────
print("\n[6] Lưu model...")
model_path = os.path.join(MODEL_DIR, 'cart_model.pkl')
features_path = os.path.join(MODEL_DIR, 'feature_names.pkl')
metrics_path = os.path.join(MODEL_DIR, 'metrics.pkl')

joblib.dump(model, model_path)
joblib.dump(feature_names, features_path)
joblib.dump({
    'accuracy': acc,
    'roc_auc': auc,
    'cv_auc_mean': float(cv_scores.mean()),
    'cv_auc_std': float(cv_scores.std()),
    'n_leaves': model.get_n_leaves(),
    'depth': model.get_depth(),
    'n_train': len(X_train),
    'n_test': len(X_test),
}, metrics_path)

print(f"    → Model: {model_path}")
print(f"    → Features: {features_path}")
print(f"    → Metrics: {metrics_path}")
print("\n✅ Train hoàn tất! Chạy app bằng: streamlit run app.py")
print("=" * 60)
