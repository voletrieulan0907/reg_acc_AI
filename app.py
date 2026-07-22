#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clone AI - Professional MMO-style tool interface (PyQt5)

Modular Architecture:
- Imports temp mail helper from `readmail.py` (create_email, wait_for_otp)
- Imports Meitu API workflow from `main.py` (register_meitu_step_request_captcha, solve_tencent_captcha, etc.)
- GUI and Thread Pool execution in `app.py`
"""

import sys
import os
import time
import json
import string
import random
from concurrent.futures import ThreadPoolExecutor

import ctypes
from ctypes import wintypes

from PyQt5.QtCore import Qt, QPoint, QSize, QThread, pyqtSignal
from PyQt5.QtGui import QColor, QIcon, QFont, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QWidget, QMainWindow, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QCheckBox, QRadioButton, QButtonGroup, QSpinBox, QLineEdit, QMenu,
    QAction, QFileDialog, QMessageBox, QFrame, QGridLayout, QAbstractItemView,
    QSizePolicy, QGraphicsDropShadowEffect, QScrollArea
)

# --- Import các hàm xử lý từ 2 file main.py và readmail.py ---
from readmail import create_email, wait_for_otp
from main import (
    register_meitu_step_request_captcha,
    solve_tencent_captcha,
    register_meitu_step_send_otp,
    register_meitu_step_create_account
)


# ----------------------------------------------------------------------
# Style sheet — smooth, premium dark theme
# ----------------------------------------------------------------------
STYLE_SHEET = """
* {
    outline: none;
}

QWidget {
    background-color: #14151c;
    color: #c9cddb;
    font-family: 'Segoe UI', 'Inter', 'Helvetica Neue', 'Arial';
    font-size: 13px;
}

QLabel, QCheckBox, QRadioButton, QWidget#CheckCell, QFrame#Transparent {
    background: transparent;
}

#TitleBar {
    background-color: #0e0f15;
    border-top-left-radius: 14px;
    border-top-right-radius: 14px;
    border-bottom: 1px solid #1e2029;
}

#TitleLabel {
    color: #eef0f7;
    font-weight: 600;
    font-size: 13px;
    letter-spacing: 0.6px;
}

#TitleBadge {
    color: #8f9bff;
    font-weight: 700;
    font-size: 13px;
    letter-spacing: 0.5px;
}

#VersionLabel {
    color: #454a5e;
    font-size: 11px;
}

#MainFrame {
    background-color: #14151c;
    border: 1px solid #1f212c;
    border-radius: 14px;
}

QFrame#SidePanel {
    background-color: #101118;
    border-right: 1px solid #1e2029;
}

#SettingsTitle {
    color: #f2f3f9;
    font-size: 16px;
    font-weight: 700;
    letter-spacing: 0.3px;
}

#SettingsSubtitle {
    color: #4d5266;
    font-size: 11px;
}

QLabel.section {
    color: #6b74ff;
    font-weight: 600;
    font-size: 11px;
    letter-spacing: 0.4px;
    padding-top: 10px;
}

QFrame#Card {
    background-color: #171923;
    border: 1px solid #21232f;
    border-radius: 12px;
}

QFrame#Divider {
    background-color: #1e2029;
    max-height: 1px;
    min-height: 1px;
    border: none;
}

QLineEdit, QSpinBox {
    background-color: #1a1c26;
    border: 1px solid #262939;
    border-radius: 9px;
    padding: 8px 12px;
    color: #eef0f7;
    selection-background-color: #5b6dff;
}
QLineEdit:hover, QSpinBox:hover {
    border: 1px solid #333752;
}
QLineEdit:focus, QSpinBox:focus {
    border: 1px solid #5b6dff;
    background-color: #1c1f2b;
}

QRadioButton {
    color: #c9cddb;
    font-size: 12px;
    spacing: 6px;
}

QPushButton#StartBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #5b6dff, stop:1 #7752ff);
    color: white;
    font-weight: 700;
    border-radius: 10px;
    border: none;
    font-size: 13.5px;
}
QPushButton#StartBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6b7dff, stop:1 #8762ff);
}

QPushButton#StopBtn {
    background-color: #211c27;
    color: #ff5f57;
    font-weight: 600;
    border-radius: 10px;
    border: 1px solid #3a222e;
    font-size: 13px;
}
QPushButton#StopBtn:hover {
    background-color: #2c2030;
    border: 1px solid #4a2839;
}

