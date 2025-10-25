import sys
from PySide2.QtCore import Qt
from PySide2.QtGui import QFont, QColor
from PySide2.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QTabBar, QPushButton, QGridLayout, QLabel, QFrame, QButtonGroup,
                               QTextBrowser, QScrollArea)
from PySide2.QtWidgets import QGraphicsDropShadowEffect
from PySide2.QtCore import QCoreApplication

import ustc_badminton_advanced

class RoundedButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(25)  # 减小高度
        self.setCheckable(True)

        # 设置样式 - 使用不同的颜色和最大圆角
        self.setStyleSheet("""
            QPushButton {
                background-color: #ced4da;
                border: 2px solid #dee2e6;
                border-radius: 12px;  /* 最大圆角 */
                color: #495057;
                font-weight: normal;
                font-size: 12px;
                padding: 2px 8px;
            }
            QPushButton:checked {
                background-color: #6f42c1;  /* 紫色，与选项卡区分 */
                border: 3px solid #333333;
                color: white;
            }
            QPushButton:disabled {
                background-color: #e9ecef;
                border: 2px solid #dee2e6;
                color: #adb5bd;
            }
            QPushButton:disabled:checked {
                background-color: #6f42c1;
                border: 3px solid #333333;
                color: white;
            }
        """)


class CampusTabBar(QTabBar):
    def __init__(self):
        super().__init__()
        self.setExpanding(True)
        self.setDrawBase(False)

        # 设置样式 - 使用方块样式
        self.setStyleSheet("""
            QTabBar::tab {
                background-color: #e9ecef;
                border: 2px solid #dee2e6;
                border-radius: 6px;
                padding: 4px 12px;
                margin-right: 4px;
                color: #495057;
                font-weight: bold;
                font-size: 12px;
            }
            QTabBar::tab:selected {
                background-color: #002FA7;
                border: 2px solid #333333;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background-color: #dee2e6;
            }
            QTabBar::tab:disabled {
                background-color: #f8f9fa;
                border: 2px solid #e9ecef;
                color: #adb5bd;
            }
            QTabBar::tab:disabled:selected {
                background-color: #002FA7;
                border: 2px solid #333333;
                color: white;
            }
        """)


class TimeBlock(QFrame):
    def __init__(self, row, col, main_window, parent=None):
        super().__init__(parent)
        self.row = row
        self.col = col
        self.main_window = main_window  # 保存对主窗口的引用
        self.selected = False
        self.setFixedSize(20, 20)

        # 移除边框，使用内嵌凹槽效果
        self.setFrameStyle(QFrame.NoFrame)

        # 移除阴影效果，创建内嵌效果
        self.update_style()

    def update_style(self):
        if self.selected:
            self.setStyleSheet("""
                QFrame {
                    background-color: #4CAF50;  /* 绿色选中效果 */
                    border: 2px solid #555555;
                    border-radius: 4px;  /* 圆角 */
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #d1d5db;  /* 更深的灰色 */
                    border: 2px solid #9ca3af;
                    border-radius: 4px;  /* 圆角 */
                }
                QFrame:hover {
                    background-color: #c7d2fe;
                    border-color: #818cf8
                }
                QFrame:disabled {
                    background-color: #e9ecef;
                    border: 2px solid #dee2e6;
                }
            """)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 检查是否处于锁定状态
            if not self.main_window.is_locked:
                # 直接调用主窗口的方法
                self.main_window.block_clicked(self.row, self.col)

    def setSelected(self, selected):
        self.selected = selected
        self.update_style()


class CompanionBlock(QPushButton):
    def __init__(self, text, coord, parent=None):
        super().__init__(text, parent)
        self.coord = coord
        self.setFixedSize(65, 25)
        self.setCheckable(True)

        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(1, 1)
        self.setGraphicsEffect(shadow)

        # 移除悬停效果
        self.setStyleSheet("""
            QPushButton {
                background-color: #e9ecef;
                border: 2px solid #dee2e6;
                border-radius: 6px;
                color: #495057;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:checked {
                background-color: #FF7F50;
                border: 2px solid #333333;
                color: white;
            }
            QPushButton:disabled {
                background-color: #f8f9fa;
                border: 2px solid #e9ecef;
                color: #adb5bd;
            }
            QPushButton:disabled:checked {
                background-color: #FF7F50;
                border: 2px solid #333333;
                color: white;
            }
        """)


class SubmitButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(25)  # 高度减半
        self.is_submit_state = True  # 初始状态为提交

        self.update_style()

    def update_style(self):
        if self.is_submit_state:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    border: none;
                    border-radius: 12px;
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
                QPushButton:pressed {
                    background-color: #1e7e34;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    border: none;
                    border-radius: 12px;
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
                QPushButton:pressed {
                    background-color: #bd2130;
                }
            """)

    def set_stop_state(self):
        self.is_submit_state = False
        self.setText("Stop")
        self.update_style()

    def set_submit_state(self):
        self.is_submit_state = True
        self.setText("Submit Reservation")
        self.update_style()


class SportsFieldBooking(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sports Field Booking System")
        self.setFixedSize(700, 420)

        # 添加锁定状态标志
        self.is_locked = False

        # 设置应用样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QScrollArea {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                background-color: #f8f9fa;
            }
        """)
        self.log_browser = None

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局 - 整体按左右划分
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(12, 8, 12, 12)  # l t r b

        # -----------------------
        # 左侧区域（垂直排列：上-选项，下-时间网格）
        # -----------------------
        left_container = QVBoxLayout()
        left_container.setSpacing(8)

        # 左侧的第一行：校区选项卡 + 日期选择（在同一水平行内）
        left_top_row = QHBoxLayout()
        left_top_row.setSpacing(6)

        # 校区选择选项卡（左侧最左）
        self.campus_tabs = CampusTabBar()
        campuses = ["East", "Middle", "West", "HighTech"]
        for campus in campuses:
            self.campus_tabs.addTab(campus)

        # 日期选择（紧跟在选项卡右侧）
        # 我们把日期按钮放在一个小水平布局里，以便精确控制按钮间距和斜杠
        date_layout = QHBoxLayout()
        date_layout.setSpacing(4)  # 按钮和斜杠之间的小间距

        self.today_btn = RoundedButton("today")
        self.tomorrow_btn = RoundedButton("tomorrow")
        slash_label = QLabel("/")
        slash_label.setAlignment(Qt.AlignCenter)
        slash_label.setStyleSheet("color: #6c757d; font-weight: bold;")

        # 分组（互斥）
        self.date_group = QButtonGroup(self)
        self.date_group.addButton(self.today_btn)
        self.date_group.addButton(self.tomorrow_btn)
        self.date_group.setExclusive(True)

        # 控制两个日期按钮之间的精确间距：使用一个 Fixed spacer
        date_layout.addWidget(self.today_btn)
        date_layout.addSpacing(2)  # today 与 '/' 之间微间距
        date_layout.addWidget(slash_label)
        date_layout.addSpacing(2)  # '/' 与 tomorrow 之间微间距
        date_layout.addWidget(self.tomorrow_btn)

        # 把选项卡和日期放到 left_top_row（选项卡靠左，日期紧随其右）
        left_top_row.addWidget(self.campus_tabs, 0)  # stretch 0 保持自然宽度
        left_top_row.addSpacing(8)
        left_top_row.addLayout(date_layout)
        left_top_row.addStretch()  # 将上面元素推到左侧

        # 将 left_top_row 添加到左侧容器（顶部）
        left_container.addLayout(left_top_row)

        # 左侧下方：时间网格（滚动区）
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setFixedHeight(360)

        self.time_grid_widget = QWidget()
        self.time_grid_layout = QGridLayout(self.time_grid_widget)
        self.time_grid_layout.setSpacing(2)
        self.time_grid_layout.setContentsMargins(0, 4, 4, 4)

        # 初始化时间相关属性（保留你原先逻辑）
        self.current_campus_index = 0
        self.field_counts = [6, 14, 8, 12]
        self.time_slots = self.generate_time_slots()
        self.time_blocks = []
        self.selected_blocks = []
        self.current_column = -1

        self.create_time_grid()

        self.scroll_area.setWidget(self.time_grid_widget)
        left_container.addWidget(self.scroll_area)

        # 左侧到此完成（上：选项， 下：时间网格）

        # -----------------------
        # 右侧区域（垂直排列：上-Companion Position + 网格， 下-日志 + 提交）
        # -----------------------
        right_container = QVBoxLayout()
        right_container.setSpacing(4)
        right_container.setContentsMargins(0, 0, 0, 0)  # 左侧边距5px，其他为0

        # 右侧顶部：Companion Position label（居左）和同伴选择网格（紧接其下）
        right_container.addSpacing(5)
        companion_label = QLabel("Companion Position:")
        companion_label.setStyleSheet("font-weight: bold; color: #495057; font-size: 14px;")
        companion_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        # Companion grid
        self.companion_grid = QGridLayout()
        self.companion_grid.setSpacing(6)
        self.companion_grid.setContentsMargins(0, 0, 0, 0)  # 移除所有边距
        self.companion_blocks = []
        self.companion_group = QButtonGroup(self)

        for i in range(2):
            for j in range(3):
                block = CompanionBlock(f"({i + 1},{j + 1})", (i + 1, j + 1))
                self.companion_grid.addWidget(block, i, j)
                self.companion_blocks.append(block)
                self.companion_group.addButton(block)

        companion_widget = QWidget()
        companion_widget.setLayout(self.companion_grid)

        # 右侧把 label 和网格垂直放置
        right_container.addWidget(companion_label)
        right_container.addWidget(companion_widget)

        # 中间使用弹性空间把日志推到下方
        # right_container.addStretch()

        # 日志区
        log_label = QLabel("Operation Log:")
        log_label.setStyleSheet(
            "font-weight: bold; color: #495057; font-size: 14px; margin-bottom: 5px;")
        self.log_browser = QTextBrowser()
        self.log_browser.setMaximumHeight(260)
        # shadow
        # shadow = QGraphicsDropShadowEffect()
        # shadow.setBlurRadius(12)  # 模糊半径
        # shadow.setOffset(5, 5)  # x, y 偏移
        # shadow.setColor(QColor(0, 0, 0, 80))  # 阴影颜色，最后一位是透明度
        # self.log_browser.setGraphicsEffect(shadow)

        self.log_browser.setStyleSheet("""
            QTextBrowser {
                background-color: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 #f8f9fa,
                stop:1 #e9ecef
            );
                border: 2px solid #adb5bd;
                border-radius: 6px;
                padding: 6px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                color: #495057;
            }
        """)

        # 提交按钮
        self.submit_btn = SubmitButton("Submit Reservation")
        self.submit_btn.clicked.connect(self.on_submit)
        self.submit_btn.setMinimumWidth(200)

        # 把日志和提交放到底部（垂直）
        right_container.addWidget(log_label)
        right_container.addWidget(self.log_browser)
        right_container.addWidget(self.submit_btn)

        # -----------------------
        # 将左右容器加入主布局，控制左右宽度比
        # -----------------------
        # 左侧占比更大（例如 7），右侧较窄（例如 3）
        main_layout.addLayout(left_container, 7)
        main_layout.addLayout(right_container, 3)

        # 连接信号
        self.campus_tabs.currentChanged.connect(self.on_campus_changed)
        self.today_btn.clicked.connect(self.on_date_changed)
        self.tomorrow_btn.clicked.connect(self.on_date_changed)

        # 设置默认值
        self.set_default_values()

    def lock_controls(self):
        """锁定所有控件"""
        self.is_locked = True
        self.campus_tabs.setEnabled(False)
        self.today_btn.setEnabled(False)
        self.tomorrow_btn.setEnabled(False)

        # 锁定同伴选择块
        for block in self.companion_blocks:
            block.setEnabled(False)

        # 锁定时间块
        for column in self.time_blocks:
            for block in column:
                block.setEnabled(False)

        self.log_message("All controls locked")

    def unlock_controls(self):
        """解锁所有控件"""
        self.is_locked = False
        self.campus_tabs.setEnabled(True)
        self.today_btn.setEnabled(True)
        self.tomorrow_btn.setEnabled(True)

        # 解锁同伴选择块
        for block in self.companion_blocks:
            block.setEnabled(True)

        # 解锁时间块
        for column in self.time_blocks:
            for block in column:
                block.setEnabled(True)

        self.log_message("All controls unlocked")

    def set_default_values(self):
        """设置默认值"""
        # 设置tomorrow为默认选中
        self.tomorrow_btn.setChecked(True)
        self.log_message("Default date set to: Tomorrow")

        # 设置(1,1)为默认选中
        for block in self.companion_blocks:
            if block.coord == (1, 1):
                block.setChecked(True)
                self.log_message("Default companion position set to: (1,1)")
                break

    def on_date_changed(self):
        """日期选择变化事件"""
        if self.today_btn.isChecked():
            self.log_message("Date changed to: Today")
        elif self.tomorrow_btn.isChecked():
            self.log_message("Date changed to: Tomorrow")

    def log_message(self, message):
        """添加日志消息"""
        if self.log_browser:
            from datetime import datetime
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.log_browser.append(f"[{timestamp}] {message}")
            # 自动滚动到底部
            self.log_browser.verticalScrollBar().setValue(
                self.log_browser.verticalScrollBar().maximum()
            )

    def generate_time_slots(self):
        """生成时间槽：8:00-22:15，每15分钟一个"""
        slots = []
        for hour in range(8, 22):
            for minute in [0, 15, 30, 45]:
                slots.append(f"{hour:02d}:{minute:02d}")
        slots.append("22:00")
        slots.append("22:15")
        return slots

    def create_time_grid(self):
        """创建时间块网格"""
        # 清除现有网格
        for i in reversed(range(self.time_grid_layout.count())):
            widget = self.time_grid_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        self.time_blocks = []
        self.selected_blocks = []
        self.current_column = -1

        # 添加时间标签 - 显示每个时间点
        for i, time_slot in enumerate(self.time_slots):
            label = QLabel(time_slot)
            label.setStyleSheet("font-size: 9px; color: #374151; font-weight: bold;")  # 减小字体大小
            label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            label.setFixedSize(35, 20)  # 减小宽度，使时间标签更靠左
            self.time_grid_layout.addWidget(label, i + 1, 0)

        # 添加场地区块
        field_count = self.field_counts[self.current_campus_index]
        for col in range(field_count):
            # 场地编号 - 只显示数字，没有"Field"文本
            field_label = QLabel(f"{col + 1}")  # 只显示数字
            field_label.setStyleSheet("font-weight: bold; color: #374151; font-size: 11px;")
            field_label.setAlignment(Qt.AlignCenter)
            self.time_grid_layout.addWidget(field_label, 0, col + 1)

            # 时间块
            column_blocks = []
            for row in range(len(self.time_slots)):
                # 传递self作为main_window参数
                block = TimeBlock(row, col, self, self.time_grid_widget)
                self.time_grid_layout.addWidget(block, row + 1, col + 1)
                column_blocks.append(block)
            self.time_blocks.append(column_blocks)

    def block_clicked(self, row, col):
        """处理时间块点击事件"""
        # 如果点击了不同列，清空之前的选择
        if self.current_column != col and self.current_column != -1:
            self.clear_column_selection(self.current_column)
            self.current_column = col

        self.current_column = col
        block = self.time_blocks[col][row]

        if block.selected:
            # 取消选择
            block.setSelected(False)
            if block in self.selected_blocks:
                self.selected_blocks.remove(block)
        else:
            # 选择当前块
            block.setSelected(True)
            self.selected_blocks.append(block)

            # 自动选择同一列中连续的块
            self.auto_select_continuous_blocks(col)

        # 检查选择数量并限制最多6个块
        self.limit_selection_count()

        # 检查选择数量
        self.validate_selection()

        time_slot = self.time_slots[row]
        field_num = col + 1
        if block.selected:
            self.log_message(f"Selected: Field {field_num} {time_slot}")  # 英文
        else:
            self.log_message(f"Deselected: Field {field_num} {time_slot}")  # 英文

    def limit_selection_count(self):
        """限制选择数量最多为6个块"""
        if len(self.selected_blocks) <= 6:
            return

        # 如果超过6个，只保留前6个（按时间顺序）
        selected_in_column = [block for block in self.selected_blocks if block.col == self.current_column]
        if len(selected_in_column) <= 6:
            return

        # 按行号排序
        selected_in_column.sort(key=lambda b: b.row)

        # 保留前6个，取消选择其他的
        for i, block in enumerate(selected_in_column):
            if i >= 6:
                block.setSelected(False)
                if block in self.selected_blocks:
                    self.selected_blocks.remove(block)

        self.log_message("Note: Maximum 6 consecutive time blocks allowed")  # 英文

    def clear_column_selection(self, col):
        """清除指定列的所有选择"""
        for block in self.time_blocks[col]:
            if block.selected:
                block.setSelected(False)
                if block in self.selected_blocks:
                    self.selected_blocks.remove(block)

    def auto_select_continuous_blocks(self, col):
        """自动选择同一列中连续的块"""
        selected_in_column = [block for block in self.selected_blocks if block.col == col]
        if len(selected_in_column) < 2:
            return

        # 获取选中的行索引
        selected_rows = sorted([block.row for block in selected_in_column])
        min_row = selected_rows[0]
        max_row = selected_rows[-1]

        # 选择最小和最大行之间的所有块
        for row in range(min_row, max_row + 1):
            block = self.time_blocks[col][row]
            if not block.selected:
                block.setSelected(True)
                if block not in self.selected_blocks:
                    self.selected_blocks.append(block)

    def validate_selection(self):
        """验证选择是否满足条件"""
        # 检查选择数量是否在2-6之间
        total_selected = len(self.selected_blocks)
        if total_selected < 2 or total_selected > 6:
            # 可以在这里添加视觉反馈
            pass

    def check_continuity(self):
        """检查所选时间块是否连续"""
        if len(self.selected_blocks) < 2:
            return True, ""  # 单个块或没有块被认为是连续的

        # 获取选中的行索引并排序
        selected_rows = sorted([block.row for block in self.selected_blocks])

        # 检查是否连续（相邻行号差为1）
        for i in range(1, len(selected_rows)):
            if selected_rows[i] - selected_rows[i - 1] != 1:
                return False, f"Time blocks are not continuous. Gap found between {self.time_slots[selected_rows[i - 1]]} and {self.time_slots[selected_rows[i]]}"

        return True, ""

    def on_campus_changed(self, index):
        """校区切换事件"""
        self.current_campus_index = index
        self.create_time_grid()
        campus_name = self.campus_tabs.tabText(index)
        self.log_message(f"Campus changed to: {campus_name}, {self.field_counts[index]} fields available")  # 英文

    def on_submit(self):
        """提交按钮点击事件"""
        if self.submit_btn.is_submit_state:
            # 提交状态
            self.log_message("Starting reservation request...")  # 英文
            # 检查条件
            is_valid, error_msg = self.check_conditions()
            if not is_valid:
                self.log_message(f"Submission failed: {error_msg}")  # 英文
                return

            # 获取选择的数据
            campus = self.campus_tabs.tabText(self.current_campus_index)
            date = "Today" if self.today_btn.isChecked() else "Tomorrow"  # 英文

            # 获取选中的时间块信息
            if self.selected_blocks:
                selected_col = self.selected_blocks[0].col
                selected_rows = [block.row for block in self.selected_blocks]
                start_time = self.time_slots[min(selected_rows)]
                end_time = self.time_slots[max(selected_rows)]
                field_number = selected_col + 1
            else:
                start_time = end_time = field_number = None

            # 获取同伴坐标
            companion_coord = None
            for block in self.companion_blocks:
                if block.isChecked():
                    companion_coord = block.coord
                    self.log_message(f"Companion position selected: {companion_coord}")
                    break

            # 调用用户函数
            self.run(campus, date, field_number, start_time, end_time, companion_coord)

            # 成功提交后变为停止状态并锁定所有控件
            self.submit_btn.set_stop_state()
            self.lock_controls()
        else:
            # 停止状态
            self.log_message("Stopping reservation process...")  # 英文
            # 恢复为提交状态并解锁所有控件
            self.submit_btn.set_submit_state()
            self.unlock_controls()
            self.log_message("Reservation process stopped")  # 英文

    def check_conditions(self):
        """检查提交条件"""
        # 检查校区选择
        if self.campus_tabs.currentIndex() == -1:
            return False, "No campus selected"

        # 检查日期选择
        if not self.today_btn.isChecked() and not self.tomorrow_btn.isChecked():
            return False, "No date selected (Today/Tomorrow)"

        # 检查时间块选择
        if len(self.selected_blocks) < 2:
            return False, "Not enough time blocks selected (minimum 2 required)"

        if len(self.selected_blocks) > 6:
            return False, "Too many time blocks selected (maximum 6 allowed)"

        # 检查是否在同一列
        columns = set(block.col for block in self.selected_blocks)
        if len(columns) != 1:
            return False, "Time blocks must be in the same column"

        # 检查连续性
        is_continuous, continuity_error = self.check_continuity()
        if not is_continuous:
            return False, continuity_error

        # 检查同伴选择
        companion_selected = any(block.isChecked() for block in self.companion_blocks)
        if not companion_selected:
            return False, "No companion position selected"

        return True, "All conditions satisfied"

    def run(self, campus, date, field_number, start_time, end_time, companion_coord):
        self.log_message(f"Campus: {campus}, Date: {date}")  # 英文
        self.log_message(f"Field: {field_number}, Time: {start_time} - {end_time}")  # 英文
        self.log_message(f"Companion position: {companion_coord}")  # 英文
        self.log_message("Processing reservation...")  # 英文

        # 您的业务逻辑

        # 在处理的关键步骤添加日志
        self.log_message("Reservation successful!")  # 英文


def main():
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)

    # 设置应用字体
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)

    window = SportsFieldBooking()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()