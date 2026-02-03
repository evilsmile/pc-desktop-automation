# 导入系统模块
import sys
# 导入线程模块，用于后台执行录制和播放操作
import threading

# 从 PyQt5 导入 UI 组件
from PyQt5.QtWidgets import (
    QApplication,      # 应用程序类
    QMainWindow,       # 主窗口类
    QWidget,           # 基础窗口部件
    QVBoxLayout,       # 垂直布局管理器
    QHBoxLayout,       # 水平布局管理器
    QPushButton,       # 按钮控件
    QLabel,            # 标签控件
    QTextEdit,         # 文本编辑控件
    QLineEdit,         # 单行文本输入控件
    QComboBox,         # 下拉选择框
    QCheckBox,         # 复选框
    QListWidget,       # 列表控件
    QListWidgetItem,   # 列表项
    QGroupBox,         # 分组框
    QStatusBar,        # 状态栏
    QMessageBox,       # 消息框
    QSizePolicy        # 大小策略
)

# 从 PyQt5 导入核心功能
from PyQt5.QtCore import (
    Qt,                # Qt 核心常量
    QTimer             # 定时器
)

# 导入工具模块
import utils

# 从录制模块导入函数
from recorder import start_recording, stop_recording

# 从播放模块导入函数
from player import play_operations, stop_playback

# 从序列管理模块导入函数
from sequence import save_sequence, load_sequence, delete_sequence, load_all_sequences, rename_sequence
# 从录制模块导入修饰键常量
from recorder import MODIFIER_KEYS