QPushButton#GhostBtn {
    background-color: #171923;
    color: #aeb4c6;
    border: 1px solid #232637;
    border-radius: 9px;
    font-size: 12px;
    font-weight: 500;
}
QPushButton#GhostBtn:hover {
    background-color: #1e2130;
    color: #eef0f7;
    border: 1px solid #31364d;
}

QTableWidget {
    background-color: #101118;
    border: 1px solid #1e2029;
    border-radius: 12px;
    gridline-color: transparent;
    alternate-background-color: #151722;
}
QTableWidget::item {
    padding: 6px;
    border-bottom: 1px solid #181924;
    color: #c9cddb;
}
QTableWidget::item:alternate {
    background-color: #151722;
    color: #c9cddb;
}
QTableWidget::item:selected {
    background-color: #21263e;
    color: #ffffff;
}

QHeaderView::section {
    background-color: #14151f;
    color: #636b85;
    padding: 10px;
    border: none;
    font-weight: 700;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    border-bottom: 1px solid #1e2029;
}

QMenu {
    background-color: #191b26;
    border: 1px solid #262939;
    padding: 6px;
    border-radius: 10px;
}
QMenu::item {
    padding: 8px 26px 8px 14px;
    border-radius: 7px;
    color: #dfe1ec;
}
QMenu::item:selected {
    background-color: #5b6dff;
    color: white;
}

#StatusBar {
    background-color: #0e0f15;
    border-top: 1px solid #1e2029;
    border-bottom-left-radius: 14px;
    border-bottom-right-radius: 14px;
}

#StatusText { color: #7c8296; font-size: 11.5px; }
#StatusDot { font-size: 11.5px; font-weight: 700; }
#CounterPill {
    background-color: #171923;
    border: 1px solid #21232f;
    border-radius: 9px;
    padding: 4px 12px;
    font-size: 11.5px;
    font-weight: 700;
}
"""


def resource_path(relative_path):
    """Lấy đường dẫn tài nguyên (tương thích khi chạy file .py gốc và khi nén file .exe PyInstaller)"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def generate_random_password(length=12):
    """Sinh mật khẩu ngẫu nhiên có chữ hoa, chữ thường, chữ số và ký hiệu"""
    chars = string.ascii_letters + string.digits + "@#$!%*?"
    password = [
        random.choice(string.ascii_uppercase),
        random.choice(string.ascii_lowercase),
        random.choice(string.digits),
        random.choice("@#$!%*?"),
    ]
    password += [random.choice(chars) for _ in range(length - 4)]
    random.shuffle(password)
    return "".join(password)


