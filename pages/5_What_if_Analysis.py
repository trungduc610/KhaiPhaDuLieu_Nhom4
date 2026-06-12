"""
Trang 5: What-if Analysis — Mô phỏng kịch bản thay đổi thông tin nhân viên.
"""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="What-if Analysis | HR Analytics", page_icon="🔄", layout="wide")

from utils.styles import apply_styles, page_header, section_header
from utils.data_manager import load_employees
from utils.predictor import predict_one
from utils.history_manager import add_history_record
from utils.preprocessor import (DEPT_OPTIONS, JOBROLE_OPTIONS, BUSINESSTRAVEL_OPTIONS,
                                  MARITALSTATUS_OPTIONS, GENDER_OPTIONS)

apply_styles()
page_header("🔄 What-if Analysis",
            "Mô phỏng kịch bản: thay đổi thông số và xem ảnh hưởng đến nguy cơ nghỉ việc")

PLOTLY_DARK = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#e2e8f0"),
    margin=dict(l=20, r=20, t=40, b=20),
)

df_all = load_employees()

# ── Chọn nhân viên ────────────────────────────────────────────
section_header("1️⃣ Chọn nhân viên")
emp_labels = df_all.apply(
    lambda r: f"{r['TenNhanVien']} (#{int(r['EmployeeNumber'])}) — {r.get('Department','')} | {r.get('JobRole','')}",
    axis=1
).tolist()
selected = st.selectbox("👤 Nhân viên", emp_labels, label_visibility="collapsed")
sel_idx = emp_labels.index(selected)
emp_row = df_all.iloc[sel_idx].to_dict()
emp_num = int(emp_row['EmployeeNumber'])

# ── Dự đoán gốc ────────────────────────────────────────────
try:
    with st.spinner("Đang tính xác suất gốc..."):
        original_result = predict_one(emp_row)
    orig_prob = original_result['probability']
    orig_label = original_result['label']
    orig_risk = original_result['risk_level']
    orig_color = original_result['risk_color']
except FileNotFoundError as e:
    st.error(f"❌ {e}")
    st.code("python model/train_model.py", language="bash")
    st.stop()

st.markdown("---")

# ── Bố cục 2 cột: Thông số hiện tại | Thay đổi ────────────
col_orig, col_new = st.columns(2)

with col_orig:
    section_header("📋 Thông số hiện tại")
    st.markdown(f"""
    <div class="compare-card compare-before">
        <div style="font-size:0.85rem; color:#94a3b8; margin-bottom:0.5rem">Xác suất nghỉ việc</div>
        <div style="font-size:2.5rem; font-weight:800; color:{orig_color}">{orig_prob*100:.1f}%</div>
        <div style="color:{orig_color}; font-weight:600">{orig_label}</div>
        <div style="margin-top:0.5rem">
            <span class="badge-{'high' if orig_risk=='Cao' else 'medium' if orig_risk=='Trung bình' else 'low'}">
                Nguy cơ: {orig_risk}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Hiện thông tin hiện tại
    info_items = [
        ('💰 Thu nhập/tháng', f"${int(emp_row.get('MonthlyIncome',0)):,}"),
        ('⏰ Làm thêm giờ', str(emp_row.get('OverTime',''))),
        ('🏢 Phòng ban', str(emp_row.get('Department',''))),
        ('💼 Chức vụ', str(emp_row.get('JobRole',''))),
        ('📅 Năm tại công ty', str(emp_row.get('YearsAtCompany',''))),
        ('😊 HLS công việc', str(emp_row.get('JobSatisfaction',''))),
        ('🌿 HLS môi trường', str(emp_row.get('EnvironmentSatisfaction',''))),
        ('⚖️ Cân bằng cuộc sống', str(emp_row.get('WorkLifeBalance',''))),
        ('🏠 Khoảng cách nhà', f"{emp_row.get('DistanceFromHome','')} km"),
        ('📊 Năm ở vị trí hiện tại', str(emp_row.get('YearsInCurrentRole',''))),
    ]
    for label, val in info_items:
        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; padding:0.3rem 0;
                    border-bottom:1px solid rgba(255,255,255,0.05);">
            <span style="color:#94a3b8; font-size:0.85rem">{label}</span>
            <span style="color:#e2e8f0; font-weight:600; font-size:0.85rem">{val}</span>
        </div>
        """, unsafe_allow_html=True)

