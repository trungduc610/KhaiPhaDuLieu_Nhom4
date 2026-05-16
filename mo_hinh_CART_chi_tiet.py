import numpy as np
from collections import Counter

# ==========================================
# BƯỚC 1: ĐỊNH NGHĨA CẤU TRÚC MỘT NÚT (NODE)
# ==========================================
class Node:
    def __init__(self, feature=None, threshold=None, left=None, right=None, *, value=None):
        self.feature = feature      # Chỉ mục của cột được chọn để chia
        self.threshold = threshold  # Ngưỡng giá trị để chia nhánh
        self.left = left            # Nhánh con bên trái (<= threshold)
        self.right = right          # Nhánh con bên phải (> threshold)
        self.value = value          # Giá trị dự đoán (chỉ tồn tại nếu đây là nút lá)

    def is_leaf(self):
        # Kiểm tra xem đây có phải là nút lá không
        return self.value is not None

# ==========================================
# BƯỚC 2: XÂY DỰNG LỚP CÂY QUYẾT ĐỊNH
# ==========================================
class CustomDecisionTree:
    def __init__(self, max_depth=4):
        self.max_depth = max_depth
        self.root = None # Rễ cây ban đầu trống

    def fit(self, X, y):
        # Đảm bảo đầu vào là numpy array để xử lý toán học dễ hơn
        X = np.array(X)
        y = np.array(y)
        self.root = self._build_tree(X, y, depth=0)

    def predict(self, X):
        X = np.array(X)
        return np.array([self._traverse_tree(x, self.root) for x in X])

    # --- CÁC HÀM XỬ LÝ LÕI TOÁN HỌC ---
    
    def _gini(self, y):
        """Tính chỉ số Gini Impurity của một tập nhãn y"""
        # Đếm số lượng mỗi nhãn lớp
        hist = np.bincount(y)
        # Tính xác suất (tỷ lệ) của mỗi nhãn
        ps = hist / len(y)
        # Công thức Gini: 1 - Sum(p^2)
        return 1 - np.sum([p**2 for p in ps if p > 0])

    def _split(self, X_column, threshold):
        """Chia dữ liệu thành 2 nhóm dựa trên ngưỡng"""
        left_idxs = np.argwhere(X_column <= threshold).flatten()
        right_idxs = np.argwhere(X_column > threshold).flatten()
        return left_idxs, right_idxs

    def _information_gain(self, y, X_column, threshold):
        """Tính mức độ giảm vẩn đục (Information Gain) nếu chia tại ngưỡng này"""
        parent_gini = self._gini(y)
        
        left_idxs, right_idxs = self._split(X_column, threshold)
        if len(left_idxs) == 0 or len(right_idxs) == 0:
            return 0 # Nếu việc chia không tách được dữ liệu, Gain = 0
            
        n = len(y)
        n_l, n_r = len(left_idxs), len(right_idxs)
        e_l, e_r = self._gini(y[left_idxs]), self._gini(y[right_idxs])
        
        # Gini của 2 nút con sau khi chia (tính trung bình có trọng số)
        child_gini = (n_l / n) * e_l + (n_r / n) * e_r
        
        # Độ tăng thông tin (Gain)
        ig = parent_gini - child_gini
        return ig

    def _best_split(self, X, y):
        """Thuật toán Tham lam: Duyệt qua TẤT CẢ các cột và TẤT CẢ các giá trị để tìm phép chia tốt nhất"""
        best_ig = -1
        split_idx, split_thresh = None, None
        n_samples, n_features = X.shape

        for feat_idx in range(n_features):
            X_column = X[:, feat_idx]
            # Chỉ thử nghiệm các ngưỡng là các giá trị thực tế xuất hiện trong cột đó
            thresholds = np.unique(X_column)
            
            for threshold in thresholds:
                ig = self._information_gain(y, X_column, threshold)
                
                if ig > best_ig:
                    best_ig = ig
                    split_idx = feat_idx
                    split_thresh = threshold

        return split_idx, split_thresh

    def _build_tree(self, X, y, depth):
        """Hàm đệ quy để xây cây nhánh theo nhánh"""
        n_samples, n_features = X.shape
        n_labels = len(np.unique(y))

        # ĐIỀU KIỆN DỪNG (Stopping Criteria)
        # 1. Đạt độ sâu tối đa (max_depth)
        # 2. Nút thuần khiết (chỉ còn 1 loại nhãn)
        # 3. Quá ít mẫu để chia tiếp
        if (depth >= self.max_depth) or (n_labels == 1) or (n_samples < 2):
            leaf_value = self._most_common_label(y)
            return Node(value=leaf_value)

        # TÌM PHÉP CHIA TỐT NHẤT
        best_feat, best_thresh = self._best_split(X, y)

        # Nếu không tìm được cách chia nào tốt hơn (Gain = 0), dừng lại thành nút lá
        if best_feat is None:
            leaf_value = self._most_common_label(y)
            return Node(value=leaf_value)

        # CHIA DỮ LIỆU VÀ GỌI ĐỆ QUY CHO 2 NHÁNH CON
        left_idxs, right_idxs = self._split(X[:, best_feat], best_thresh)
        left_child = self._build_tree(X[left_idxs, :], y[left_idxs], depth + 1)
        right_child = self._build_tree(X[right_idxs, :], y[right_idxs], depth + 1)

        return Node(best_feat, best_thresh, left_child, right_child)

    def _most_common_label(self, y):
        """Trả về nhãn xuất hiện nhiều nhất tại nút lá (Bầu chọn theo số đông)"""
        counter = Counter(y)
        value = counter.most_common(1)[0][0]
        return value

    def _traverse_tree(self, x, node):
        """Duyệt từng dòng dữ liệu từ rễ xuống lá để dự đoán"""
        if node.is_leaf():
            return node.value

        if x[node.feature] <= node.threshold:
            return self._traverse_tree(x, node.left)
        return self._traverse_tree(x, node.right)

    # --- HÀM BỔ TRỢ: IN RA BỘ QUY TẮC ---
    def print_tree(self, node=None, depth=0, feature_names=None):
        node = node or self.root
        if node.is_leaf():
            print("  " * depth + f"➜ DỰ ĐOÁN LỚP: {node.value}")
            return
        
        feat_name = feature_names[node.feature] if feature_names else f"Cột_{node.feature}"
        print("  " * depth + f"NẾU {feat_name} <= {node.threshold}:")
        self.print_tree(node.left, depth + 1, feature_names)
        
        print("  " * depth + f"NGƯỢC LẠI ({feat_name} > {node.threshold}):")
        self.print_tree(node.right, depth + 1, feature_names)