# ----------------------------------------------------------------------
# Multithreaded Registration Worker Thread
# ----------------------------------------------------------------------
class RegWorkerThread(QThread):
    sig_update_row = pyqtSignal(int, str, str, str)  # row_idx, email, password, status
    sig_finished = pyqtSignal()

    def __init__(self, tasks, captcha_key, num_threads):
        super().__init__()
        self.tasks = tasks  # list of tuples: (row_idx, password)
        self.captcha_key = captcha_key
        self.num_threads = num_threads
        self.is_running = True

    def run(self):
        with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            futures = [executor.submit(self.process_account, row_idx, pwd) for row_idx, pwd in self.tasks]
            for future in futures:
                if not self.is_running:
                    break
                try:
                    future.result()
                except Exception:
                    pass
        self.sig_finished.emit()

    def stop(self):
        self.is_running = False

    def process_account(self, row_idx, password):
        if not self.is_running:
            return

        # 1. Gọi hàm tạo Email từ readmail.py
        self.sig_update_row.emit(row_idx, "---", password, "Đang tạo email...")
        try:
            mail_info = create_email(captcha_key=self.captcha_key)
            email = mail_info.get('address')
            timestamp = mail_info.get('timestamp')
            key = mail_info.get('key')

            if not email or not key:
                self.sig_update_row.emit(row_idx, "---", password, "Lỗi: Không tạo được mail")
                return
        except Exception as e:
            self.sig_update_row.emit(row_idx, "---", password, f"Lỗi tạo mail: {str(e)[:25]}")
            return

        # Cập nhật Email thực vừa tạo vào dòng TreeView
        self.sig_update_row.emit(row_idx, email, password, "Đang xin Captcha Meitu...")

        # 2. Bước 1: Yêu cầu mã Captcha Meitu (main.py)
        try:
            session, base_params, app_id, register_token = register_meitu_step_request_captcha(email, password)
        except Exception as e:
            self.sig_update_row.emit(row_idx, email, password, f"Lỗi xin Captcha: {str(e)[:25]}")
            return

        # 3. Bước 2: Giải Captcha Tencent qua 2Captcha (main.py)
        self.sig_update_row.emit(row_idx, email, password, "Đang giải Captcha Meitu...")
        try:
            ticket, randstr = solve_tencent_captcha(app_id, self.captcha_key)
        except Exception as e:
            self.sig_update_row.emit(row_idx, email, password, f"Lỗi giải Captcha: {str(e)[:25]}")
            return

        # 4. Bước 3: Kích hoạt gửi OTP (main.py)
        self.sig_update_row.emit(row_idx, email, password, "Đang kích gửi OTP...")
        try:
            resp3 = register_meitu_step_send_otp(session, base_params, email, ticket, randstr)
            if resp3.get('meta', {}).get('code') != 0:
                self.sig_update_row.emit(row_idx, email, password, f"Lỗi kích OTP ({resp3.get('meta',{}).get('code')})")
                return
        except Exception as e:
            self.sig_update_row.emit(row_idx, email, password, f"Lỗi gửi OTP: {str(e)[:25]}")
            return

        # 5. Bước 4: Chờ nhận OTP từ Smailpro (readmail.py)
        self.sig_update_row.emit(row_idx, email, password, "Đang chờ mã OTP từ mail...")
        otp_code = wait_for_otp(email, timestamp, key, timeout=60)
        
        if not otp_code:
            self.sig_update_row.emit(row_idx, email, password, "Lỗi: Không nhận được OTP")
            return

        # 6. Bước 5: Đăng ký tài khoản (main.py)
        self.sig_update_row.emit(row_idx, email, password, f"Có OTP ({otp_code}) — Đang reg...")
        try:
            resp_create = register_meitu_step_create_account(session, base_params, email, password, otp_code, register_token)
            code = resp_create.get('meta', {}).get('code')
            
            if code == 0:
                uid = resp_create.get('response', {}).get('uid', 'OK')
                self.sig_update_row.emit(row_idx, email, password, f"Thành công (UID: {uid})")
            else:
                msg = resp_create.get('meta', {}).get('msg', f'Code {code}')
                self.sig_update_row.emit(row_idx, email, password, f"Thất bại: {msg}")
        except Exception as e:
            self.sig_update_row.emit(row_idx, email, password, f"Lỗi Reg: {str(e)[:25]}")