with col_new:
    section_header("✏️ Thay đổi thông số (tạm thời)")
    st.markdown("""
    <div class="info-box">
        ⚠️ Các thay đổi này <b>không ảnh hưởng</b> đến dữ liệu gốc.
        Chỉ dùng để mô phỏng kịch bản.
    </div>
    """, unsafe_allow_html=True)

    # Form nhập giá trị mới
    new_vals = emp_row.copy()

    w1, w2 = st.columns(2)
    with w1:
        new_vals['MonthlyIncome'] = st.number_input(
            "💰 Thu nhập tháng ($)", 1000, 200000,
            int(emp_row.get('MonthlyIncome', 5000)), step=500
        )
        new_vals['OverTime'] = st.selectbox(
            "⏰ Làm thêm giờ", ['No', 'Yes'],
            index=0 if str(emp_row.get('OverTime','No')) == 'No' else 1
        )
        new_vals['JobSatisfaction'] = st.select_slider(
            "😊 HLS công việc (1-4)", [1,2,3,4],
            value=int(emp_row.get('JobSatisfaction', 3))
        )
        new_vals['EnvironmentSatisfaction'] = st.select_slider(
            "🌿 HLS môi trường (1-4)", [1,2,3,4],
            value=int(emp_row.get('EnvironmentSatisfaction', 3))
        )
        new_vals['WorkLifeBalance'] = st.select_slider(
            "⚖️ Cân bằng cuộc sống (1-4)", [1,2,3,4],
            value=int(emp_row.get('WorkLifeBalance', 3))
        )
    with w2:
        new_vals['YearsAtCompany'] = st.number_input(
            "📅 Năm tại công ty", 0, 40, int(emp_row.get('YearsAtCompany', 4))
        )
        new_vals['YearsInCurrentRole'] = st.number_input(
            "📊 Năm ở vị trí hiện tại", 0, 20, int(emp_row.get('YearsInCurrentRole', 2))
        )
        new_vals['DistanceFromHome'] = st.number_input(
            "🏠 Khoảng cách nhà (km)", 1, 30, int(emp_row.get('DistanceFromHome', 5))
        )
        new_vals['StockOptionLevel'] = st.selectbox(
            "📈 Mức cổ phiếu (0-3)", [0,1,2,3],
            index=int(emp_row.get('StockOptionLevel', 1))
        )
        new_vals['TrainingTimesLastYear'] = st.number_input(
            "📚 Số lần đào tạo/năm", 0, 6, int(emp_row.get('TrainingTimesLastYear', 3))
        )

    run_whatif = st.button("🔄 Chạy dự đoán với thông số mới", type="primary", use_container_width=True)

# ── So sánh kết quả ──────────────────────────────────────────
if run_whatif:
    with st.spinner("Đang tính toán..."):
        new_result = predict_one(new_vals)
    st.session_state['whatif_result'] = new_result
    st.session_state['whatif_orig'] = orig_prob

if 'whatif_result' in st.session_state:
    new_result = st.session_state['whatif_result']
    new_prob = new_result['probability']
    new_label = new_result['label']
    new_risk = new_result['risk_level']
    new_color = new_result['risk_color']
    delta = new_prob - orig_prob

    st.markdown("---")
    section_header("📊 So sánh Kết quả")

    comp1, comp2, comp3 = st.columns([2, 1, 2])

    with comp1:
        st.markdown(f"""
        <div class="compare-card compare-before">
            <div style="font-size:0.85rem; color:#f87171;">🔴 Trước thay đổi</div>
            <div style="font-size:2.8rem; font-weight:800; color:{orig_color}; line-height:1">{orig_prob*100:.1f}%</div>
            <div style="color:{orig_color}">{original_result['label']}</div>
            <div style="margin-top:0.5rem">
                <span class="badge-{'high' if orig_risk=='Cao' else 'medium' if orig_risk=='Trung bình' else 'low'}">
                    {orig_risk}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with comp2:
        delta_pct = abs(delta) * 100
        arrow = "📉" if delta < 0 else "📈"
        delta_color = "#10b981" if delta < 0 else "#ef4444"
        st.markdown(f"""
        <div style="text-align:center; padding:2rem 0.5rem;">
            <div style="font-size:2rem">{arrow}</div>
            <div style="font-size:1.5rem; font-weight:800; color:{delta_color}">
                {'+' if delta > 0 else ''}{delta*100:+.1f}%
            </div>
            <div style="color:#94a3b8; font-size:0.8rem; margin-top:0.3rem">
                {'Tăng nguy cơ' if delta > 0 else 'Giảm nguy cơ'}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with comp3:
        st.markdown(f"""
        <div class="compare-card compare-after">
            <div style="font-size:0.85rem; color:#34d399;">🟢 Sau thay đổi</div>
            <div style="font-size:2.8rem; font-weight:800; color:{new_color}; line-height:1">{new_prob*100:.1f}%</div>
            <div style="color:{new_color}">{new_label}</div>
            <div style="margin-top:0.5rem">
                <span class="badge-{'high' if new_risk=='Cao' else 'medium' if new_risk=='Trung bình' else 'low'}">
                    {new_risk}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Gauge so sánh
    fig = go.Figure()
    for val, name, color in [
        (orig_prob * 100, "Trước thay đổi", orig_color),
        (new_prob * 100, "Sau thay đổi", new_color),
    ]:
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=val,
            number={'suffix': '%', 'font': {'size': 28}},
            title={'text': f"<span style='color:#94a3b8;font-size:13px'>{name}</span>"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': color, 'thickness': 0.3},
                'bgcolor': 'rgba(0,0,0,0)',
                'steps': [
                    {'range': [0, 40],  'color': 'rgba(16,185,129,0.12)'},
                    {'range': [40, 70], 'color': 'rgba(245,158,11,0.12)'},
                    {'range': [70, 100],'color': 'rgba(239,68,68,0.12)'},
                ],
            },
            domain={'row': 0, 'column': fig.data.__len__()}
        ))

    fig.update_layout(
        **PLOTLY_DARK,
        grid={'rows': 1, 'columns': 2, 'pattern': 'independent'},
        height=220
    )
    st.plotly_chart(fig, use_container_width=True)

    # Lưu kịch bản
    col_save, _ = st.columns([2, 5])
    with col_save:
        if st.button("💾 Lưu kịch bản mô phỏng", type="primary", use_container_width=True):
            ghi_chu = f"What-if: trước={orig_prob*100:.1f}%, sau={new_prob*100:.1f}%, delta={delta*100:+.1f}%"
            hid = add_history_record(
                loai="What-if",
                emp_number=emp_num,
                ten_nv=str(emp_row.get('TenNhanVien', '')),
                xac_suat=new_prob,
                ket_qua=new_label,
                muc_rui_ro=new_risk,
                ghi_chu=ghi_chu,
            )
            st.success(f"✅ Đã lưu kịch bản (ID: {hid})")
