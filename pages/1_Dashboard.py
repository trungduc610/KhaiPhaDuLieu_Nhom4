"""
Trang 1: Dashboard - Tổng quan nhân sự và kết quả dự đoán.
"""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Dashboard | HR Analytics", page_icon="📊", layout="wide")

from utils.styles import apply_styles, page_header, section_header, metric_card
from utils.data_manager import load_employees
from utils.predictor import predict_batch
from utils.preprocessor import get_risk_level

apply_styles()
page_header("📊 Dashboard", "Tổng quan tình trạng nhân sự và nguy cơ nghỉ việc")

PLOTLY_DARK = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#e2e8f0"),
    margin=dict(l=10, r=10, t=40, b=10),
)


@st.cache_data(ttl=60, show_spinner="Đang chạy dự đoán toàn bộ nhân viên...")
def get_predictions():
    df = load_employees()
    return predict_batch(df)


try:
    df = get_predictions()
except FileNotFoundError as e:
    st.error(f"❌ {e}")
    st.code("python model/train_model.py", language="bash")
    st.stop()

n_total = len(df)
n_high   = (df['MucRuiRo'] == 'Cao').sum()
n_medium = (df['MucRuiRo'] == 'Trung bình').sum()
n_low    = (df['MucRuiRo'] == 'Thấp').sum()

# ── Metric cards ──────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1: metric_card("👥", f"{n_total:,}", "Tổng nhân viên")
with c2: metric_card("🔴", f"{n_high:,}", "Nguy cơ Cao (>70%)", "#ef4444")
with c3: metric_card("🟡", f"{n_medium:,}", "Nguy cơ Trung bình (40-70%)", "#f59e0b")
with c4: metric_card("🟢", f"{n_low:,}", "Nguy cơ Thấp (<40%)", "#10b981")

st.markdown("<br>", unsafe_allow_html=True)

# ── Biểu đồ hàng 1 ───────────────────────────────────────────
col_l, col_r = st.columns(2)

with col_l:
    section_header("Phân bố xác suất nghỉ việc")
    fig = px.histogram(
        df, x='XacSuatNghiViec', nbins=30,
        color_discrete_sequence=['#6366f1'],
        labels={'XacSuatNghiViec': 'Xác suất nghỉ việc'},
    )
    fig.add_vline(x=0.4, line_dash="dot", line_color="#f59e0b", annotation_text="40%")
    fig.add_vline(x=0.7, line_dash="dot", line_color="#ef4444", annotation_text="70%")
    fig.update_layout(**PLOTLY_DARK, height=280,
                      xaxis_title="Xác suất", yaxis_title="Số nhân viên")
    st.plotly_chart(fig, use_container_width=True)

with col_r:
    section_header("Tỷ lệ mức rủi ro")
    pie_data = pd.DataFrame({
        'Mức độ': ['Cao (>70%)', 'Trung bình (40-70%)', 'Thấp (<40%)'],
        'Số lượng': [n_high, n_medium, n_low]
    })
    fig2 = px.pie(
        pie_data, values='Số lượng', names='Mức độ',
        color='Mức độ',
        color_discrete_map={
            'Cao (>70%)': '#ef4444',
            'Trung bình (40-70%)': '#f59e0b',
            'Thấp (<40%)': '#10b981'
        },
        hole=0.5,
    )
    fig2.update_traces(textposition='outside', textinfo='percent+label')
    fig2.update_layout(**PLOTLY_DARK, height=280, showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

# ── Biểu đồ hàng 2 ───────────────────────────────────────────
col_a, col_b = st.columns(2)

if 'Department' in df.columns:
    with col_a:
        section_header("Số nhân viên theo Phòng ban")
        dept_count = df.groupby('Department').size().reset_index(name='Số lượng')
        fig3 = px.bar(dept_count, x='Department', y='Số lượng',
                      color_discrete_sequence=['#6366f1'],
                      labels={'Department': 'Phòng ban'})
        fig3.update_layout(**PLOTLY_DARK, height=260)
        st.plotly_chart(fig3, use_container_width=True)

    with col_b:
        section_header("Tỷ lệ nguy cơ cao theo Phòng ban")
        dept_risk = df.groupby('Department').agg(
            Tong=('EmployeeNumber', 'count'),
            NguyCoC=('MucRuiRo', lambda x: (x == 'Cao').sum())
        ).reset_index()
        dept_risk['PhanTram'] = (dept_risk['NguyCoC'] / dept_risk['Tong'] * 100).round(1)
        fig4 = px.bar(dept_risk, x='Department', y='PhanTram',
                      color='PhanTram',
                      color_continuous_scale=['#10b981', '#f59e0b', '#ef4444'],
                      labels={'Department': 'Phòng ban', 'PhanTram': '% Nguy cơ cao'},
                      text='PhanTram')
        fig4.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig4.update_layout(**PLOTLY_DARK, height=260, coloraxis_showscale=False)
        st.plotly_chart(fig4, use_container_width=True)

# ── Bảng cảnh báo top 15 ─────────────────────────────────────
section_header("🚨 Cảnh báo: Top 15 nhân viên nguy cơ cao nhất")

top15 = (df[df['MucRuiRo'] == 'Cao']
         .sort_values('XacSuatNghiViec', ascending=False)
         .head(15))

if len(top15) == 0:
    top15 = df.sort_values('XacSuatNghiViec', ascending=False).head(15)

cols_show = ['EmployeeNumber', 'TenNhanVien', 'Department', 'JobRole',
             'MonthlyIncome', 'OverTime', 'XacSuatNghiViec', 'MucRuiRo']
cols_show = [c for c in cols_show if c in top15.columns]

display = top15[cols_show].copy()
display['XacSuatNghiViec'] = (display['XacSuatNghiViec'] * 100).round(1).astype(str) + '%'
display.columns = [
    {'EmployeeNumber': 'Mã NV', 'TenNhanVien': 'Tên NV',
     'Department': 'Phòng ban', 'JobRole': 'Chức vụ',
     'MonthlyIncome': 'Thu nhập/tháng', 'OverTime': 'OT',
     'XacSuatNghiViec': 'Xác suất (%)', 'MucRuiRo': 'Mức rủi ro'}.get(c, c)
    for c in cols_show
]

st.dataframe(display, use_container_width=True, hide_index=True,
             column_config={
                 'Mức rủi ro': st.column_config.TextColumn('Mức rủi ro'),
                 'Xác suất (%)': st.column_config.TextColumn('Xác suất'),
             })