# ----------------------------------------------------------------------
# macOS-style Traffic Control Buttons
# ----------------------------------------------------------------------
class TrafficButton(QPushButton):
    def __init__(self, color, hover_color, parent=None):
        super().__init__(parent)
        self.setFixedSize(13, 13)
        self.setCursor(Qt.PointingHandCursor)
        self._color = color
        self._hover = hover_color
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border-radius: 6px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {color};
            }}
        """)


# ----------------------------------------------------------------------
# Custom Title Bar
# ----------------------------------------------------------------------
class TitleBar(QWidget):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.setObjectName("TitleBar")
        self.setFixedHeight(44)
        self._drag_pos = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(9)

        self.btn_close = TrafficButton("#ff5f57", "#ff8078")
        self.btn_min = TrafficButton("#ffbd2e", "#ffcf60")
        self.btn_max = TrafficButton("#28c840", "#5bd671")

        self.btn_close.clicked.connect(self.parent_window.close)
        self.btn_min.clicked.connect(self.parent_window.showMinimized)
        self.btn_max.clicked.connect(self.toggle_max_restore)

        layout.addWidget(self.btn_close)
        layout.addWidget(self.btn_min)
        layout.addWidget(self.btn_max)
        layout.addSpacing(16)

        icon_path = resource_path(os.path.join("image", "ai.png"))
        if os.path.exists(icon_path):
            icon_lbl = QLabel()
            pix = QPixmap(icon_path).scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_lbl.setPixmap(pix)
            layout.addWidget(icon_lbl)
        else:
            badge = QLabel("◆")
            badge.setObjectName("TitleBadge")
            layout.addWidget(badge)

        title = QLabel("Clone AI")
        title.setObjectName("TitleLabel")
        layout.addWidget(title)

        subtitle = QLabel("Mass Register Tool (RoboNeo / Meitu)")
        subtitle.setStyleSheet("color:#454a5e; font-size:12px; padding-left:4px;")
        layout.addWidget(subtitle)

        layout.addStretch()

        ver = QLabel("v1.3.0")
        ver.setObjectName("VersionLabel")
        layout.addWidget(ver)

    def toggle_max_restore(self):
        if self.parent_window.isMaximized():
            self.parent_window.showNormal()
        else:
            self.parent_window.showMaximized()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.parent_window.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._drag_pos is not None:
            self.parent_window.move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseDoubleClickEvent(self, event):
        self.toggle_max_restore()


# ----------------------------------------------------------------------
# Settings Side Panel
# ----------------------------------------------------------------------
class SettingsPanel(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("SidePanel")
        self.setFixedWidth(280)

        frame_layout = QVBoxLayout(self)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setObjectName("SettingsScroll")
        scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollArea > QWidget > QWidget { background: transparent; }
            QScrollBar:vertical {
                background: #14151c; width: 6px; border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: #2e3048; border-radius: 3px; min-height: 30px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """)

        scroll_content = QWidget()
        scroll_content.setObjectName("SidePanelInner")
        outer = QVBoxLayout(scroll_content)
        outer.setContentsMargins(20, 22, 20, 20)
        outer.setSpacing(0)

        title = QLabel("Cấu hình Tiến trình")
        title.setObjectName("SettingsTitle")
        outer.addWidget(title)
        subtitle = QLabel("Thiết lập luồng đăng ký & Captcha")
        subtitle.setObjectName("SettingsSubtitle")
        outer.addWidget(subtitle)
        outer.addSpacing(16)

        # ---- Card: Thread & Reg Quantity ----
        card1 = QFrame()
        card1.setObjectName("Card")
        c1 = QVBoxLayout(card1)
        c1.setContentsMargins(14, 14, 14, 14)
        c1.setSpacing(6)

        c1.addWidget(self._section_label("SỐ LUỒNG CHẠY (THREADS)"))
        self.spin_thread = QSpinBox()
        self.spin_thread.setRange(1, 50)
        self.spin_thread.setValue(3)
        self.spin_thread.setFixedHeight(36)
        c1.addWidget(self.spin_thread)

        c1.addSpacing(8)
        c1.addWidget(self._section_label("SỐ LƯỢNG TÀI KHOẢN CẦN REG"))
        self.spin_reg_qty = QSpinBox()
        self.spin_reg_qty.setRange(1, 10000)
        self.spin_reg_qty.setValue(5)
        self.spin_reg_qty.setFixedHeight(36)
        c1.addWidget(self.spin_reg_qty)

        outer.addWidget(card1)
        outer.addSpacing(10)

        # ---- Card: Password settings (Random vs Fixed) ----
        card_pass = QFrame()
        card_pass.setObjectName("Card")
        cp = QVBoxLayout(card_pass)
        cp.setContentsMargins(14, 14, 14, 14)
        cp.setSpacing(8)

        cp.addWidget(self._section_label("TÙY CHỌN MẬT KHẨU"))
        
        self.radio_pass_random = QRadioButton("Mật khẩu ngẫu nhiên (chữ, số, ký hiệu)")
        self.radio_pass_fixed = QRadioButton("Mật khẩu cố định:")
        self.radio_pass_random.setChecked(True)

        self.pass_group = QButtonGroup(self)
        self.pass_group.addButton(self.radio_pass_random, 1)
        self.pass_group.addButton(self.radio_pass_fixed, 2)

        cp.addWidget(self.radio_pass_random)
        cp.addWidget(self.radio_pass_fixed)

        self.input_fixed_password = QLineEdit()
        self.input_fixed_password.setText("Shinasd980970@")
        self.input_fixed_password.setPlaceholderText("Nhập mật khẩu dùng chung...")
        self.input_fixed_password.setFixedHeight(34)
        self.input_fixed_password.setEnabled(False)
        cp.addWidget(self.input_fixed_password)

        self.radio_pass_fixed.toggled.connect(
            lambda checked: self.input_fixed_password.setEnabled(checked)
        )

        outer.addWidget(card_pass)
        outer.addSpacing(10)

        # ---- Card: 2Captcha API Key ----
        card2 = QFrame()
        card2.setObjectName("Card")
        c2 = QVBoxLayout(card2)
        c2.setContentsMargins(14, 14, 14, 14)
        c2.setSpacing(6)

        c2.addWidget(self._section_label("2CAPTCHA API KEY"))
        self.input_captcha_key = QLineEdit()
        self.input_captcha_key.setText("35aa7bbf75db184cb0219c9d497d74ac")
        self.input_captcha_key.setPlaceholderText("Nhập API Key 2Captcha...")
        self.input_captcha_key.setEchoMode(QLineEdit.Password)
        self.input_captcha_key.setFixedHeight(36)
        c2.addWidget(self.input_captcha_key)

        self.chk_show_key = QCheckBox("Hiện API Key")
        self.chk_show_key.stateChanged.connect(self._toggle_key_visibility)
        c2.addWidget(self.chk_show_key)

        outer.addWidget(card2)
        outer.addSpacing(14)

        divider = QFrame()
        divider.setObjectName("Divider")
        outer.addWidget(divider)
        outer.addSpacing(14)

        # ---- Action buttons ----
        self.btn_start = QPushButton("▶   Bắt đầu")
        self.btn_start.setObjectName("StartBtn")
        self.btn_start.setFixedHeight(42)
        self.btn_stop = QPushButton("■   Dừng lại")
        self.btn_stop.setObjectName("StopBtn")
        self.btn_stop.setFixedHeight(42)
        self.btn_stop.setEnabled(False)

        outer.addWidget(self.btn_start)
        outer.addSpacing(6)
        outer.addWidget(self.btn_stop)

        outer.addSpacing(12)
        self.btn_add_account = QPushButton("＋   Thêm dòng mới")
        self.btn_add_account.setObjectName("GhostBtn")
        self.btn_export = QPushButton("⭱   Xuất danh sách TXT")
        self.btn_export.setObjectName("GhostBtn")
        for b in (self.btn_add_account, self.btn_export):
            b.setFixedHeight(36)
            outer.addWidget(b)
            outer.addSpacing(6)

        outer.addStretch()

        note = QLabel("Clone AI Engine  ·  © 2026")
        note.setStyleSheet("color:#33374a; font-size:10.5px;")
        note.setAlignment(Qt.AlignCenter)
        outer.addWidget(note)

        scroll.setWidget(scroll_content)
        frame_layout.addWidget(scroll)

    @staticmethod
    def _section_label(text):
        lbl = QLabel(text)
        lbl.setProperty("class", "section")
        lbl.setStyleSheet("color:#6b74ff; font-weight:600; font-size:10.5px; "
                           "letter-spacing:0.5px; padding-top:0px;")
        return lbl

    def _toggle_key_visibility(self, state):
        self.input_captcha_key.setEchoMode(
            QLineEdit.Normal if state == Qt.Checked else QLineEdit.Password
        )


