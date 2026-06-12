"""
Trang 3: Dự đoán nghỉ việc cho 1 nhân viên cụ thể.
"""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Dự đoán 1 NV | HR Analytics", page_icon="🔍", layout="wide")

from utils.styles import apply_styles, page_header, section_header
from utils.data_manager import load_employees
from utils.predictor import predict_one, get_feature_importance
from utils.history_manager import add_history_record
from utils.preprocessor import FIELD_LABELS, get_risk_level

apply_styles()
page_header("🔍 Dự đoán Nghỉ việc — 1 Nhân viên",
            "Chọn nhân viên, chạy mô hình CART và xem phân tích nguyên nhân chi tiết")

PLOTLY_DARK = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#e2e8f0"),
    margin=dict(l=10, r=10, t=40, b=10),
)

# ── Chọn nhân viên ─────────────────────────────────────────────
df = load_employees()

c_sel, c_btn = st.columns([4, 1])
with c_sel:
    emp_options = df.apply(
        lambda r: f"{r['TenNhanVien']} (#{int(r['EmployeeNumber'])}) — {r.get('Department','')} | {r.get('JobRole','')}",
        axis=1
    ).tolist()
    selected = st.selectbox("👤 Chọn nhân viên", emp_options)
    sel_idx = emp_options.index(selected)
    emp_row = df.iloc[sel_idx]
    emp_num = int(emp_row['EmployeeNumber'])

with c_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    predict_clicked = st.button("🚀 Dự đoán", type="primary", use_container_width=True)

# ── Hiển thị thông tin nhân viên ────────────────────────────
with st.expander("ℹ️ Thông tin nhân viên", expanded=False):
    info_cols = {
        'Tuổi': emp_row.get('Age'), 'Giới tính': emp_row.get('Gender'),
        'Hôn nhân': emp_row.get('MaritalStatus'), 'Phòng ban': emp_row.get('Department'),
        'Chức vụ': emp_row.get('JobRole'), 'Cấp độ': emp_row.get('JobLevel'),
        'Làm thêm giờ': emp_row.get('OverTime'), 'Thu nhập/tháng': f"${emp_row.get('MonthlyIncome', 0):,}",
        'Năm KN': emp_row.get('TotalWorkingYears'), 'Năm tại CT': emp_row.get('YearsAtCompany'),
        'HLS công việc (1-4)': emp_row.get('JobSatisfaction'),
        'HLS môi trường (1-4)': emp_row.get('EnvironmentSatisfaction'),
        'Khoảng cách nhà': f"{emp_row.get('DistanceFromHome', 0)} km",
        'Công tác': emp_row.get('BusinessTravel'),
    }
    cols = st.columns(4)
    for i, (k, v) in enumerate(info_cols.items()):
        with cols[i % 4]:
            st.metric(k, str(v) if v is not None else "—")

