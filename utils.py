import sys
import os
import logging
from PyQt5.QtCore import QObject, pyqtSignal
import pyautogui

# 配置日志
logs_dir = "logs"
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# 日志格式
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'

# 创建日志记录器
logger = logging.getLogger('desktop_automation')
logger.setLevel(logging.DEBUG)

# 文件处理器
file_handler = logging.FileHandler(os.path.join(logs_dir, 'automation.log'), encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(log_format))

# 控制台处理器（可选，保留以便在开发时查看）
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(log_format))

# 添加处理器到记录器
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

# 全局变量
# 全局录制/播放控制标志
is_recording = False          # 是否正在录制操作
is_playing = False            # 是否正在播放操作
recorded_operations = []      # 存储录制到的操作序列
recording_thread = None       # 录制线程对象
playback_thread = None        # 播放线程对象
recording_start_time = 0      # 录制开始时间（用于计算相对时间戳）
is_looping = False            # 是否启用循环播放
loop_count = 0                # 当前循环次数
current_sequence = ""         # 当前选中的序列名称
sequences = {}                # 已加载的序列字典，键为序列名，值为操作列表
sequences_dir = "sequences"   # 存放序列文件的目录名
playback_speed = 1.0          # 默认播放速度（倍率，1.0 为正常速度）

# 修饰键状态跟踪
modifier_keys = {
    'ctrl': False,
    'shift': False,
    'alt': False,
    'win': False
}

# 配置
pyautogui.FAILSAFE = True  # 启用安全模式，移动鼠标到左上角可停止操作
pyautogui.PAUSE = 0.01  # 操作之间的暂停时间

# 循环次数配置
max_loop_count = 1  # 默认循环1次

# 信号类
class PlaybackSignals(QObject):
    completed = pyqtSignal()

class RecordingSignals(QObject):
    stopped = pyqtSignal()

# 信号实例
playback_signals = PlaybackSignals()
recording_signals = RecordingSignals()

# 确保序列目录存在
def ensure_sequences_dir():
    if not os.path.exists(sequences_dir):
        os.makedirs(sequences_dir)

# 初始化函数
def init_utils():
    ensure_sequences_dir()
    logger.info("应用程序启动，日志系统初始化完成")
