"""主窗口"""
import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QMessageBox,
    QLineEdit, QSizePolicy, QTextEdit, QStackedWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

from core.env_checker import check_environment
from core.installer import install_software, install_claude_code, install_ccswitch, install_vscode
from core.activation import is_activated, save_activation, get_machine_code


class InstallWorker(QThread):
    """后台安装线程"""
    log_signal = pyqtSignal(str)
    finish_signal = pyqtSignal(bool, str)

    def __init__(self, func):
        super().__init__()
        self.func = func

    def run(self):
        try:
            ok, msg = self.func(self.log_signal.emit)
            self.finish_signal.emit(ok, msg)
        except Exception as e:
            self.finish_signal.emit(False, str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Claude Code 一键安装工具')
        self.resize(800, 600)
        self.current_step = 0
        self.env_results = []
        self.worker = None

        self._apply_dark_theme()

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 堆叠两个页面：激活页 / 功能页
        self.stacked = QStackedWidget()
        self.activation_page = self._create_activation_page()
        self.main_page = self._create_main_page()
        self.stacked.addWidget(self.activation_page)
        self.stacked.addWidget(self.main_page)
        main_layout.addWidget(self.stacked)

        # 判断显示哪个页面
        QTimer.singleShot(100, self._check_activation)

    # ============================================================
    #  激活页面
    # ============================================================

    def _create_activation_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(16)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 标题
        layout.addStretch()

        title = QLabel('🔐 软件激活')
        title.setFont(QFont('Microsoft YaHei UI', 22, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            'color: qlineargradient(x1:0, y1:0, x2:1, y2:0, '
            'stop:0 #f59e0b, stop:1 #ef4444);'
        )
        layout.addWidget(title)

        desc = QLabel('请输入激活码以继续使用')
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet('color: #9ca3af; font-size: 13px;')
        layout.addWidget(desc)

        # 机器码显示
        layout.addSpacing(8)
        machine_label = QLabel('你的机器码（复制发送给管理员获取激活码）')
        machine_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        machine_label.setStyleSheet('color: #6b7280; font-size: 11px;')
        layout.addWidget(machine_label)

        machine_frame = QFrame()
        machine_frame.setFixedWidth(400)
        machine_frame.setStyleSheet(
            'QFrame { background: #1e293b; border: 1px solid #374151; border-radius: 8px; }'
        )
        machine_layout = QHBoxLayout(machine_frame)
        machine_layout.setContentsMargins(16, 10, 8, 10)
        mc = get_machine_code()
        self.machine_code_label = QLabel(mc)
        self.machine_code_label.setFont(QFont('Consolas', 14))
        self.machine_code_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.machine_code_label.setStyleSheet('color: #fbbf24; border: none;')
        self.machine_code_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        machine_layout.addWidget(self.machine_code_label, 1)

        copy_btn = QPushButton('📋 复制')
        copy_btn.setFixedHeight(32)
        copy_btn.setToolTip('复制机器码到剪贴板')
        copy_btn.setStyleSheet('''
            QPushButton {
                background: #374151; border-radius: 6px;
                padding: 4px 10px; font-size: 12px;
            }
            QPushButton:hover { background: #4b5563; }
        ''')
        copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(mc))
        machine_layout.addWidget(copy_btn)

        # 居中放置
        mc_hbox = QHBoxLayout()
        mc_hbox.addStretch()
        mc_hbox.addWidget(machine_frame)
        mc_hbox.addStretch()
        layout.addLayout(mc_hbox)

        # 激活码输入
        layout.addSpacing(8)
        code_label = QLabel('激活码')
        code_label.setStyleSheet('color: #e2e8f0; font-size: 13px;')
        code_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(code_label)

        self.activation_input = QLineEdit()
        self.activation_input.setPlaceholderText('输入激活码，如 XXXX-XXXX')
        self.activation_input.setFixedWidth(320)
        self.activation_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.activation_input.setFont(QFont('Consolas', 14))
        self.activation_input.setMaxLength(20)
        self.activation_input.returnPressed.connect(self._do_activate)
        self.activation_input.setStyleSheet('''
            QLineEdit {
                background-color: #1e293b;
                color: #e2e8f0;
                border: 1px solid #374151;
                border-radius: 8px;
                padding: 10px 16px;
                font-size: 14px;
            }
            QLineEdit:focus { border-color: #f59e0b; }
        ''')

        hbox = QHBoxLayout()
        hbox.addStretch()
        hbox.addWidget(self.activation_input)
        hbox.addStretch()
        layout.addLayout(hbox)

        # 激活按钮
        layout.addSpacing(8)
        self.activate_btn = QPushButton('✅ 激活')
        self.activate_btn.setFixedWidth(200)
        self.activate_btn.setFixedHeight(44)
        self.activate_btn.clicked.connect(self._do_activate)

        btn_hbox = QHBoxLayout()
        btn_hbox.addStretch()
        btn_hbox.addWidget(self.activate_btn)
        btn_hbox.addStretch()
        layout.addLayout(btn_hbox)

        # 状态提示
        self.activation_status = QLabel('')
        self.activation_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.activation_status.setWordWrap(True)
        layout.addWidget(self.activation_status)

        layout.addStretch()
        return page

    def _do_activate(self):
        code = self.activation_input.text().strip()
        if not code:
            self.activation_status.setStyleSheet('color: #ef4444; font-size: 12px;')
            self.activation_status.setText('请输入激活码')
            return

        ok = save_activation(code)
        if ok:
            self.activation_status.setStyleSheet('color: #4ade80; font-size: 13px;')
            self.activation_status.setText('✅ 激活成功！正在进入...')
            # 延迟进入，让用户看到成功提示
            QTimer.singleShot(800, self._enter_main)
        else:
            self.activation_status.setStyleSheet('color: #ef4444; font-size: 12px;')
            self.activation_status.setText('❌ 激活码无效，请检查后重试')
            self.activation_input.selectAll()

    def _check_activation(self):
        """检查是否已激活（暂不启用）"""
        # TODO: 需要激活时取消下面注释，恢复下行
        # if is_activated():
        #     self._enter_main()
        self._enter_main()

    def _enter_main(self):
        self.stacked.setCurrentWidget(self.main_page)
        self.activation_page.deleteLater()
        self._do_check_env()

    # ============================================================
    #  功能主页面
    # ============================================================

    def _create_main_page(self):
        page = QWidget()
        main_layout = QVBoxLayout(page)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(20, 16, 20, 16)

        # 标题
        title = QLabel('Claude Code 一键安装工具')
        title.setFont(QFont('Microsoft YaHei UI', 22, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            'color: qlineargradient(x1:0, y1:0, x2:1, y2:0, '
            'stop:0 #c084fc, stop:1 #f472b6);'
        )
        main_layout.addWidget(title)

        subtitle = QLabel('专为国内用户打造 · 无需技术背景 · 三步搞定')
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet('color: #9ca3af; font-size: 12px;')
        main_layout.addWidget(subtitle)

        # 步骤导航
        self._add_step_bar(main_layout)

        # 内容区域（固定大小，三个步骤的页面堆叠）
        self.content_frame = QFrame()
        self.content_frame.setObjectName('content_frame')
        self.content_frame.setStyleSheet('QFrame#content_frame { background: transparent; }')
        self.content_layout = QVBoxLayout(self.content_frame)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.content_frame)
        self.content_frame.setFixedHeight(200)

        # 三个步骤页面 → 改为四个
        self.step_pages = []
        for i in range(4):
            p = QWidget()
            p_layout = QVBoxLayout(p)
            p_layout.setContentsMargins(0, 0, 0, 0)
            p_layout.setSpacing(12)
            p_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            self.content_layout.addWidget(p)
            self.step_pages.append(p)
            if i > 0:
                p.hide()

        self._render_step0()
        self._render_step1()
        self._render_step2()
        self._render_step3()

        # 日志区域
        self._add_log_area(main_layout)

        # 底部导航
        self._add_bottom_nav(main_layout)

        return page

    def _apply_dark_theme(self):
        self.setStyleSheet('''
            QMainWindow { background-color: #0f172a; }
            QPushButton {
                background-color: #7c3aed;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #6d28d9; }
            QPushButton:pressed { background-color: #5b21b6; }
            QPushButton:disabled { background-color: #4b5563; color: #9ca3af; }
            QLineEdit {
                background-color: #1e293b;
                color: #e2e8f0;
                border: 1px solid #374151;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #7c3aed;
            }
        ''')

    # ---- 步骤导航 ----

    def _add_step_bar(self, parent_layout):
        bar = QWidget()
        bar.setStyleSheet('background: transparent;')
        bar_layout = QHBoxLayout(bar)
        bar_layout.setSpacing(8)
        bar_layout.setContentsMargins(0, 0, 0, 0)

        self.step_labels = []
        step_names = ['环境检查', '安装 Claude Code', '安装 ccswitch', '安装 VS Code']
        for i, name in enumerate(step_names):
            btn = QPushButton(f'{i + 1}. {name}')
            btn.setCheckable(True)
            btn.setFlat(True)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            btn.setStyleSheet('''
                QPushButton {
                    background: transparent;
                    color: #6b7280;
                    font-size: 13px;
                    padding: 8px 16px;
                    border: 1px solid #374151;
                    border-radius: 20px;
                }
                QPushButton:checked {
                    background: #7c3aed;
                    color: white;
                    border-color: #7c3aed;
                }
            ''')
            btn.clicked.connect(lambda checked, idx=i: self._go_to_step(idx))
            bar_layout.addWidget(btn)
            self.step_labels.append(btn)

        parent_layout.addWidget(bar)

    # ---- 日志区域 ----

    def _add_log_area(self, parent_layout):
        self.log_label = QLabel('📋 安装日志')
        self.log_label.setFont(QFont('Microsoft YaHei UI', 11, QFont.Weight.Bold))
        self.log_label.setStyleSheet('color: #9ca3af;')
        parent_layout.addWidget(self.log_label)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont('Consolas', 11))
        self.log_text.setMaximumHeight(100)
        self.log_text.setStyleSheet(
            'color: #4ade80; background: #00000044; '
            'border: 1px solid #1e293b; border-radius: 8px;'
        )
        parent_layout.addWidget(self.log_text)

    # ---- 底部导航 ----

    def _add_bottom_nav(self, parent_layout):
        nav = QWidget()
        nav.setStyleSheet('background: transparent;')
        nav_layout = QHBoxLayout(nav)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.addStretch()

        self.prev_btn = QPushButton('← 上一步')
        self.prev_btn.setEnabled(False)
        self.prev_btn.setStyleSheet('''
            QPushButton { background: #374151; border-radius: 8px; padding: 10px 24px; }
            QPushButton:hover { background: #4b5563; }
        ''')
        self.prev_btn.clicked.connect(lambda: self._go_to_step(self.current_step - 1))
        nav_layout.addWidget(self.prev_btn)

        self.next_btn = QPushButton('下一步 →')
        self.next_btn.setStyleSheet('''
            QPushButton { background: #7c3aed; border-radius: 8px; padding: 10px 24px; }
            QPushButton:hover { background: #6d28d9; }
        ''')
        self.next_btn.clicked.connect(lambda: self._go_to_step(self.current_step + 1))
        nav_layout.addWidget(self.next_btn)

        parent_layout.addWidget(nav)

    def _go_to_step(self, step):
        if step < 0 or step >= 4:
            return
        self.current_step = step
        for i, btn in enumerate(self.step_labels):
            btn.setChecked(i == step)
        self.prev_btn.setEnabled(step > 0)
        self.next_btn.setEnabled(step < 3)
        for i, page in enumerate(self.step_pages):
            page.setVisible(i == step)

    # ---- 步骤 0: 环境检查 ----

    def _render_step0(self):
        layout = self.step_pages[0].layout()

        # 2x2 网格布局
        grid = QWidget()
        grid_layout = QVBoxLayout(grid)
        grid_layout.setSpacing(8)
        grid_layout.setContentsMargins(0, 0, 0, 0)

        self.env_items = []
        for row in range(2):
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setSpacing(12)
            row_layout.setContentsMargins(0, 0, 0, 0)
            for col in range(2):
                idx = row * 2 + col
                name = ['Node.js', 'npm', 'Git', 'Python'][idx]
                icon, ver_label, install_btn, row_w = self._make_env_row(name)
                self.env_items.append((icon, ver_label, install_btn, row_w))
                row_layout.addWidget(row_w, 1)
            grid_layout.addWidget(row_widget)

        layout.addWidget(grid)

        self.install_all_btn = QPushButton('📦 一键安装全部缺失项')
        self.install_all_btn.setFixedHeight(40)
        self.install_all_btn.setVisible(False)
        self.install_all_btn.setStyleSheet('''
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7c3aed, stop:1 #db2777);
                border-radius: 8px; font-size: 14px; font-weight: bold;
            }
        ''')
        self.install_all_btn.clicked.connect(self._do_install_all)
        layout.addWidget(self.install_all_btn)

    def _make_env_row(self, name):
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(12)

        icon = QLabel('⏳')
        icon.setFixedWidth(30)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row_layout.addWidget(icon)

        info = QWidget()
        info_layout = QVBoxLayout(info)
        info_layout.setSpacing(2)
        name_label = QLabel(name)
        name_label.setFont(QFont('Microsoft YaHei UI', 13, QFont.Weight.Bold))
        name_label.setStyleSheet('color: #e2e8f0;')
        ver_label = QLabel('等待检测...')
        ver_label.setStyleSheet('color: #9ca3af; font-size: 12px;')
        info_layout.addWidget(name_label)
        info_layout.addWidget(ver_label)
        row_layout.addWidget(info, 1)

        install_btn = QPushButton('安装')
        install_btn.setEnabled(False)
        install_btn.setProperty('install_for', name)
        install_btn.clicked.connect(self._do_install_missing)
        row_layout.addWidget(install_btn)

        return (icon, ver_label, install_btn, row)

    # ---- 步骤 1: 安装 Claude Code ----

    def _render_step1(self):
        layout = self.step_pages[1].layout()

        card = QFrame()
        card.setObjectName('install_card')
        card.setStyleSheet('''
            QFrame#install_card { background: #1e293b; border-radius: 12px; }
            QFrame#install_card QLabel { color: #e2e8f0; }
        ''')
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(8)
        card_layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel('🚀 安装 Claude Code')
        title.setFont(QFont('Microsoft YaHei UI', 14, QFont.Weight.Bold))
        card_layout.addWidget(title)

        desc = QLabel('Anthropic 官方的 AI 编程助手，让你的编码效率提升 10 倍')
        desc.setStyleSheet('color: #9ca3af; font-size: 11px;')
        card_layout.addWidget(desc)

        divider = QLabel('━' * 30)
        divider.setStyleSheet('color: #374151;')
        card_layout.addWidget(divider)

        self.claude_btn = QPushButton('📥 一键安装 Claude Code')
        self.claude_btn.setFixedHeight(40)
        self.claude_btn.clicked.connect(self._do_install_claude)
        card_layout.addWidget(self.claude_btn)
        card_layout.addStretch()

        layout.addWidget(card)

    # ---- 步骤 2: 安装 ccswitch ----

    def _render_step2(self):
        layout = self.step_pages[2].layout()

        card = QFrame()
        card.setObjectName('install_card')
        card.setStyleSheet('''
            QFrame#install_card { background: #1e293b; border-radius: 12px; }
            QFrame#install_card QLabel { color: #e2e8f0; }
        ''')
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(8)
        card_layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel('🔄 安装 ccswitch')
        title.setFont(QFont('Microsoft YaHei UI', 14, QFont.Weight.Bold))
        card_layout.addWidget(title)

        desc = QLabel('Claude Code 模型切换工具，可在 Opus / Sonnet / Haiku / Fable 之间自由切换')
        desc.setStyleSheet('color: #9ca3af; font-size: 11px;')
        card_layout.addWidget(desc)

        divider = QLabel('━' * 30)
        divider.setStyleSheet('color: #374151;')
        card_layout.addWidget(divider)

        self.ccswitch_btn = QPushButton('📥 一键安装 ccswitch')
        self.ccswitch_btn.setFixedHeight(40)
        self.ccswitch_btn.clicked.connect(self._do_install_ccswitch)
        card_layout.addWidget(self.ccswitch_btn)
        card_layout.addStretch()

        layout.addWidget(card)

    # ---- 步骤 3: 安装 VS Code（选装） ----

    def _render_step3(self):
        layout = self.step_pages[3].layout()

        card = QFrame()
        card.setObjectName('install_card')
        card.setStyleSheet('''
            QFrame#install_card { background: #1e293b; border-radius: 12px; }
            QFrame#install_card QLabel { color: #e2e8f0; }
        ''')
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(8)
        card_layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel('📝 安装 VS Code（建议安装）')
        title.setFont(QFont('Microsoft YaHei UI', 14, QFont.Weight.Bold))
        card_layout.addWidget(title)

        desc = QLabel('Claude Code 需要搭配编辑器使用，VS Code 是目前最流行的代码编辑器')
        desc.setStyleSheet('color: #9ca3af; font-size: 11px;')
        card_layout.addWidget(desc)

        tip = QLabel('💡 如果你已有其他编辑器（如 Cursor、WebStorm），可以跳过此步骤')
        tip.setStyleSheet('color: #6b7280; font-size: 11px;')
        card_layout.addWidget(tip)

        divider = QLabel('━' * 30)
        divider.setStyleSheet('color: #374151;')
        card_layout.addWidget(divider)

        self.vscode_btn = QPushButton('📥 安装 VS Code')
        self.vscode_btn.setFixedHeight(40)
        self.vscode_btn.clicked.connect(self._do_install_vscode)
        card_layout.addWidget(self.vscode_btn)
        card_layout.addStretch()

        layout.addWidget(card)

    def _update_env_item(self, index, icon_text, version_text, show_install=False):
        icon, ver_label, install_btn, _ = self.env_items[index]
        icon.setText(icon_text)
        ver_label.setText(version_text)
        install_btn.setEnabled(show_install)

    def _append_log(self, msg):
        self.log_text.appendPlainText(msg)

    # ---- 动作方法 ----

    def _do_check_env(self):
        self.env_results = check_environment()
        for i, result in enumerate(self.env_results):
            if result['installed'] and result['pass']:
                self._update_env_item(i, '✅', f'已安装 {result["version"]} ✓', False)
            elif result['installed']:
                self._update_env_item(
                    i, '⚠️',
                    f'已安装 {result["version"]} (版本过低，需要 >= {result["min_ver"]})',
                    True
                )
            else:
                self._update_env_item(i, '❌', '未安装', True)

        has_missing = any(not r['pass'] for r in self.env_results)
        self.install_all_btn.setVisible(has_missing)

    def _do_install_missing(self):
        btn = self.sender()
        name = btn.property('install_for')
        self._install_task(lambda cb: install_software(name, cb), f'{name} 安装')

    def _do_install_all(self):
        missing = [r['name'] for r in self.env_results if not r['pass']]
        if not missing:
            QMessageBox.information(self, '提示', '所有环境都已满足要求！')
            return

        def install_all(cb):
            for name in missing:
                cb(f'正在安装 {name}...')
                install_software(name, cb)
            return True, '全部安装完成'

        self._install_task(install_all, '批量安装')

    def _do_install_claude(self):
        self._install_task(
            lambda cb: install_claude_code(callback=cb),
            'Claude Code 安装'
        )

    def _do_install_ccswitch(self):
        self._install_task(
            lambda cb: install_ccswitch(callback=cb),
            'ccswitch 安装'
        )

    def _do_install_vscode(self):
        self._install_task(
            lambda cb: install_vscode(callback=cb),
            'VS Code 安装'
        )

    def _install_task(self, install_func, label):
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self, '提示', f'正在安装 {label}，请稍候...')
            return

        self._append_log(f'=== 开始 {label} ===')
        self.worker = InstallWorker(install_func)
        self.worker.log_signal.connect(self._append_log)
        self.worker.finish_signal.connect(
            lambda ok, msg: self._on_install_finished(ok, msg, label)
        )
        self.worker.start()

    def _on_install_finished(self, ok, msg, label):
        status = '✅' if ok else '❌'
        self._append_log(f'{status} {label}: {msg}')
        if ok:
            QMessageBox.information(self, '成功', f'{label} 完成！\n\n{msg}')
        else:
            QMessageBox.critical(self, '失败', f'{label} 失败！\n\n{msg}')
        if label in ('Node.js 安装', 'Python 安装', 'Git 安装'):
            self._do_check_env()


def main():
    os.system('chcp 65001 >nul 2>&1')
    app = QApplication(sys.argv)
    app.setFont(QFont('Microsoft YaHei UI', 10))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