# ── Kết quả dự đoán ────────────────────────────────────────
if predict_clicked or st.session_state.get(f'result_{emp_num}'):
    try:
        if predict_clicked:
            with st.spinner("Đang chạy mô hình CART..."):
                result = predict_one(emp_row)
            st.session_state[f'result_{emp_num}'] = result
        else:
            result = st.session_state[f'result_{emp_num}']

        prob = result['probability']
        label = result['label']
        risk, risk_color = result['risk_level'], result['risk_color']
        rules = result['rules']

        st.markdown("---")

        # ── Card kết quả + Gauge ──────────────────────────────
        col_res, col_gauge, col_feat = st.columns([2, 2, 3])

        with col_res:
            section_header("Kết quả Dự đoán")
            is_attrition = label == 'Nghỉ việc'
            card_class = 'result-card-attrition' if is_attrition else 'result-card-no-attrition'
            emoji = "🚨" if is_attrition else "✅"
            txt_color = "#f87171" if is_attrition else "#34d399"
            st.markdown(f"""
            <div class="{card_class}">
                <div style="font-size:3rem">{emoji}</div>
                <div class="result-label" style="color:{txt_color}">{label}</div>
                <div class="result-prob" style="color:{risk_color}">{prob*100:.1f}%</div>
                <div class="result-subtitle">xác suất nghỉ việc</div>
                <div style="margin-top:0.8rem">
                    <span class="badge-{'high' if risk=='Cao' else 'medium' if risk=='Trung bình' else 'low'}">
                        Nguy cơ: {risk}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_gauge:
            section_header("Biểu đồ Xác suất")
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=prob * 100,
                number={'suffix': '%', 'font': {'size': 36, 'color': risk_color}},
                gauge={
                    'axis': {'range': [0, 100], 'tickwidth': 1,
                              'tickcolor': '#475569', 'tickfont': {'color': '#94a3b8'}},
                    'bar': {'color': risk_color, 'thickness': 0.35},
                    'bgcolor': 'rgba(0,0,0,0)',
                    'borderwidth': 0,
                    'steps': [
                        {'range': [0, 40],  'color': 'rgba(16,185,129,0.15)'},
                        {'range': [40, 70], 'color': 'rgba(245,158,11,0.15)'},
                        {'range': [70, 100],'color': 'rgba(239,68,68,0.15)'},
                    ],
                    'threshold': {
                        'line': {'color': '#ffffff', 'width': 2},
                        'thickness': 0.75,
                        'value': prob * 100
                    },
                },
                title={'text': f"<span style='color:#94a3b8;font-size:14px'>{result['label']}</span>"}
            ))
            fig_gauge.update_layout(**PLOTLY_DARK, height=260)
            st.plotly_chart(fig_gauge, use_container_width=True)

        with col_feat:
            section_header("Top Features Quan trọng")
            df_imp = get_feature_importance(12)
            fig_imp = px.bar(df_imp, x='Importance', y='ViName', orientation='h',
                              color='Importance',
                              color_continuous_scale=['#06b6d4', '#6366f1', '#ec4899'],
                              labels={'ViName': '', 'Importance': 'Mức quan trọng'})
            fig_imp.update_layout(**PLOTLY_DARK, height=260, coloraxis_showscale=False,
                                   yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(fig_imp, use_container_width=True)

        # ── Phân tích nguyên nhân (CART path) ─────────────────
        section_header("🌳 Phân tích Nguyên nhân — Đường đi qua cây CART")
        st.markdown(f"""
        <div class="info-box">
            Đây là chuỗi các điều kiện mà mô hình CART đã sử dụng để
            đưa ra kết quả <b>{label}</b> với xác suất <b>{prob*100:.1f}%</b>:
        </div>
        """, unsafe_allow_html=True)

        for i, rule in enumerate(rules):
            if rule.startswith("📌"):
                st.markdown(f'<div class="decision-final">{rule}</div>', unsafe_allow_html=True)
            else:
                st.markdown(
                    f'<div class="decision-rule">{"→ " * min(i, 6)}{i+1}. {rule}</div>',
                    unsafe_allow_html=True
                )

        # ── Lưu kết quả ───────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        col_save, col_info = st.columns([2, 5])
        with col_save:
            if st.button("💾 Lưu kết quả vào lịch sử", use_container_width=True):
                rule_text = " | ".join(rules[:5])
                hid = add_history_record(
                    loai="Đơn lẻ",
                    emp_number=emp_num,
                    ten_nv=str(emp_row.get('TenNhanVien', '')),
                    xac_suat=prob,
                    ket_qua=label,
                    muc_rui_ro=risk,
                    ghi_chu=rule_text[:300],
                )
                st.success(f"✅ Đã lưu lịch sử (ID: {hid})")

    except FileNotFoundError as e:
        st.error(f"❌ {e}")
        st.code("python model/train_model.py", language="bash")
    except Exception as e:
        st.error(f"❌ Lỗi: {e}")
        import traceback; st.code(traceback.format_exc())
else:
    st.markdown("""
    <div class="info-box" style="text-align:center; padding:2rem;">
        👆 Chọn nhân viên và nhấn <b>🚀 Dự đoán</b> để xem kết quả phân tích
    </div>
    """, unsafe_allow_html=True)