# 主窗口类，继承自 QMainWindow
class MainWindow(QMainWindow):
    """主窗口类，包含整个应用的用户界面和逻辑"""
    
    def __init__(self):
        """初始化主窗口"""
        # 调用父类 QMainWindow 的初始化方法
        super().__init__()
        
        # 初始化用户界面
        self.initUI()
        
        # 创建状态更新定时器
        self.status_timer = QTimer(self)
        # 连接定时器超时信号到 update_status 方法
        self.status_timer.timeout.connect(self.update_status)
        # 启动定时器，每秒触发一次
        self.status_timer.start(1000)  # 每秒更新一次状态
        
        # 连接播放完成信号，当播放结束时触发 on_playback_completed 方法
        utils.playback_signals.completed.connect(self.on_playback_completed)
        
        # 连接录制停止信号，当录制停止时触发 on_recording_stopped 方法
        utils.recording_signals.stopped.connect(self.on_recording_stopped)
        
        # 添加窗口淡入效果
        self.setWindowOpacity(0.0)
        self.fade_timer = QTimer(self)
        self.fade_timer.timeout.connect(self.fade_in)
        self.fade_timer.start(20)
        self.fade_value = 0.0
    
    def fade_in(self):
        """窗口淡入效果"""
        self.fade_value += 0.05
        if self.fade_value >= 1.0:
            self.fade_value = 1.0
            self.fade_timer.stop()
        self.setWindowOpacity(self.fade_value)
    
    def load_stylesheet(self, filename):
        """从文件加载样式表"""
        import os
        import sys
        
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            # 如果是打包后的可执行文件，从临时目录加载
            base_path = sys._MEIPASS
        else:
            # 如果是直接运行的Python脚本，从脚本所在目录加载
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        filepath = os.path.join(base_path, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"加载样式表失败: {e}")
            return ''
    
    def initUI(self):
        """初始化用户界面"""
        # 设置窗口标题和大小
        # 标题：Windows桌面自动化工具
        # 位置：屏幕左上角(100, 100)像素
        # 大小：700x450像素（固定窗口大小）
        self.setWindowTitle('桌面操作自动重放工具')
        self.setGeometry(100, 100, 800, 800)
        # 设置窗口不可最大化
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)
        # 设置窗口不可缩放
        self.setFixedSize(800, 800)
        
        # 从外部文件加载现代化浅色主题样式
        stylesheet = self.load_stylesheet('styles.css')
        self.setStyleSheet(stylesheet)
        
        # 创建中心部件
        # QMainWindow 需要一个中心部件来放置内容
        central_widget = QWidget()
        # 设置中心部件
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        # 使用垂直布局管理器，从上到下排列控件
        main_layout = QVBoxLayout(central_widget)
        
        # 创建顶部状态栏
        # 显示录制、播放和循环状态
        status_bar = QHBoxLayout()
        status_bar.setContentsMargins(5, 5, 5, 5)
        status_bar.setSpacing(20)
        
        # 录制状态标签
        self.recording_status = QLabel('未录制')
        self.recording_status.setStyleSheet('font-weight: 600; color: #666666;')
        # 播放状态标签
        self.playback_status = QLabel('未播放')
        self.playback_status.setStyleSheet('font-weight: 600; color: #666666;')
        # 循环状态标签
        self.loop_status = QLabel('未循环')
        self.loop_status.setStyleSheet('font-weight: 600; color: #666666;')
        
        # 创建状态容器
        recording_container = QWidget()
        recording_layout = QHBoxLayout(recording_container)  # 改为水平布局
        recording_layout.setContentsMargins(0, 0, 0, 0)
        recording_layout.setSpacing(5)  # 设置水平间距
        recording_title = QLabel('录制状态:')
        recording_title.setStyleSheet('font-size: 12px; color: #999999;')
        recording_layout.addWidget(recording_title)
        recording_layout.addWidget(self.recording_status)
        
        playback_container = QWidget()
        playback_layout = QHBoxLayout(playback_container)  # 改为水平布局
        playback_layout.setContentsMargins(0, 0, 0, 0)
        playback_layout.setSpacing(5)  # 设置水平间距
        playback_title = QLabel('播放状态:')
        playback_title.setStyleSheet('font-size: 12px; color: #999999;')
        playback_layout.addWidget(playback_title)
        playback_layout.addWidget(self.playback_status)
        
        loop_container = QWidget()
        loop_layout = QHBoxLayout(loop_container)  # 改为水平布局
        loop_layout.setContentsMargins(0, 0, 0, 0)
        loop_layout.setSpacing(5)  # 设置水平间距
        loop_title = QLabel('循环状态:')
        loop_title.setStyleSheet('font-size: 12px; color: #999999;')
        loop_layout.addWidget(loop_title)
        loop_layout.addWidget(self.loop_status)
        
        # 添加状态容器到状态栏布局
        status_bar.addWidget(recording_container)
        status_bar.addWidget(playback_container)
        status_bar.addWidget(loop_container)
        status_bar.addStretch()  # 弹簧，将内容推到左侧
        
        # 将状态栏添加到主布局
        main_layout.addLayout(status_bar)
        
        # 创建主内容区域
        # 使用水平布局管理器，将界面分为左右两部分
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(10, 10, 10, 10)  # 减小边距
        content_layout.setSpacing(15)  # 减小间距
        
        # 左侧控制面板
        # 包含录制控制、播放控制、系统状态和序列管理
        left_panel = QVBoxLayout()
        left_panel.setSpacing(10)  # 减小间距
        
        # 录制控制分组
        record_group = QGroupBox('录制控制')
        record_layout = QVBoxLayout()
        record_layout.setSpacing(10)  # 减小间距
        
        # 录制按钮布局
        record_buttons = QHBoxLayout()
        record_buttons.setSpacing(10)  # 减小间距
        # 开始录制按钮
        self.start_record_btn = QPushButton('开始录制')
        self.start_record_btn.setMinimumSize(90, 30)  # 减小按钮大小
        self.start_record_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)  # 设置大小策略
        # 停止录制按钮
        self.stop_record_btn = QPushButton('停止录制')
        self.stop_record_btn.setMinimumSize(90, 30)  # 减小按钮大小
        self.stop_record_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)  # 设置大小策略
        # 设置按钮对象名，用于样式表选择
        self.stop_record_btn.setObjectName('stop_record_btn')
        # 初始禁用停止按钮
        self.stop_record_btn.setEnabled(False)
        
        # 连接按钮点击信号到对应的槽函数
        self.start_record_btn.clicked.connect(self.on_start_record)
        self.stop_record_btn.clicked.connect(self.on_stop_record)
        
        # 添加按钮到布局
        record_buttons.addWidget(self.start_record_btn)
        record_buttons.addWidget(self.stop_record_btn)
        
        # 添加按钮布局和提示信息到录制控制布局
        record_layout.addLayout(record_buttons)
        hint_label = QLabel('提示：按esc可停止录制')
        hint_label.setStyleSheet('color: #999999; font-size: 12px;')
        record_layout.addWidget(hint_label)
        
        # 设置录制控制分组的布局
        record_group.setLayout(record_layout)
        # 添加到左侧面板
        left_panel.addWidget(record_group)
        
        # 播放控制分组
        play_group = QGroupBox('播放控制')
        play_layout = QVBoxLayout()
        play_layout.setSpacing(10)  # 减小间距
        play_layout.setContentsMargins(5, 5, 5, 5)  # 减小边距
        
        # 播放按钮布局
        play_buttons = QHBoxLayout()
        play_buttons.setSpacing(10)  # 减小间距
        play_buttons.setContentsMargins(0, 0, 0, 0)
        # 播放按钮
        self.play_btn = QPushButton('播放')
        self.play_btn.setMinimumSize(90, 30)  # 减小按钮大小
        self.play_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)  # 设置大小策略
        # 设置播放按钮对象名
        self.play_btn.setObjectName('play_btn')
        # 停止按钮
        self.stop_play_btn = QPushButton('停止')
        self.stop_play_btn.setMinimumSize(90, 30)  # 减小按钮大小
        self.stop_play_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)  # 设置大小策略
        # 初始禁用停止按钮
        self.stop_play_btn.setEnabled(False)
        # 设置按钮对象名
        self.stop_play_btn.setObjectName('stop_play_btn')
        
        # 连接按钮点击信号
        self.play_btn.clicked.connect(self.on_play)
        self.stop_play_btn.clicked.connect(self.on_stop_play)
        
        # 添加按钮到布局
        play_buttons.addWidget(self.play_btn)
        play_buttons.addWidget(self.stop_play_btn)
        
        # 添加按esc键停止播放的说明
        play_hint_label = QLabel('提示：按esc键可停止播放')
        play_hint_label.setStyleSheet('color: #999999; font-size: 12px;')
        
        # 循环设置布局
        loop_layout = QHBoxLayout()
        loop_layout.setSpacing(15)
        loop_layout.setContentsMargins(0, 0, 0, 0)
        # 自动循环复选框
        self.loop_checkbox = QCheckBox('自动循环')
        # 循环次数标签
        self.loop_count_label = QLabel('循环次数：0')
        self.loop_count_label.setStyleSheet('font-weight: 500;')
        
        # 连接复选框状态变化信号
        self.loop_checkbox.stateChanged.connect(self.on_loop_changed)
        
        # 添加到循环布局
        loop_layout.addWidget(self.loop_checkbox)
        loop_layout.addStretch()
        loop_layout.addWidget(self.loop_count_label)
        
        # 循环次数配置布局
        loop_config_layout = QHBoxLayout()
        loop_config_layout.setSpacing(15)
        loop_config_layout.setContentsMargins(0, 0, 0, 0)
        # 循环次数输入框
        self.loop_count_input = QLineEdit()
        self.loop_count_input.setPlaceholderText('循环次数')
        self.loop_count_input.setText('1')  # 默认值
        self.loop_count_input.setMinimumSize(120, 35)  # 设置最小大小
        self.loop_count_input.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)  # 设置大小策略
        
        # 连接输入框文本变化信号
        self.loop_count_input.textChanged.connect(self.on_loop_count_changed)
        
        # 添加到循环配置布局
        loop_config_layout.addWidget(QLabel('循环配置：'))
        loop_config_layout.addWidget(self.loop_count_input)
        loop_config_layout.addStretch()
        
        # 播放速度配置布局
        speed_layout = QHBoxLayout()
        speed_layout.setSpacing(15)
        speed_layout.setContentsMargins(0, 0, 0, 0)
        # 播放速度下拉框
        self.speed_combo = QComboBox()
        # 添加速度选项，第一个参数是显示文本，第二个是对应的数据值
        self.speed_combo.addItem('1.0倍速', 1.0)
        self.speed_combo.addItem('1.5倍速', 1.5)
        self.speed_combo.addItem('2.0倍速', 2.0)
        self.speed_combo.addItem('3.0倍速', 3.0)
        self.speed_combo.addItem('5.0倍速', 5.0)
        self.speed_combo.addItem('10.0倍速', 10.0)
        self.speed_combo.addItem('15.0倍速', 15.0)
        self.speed_combo.addItem('20.0倍速', 20.0)
        self.speed_combo.setMinimumSize(180, 35)  # 设置最小大小
        self.speed_combo.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)  # 设置大小策略
        
        # 添加到速度布局
        speed_layout.addWidget(QLabel('播放速度：'))
        speed_layout.addWidget(self.speed_combo)
        speed_layout.addStretch()
        
        # 将所有布局添加到播放控制布局
        play_layout.addLayout(play_buttons)
        play_layout.addWidget(play_hint_label)
        play_layout.addLayout(loop_layout)
        play_layout.addLayout(loop_config_layout)
        play_layout.addLayout(speed_layout)
        
        # 设置播放控制分组的布局
        play_group.setLayout(play_layout)
        # 添加到左侧面板
        left_panel.addWidget(play_group)
        
        # 系统状态分组
        #system_group = QGroupBox('系统状态')
        #system_layout = QVBoxLayout()
        ## 添加系统状态信息
        #system_layout.addWidget(QLabel('Python 已检测到'))
        #system_layout.addWidget(QLabel('使用PyAutoGUI控制实际Windows桌面'))
        ## 设置系统状态分组的布局
        #system_group.setLayout(system_layout)
        ## 添加到左侧面板
        #left_panel.addWidget(system_group)
        
        # 序列管理分组
        sequence_group = QGroupBox('序列管理')
        sequence_layout = QVBoxLayout()
        sequence_layout.setSpacing(10)  # 减小间距
        sequence_layout.setContentsMargins(5, 5, 5, 5)  # 减小边距
        
        # 保存序列布局
        save_layout = QHBoxLayout()
        save_layout.setSpacing(10)  # 减小间距
        save_layout.setContentsMargins(0, 0, 0, 0)
        # 序列名称输入框
        self.sequence_name = QLineEdit()
        self.sequence_name.setPlaceholderText('输入序列名称')
        self.sequence_name.setMinimumSize(100, 25)  # 减小输入框大小
        self.sequence_name.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)  # 设置大小策略
        # 保存按钮
        self.save_btn = QPushButton('保存')
        self.save_btn.setMinimumSize(60, 25)  # 减小按钮大小
        self.save_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)  # 设置大小策略
        # 设置保存按钮对象名
        self.save_btn.setObjectName('save_btn')
        
        # 连接保存按钮点击信号
        self.save_btn.clicked.connect(self.on_save_sequence)
        
        # 添加到保存布局
        save_layout.addWidget(self.sequence_name)
        save_layout.addWidget(self.save_btn)
        
        # 加载序列布局
        load_layout = QHBoxLayout()
        load_layout.setSpacing(10)  # 减小间距
        load_layout.setContentsMargins(0, 0, 0, 0)
        # 加载序列下拉框
        self.load_combo = QComboBox()
        self.load_combo.addItem('选择序列')
        self.load_combo.setMinimumSize(100, 25)  # 减小下拉框大小
        self.load_combo.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)  # 设置大小策略
        # 加载按钮
        self.load_btn = QPushButton('加载')
        self.load_btn.setMinimumSize(60, 25)  # 减小按钮大小
        self.load_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)  # 设置大小策略
        # 设置加载按钮对象名
        self.load_btn.setObjectName('load_btn')
        
        # 连接加载按钮点击信号
        self.load_btn.clicked.connect(self.on_load_sequence)
        
        # 添加到加载布局
        load_layout.addWidget(self.load_combo)
        load_layout.addWidget(self.load_btn)
        
        # 删除序列布局
        delete_layout = QHBoxLayout()
        delete_layout.setSpacing(10)  # 减小间距
        delete_layout.setContentsMargins(0, 0, 0, 0)
        # 删除序列下拉框
        self.delete_combo = QComboBox()
        self.delete_combo.addItem('选择序列')
        self.delete_combo.setMinimumSize(100, 25)  # 减小下拉框大小
        self.delete_combo.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)  # 设置大小策略
        # 删除按钮
        self.delete_btn = QPushButton('删除')
        self.delete_btn.setMinimumSize(60, 25)  # 减小按钮大小
        self.delete_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)  # 设置大小策略
        # 设置删除按钮对象名
        self.delete_btn.setObjectName('delete_btn')
        
        # 连接删除按钮点击信号
        self.delete_btn.clicked.connect(self.on_delete_sequence)
        
        # 添加到删除布局
        delete_layout.addWidget(self.delete_combo)
        delete_layout.addWidget(self.delete_btn)
        
        # 修改序列布局
        rename_layout = QHBoxLayout()
        rename_layout.setSpacing(10)  # 减小间距
        rename_layout.setContentsMargins(0, 0, 0, 0)
        # 修改序列下拉框
        self.rename_combo = QComboBox()
        self.rename_combo.addItem('选择序列')
        self.rename_combo.setMinimumSize(100, 25)  # 减小下拉框大小
        self.rename_combo.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)  # 设置大小策略
        # 新名称输入框
        self.rename_input = QLineEdit()
        self.rename_input.setPlaceholderText('新名称')
        self.rename_input.setMinimumSize(100, 25)  # 减小输入框大小
        self.rename_input.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)  # 设置大小策略
        # 修改按钮
        self.rename_btn = QPushButton('修改')
        self.rename_btn.setMinimumSize(60, 25)  # 减小按钮大小
        self.rename_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)  # 设置大小策略
        # 设置修改按钮对象名
        self.rename_btn.setObjectName('rename_btn')
        
        # 连接修改按钮点击信号
        self.rename_btn.clicked.connect(self.on_rename_sequence)
        
        # 添加到修改布局
        rename_layout.addWidget(self.rename_combo)
        rename_layout.addWidget(self.rename_input)
        rename_layout.addWidget(self.rename_btn)
        
        # 当前序列标签
        self.current_sequence_label = QLabel('当前序列：无')
        self.current_sequence_label.setStyleSheet('font-weight: 600; color: #666666; margin-top: 10px;')
        
        # 将所有布局和标签添加到序列管理布局
        sequence_layout.addLayout(save_layout)
        sequence_layout.addLayout(load_layout)
        sequence_layout.addLayout(delete_layout)
        sequence_layout.addLayout(rename_layout)
        sequence_layout.addWidget(self.current_sequence_label)
        
        # 设置序列管理分组的布局
        sequence_group.setLayout(sequence_layout)
        # 添加到左侧面板
        left_panel.addWidget(sequence_group)
        
        # 添加弹簧，将内容推到顶部
        left_panel.addStretch()
        
        # 右侧操作区域
        # 包含操作序列和操作详情
        right_panel = QVBoxLayout()
        right_panel.setSpacing(8)  # 减小间距
        
        # 操作序列分组
        operations_group = QGroupBox('操作序列')
        operations_layout = QVBoxLayout()
        operations_layout.setSpacing(10)  # 减小间距
        
        # 操作列表控件
        self.operations_list = QListWidget()
        self.operations_list.setMinimumHeight(120)  # 减小最小高度
        self.operations_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # 设置大小策略
        # 设置为多选模式
        self.operations_list.setSelectionMode(QListWidget.MultiSelection)
        self.operations_list.setStyleSheet('''
            QListWidget {
                border-radius: 8px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 6px;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
        ''')
        # 操作管理按钮布局
        operations_buttons = QHBoxLayout()
        operations_buttons.setSpacing(8)
        # 添加操作按钮
        self.add_operation_btn = QPushButton('添加')
        self.add_operation_btn.setMinimumSize(70, 25)
        self.add_operation_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.add_operation_btn.setStyleSheet('background-color: #4CAF50; color: white;')
        # 编辑操作按钮
        self.edit_operation_btn = QPushButton('编辑')
        self.edit_operation_btn.setMinimumSize(70, 25)
        self.edit_operation_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.edit_operation_btn.setStyleSheet('background-color: #2196F3; color: white;')
        # 复制操作按钮
        self.copy_operation_btn = QPushButton('复制')
        self.copy_operation_btn.setMinimumSize(70, 25)
        self.copy_operation_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.copy_operation_btn.setStyleSheet('background-color: #FF9800; color: white;')
        # 删除操作按钮
        self.delete_operation_btn = QPushButton('删除')
        self.delete_operation_btn.setMinimumSize(70, 25)
        self.delete_operation_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.delete_operation_btn.setStyleSheet('background-color: #f44336; color: white;')
        # 清空操作按钮
        self.clear_btn = QPushButton('清空')
        self.clear_btn.setMinimumSize(70, 25)
        self.clear_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.clear_btn.setStyleSheet('background-color: #9e9e9e; color: white;')
        # 设置按钮对象名
        self.clear_btn.setObjectName('clear_btn')
        
        # 连接按钮点击信号
        self.clear_btn.clicked.connect(self.on_clear_operations)
        self.add_operation_btn.clicked.connect(self.on_add_operation)
        self.edit_operation_btn.clicked.connect(self.on_edit_operation)
        self.copy_operation_btn.clicked.connect(self.on_copy_operation)
        self.delete_operation_btn.clicked.connect(self.on_delete_operation)
        
        # 添加按钮到布局
        operations_buttons.addWidget(self.add_operation_btn)
        operations_buttons.addWidget(self.edit_operation_btn)
        operations_buttons.addWidget(self.copy_operation_btn)
        operations_buttons.addWidget(self.delete_operation_btn)
        operations_buttons.addWidget(self.clear_btn)
        
        # 添加到操作序列布局
        operations_layout.addWidget(self.operations_list)
        operations_layout.addLayout(operations_buttons)
        
        # 设置操作序列分组的布局
        operations_group.setLayout(operations_layout)
        # 添加到右侧面板
        right_panel.addWidget(operations_group)
        
        # 操作详情分组
        detail_group = QGroupBox('操作详情')
        detail_layout = QVBoxLayout()
        detail_layout.setSpacing(8)  # 减小间距
        
        # 操作详情文本框
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)  # 设置为只读
        self.detail_text.setMinimumHeight(100)  # 减小最小高度
        self.detail_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # 设置大小策略
        self.detail_text.setStyleSheet('''
            QTextEdit {
                border-radius: 8px;
                padding: 10px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
                line-height: 1.3;
            }
        ''')
        
        # 添加到操作详情布局
        detail_layout.addWidget(self.detail_text)
        # 设置操作详情分组的布局
        detail_group.setLayout(detail_layout)
        # 添加到右侧面板
        right_panel.addWidget(detail_group)
        
        # 将左侧和右侧面板添加到主内容布局
        # 调整比例，确保左侧面板有足够的空间显示所有控件
        # 左侧面板占1份，右侧面板占1份，适应固定窗口大小
        content_layout.addLayout(left_panel, 1)
        content_layout.addLayout(right_panel, 1)
        
        # 将主内容布局添加到主布局
        main_layout.addLayout(content_layout)
        

        
        # 加载序列列表
        # 启动时从文件加载已保存的序列
        try:
            self.load_sequences_list()
        except Exception as e:
            # 捕获并打印加载错误
            utils.logger.error(f"加载序列列表时出错: {e}")
    
    def on_start_record(self):
        """开始录制操作"""
        # 更新按钮状态
        self.start_record_btn.setEnabled(False)  # 禁用开始录制按钮
        self.stop_record_btn.setEnabled(True)    # 启用停止录制按钮

        # 禁用其他功能按钮
        self.play_btn.setEnabled(False)    # 禁用播放按钮
        self.save_btn.setEnabled(False)    # 禁用保存按钮
        self.load_btn.setEnabled(False)    # 禁用加载按钮
        self.delete_btn.setEnabled(False)  # 禁用删除按钮
        
        # 最小化窗口，方便用户操作
        self.showMinimized()
        
        # 启动录制线程
        # 创建线程，目标函数为 start_recording
        recording_thread = threading.Thread(target=start_recording)
        # 设置为守护线程，主程序退出时自动退出
        recording_thread.daemon = True
        # 启动线程
        recording_thread.start()
    
    def on_stop_record(self):
        """停止录制操作"""
        # 调用停止录制函数
        stop_recording()
        
        # 恢复窗口
        self.showNormal()        # 从最小化状态恢复
        self.activateWindow()    # 激活窗口
        
        # 重新启用按钮
        self.start_record_btn.setEnabled(True)   # 启用开始录制按钮
        self.stop_record_btn.setEnabled(False)   # 禁用停止录制按钮
        self.play_btn.setEnabled(True)           # 启用播放按钮
        self.save_btn.setEnabled(True)           # 启用保存按钮
        self.load_btn.setEnabled(True)           # 启用加载按钮
        self.delete_btn.setEnabled(True)         # 启用删除按钮
        
        # 更新操作列表，显示录制的操作
        self.update_operations_list()
    
    def on_play(self):
        """开始播放操作"""
        # 更新播放设置
        utils.is_looping = self.loop_checkbox.isChecked()  # 设置是否循环播放
        utils.playback_speed = self.speed_combo.currentData()  # 获取播放速度
        
        # 更新按钮状态
        self.play_btn.setEnabled(False)           # 禁用播放按钮
        self.stop_play_btn.setEnabled(True)       # 启用停止按钮
        self.start_record_btn.setEnabled(False)   # 禁用开始录制按钮
        
        # 最小化窗口，方便操作执行
        self.showMinimized()
        
        # 启动播放线程
        # 创建线程，目标函数为 play_operations
        playback_thread = threading.Thread(target=play_operations)
        # 设置为守护线程
        playback_thread.daemon = True
        # 启动线程
        playback_thread.start()
    
    def on_stop_play(self):
        """停止播放操作"""
        # 调用停止播放函数
        stop_playback()
        
        # 恢复窗口
        self.showNormal()        # 从最小化状态恢复
        self.activateWindow()    # 激活窗口
        
        # 更新按钮状态
        self.play_btn.setEnabled(True)           # 启用播放按钮
        self.stop_play_btn.setEnabled(False)     # 禁用停止按钮
        self.start_record_btn.setEnabled(True)   # 启用开始录制按钮
    
    def on_playback_completed(self):
        """播放完成时的处理"""
        # 播放完成，恢复窗口
        self.showNormal()        # 从最小化状态恢复
        self.activateWindow()    # 激活窗口

        # 重置循环次数
        utils.loop_count = 0

        # 播放完成，弹出提示
        QMessageBox.information(self, '播放完成', '操作序列播放已完成！')
        
        # 更新按钮状态
        self.play_btn.setEnabled(True)           # 启用播放按钮
        self.stop_play_btn.setEnabled(False)     # 禁用停止按钮
        self.start_record_btn.setEnabled(True)   # 启用开始录制按钮
    
    def on_recording_stopped(self):
        """录制停止时的处理"""
        # 恢复窗口
        self.showNormal()        # 从最小化状态恢复
        self.activateWindow()    # 激活窗口
        
        # 重新启用按钮
        self.start_record_btn.setEnabled(True)   # 启用开始录制按钮
        self.stop_record_btn.setEnabled(False)   # 禁用停止录制按钮
        self.play_btn.setEnabled(True)           # 启用播放按钮
        self.save_btn.setEnabled(True)           # 启用保存按钮
        self.load_btn.setEnabled(True)           # 启用加载按钮
        self.delete_btn.setEnabled(True)         # 启用删除按钮
        
        # 更新操作列表，显示录制的操作
        self.update_operations_list()
        
        # 显示录制完成提示
        QMessageBox.information(self, '录制完成', '操作序列录制已完成！')
    
    def on_loop_changed(self, state):
        """循环设置变化时的处理"""
        # 更新循环状态
        # 当复选框被选中时，state == Qt.Checked 为 True
        utils.is_looping = state == Qt.Checked
    
    def on_loop_count_changed(self, text):
        """循环次数变化时的处理"""
        try:
            # 尝试将输入文本转换为整数
            count = int(text)
            # 确保循环次数大于0
            if count > 0:
                utils.max_loop_count = count
            else:
                # 输入无效时，默认为1
                utils.max_loop_count = 1
        except ValueError:
            # 转换失败时，默认为1
            utils.max_loop_count = 1
    
    def on_save_sequence(self):
        """保存序列操作"""
        # 获取序列名称，去除首尾空格
        name = self.sequence_name.text().strip()
        
        # 验证序列名称
        if not name:
            # 显示警告消息框
            QMessageBox.warning(self, '错误', '请输入序列名称')
            return
        
        # 调用保存序列函数
        success, message = save_sequence(name)
        
        # 根据保存结果显示相应消息
        if success:
            # 保存成功
            QMessageBox.information(self, '成功', message)
            # 清空序列名称输入框
            self.sequence_name.clear()
            # 重新加载序列列表
            self.load_sequences_list()
        else:
            # 保存失败
            QMessageBox.warning(self, '错误', message)
    
    def on_load_sequence(self):
        """加载序列操作"""
        # 获取选中的序列名称
        name = self.load_combo.currentText()
        
        # 验证选择
        if name == '选择序列':
            # 显示警告消息框
            QMessageBox.warning(self, '错误', '请选择要加载的序列')
            return
        
        # 调用加载序列函数
        success, message = load_sequence(name)
        
        # 根据加载结果显示相应消息
        if success:
            # 加载成功
            QMessageBox.information(self, '成功', message)
            # 更新操作列表
            self.update_operations_list()
            # 更新当前序列标签
            self.current_sequence_label.setText(f'当前序列：{utils.current_sequence}')
        else:
            # 加载失败
            QMessageBox.warning(self, '错误', message)
    
    def on_delete_sequence(self):
        """删除序列操作"""
        # 获取选中的序列名称
        name = self.delete_combo.currentText()
        
        # 验证选择
        if name == '选择序列':
            # 显示警告消息框
            QMessageBox.warning(self, '错误', '请选择要删除的序列')
            return
        
        # 显示确认对话框
        if QMessageBox.question(self, '确认', f'确定要删除序列 "{name}" 吗？', 
                               QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            # 用户确认删除
            # 调用删除序列函数
            success, message = delete_sequence(name)
            
            # 根据删除结果显示相应消息
            if success:
                # 删除成功
                QMessageBox.information(self, '成功', message)
                # 重新加载序列列表
                self.load_sequences_list()
                # 更新当前序列标签
                self.current_sequence_label.setText(f'当前序列：{utils.current_sequence}')
            else:
                # 删除失败
                QMessageBox.warning(self, '错误', message)

    def on_rename_sequence(self):
        """修改序列名称操作"""
        # 获取选中的旧序列名称
        old_name = self.rename_combo.currentText()
        # 获取新序列名称，去除首尾空格
        new_name = self.rename_input.text().strip()
        
        # 验证选择
        if old_name == '选择序列':
            # 显示警告消息框
            QMessageBox.warning(self, '错误', '请选择要修改的序列')
            return
        
        # 验证新名称
        if not new_name:
            # 显示警告消息框
            QMessageBox.warning(self, '错误', '请输入新序列名称')
            return
        
        # 显示确认对话框
        if QMessageBox.question(self, '确认', f'确定要将序列 "{old_name}" 重命名为 "{new_name}" 吗？', 
                               QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            # 用户确认修改
            # 调用修改序列函数
            success, message = rename_sequence(old_name, new_name)
            
            # 根据修改结果显示相应消息
            if success:
                # 修改成功
                QMessageBox.information(self, '成功', message)
                # 清空新名称输入框
                self.rename_input.clear()
                # 重新加载序列列表
                self.load_sequences_list()
                # 更新当前序列标签
                self.current_sequence_label.setText(f'当前序列：{utils.current_sequence}')
            else:
                # 修改失败
                QMessageBox.warning(self, '错误', message)

    def on_clear_operations(self):
        """清空操作记录"""
        # 显示确认对话框
        if QMessageBox.question(self, '确认', '确定要清空所有操作记录吗？', 
                               QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            # 用户确认清空
            # 清空操作列表
            utils.recorded_operations = []
            # 清空当前序列
            utils.current_sequence = ""
            # 清空操作列表控件
            self.operations_list.clear()
            # 清空操作详情文本框
            self.detail_text.clear()
            # 更新当前序列标签
            self.current_sequence_label.setText(f'当前序列：{utils.current_sequence}')
    
    def load_sequences_list(self):
        """加载序列列表"""
        # 获取所有已保存的序列
        sequences = load_all_sequences()
        
        # 清空并重新填充加载序列下拉框
        self.load_combo.clear()
        self.load_combo.addItem('选择序列')
        for seq in sequences:
            self.load_combo.addItem(seq)
        
        # 清空并重新填充删除序列下拉框
        self.delete_combo.clear()
        self.delete_combo.addItem('选择序列')
        for seq in sequences:
            self.delete_combo.addItem(seq)
        
        # 清空并重新填充修改序列下拉框
        self.rename_combo.clear()
        self.rename_combo.addItem('选择序列')
        for seq in sequences:
            self.rename_combo.addItem(seq)
    
    def update_operations_list(self):
        """更新操作列表"""
        # 清空操作列表控件
        self.operations_list.clear()
        
        # 遍历录制的操作列表
        for i, op in enumerate(utils.recorded_operations):
            # 根据操作类型生成显示文本
            if op['type'] == 'mousemove':
                item_text = f'{i+1}. 鼠标移动到 ({int(op["x"])}, {int(op["y"])})'
            elif op['type'] == 'mousedown':
                item_text = f'{i+1}. 鼠标按下 ({int(op["x"])}, {int(op["y"])})'
            elif op['type'] == 'mouseup':
                item_text = f'{i+1}. 鼠标释放 ({int(op["x"])}, {int(op["y"])})'
            elif op['type'] == 'keydown':
                if 'modifiers' in op and op['modifiers']:
                    item_text = f'{i+1}. 组合键按下: {op["key"]}'
                else:
                    item_text = f'{i+1}. 按键按下: {op["key"]}'
            elif op['type'] == 'keyup':
                if 'modifiers' in op and op['modifiers']:
                    item_text = f'{i+1}. 组合键释放: {op["key"]}'
                else:
                    item_text = f'{i+1}. 按键释放: {op["key"]}'
            else:
                item_text = f'{i+1}. 未知操作'
            
            # 创建列表项
            item = QListWidgetItem(item_text)
            # 存储操作数据到列表项
            item.setData(Qt.UserRole, op)
            # 添加列表项到控件
            self.operations_list.addItem(item)
        
        # 连接点击事件到处理函数
        self.operations_list.itemClicked.connect(self.on_operation_clicked)
    
    def on_operation_clicked(self, item):
        """操作项点击事件处理"""
        # 获取存储在列表项中的操作数据
        op = item.data(Qt.UserRole)
        
        # 构建操作详情文本
        detail = f"类型: {op['type']}\n"
        # 添加位置信息（如果有）
        if 'x' in op and 'y' in op:
            detail += f"位置: ({int(op['x'])}, {int(op['y'])})\n"
        # 添加按键信息（如果有）
        if 'key' in op:
            detail += f"按键: {op['key']}\n"
        # 添加修饰键信息（如果有）
        if 'modifiers' in op and op['modifiers']:
            detail += f"修饰键: {', '.join(op['modifiers'])}\n"
        # 添加基础键信息（如果有）
        if 'base_key' in op:
            detail += f"基础键: {op['base_key']}\n"
        # 添加按钮信息（如果有）
        if 'button' in op:
            detail += f"按钮: {op['button']}\n"
        # 添加时间戳信息
        detail += f"时间戳: {op['timestamp']:.2f}秒"
        
        # 更新详情文本框
        self.detail_text.setText(detail)
    
    def update_status(self):
        """更新状态信息"""
        # 更新录制状态
        recording_text = f'{"正在录制" if utils.is_recording else "未录制"}'
        if self.recording_status.text() != recording_text:
            self.recording_status.setText(recording_text)
            self.animate_widget(self.recording_status)
        
        # 更新播放状态
        playback_text = f'{"正在播放" if utils.is_playing else "未播放"}'
        if self.playback_status.text() != playback_text:
            self.playback_status.setText(playback_text)
            self.animate_widget(self.playback_status)
        
        # 更新循环状态
        loop_text = f'{"开启" if utils.is_looping else "关闭"}'
        if self.loop_status.text() != loop_text:
            self.loop_status.setText(loop_text)
            self.animate_widget(self.loop_status)
        
        # 更新循环次数
        loop_count_text = f'循环次数：{utils.loop_count}'
        if self.loop_count_label.text() != loop_count_text:
            self.loop_count_label.setText(loop_count_text)
            self.animate_widget(self.loop_count_label)
        
        # 更新当前序列信息
        sequence_text = f'当前序列：{utils.current_sequence or "无"}'
        if self.current_sequence_label.text() != sequence_text:
            self.current_sequence_label.setText(sequence_text)
            self.animate_widget(self.current_sequence_label)
        
        # 更新按钮状态
        if utils.is_recording:
            if self.start_record_btn.isEnabled():
                self.start_record_btn.setEnabled(False)
                self.animate_widget(self.start_record_btn)
            if not self.stop_record_btn.isEnabled():
                self.stop_record_btn.setEnabled(True)
                self.animate_widget(self.stop_record_btn)
            if self.play_btn.isEnabled():
                self.play_btn.setEnabled(False)
                self.animate_widget(self.play_btn)
        else:
            if not self.start_record_btn.isEnabled():
                self.start_record_btn.setEnabled(True)
                self.animate_widget(self.start_record_btn)
            if self.stop_record_btn.isEnabled():
                self.stop_record_btn.setEnabled(False)
                self.animate_widget(self.stop_record_btn)
            play_enabled = not utils.is_playing and len(utils.recorded_operations) > 0
            if self.play_btn.isEnabled() != play_enabled:
                self.play_btn.setEnabled(play_enabled)
                self.animate_widget(self.play_btn)
        
        if utils.is_playing:
            if self.play_btn.isEnabled():
                self.play_btn.setEnabled(False)
                self.animate_widget(self.play_btn)
            if not self.stop_play_btn.isEnabled():
                self.stop_play_btn.setEnabled(True)
                self.animate_widget(self.stop_play_btn)
            if self.start_record_btn.isEnabled():
                self.start_record_btn.setEnabled(False)
                self.animate_widget(self.start_record_btn)
        else:
            play_enabled = len(utils.recorded_operations) > 0
            if self.play_btn.isEnabled() != play_enabled:
                self.play_btn.setEnabled(play_enabled)
                self.animate_widget(self.play_btn)
            if self.stop_play_btn.isEnabled():
                self.stop_play_btn.setEnabled(False)
                self.animate_widget(self.stop_play_btn)
            if not self.start_record_btn.isEnabled() and not utils.is_recording:
                self.start_record_btn.setEnabled(True)
                self.animate_widget(self.start_record_btn)
    
    def animate_widget(self, widget):
        """为控件添加动画效果"""
        original_style = widget.styleSheet()
        
        if isinstance(widget, QLabel):
            widget.setStyleSheet(original_style + '; color: #FF5A5F; font-weight: 700;')
        elif isinstance(widget, QPushButton):
            widget.setStyleSheet(original_style + '; background-color: #FF7A7F;')
        
        QTimer.singleShot(300, lambda: widget.setStyleSheet(original_style))
    
    def _process_key_operation(self, key_value):
        """处理按键操作的 modifiers 和 base_key 设置"""
        operation = {
            'modifiers': [],
            'base_key': key_value
        }
        
        # 检查是否为修饰键
        if key_value.lower() in MODIFIER_KEYS:
            # 修饰键
            pass  # 已设置默认值
        elif key_value.startswith('Key.'):
            # 特殊按键（如 Key.enter）
            pass  # 已设置默认值
        else:
            # 普通按键
            pass  # 已设置默认值
        
        return operation
    
    def on_add_operation(self):
        """添加操作"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QDialogButtonBox
        
        # 创建添加操作对话框
        dialog = QDialog(self)
        dialog.setWindowTitle('添加操作')
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        # 操作类型选择
        type_layout = QHBoxLayout()
        type_label = QLabel('操作类型:')
        self.operation_type_combo = QComboBox()
        self.operation_type_combo.addItems(['鼠标移动', '鼠标按下', '鼠标释放', '按键按下', '按键释放'])
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.operation_type_combo)
        layout.addLayout(type_layout)
        
        # 参数输入区域
        self.params_layout = QVBoxLayout()
        layout.addLayout(self.params_layout)
        
        # 时间戳输入
        timestamp_layout = QHBoxLayout()
        timestamp_label = QLabel('时间戳:')
        self.timestamp_input = QLineEdit()
        self.timestamp_input.setPlaceholderText('输入时间戳')
        timestamp_layout.addWidget(timestamp_label)
        timestamp_layout.addWidget(self.timestamp_input)
        layout.addLayout(timestamp_layout)
        
        # 动态生成参数输入字段
        def update_params():
            # 清空现有布局
            for i in reversed(range(self.params_layout.count())):
                item = self.params_layout.itemAt(i)
                if item.widget():
                    item.widget().deleteLater()
                elif item.layout():
                    # 递归清空子布局
                    sub_layout = item.layout()
                    for j in reversed(range(sub_layout.count())):
                        sub_item = sub_layout.itemAt(j)
                        if sub_item.widget():
                            sub_item.widget().deleteLater()
                    sub_layout.deleteLater()
            
            # 重置输入组件引用
            self.x_input = None
            self.y_input = None
            self.button_combo = None
            self.key_input = None
            
            operation_type = self.operation_type_combo.currentText()
            
            if operation_type in ['鼠标移动', '鼠标按下', '鼠标释放']:
                # 鼠标操作参数
                x_layout = QHBoxLayout()
                x_label = QLabel('X坐标:')
                self.x_input = QLineEdit()
                self.x_input.setPlaceholderText('输入X坐标')
                x_layout.addWidget(x_label)
                x_layout.addWidget(self.x_input)
                self.params_layout.addLayout(x_layout)
                
                y_layout = QHBoxLayout()
                y_label = QLabel('Y坐标:')
                self.y_input = QLineEdit()
                self.y_input.setPlaceholderText('输入Y坐标')
                y_layout.addWidget(y_label)
                y_layout.addWidget(self.y_input)
                self.params_layout.addLayout(y_layout)
                
                if operation_type in ['鼠标按下', '鼠标释放']:
                    # 鼠标按钮选择
                    button_layout = QHBoxLayout()
                    button_label = QLabel('鼠标按钮:')
                    self.button_combo = QComboBox()
                    self.button_combo.addItems(['左键', '右键', '中键'])
                    button_layout.addWidget(button_label)
                    button_layout.addWidget(self.button_combo)
                    self.params_layout.addLayout(button_layout)
            elif operation_type in ['按键按下', '按键释放']:
                # 键盘操作参数
                key_layout = QHBoxLayout()
                key_label = QLabel('按键:')
                self.key_input = QLineEdit()
                self.key_input.setPlaceholderText('输入按键名称')
                key_layout.addWidget(key_label)
                key_layout.addWidget(self.key_input)
                self.params_layout.addLayout(key_layout)
        
        # 初始更新参数输入字段
        update_params()
        # 连接类型变化信号
        self.operation_type_combo.currentTextChanged.connect(update_params)
        
        # 按钮盒
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        # 显示对话框
        if dialog.exec_() == QDialog.Accepted:
            import time
            
            # 获取操作类型
            operation_type = self.operation_type_combo.currentText()
            
            # 创建操作对象
            timestamp = float(self.timestamp_input.text()) if self.timestamp_input.text() else 0
            operation = {
                'timestamp': timestamp,
                'type': ''
            }
            
            # 根据操作类型设置参数
            if operation_type == '鼠标移动':
                operation['type'] = 'mousemove'
                operation['x'] = float(self.x_input.text()) if self.x_input.text() else 0
                operation['y'] = float(self.y_input.text()) if self.y_input.text() else 0
            elif operation_type == '鼠标按下':
                operation['type'] = 'mousedown'
                operation['x'] = float(self.x_input.text()) if self.x_input.text() else 0
                operation['y'] = float(self.y_input.text()) if self.y_input.text() else 0
                button_map = {'左键': 'left', '右键': 'right', '中键': 'middle'}
                operation['button'] = button_map.get(self.button_combo.currentText(), 'left')
            elif operation_type == '鼠标释放':
                operation['type'] = 'mouseup'
                operation['x'] = float(self.x_input.text()) if self.x_input.text() else 0
                operation['y'] = float(self.y_input.text()) if self.y_input.text() else 0
                button_map = {'左键': 'left', '右键': 'right', '中键': 'middle'}
                operation['button'] = button_map.get(self.button_combo.currentText(), 'left')
            elif operation_type == '按键按下':
                operation['type'] = 'keydown'
                key_value = self.key_input.text()
                operation['key'] = key_value
                # 使用辅助函数处理按键参数
                key_params = self._process_key_operation(key_value)
                operation.update(key_params)
            elif operation_type == '按键释放':
                operation['type'] = 'keyup'
                key_value = self.key_input.text()
                operation['key'] = key_value
                # 使用辅助函数处理按键参数
                key_params = self._process_key_operation(key_value)
                operation.update(key_params)
            
            # 添加到操作列表
            utils.recorded_operations.append(operation)
            
            # 更新操作列表
            self.update_operations_list()
            
            # 显示成功提示
            QMessageBox.information(self, '成功', '操作已添加')
    
    def on_edit_operation(self):
        """编辑操作"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QDialogButtonBox
        
        # 检查是否有选中的操作
        selected_items = self.operations_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, '错误', '请先选择要编辑的操作')
            return
        
        selected_item = selected_items[0]
        operation = selected_item.data(Qt.UserRole)
        operation_index = self.operations_list.row(selected_item)
        
        # 创建编辑操作对话框
        dialog = QDialog(self)
        dialog.setWindowTitle('编辑操作')
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        # 操作类型显示
        type_layout = QHBoxLayout()
        type_label = QLabel('操作类型:')
        type_value = QLabel()
        type_map = {
            'mousemove': '鼠标移动',
            'mousedown': '鼠标按下',
            'mouseup': '鼠标释放',
            'keydown': '按键按下',
            'keyup': '按键释放'
        }
        type_value.setText(type_map.get(operation['type'], '未知操作'))
        type_layout.addWidget(type_label)
        type_layout.addWidget(type_value)
        layout.addLayout(type_layout)
        
        # 参数输入区域
        params_layout = QVBoxLayout()
        layout.addLayout(params_layout)
        
        # 时间戳输入
        timestamp_layout = QHBoxLayout()
        timestamp_label = QLabel('时间戳:')
        timestamp_input = QLineEdit()
        timestamp_input.setText(str(operation.get('timestamp', 0)))
        timestamp_input.setPlaceholderText('输入时间戳')
        timestamp_layout.addWidget(timestamp_label)
        timestamp_layout.addWidget(timestamp_input)
        params_layout.addLayout(timestamp_layout)
        
        # 根据操作类型生成参数输入字段
        if operation['type'] in ['mousemove', 'mousedown', 'mouseup']:
            # 鼠标操作参数
            x_layout = QHBoxLayout()
            x_label = QLabel('X坐标:')
            x_input = QLineEdit()
            x_input.setText(str(operation.get('x', 0)))
            x_layout.addWidget(x_label)
            x_layout.addWidget(x_input)
            params_layout.addLayout(x_layout)
            
            y_layout = QHBoxLayout()
            y_label = QLabel('Y坐标:')
            y_input = QLineEdit()
            y_input.setText(str(operation.get('y', 0)))
            y_layout.addWidget(y_label)
            y_layout.addWidget(y_input)
            params_layout.addLayout(y_layout)
            
            if operation['type'] in ['mousedown', 'mouseup']:
                # 鼠标按钮选择
                button_layout = QHBoxLayout()
                button_label = QLabel('鼠标按钮:')
                button_combo = QComboBox()
                button_combo.addItems(['左键', '右键', '中键'])
                button_map = {'left': '左键', 'right': '右键', 'middle': '中键'}
                current_button = button_map.get(operation.get('button', 'left'), '左键')
                button_combo.setCurrentText(current_button)
                button_layout.addWidget(button_label)
                button_layout.addWidget(button_combo)
                params_layout.addLayout(button_layout)
        elif operation['type'] in ['keydown', 'keyup']:
            # 键盘操作参数
            key_layout = QHBoxLayout()
            key_label = QLabel('按键:')
            key_input = QLineEdit()
            key_input.setText(operation.get('key', ''))
            key_layout.addWidget(key_label)
            key_layout.addWidget(key_input)
            params_layout.addLayout(key_layout)
        
        # 按钮盒
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        # 显示对话框
        if dialog.exec_() == QDialog.Accepted:
            # 更新时间戳
            operation['timestamp'] = float(timestamp_input.text()) if timestamp_input.text() else 0
            
            # 更新操作参数
            if operation['type'] in ['mousemove', 'mousedown', 'mouseup']:
                operation['x'] = float(x_input.text()) if x_input.text() else 0
                operation['y'] = float(y_input.text()) if y_input.text() else 0
                if operation['type'] in ['mousedown', 'mouseup']:
                    button_map_reverse = {'左键': 'left', '右键': 'right', '中键': 'middle'}
                    operation['button'] = button_map_reverse.get(button_combo.currentText(), 'left')
            elif operation['type'] in ['keydown', 'keyup']:
                key_value = key_input.text()
                operation['key'] = key_value
                # 使用辅助函数处理按键参数
                key_params = self._process_key_operation(key_value)
                operation.update(key_params)
            
            # 更新操作列表
            utils.recorded_operations[operation_index] = operation
            self.update_operations_list()
            
            # 显示成功提示
            QMessageBox.information(self, '成功', '操作已更新')
    
    def on_copy_operation(self):
        """复制操作"""
        import copy
        import time
        
        # 检查是否有选中的操作
        selected_items = self.operations_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, '错误', '请先选择要复制的操作')
            return
        
        # 获取选中操作的索引并排序
        selected_indices = [self.operations_list.row(item) for item in selected_items]
        selected_indices.sort()
        
        # 复制选中的操作
        copied_operations = []
        for index in selected_indices:
            operation = utils.recorded_operations[index]
            # 深拷贝操作对象
            copied_operation = copy.deepcopy(operation)
            # 更新时间戳
            copied_operation['timestamp'] = time.time() - utils.start_time if hasattr(utils, 'start_time') else 0
            copied_operations.append(copied_operation)
        
        # 将复制的操作添加到操作列表末尾
        for operation in copied_operations:
            utils.recorded_operations.append(operation)
        
        # 更新操作列表
        self.update_operations_list()
        
        # 显示成功提示
        QMessageBox.information(self, '成功', f'已复制 {len(copied_operations)} 个操作')
    
    def on_delete_operation(self):
        """删除操作"""
        # 检查是否有选中的操作
        selected_items = self.operations_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, '错误', '请先选择要删除的操作')
            return
        
        # 获取选中操作的索引并排序（从后往前删除）
        selected_indices = [self.operations_list.row(item) for item in selected_items]
        selected_indices.sort(reverse=True)
        
        # 显示确认对话框
        if QMessageBox.question(self, '确认', f'确定要删除选中的 {len(selected_items)} 个操作吗？', 
                               QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            # 从操作列表中移除（从后往前删除避免索引变化）
            for index in selected_indices:
                del utils.recorded_operations[index]
            
            # 更新操作列表
            self.update_operations_list()
            
            # 显示成功提示
            QMessageBox.information(self, '成功', f'已删除 {len(selected_items)} 个操作')
