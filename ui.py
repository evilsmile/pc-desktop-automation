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
    QFormLayout,       # 表单布局
    QStatusBar,        # 状态栏
    QMessageBox,       # 消息框
    QSplitter          # 分隔器
)

# 从 PyQt5 导入核心功能
from PyQt5.QtCore import (
    Qt,                # Qt 核心常量
    QTimer,            # 定时器
    pyqtSignal,        # 信号
    QObject            # 对象基类
)

# 从 PyQt5 导入 GUI 功能
from PyQt5.QtGui import (
    QIcon,             # 图标
    QFont              # 字体
)

# 导入工具模块
import utils

# 从录制模块导入函数
from recorder import start_recording, stop_recording

# 从播放模块导入函数
from player import play_operations, stop_playback

# 从序列管理模块导入函数
from sequence import save_sequence, load_sequence, delete_sequence, load_all_sequences

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
    
    def initUI(self):
        """初始化用户界面"""
        # 设置窗口标题和大小
        # 标题：Windows桌面自动化工具
        # 位置：屏幕左上角(100, 100)像素
        # 大小：1000x750像素
        self.setWindowTitle('Windows桌面自动化工具')
        self.setGeometry(100, 100, 1000, 750)
        
        # 设置深色主题样式
        # 使用CSS风格的样式表定义界面元素的外观
        self.setStyleSheet('''
            /* 主窗口样式 */
            QMainWindow {
                background-color: #1e1e1e; /* 深色背景 */
                color: #d4d4d4;           /* 浅灰色文本 */
            }
            
            /* 通用部件样式 */
            QWidget {
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
            
            /* 分组框样式 */
            QGroupBox {
                background-color: #252526; /* 稍亮的背景 */
                color: #d4d4d4;
                border: 1px solid #3e3e42; /* 边框 */
                border-radius: 4px;        /* 圆角 */
                margin-top: 10px;          /* 顶部边距 */
            }
            
            /* 分组框标题样式 */
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                top: 0px;
                padding: 0 5px 0 5px;
                background-color: #252526;
                color: #d4d4d4;
            }
            
            /* 按钮样式 */
            QPushButton {
                background-color: #0e639c; /* 蓝色背景 */
                color: white;
                border: none;
                border-radius: 3px;
                padding: 6px 12px;
                font-weight: 500;
            }
            
            /* 按钮悬停效果 */
            QPushButton:hover {
                background-color: #1177bb; /* 亮蓝色 */
            }
            
            /* 禁用按钮样式 */
            QPushButton:disabled {
                background-color: #808080; /* 灰色背景 */
                color: #ffffff;            /* 白色字体 */
                border: 1px solid #555;
                opacity: 0.6;
            }
            
            /* 停止按钮样式 */
            QPushButton#stop_record_btn, QPushButton#stop_play_btn {
                background-color: #d13438; /* 红色背景 */
            }
            
            /* 停止按钮悬停效果 */
            QPushButton#stop_record_btn:hover, QPushButton#stop_play_btn:hover {
                background-color: #e54b4f; /* 亮红色 */
            }
            
            /* 标签样式 */
            QLabel {
                color: #d4d4d4;
            }
            
            /* 列表控件样式 */
            QListWidget {
                background-color: #252526;
                color: #d4d4d4;
                border: 1px solid #3e3e42;
                border-radius: 3px;
            }
            
            /* 列表项样式 */
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #3e3e42;
            }
            
            /* 列表项悬停效果 */
            QListWidget::item:hover {
                background-color: #2a2d2e;
            }
            
            /* 文本编辑框样式 */
            QTextEdit {
                background-color: #252526;
                color: #d4d4d4;
                border: 1px solid #3e3e42;
                border-radius: 3px;
            }
            
            /* 单行输入框样式 */
            QLineEdit {
                background-color: #252526;
                color: #d4d4d4;
                border: 1px solid #3e3e42;
                border-radius: 3px;
                padding: 5px;
            }
            
            /* 下拉选择框样式 */
            QComboBox {
                background-color: #252526;
                color: #d4d4d4;
                border: 1px solid #3e3e42;
                border-radius: 3px;
                padding: 5px;
            }
            
            /* 下拉箭头样式 */
            QComboBox::drop-down {
                border-left: 1px solid #3e3e42;
            }
            
            /* 下拉箭头图标 */
            QComboBox::down-arrow {
                image: url(:/icons/down_arrow.png);
                width: 12px;
                height: 12px;
            }
            
            /* 复选框样式 */
            QCheckBox {
                color: #d4d4d4;
            }
            
            /* 状态栏样式 */
            QStatusBar {
                background-color: #252526;
                color: #d4d4d4;
                border-top: 1px solid #3e3e42;
            }
        ''')
        
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
        
        # 录制状态标签
        self.recording_status = QLabel('未录制')
        # 播放状态标签
        self.playback_status = QLabel('未播放')
        # 循环状态标签
        self.loop_status = QLabel('未循环')
        
        # 添加状态标签到状态栏布局
        status_bar.addWidget(self.recording_status)
        status_bar.addWidget(QLabel(' | '))  # 分隔符
        status_bar.addWidget(self.playback_status)
        status_bar.addWidget(QLabel(' | '))  # 分隔符
        status_bar.addWidget(self.loop_status)
        status_bar.addStretch()  # 弹簧，将内容推到左侧
        
        # 将状态栏添加到主布局
        main_layout.addLayout(status_bar)
        
        # 创建主内容区域
        # 使用水平布局管理器，将界面分为左右两部分
        content_layout = QHBoxLayout()
        
        # 左侧控制面板
        # 包含录制控制、播放控制、系统状态和序列管理
        left_panel = QVBoxLayout()
        
        # 录制控制分组
        record_group = QGroupBox('录制控制')
        record_layout = QVBoxLayout()
        
        # 录制按钮布局
        record_buttons = QHBoxLayout()
        # 开始录制按钮
        self.start_record_btn = QPushButton('开始录制')
        # 停止录制按钮
        self.stop_record_btn = QPushButton('停止录制')
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
        record_layout.addWidget(QLabel('提示：按esc可停止录制'))
        
        # 设置录制控制分组的布局
        record_group.setLayout(record_layout)
        # 添加到左侧面板
        left_panel.addWidget(record_group)
        
        # 播放控制分组
        play_group = QGroupBox('播放控制')
        play_layout = QVBoxLayout()
        
        # 播放按钮布局
        play_buttons = QHBoxLayout()
        # 播放按钮
        self.play_btn = QPushButton('播放')
        # 停止按钮
        self.stop_play_btn = QPushButton('停止')
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
        
        # 循环设置布局
        loop_layout = QHBoxLayout()
        # 自动循环复选框
        self.loop_checkbox = QCheckBox('自动循环')
        # 循环次数标签
        self.loop_count_label = QLabel('循环次数：0')
        
        # 连接复选框状态变化信号
        self.loop_checkbox.stateChanged.connect(self.on_loop_changed)
        
        # 添加到循环布局
        loop_layout.addWidget(self.loop_checkbox)
        loop_layout.addStretch()
        loop_layout.addWidget(self.loop_count_label)
        
        # 循环次数配置布局
        loop_config_layout = QHBoxLayout()
        # 循环次数输入框
        self.loop_count_input = QLineEdit()
        self.loop_count_input.setPlaceholderText('循环次数')
        self.loop_count_input.setText('1')  # 默认值
        self.loop_count_input.setFixedWidth(80)  # 固定宽度
        
        # 连接输入框文本变化信号
        self.loop_count_input.textChanged.connect(self.on_loop_count_changed)
        
        # 添加到循环配置布局
        loop_config_layout.addWidget(QLabel('循环配置：'))
        loop_config_layout.addWidget(self.loop_count_input)
        loop_config_layout.addStretch()
        
        # 播放速度配置布局
        speed_layout = QHBoxLayout()
        # 播放速度下拉框
        self.speed_combo = QComboBox()
        # 添加速度选项，第一个参数是显示文本，第二个是对应的数据值
        self.speed_combo.addItem('1.0倍速', 1.0)
        self.speed_combo.addItem('1.5倍速', 1.5)
        self.speed_combo.addItem('2.0倍速', 2.0)
        self.speed_combo.addItem('3.0倍速', 3.0)
        self.speed_combo.addItem('5.0倍速', 5.0)
        self.speed_combo.addItem('10.0倍速', 10.0)
        self.speed_combo.addItem('20.0倍速', 20.0)
        self.speed_combo.setFixedWidth(140)  # 固定宽度
        
        # 添加到速度布局
        speed_layout.addWidget(QLabel('播放速度：'))
        speed_layout.addWidget(self.speed_combo)
        speed_layout.addStretch()
        
        # 将所有布局添加到播放控制布局
        play_layout.addLayout(play_buttons)
        play_layout.addLayout(loop_layout)
        play_layout.addLayout(loop_config_layout)
        play_layout.addLayout(speed_layout)
        
        # 设置播放控制分组的布局
        play_group.setLayout(play_layout)
        # 添加到左侧面板
        left_panel.addWidget(play_group)
        
        # 系统状态分组
        system_group = QGroupBox('系统状态')
        system_layout = QVBoxLayout()
        # 添加系统状态信息
        system_layout.addWidget(QLabel('Python 已检测到'))
        system_layout.addWidget(QLabel('使用PyAutoGUI控制实际Windows桌面'))
        # 设置系统状态分组的布局
        system_group.setLayout(system_layout)
        # 添加到左侧面板
        left_panel.addWidget(system_group)
        
        # 序列管理分组
        sequence_group = QGroupBox('序列管理')
        sequence_layout = QVBoxLayout()
        
        # 保存序列布局
        save_layout = QHBoxLayout()
        # 序列名称输入框
        self.sequence_name = QLineEdit()
        self.sequence_name.setPlaceholderText('输入序列名称')
        # 保存按钮
        self.save_btn = QPushButton('保存')
        
        # 连接保存按钮点击信号
        self.save_btn.clicked.connect(self.on_save_sequence)
        
        # 添加到保存布局
        save_layout.addWidget(self.sequence_name)
        save_layout.addWidget(self.save_btn)
        
        # 加载序列布局
        load_layout = QHBoxLayout()
        # 加载序列下拉框
        self.load_combo = QComboBox()
        self.load_combo.addItem('选择序列')
        # 加载按钮
        self.load_btn = QPushButton('加载')
        
        # 连接加载按钮点击信号
        self.load_btn.clicked.connect(self.on_load_sequence)
        
        # 添加到加载布局
        load_layout.addWidget(self.load_combo)
        load_layout.addWidget(self.load_btn)
        
        # 删除序列布局
        delete_layout = QHBoxLayout()
        # 删除序列下拉框
        self.delete_combo = QComboBox()
        self.delete_combo.addItem('选择序列')
        # 删除按钮
        self.delete_btn = QPushButton('删除')
        
        # 连接删除按钮点击信号
        self.delete_btn.clicked.connect(self.on_delete_sequence)
        
        # 添加到删除布局
        delete_layout.addWidget(self.delete_combo)
        delete_layout.addWidget(self.delete_btn)
        
        # 当前序列标签
        self.current_sequence_label = QLabel('当前序列：无')
        
        # 将所有布局和标签添加到序列管理布局
        sequence_layout.addLayout(save_layout)
        sequence_layout.addLayout(load_layout)
        sequence_layout.addLayout(delete_layout)
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
        
        # 操作序列分组
        operations_group = QGroupBox('操作序列')
        operations_layout = QVBoxLayout()
        
        # 操作列表控件
        self.operations_list = QListWidget()
        self.operations_list.setMinimumHeight(300)  # 设置最小高度
        # 清空操作按钮
        self.clear_btn = QPushButton('清空操作')
        
        # 连接清空按钮点击信号
        self.clear_btn.clicked.connect(self.on_clear_operations)
        
        # 添加到操作序列布局
        operations_layout.addWidget(self.operations_list)
        operations_layout.addWidget(self.clear_btn)
        
        # 设置操作序列分组的布局
        operations_group.setLayout(operations_layout)
        # 添加到右侧面板
        right_panel.addWidget(operations_group)
        
        # 操作详情分组
        detail_group = QGroupBox('操作详情')
        detail_layout = QVBoxLayout()
        
        # 操作详情文本框
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)  # 设置为只读
        self.detail_text.setMinimumHeight(200)  # 设置最小高度
        
        # 添加到操作详情布局
        detail_layout.addWidget(self.detail_text)
        # 设置操作详情分组的布局
        detail_group.setLayout(detail_layout)
        # 添加到右侧面板
        right_panel.addWidget(detail_group)
        
        # 将左侧和右侧面板添加到主内容布局
        # 左侧面板占1份，右侧面板占2份
        content_layout.addLayout(left_panel, 1)
        content_layout.addLayout(right_panel, 2)
        
        # 将主内容布局添加到主布局
        main_layout.addLayout(content_layout)
        
        # 设置窗口最小大小
        # 确保窗口在调整大小时不会变得太小
        self.setMinimumSize(800, 600)
        
        # 加载序列列表
        # 启动时从文件加载已保存的序列
        try:
            self.load_sequences_list()
        except Exception as e:
            # 捕获并打印加载错误
            utils.logger.error(f"加载序列列表时出错: {e}")
    
    def on_start_record(self):
        """开始录制操作"""
        # 声明全局录制线程变量
        global recording_thread
        
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
        # 声明全局播放线程变量
        global playback_thread
        
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
        self.recording_status.setText(f'录制: {"正在录制" if utils.is_recording else "未录制"}')
        # 更新播放状态
        self.playback_status.setText(f'播放: {"正在播放" if utils.is_playing else "未播放"}')
        # 更新循环状态
        self.loop_status.setText(f'循环: {"开启" if utils.is_looping else "关闭"}')
        # 更新循环次数
        self.loop_count_label.setText(f'循环次数：{utils.loop_count}')
        # 更新当前序列信息
        self.current_sequence_label.setText(f'当前序列：{utils.current_sequence or "无"}')
        
        # 更新按钮状态
        if utils.is_recording:
            # 正在录制时
            self.start_record_btn.setEnabled(False)  # 禁用开始录制按钮
            self.stop_record_btn.setEnabled(True)    # 启用停止录制按钮
            self.play_btn.setEnabled(False)          # 禁用播放按钮
        else:
            # 未录制时
            self.start_record_btn.setEnabled(True)   # 启用开始录制按钮
            self.stop_record_btn.setEnabled(False)   # 禁用停止录制按钮
            # 只有当不在播放且有操作记录时才启用播放按钮
            self.play_btn.setEnabled(not utils.is_playing and len(utils.recorded_operations) > 0)
        
        if utils.is_playing:
            # 正在播放时
            self.play_btn.setEnabled(False)           # 禁用播放按钮
            self.stop_play_btn.setEnabled(True)       # 启用停止按钮
            self.start_record_btn.setEnabled(False)   # 禁用开始录制按钮
        else:
            # 未播放时
            # 只有当有操作记录时才启用播放按钮
            self.play_btn.setEnabled(len(utils.recorded_operations) > 0)
            self.stop_play_btn.setEnabled(False)     # 禁用停止按钮
            self.start_record_btn.setEnabled(True)   # 启用开始录制按钮
