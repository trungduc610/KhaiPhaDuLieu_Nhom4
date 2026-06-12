"""
Quản lý lịch sử dự đoán - lưu trữ bằng CSV.
"""

import os
import json
from datetime import datetime
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HISTORY_CSV = os.path.join(BASE_DIR, 'du_lieu', 'history.csv')

HISTORY_COLS = [
    'ID', 'ThoiGian', 'LoaiDuDoan', 'EmployeeNumber', 'TenNhanVien',
    'XacSuat', 'KetQua', 'MucRuiRo', 'GhiChu'
]


def _ensure_history():
    if not os.path.exists(HISTORY_CSV):
        df = pd.DataFrame(columns=HISTORY_COLS)
        df.to_csv(HISTORY_CSV, index=False)


def load_history():
    """Tải toàn bộ lịch sử dự đoán."""
    _ensure_history()
    try:
        df = pd.read_csv(HISTORY_CSV)
        for col in HISTORY_COLS:
            if col not in df.columns:
                df[col] = ''
        return df
    except Exception:
        return pd.DataFrame(columns=HISTORY_COLS)


def save_history(df):
    _ensure_history()
    df.to_csv(HISTORY_CSV, index=False)


def add_history_record(
    loai: str,
    emp_number,
    ten_nv: str,
    xac_suat: float,
    ket_qua: str,
    muc_rui_ro: str,
    ghi_chu: str = ''
):
    """Thêm 1 bản ghi vào lịch sử."""
    df = load_history()
    new_id = int(df['ID'].max()) + 1 if len(df) > 0 and df['ID'].notna().any() else 1
    new_row = {
        'ID': new_id,
        'ThoiGian': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'LoaiDuDoan': loai,
        'EmployeeNumber': emp_number,
        'TenNhanVien': ten_nv,
        'XacSuat': round(float(xac_suat), 4),
        'KetQua': ket_qua,
        'MucRuiRo': muc_rui_ro,
        'GhiChu': ghi_chu,
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_history(df)
    return new_id


def add_history_batch(records: list):
    """
    Thêm nhiều bản ghi cùng lúc.
    records: list of dict với keys: EmployeeNumber, TenNhanVien, XacSuat, KetQua, MucRuiRo
    """
    df = load_history()
    max_id = int(df['ID'].max()) + 1 if len(df) > 0 and df['ID'].notna().any() else 1
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    new_rows = []
    for i, rec in enumerate(records):
        new_rows.append({
            'ID': max_id + i,
            'ThoiGian': now,
            'LoaiDuDoan': rec.get('LoaiDuDoan', 'Hàng loạt'),
            'EmployeeNumber': rec.get('EmployeeNumber', ''),
            'TenNhanVien': rec.get('TenNhanVien', ''),
            'XacSuat': round(float(rec.get('XacSuat', 0)), 4),
            'KetQua': rec.get('KetQua', ''),
            'MucRuiRo': rec.get('MucRuiRo', ''),
            'GhiChu': rec.get('GhiChu', ''),
        })
    df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
    save_history(df)
    return len(new_rows)


def delete_history_records(ids: list):
    """Xóa nhiều bản ghi theo ID."""
    df = load_history()
    df = df[~df['ID'].isin(ids)]
    save_history(df)
    return True


def filter_history(date_from=None, date_to=None, emp_number=None, loai=None):
    """Lọc lịch sử theo điều kiện."""
    df = load_history()
    if df.empty:
        return df
    df['ThoiGian'] = pd.to_datetime(df['ThoiGian'], errors='coerce')
    if date_from:
        df = df[df['ThoiGian'] >= pd.to_datetime(date_from)]
    if date_to:
        df = df[df['ThoiGian'] <= pd.to_datetime(str(date_to) + ' 23:59:59')]
    if emp_number:
        df = df[df['EmployeeNumber'].astype(str).str.contains(str(emp_number), na=False)]
    if loai and loai != 'Tất cả':
        df = df[df['LoaiDuDoan'] == loai]
    df['ThoiGian'] = df['ThoiGian'].dt.strftime('%Y-%m-%d %H:%M:%S')
    return df.sort_values('ThoiGian', ascending=False).reset_index(drop=True)
