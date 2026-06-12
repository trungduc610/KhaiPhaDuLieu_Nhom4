"""
Wrapper cho mô hình CART: dự đoán, giải thích đường đi qua cây.
"""

import os
import numpy as np
import pandas as pd
import joblib

from utils.preprocessor import (
    FEATURE_COLS, FEATURE_LABELS, preprocess_employee_row,
    preprocess_dataframe, get_risk_level
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'model', 'cart_model.pkl')
FEATURES_PATH = os.path.join(BASE_DIR, 'model', 'feature_names.pkl')

_model = None
_feature_names = None


def _load_model():
    global _model, _feature_names
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f'Model chưa được train! Hãy chạy: python model/train_model.py'
            )
        _model = joblib.load(MODEL_PATH)
        _feature_names = joblib.load(FEATURES_PATH)
    return _model, _feature_names


def predict_one(employee_row):
    """
    Dự đoán cho 1 nhân viên.
    employee_row: dict hoặc pd.Series theo format data_input
    Trả về dict:
        - label: 'Nghỉ việc' | 'Không nghỉ việc'
        - probability: float (0-1) xác suất nghỉ việc
        - risk_level: 'Cao' | 'Trung bình' | 'Thấp'
        - risk_color: hex color
        - rules: list[str] - đường đi qua cây CART
        - feature_contributions: dict feature → contribution (signed)
    """
    model, feature_names = _load_model()
    features = preprocess_employee_row(employee_row)
    X = np.array([[features[f] for f in feature_names]])

    prob_arr = model.predict_proba(X)[0]
    # class 1 = Attrition (nghỉ việc)
    classes = list(model.classes_)
    if 1 in classes:
        prob = prob_arr[classes.index(1)]
    else:
        prob = prob_arr[1] if len(prob_arr) > 1 else prob_arr[0]

    label = 'Nghỉ việc' if prob >= 0.5 else 'Không nghỉ việc'
    risk_level, risk_color = get_risk_level(prob)

    rules = _get_decision_rules(model, feature_names, X)

    return {
        'label': label,
        'probability': float(prob),
        'risk_level': risk_level,
        'risk_color': risk_color,
        'rules': rules,
        'X': X,
        'feature_names': feature_names,
    }


def predict_batch(df_employees):
    """
    Dự đoán hàng loạt cho DataFrame nhân viên (data_input format).
    Trả về DataFrame kết quả với các cột bổ sung:
        - XacSuatNghiViec, NhanNhan, MucRuiRo
    """
    model, feature_names = _load_model()
    X_df = preprocess_dataframe(df_employees)
    X = X_df[feature_names].values

    prob_arr = model.predict_proba(X)
    classes = list(model.classes_)
    if 1 in classes:
        probs = prob_arr[:, classes.index(1)]
    else:
        probs = prob_arr[:, 1] if prob_arr.shape[1] > 1 else prob_arr[:, 0]

    result = df_employees.copy()
    result['XacSuatNghiViec'] = probs
    result['NhanNhan'] = result['XacSuatNghiViec'].apply(
        lambda p: 'Nghỉ việc' if p >= 0.5 else 'Không nghỉ việc'
    )
    result['MucRuiRo'] = result['XacSuatNghiViec'].apply(
        lambda p: get_risk_level(p)[0]
    )
    return result


def get_feature_importance(top_n=15):
    """
    Lấy top N features quan trọng nhất.
    Trả về DataFrame với cột: Feature, ViName, Importance.
    """
    model, feature_names = _load_model()
    importances = model.feature_importances_
    df = pd.DataFrame({
        'Feature': feature_names,
        'ViName': [FEATURE_LABELS.get(f, f) for f in feature_names],
        'Importance': importances
    }).sort_values('Importance', ascending=False).head(top_n)
    return df.reset_index(drop=True)


def _get_decision_rules(model, feature_names, X):
    """Trích xuất các điều kiện trên đường đi qua cây CART."""
    from sklearn.tree import _tree

    tree = model.tree_
    feature = tree.feature
    threshold = tree.threshold

    node_indicator = model.decision_path(X)
    leaf_id = model.apply(X)[0]
    node_ids = node_indicator.indices[
        node_indicator.indptr[0]: node_indicator.indptr[1]
    ]

    rules = []
    for node_id in node_ids:
        if node_id == leaf_id:
            # Lá cây - lấy thông tin phân phối lớp
            node_val = tree.value[node_id][0]
            total = node_val.sum()
            if total > 0:
                classes = model.classes_
                class_dict = {int(c): int(v) for c, v in zip(classes, node_val)}
                count_1 = class_dict.get(1, 0)
                rules.append(
                    f'📌 Nút lá: {int(count_1)}/{int(total)} mẫu nghỉ việc '
                    f'({100*count_1/total:.0f}%)'
                )
            break

        feat_idx = feature[node_id]
        feat_name = feature_names[feat_idx]
        feat_label = FEATURE_LABELS.get(feat_name, feat_name)
        thresh = threshold[node_id]
        feat_val = float(X[0, feat_idx])

        if feat_val <= thresh:
            direction = '≤'
        else:
            direction = '>'

        # Hiển thị đẹp hơn cho binary features
        if thresh == 0.5:
            if direction == '≤':
                readable = f'{feat_label} = Không'
            else:
                readable = f'{feat_label} = Có'
        else:
            readable = f'{feat_label} {direction} {thresh:.2f} (giá trị: {feat_val:.2f})'

        rules.append(readable)

    return rules
