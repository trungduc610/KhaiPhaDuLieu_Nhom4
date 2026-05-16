import streamlit as st
import pandas as pd
import joblib
import shap
import matplotlib.pyplot as plt
import os

# --- CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="Hệ Thống Phân Tích Nhân viên Nghỉ Việc", page_icon="👥", layout="wide")
st.title("📊 PHẦN MỀM DỰ ĐOÁN & PHÂN TÍCH NHÂN SỰ NGHỈ VIỆC")

# --- 1. TẢI DỮ LIỆU & MÔ HÌNH ---
@st.cache_resource
def load_model():
    path = './Python/thong_so_mo_hinh/cart_decision_tree_model.joblib'
    if os.path.exists(path):
        return joblib.load(path)
    else:
        st.error(f"Không tìm thấy file mô hình tại: {path}")
        return None

@st.cache_data
def load_data():
    try:
        df_prepared = pd.read_csv('./Python/du_lieu/data_output.csv')
        df_raw = pd.read_csv('./Python/du_lieu/data_input.csv') 
        return df_prepared, df_raw
    except Exception as e:
        st.error(f"Lỗi tải dữ liệu: {e}")
        return None, None

model = load_model()
df_prepared, df_raw = load_data()

if model and df_prepared is not None:
    X = df_prepared.drop(columns=['Attrition']) if 'Attrition' in df_prepared.columns else df_prepared
    display_list = df_raw['EmployeeNumber'].astype(str) + " - (ID: " + df_prepared.index.astype(str) + ")"

    # --- SIDEBAR TỔNG ---
    with st.sidebar:
        st.header("⚙️ Bảng Điều Khiển")
        selected_option = st.selectbox("Lựa chọn nhân viên cần phân tích:", display_list)
        employee_id = int(selected_option.split("ID: ")[1].replace(")", ""))
        emp_base = X.iloc[[employee_id]].copy()
        base_prob = model.predict_proba(emp_base)[0][1] * 100
        
        st.markdown("---")
        st.metric(label="Xác suất nghỉ việc hiện tại", value=f"{base_prob:.1f}%")

    # --- MAIN TABS ---
    tab1, tab2 = st.tabs(["🔍 Giải thích nguyên nhân (SHAP)", "⚙️ Mô phỏng thay đổi chính sách"])

    # =====================================================================
    # TAB 1: GIẢI THÍCH TẠI SAO NGHỈ VIỆC
    # =====================================================================
    with tab1:
        st.header(f"Phân tích nhân viên ID: {employee_id}")
        st.info("💡 **Hướng dẫn đọc biểu đồ:** Các thanh màu **ĐỎ** đẩy rủi ro nghỉ việc lên cao. Các thanh màu **XANH** kéo rủi ro giữ lại an toàn.")
        
        if st.button("Tạo biểu đồ phân tích SHAP", type="primary"):
            with st.spinner("Đang tính toán mức độ ảnh hưởng của các đặc trưng..."):
                explainer = shap.TreeExplainer(model)
                shap_obj = explainer(emp_base)
                
                fig, ax = plt.subplots(figsize=(10, 6))
                try:
                    shap.plots.waterfall(shap_obj[0, :, 1], max_display=10, show=False)
                except IndexError:
                    shap.plots.waterfall(shap_obj[0], max_display=10, show=False)
                
                st.pyplot(fig, clear_figure=True)

    # =====================================================================
    # TAB 2: DỰ ĐOÁN DỰA TRÊN THÔNG SỐ 
    # =====================================================================
    with tab2:
        st.header("Mô phỏng thay đổi điều kiện làm việc")
        st.write("Thay đổi các thông số bên dưới để làm giảm nguy cơ nghỉ việc của nhân viên.")
        
        available_columns = list(X.columns)
        
        c1, c2 = st.columns(2)
        
        def render_dynamic_input(col_name, col_obj, base_df, key_suffix):
            current_val = float(base_df[col_name].values[0])
            min_val = float(X[col_name].min())
            max_val = float(X[col_name].max())
            
            if min_val == 0.0 and max_val == 1.0:
                options = [0.0, 1.0]
                idx = options.index(current_val) if current_val in options else 0
                return col_obj.selectbox(
                    f"[{col_name}] (0=Không, 1=Có):", 
                    options, 
                    index=idx, 
                    key=f"select_{col_name}_{key_suffix}"
                )
            else:
                step_val = max(0.1, (max_val - min_val) / 100)
                return col_obj.slider(
                    f"Giá trị [{col_name}]:", 
                    min_value=min_val, 
                    max_value=max_val, 
                    value=current_val, 
                    step=step_val, 
                    key=f"slider_{col_name}_{key_suffix}"
                )

        placeholder = "-- Vui lòng chọn --"
        options_1 = [placeholder] + available_columns
        
        c1, c2 = st.columns(2)
        
        with c1:
            feature_1 = st.selectbox("Chọn thông số can thiệp thứ 1:", options_1, index=0)
            if feature_1 != placeholder:
                new_val_1 = render_dynamic_input(feature_1, st, emp_base, key_suffix="1")
            else:
                new_val_1 = None

        with c2:
            if feature_1 != placeholder:
                options_2 = [placeholder] + [col for col in available_columns if col != feature_1]
            else:
                options_2 = [placeholder] + available_columns
                
            feature_2 = st.selectbox("Chọn thông số can thiệp thứ 2:", options_2, index=0)
            if feature_2 != placeholder:
                new_val_2 = render_dynamic_input(feature_2, st, emp_base, key_suffix="2")
            else:
                new_val_2 = None

        st.markdown("---")
        
        if st.button("Chạy mô phỏng kết quả", key="sim_btn", type="primary"):
            if feature_1 == placeholder and feature_2 == placeholder:
                st.warning("⚠️ Vui lòng chọn ít nhất 1 thông số từ danh sách để chạy mô phỏng!")
            else:
                emp_sim = emp_base.copy()
                
                if feature_1 != placeholder:
                    emp_sim[feature_1] = new_val_1
                if feature_2 != placeholder:
                    emp_sim[feature_2] = new_val_2
                
                new_prob = model.predict_proba(emp_sim)[0][1] * 100
                diff = new_prob - base_prob
                
                st.subheader("Kết quả mô phỏng")
                
                col_metric1, col_metric2 = st.columns([1, 2])
                with col_metric1:
                    st.metric(label="Xác suất sau mô phỏng", value=f"{new_prob:.1f}%", delta=f"{diff:.1f}%", delta_color="inverse")
                
                with col_metric2:
                    if diff < 0:
                        st.success(f"✅ Hành động này giúp **GIẢM** nguy cơ nghỉ việc xuống {abs(diff):.1f}%.")
                    elif diff > 0:
                        st.error(f"⚠️ Hành động này làm **TĂNG** nguy cơ nghỉ việc thêm {diff:.1f}%.")
                    else:
                        st.info("ℹ️ Các thay đổi này chưa đủ để tác động đến quyết định của nhân viên.")