# ----------------------------------------------------------------------
# Account Table
# ----------------------------------------------------------------------
class AccountTable(QTableWidget):
    COL_CHECK, COL_STT, COL_EMAIL, COL_PASS, COL_STATUS = range(5)

    def __init__(self):
        super().__init__()
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(["", "STT", "Email", "Password", "Trạng thái"])
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.verticalHeader().setVisible(False)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        header = self.horizontalHeader()
        header.setSectionResizeMode(self.COL_CHECK, QHeaderView.Fixed)
        header.setSectionResizeMode(self.COL_STT, QHeaderView.Fixed)
        header.setSectionResizeMode(self.COL_EMAIL, QHeaderView.Stretch)
        header.setSectionResizeMode(self.COL_PASS, QHeaderView.Stretch)
        header.setSectionResizeMode(self.COL_STATUS, QHeaderView.ResizeToContents)
        self.setColumnWidth(self.COL_CHECK, 40)
        self.setColumnWidth(self.COL_STT, 56)
        self.verticalHeader().setDefaultSectionSize(40)
        self.setShowGrid(False)
        self.setFrameShape(QFrame.NoFrame)
        self.setRowCount(0)

    def add_account(self, email="---", password="---", status="Chờ xử lý"):
        row = self.rowCount()
        self.insertRow(row)

        chk_widget = QWidget()
        chk_widget.setObjectName("CheckCell")
        chk_widget.setAutoFillBackground(False)
        chk_layout = QHBoxLayout(chk_widget)
        chk_layout.setContentsMargins(0, 0, 0, 0)
        chk_layout.setAlignment(Qt.AlignCenter)
        checkbox = QCheckBox()
        chk_layout.addWidget(checkbox)
        self.setCellWidget(row, self.COL_CHECK, chk_widget)

        self.setItem(row, self.COL_STT, self._center_item(str(row + 1)))
        self.setItem(row, self.COL_EMAIL, QTableWidgetItem(email))
        self.setItem(row, self.COL_PASS, QTableWidgetItem(password))
        self.setItem(row, self.COL_STATUS, self._status_item(status))

    def update_row_info(self, row, email, password, status):
        if row < 0 or row >= self.rowCount():
            return
        if email:
            self.setItem(row, self.COL_EMAIL, QTableWidgetItem(email))
        if password:
            self.setItem(row, self.COL_PASS, QTableWidgetItem(password))
        if status:
            self.setItem(row, self.COL_STATUS, self._status_item(status))

    @staticmethod
    def _center_item(text):
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignCenter)
        return item

    @staticmethod
    def _status_item(status):
        item = QTableWidgetItem(status)
        item.setTextAlignment(Qt.AlignCenter)
        
        if "Thành công" in status:
            color = QColor("#28c840")  # Xanh lá cây
        elif "Thất bại" in status or "Lỗi" in status:
            color = QColor("#ff5f57")  # Đỏ
        elif "Đang" in status:
            color = QColor("#ffbd2e")  # Vàng
        else:
            color = QColor("#8b93a7")  # Xám
            
        item.setForeground(color)
        return item

    def row_checkbox(self, row):
        widget = self.cellWidget(row, self.COL_CHECK)
        return widget.findChild(QCheckBox) if widget else None

    def checked_accounts(self):
        result = []
        for r in range(self.rowCount()):
            cb = self.row_checkbox(r)
            if cb and cb.isChecked():
                result.append((
                    self.item(r, self.COL_EMAIL).text(),
                    self.item(r, self.COL_PASS).text(),
                    self.item(r, self.COL_STATUS).text()
                ))
        return result

    def show_context_menu(self, pos):
        menu = QMenu(self)
        act_select_all = menu.addAction("Chọn tất cả")
        act_deselect_all = menu.addAction("Bỏ chọn tất cả")
        menu.addSeparator()
        act_export_success = menu.addAction("⭱  Xuất tài khoản THÀNH CÔNG (.txt)")
        act_export_checked = menu.addAction("⭱  Xuất dòng đã chọn (.txt)")
        act_export_all = menu.addAction("⭱  Xuất toàn bộ danh sách (.txt)")

        act_select_all.triggered.connect(self.select_all)
        act_deselect_all.triggered.connect(self.deselect_all)
        act_export_success.triggered.connect(lambda: self.export_txt(only_checked=False, only_success=True))
        act_export_checked.triggered.connect(lambda: self.export_txt(only_checked=True, only_success=False))
        act_export_all.triggered.connect(lambda: self.export_txt(only_checked=False, only_success=False))

        menu.exec_(self.viewport().mapToGlobal(pos))

    def select_all(self):
        for r in range(self.rowCount()):
            cb = self.row_checkbox(r)
            if cb:
                cb.setChecked(True)

    def deselect_all(self):
        for r in range(self.rowCount()):
            cb = self.row_checkbox(r)
            if cb:
                cb.setChecked(False)

    def export_txt(self, only_checked=False, only_success=True):
        rows_source = []
        for r in range(self.rowCount()):
            cb = self.row_checkbox(r)
            email_item = self.item(r, self.COL_EMAIL)
            pass_item = self.item(r, self.COL_PASS)
            status_item = self.item(r, self.COL_STATUS)

            if not email_item or not pass_item or not status_item:
                continue

            email = email_item.text().strip()
            password = pass_item.text().strip()
            status = status_item.text().strip()

            if only_checked and (not cb or not cb.isChecked()):
                continue

            if only_success and "Thành công" not in status:
                continue

            if email == "---" or not email:
                continue

            rows_source.append((email, password, status))

        if not rows_source:
            msg = "Không có tài khoản đã chọn nào để xuất." if only_checked else "Chưa có tài khoản nào đăng ký THÀNH CÔNG để xuất."
            QMessageBox.warning(self, "Clone AI", msg)
            return

        default_file = "success_accounts.txt" if only_success else "accounts.txt"
        path, _ = QFileDialog.getSaveFileName(self, "Xuất file TXT", default_file, "Text Files (*.txt)")
        if not path:
            return

        with open(path, "w", encoding="utf-8") as f:
            for email, password, status in rows_source:
                f.write(f"{email}|{password}\n")

        QMessageBox.information(self, "Clone AI", f"Đã xuất thành công {len(rows_source)} tài khoản ra:\n{path}")


# ----------------------------------------------------------------------
# Content Area
# ----------------------------------------------------------------------
class ContentArea(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍   Tìm kiếm email...")
        self.search_box.setFixedWidth(260)
        self.search_box.setFixedHeight(36)
        toolbar.addWidget(self.search_box)
        toolbar.addStretch()

        self.lbl_total = self._pill("Tổng: 0", "#8f9bff")
        self.lbl_success = self._pill("Thành công: 0", "#3ddc84")
        self.lbl_fail = self._pill("Thất bại: 0", "#ff6b6b")
        toolbar.addWidget(self.lbl_total)
        toolbar.addWidget(self.lbl_success)
        toolbar.addWidget(self.lbl_fail)

        layout.addLayout(toolbar)

        self.table = AccountTable()
        layout.addWidget(self.table)

        self.table.itemChanged.connect(lambda *_: self.update_counters())
        self.update_counters()

    @staticmethod
    def _pill(text, color):
        lbl = QLabel(text)
        lbl.setObjectName("CounterPill")
        lbl.setStyleSheet(f"""
            #CounterPill {{
                background-color: #171923;
                border: 1px solid #21232f;
                border-radius: 9px;
                padding: 6px 14px;
                font-size: 11.5px;
                font-weight: 700;
                color: {color};
            }}
        """)
        return lbl

    def update_counters(self):
        total = self.table.rowCount()
        success = 0
        fail = 0
        for r in range(total):
            item = self.table.item(r, self.table.COL_STATUS)
            if item is None:
                continue
            txt = item.text()
            if "Thành công" in txt:
                success += 1
            elif "Thất bại" in txt or "Lỗi" in txt:
                fail += 1
        self.lbl_total.setText(f"Tổng: {total}")
        self.lbl_success.setText(f"Thành công: {success}")
        self.lbl_fail.setText(f"Thất bại: {fail}")


# ----------------------------------------------------------------------
# Status Bar
# ----------------------------------------------------------------------
class StatusBar(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("StatusBar")
        self.setFixedHeight(34)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(8)

        self.status_dot = QLabel("●")
        self.status_dot.setObjectName("StatusDot")
        self.status_dot.setStyleSheet("color:#3ddc84; font-size:10px;")
        layout.addWidget(self.status_dot)

        self.status_text = QLabel("Sẵn sàng")
        self.status_text.setObjectName("StatusText")
        self.status_text.setStyleSheet("color:#dfe1ec; font-size:11.5px; font-weight:600;")
        layout.addWidget(self.status_text)
        layout.addStretch()

        info = QLabel("Clone AI Engine  ·  Meitu RoboNeo Core v1.3.0")
        info.setObjectName("StatusText")
        layout.addWidget(info)


# ----------------------------------------------------------------------
# Main Frameless Window
# ----------------------------------------------------------------------
class CloneAIWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.resize(1180, 720)
        self.setMinimumSize(900, 560)
        self.setWindowTitle("Clone AI")

        icon_path = resource_path(os.path.join("image", "ai.png"))
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        main_frame = QFrame()
        main_frame.setObjectName("MainFrame")
        outer.addWidget(main_frame)

        frame_layout = QVBoxLayout(main_frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.setSpacing(0)

        self.title_bar = TitleBar(self)
        frame_layout.addWidget(self.title_bar)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        self.settings_panel = SettingsPanel()
        self.content_area = ContentArea()

        body.addWidget(self.settings_panel)
        body.addWidget(self.content_area, 1)

        frame_layout.addLayout(body, 1)

        self.status_bar = StatusBar()
        frame_layout.addWidget(self.status_bar)

        # Wire up buttons
        self.settings_panel.btn_add_account.clicked.connect(self.add_blank_account)
        self.settings_panel.btn_export.clicked.connect(
            lambda: self.content_area.table.export_txt(only_checked=False, only_success=True))
        self.settings_panel.btn_start.clicked.connect(self.start_process)
        self.settings_panel.btn_stop.clicked.connect(self.stop_process)

        # Drop shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(48)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(0, 6)
        main_frame.setGraphicsEffect(shadow)

        self.worker = None

    def nativeEvent(self, eventType, message):
        retval, result = super().nativeEvent(eventType, message)
        if eventType in (b"windows_generic_MSG", "windows_generic_MSG"):
            msg = wintypes.MSG.from_address(int(message))
            if msg.message == 0x0084:  # WM_NCHITTEST
                x = msg.pt.x
                y = msg.pt.y
                rect = self.frameGeometry()
                margin = 8  # Vùng 8px xung quanh viền để nhận di chuột kéo dãn

                left = x >= rect.left() and x < rect.left() + margin
                right = x <= rect.right() and x > rect.right() - margin
                top = y >= rect.top() and y < rect.top() + margin
                bottom = y <= rect.bottom() and y > rect.bottom() - margin

                if top and left: return True, 13      # HTTOPLEFT
                if top and right: return True, 14     # HTTOPRIGHT
                if bottom and left: return True, 16   # HTBOTTOMLEFT
                if bottom and right: return True, 17  # HTBOTTOMRIGHT
                if left: return True, 10              # HTLEFT
                if right: return True, 11             # HTRIGHT
                if top: return True, 12               # HTTOP
                if bottom: return True, 15            # HTBOTTOM
        return retval, result

    def add_blank_account(self):
        self.content_area.table.add_account("---", "---", "Chờ xử lý")
        self.content_area.update_counters()

    def start_process(self):
        threads = self.settings_panel.spin_thread.value()
        qty = self.settings_panel.spin_reg_qty.value()
        captcha_key = self.settings_panel.input_captcha_key.text().strip()

        if not captcha_key:
            QMessageBox.warning(self, "Clone AI", "Vui lòng nhập API Key 2Captcha!")
            return

        is_random_pass = self.settings_panel.radio_pass_random.isChecked()
        fixed_pass = self.settings_panel.input_fixed_password.text().strip()

        if not is_random_pass and not fixed_pass:
            QMessageBox.warning(self, "Clone AI", "Vui lòng nhập mật khẩu cố định!")
            return

        # 1. Reset bảng và nạp trước danh sách số lượng tài khoản cần reg vào TreeView
        self.content_area.table.setRowCount(0)
        tasks = []

        for i in range(qty):
            pwd = generate_random_password() if is_random_pass else fixed_pass
            self.content_area.table.add_account(email="---", password=pwd, status="Chờ xử lý")
            tasks.append((i, pwd))

        self.content_area.update_counters()

        # 2. Khởi chạy luồng xử lý đa tiến trình
        self.worker = RegWorkerThread(tasks, captcha_key, threads)
        self.worker.sig_update_row.connect(self.on_update_row)
        self.worker.sig_finished.connect(self.on_process_finished)
        self.worker.start()

        self.settings_panel.btn_start.setEnabled(False)
        self.settings_panel.btn_stop.setEnabled(True)

        self.status_bar.status_text.setText(f"Đang chạy — {threads} luồng — Mục tiêu {qty} tài khoản")
        self.status_bar.status_dot.setStyleSheet("color:#ffbd2e; font-size:10px;")

    def on_update_row(self, row, email, password, status):
        self.content_area.table.update_row_info(row, email, password, status)
        self.content_area.update_counters()

    def stop_process(self):
        if self.worker:
            self.worker.stop()
        self.on_process_finished()
        self.status_bar.status_text.setText("Đã dừng tiến trình")
        self.status_bar.status_dot.setStyleSheet("color:#ff5f57; font-size:10px;")

    def on_process_finished(self):
        self.settings_panel.btn_start.setEnabled(True)
        self.settings_panel.btn_stop.setEnabled(False)
        self.status_bar.status_text.setText("Hoàn tất tiến trình")
        self.status_bar.status_dot.setStyleSheet("color:#3ddc84; font-size:10px;")


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE_SHEET)
    app.setFont(QFont("Segoe UI", 10))

    window = CloneAIWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()