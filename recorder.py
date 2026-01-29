# 导入时间模块，用于计算时间戳
import time
# 从 pynput 库导入键盘和鼠标监听器
from pynput import keyboard, mouse
# 导入工具模块，用于访问全局变量
import utils

# 鼠标事件处理
# 功能：处理鼠标移动事件
def on_move(x, y):
    """处理鼠标移动事件"""
    # 检查是否正在录制
    if utils.is_recording:
        # 计算相对时间戳（从录制开始到现在的时间差）
        timestamp = time.time() - utils.recording_start_time
        # 将鼠标移动操作添加到操作序列
        utils.recorded_operations.append({
            'type': 'mousemove',      # 操作类型：鼠标移动
            'x': x,                   # 鼠标X坐标
            'y': y,                   # 鼠标Y坐标
            'timestamp': timestamp     # 时间戳
        })


def on_click(x, y, button, pressed):
    """处理鼠标点击事件"""
    # 检查是否正在录制
    if utils.is_recording:
        # 计算相对时间戳
        timestamp = time.time() - utils.recording_start_time
        # 根据 pressed 参数判断是按下还是释放
        if pressed:
            # 鼠标按下操作
            utils.recorded_operations.append({
                'type': 'mousedown',    # 操作类型：鼠标按下
                'x': x,                 # 鼠标X坐标
                'y': y,                 # 鼠标Y坐标
                'button': str(button),  # 按钮类型（左键/右键）
                'timestamp': timestamp   # 时间戳
            })
        else:
            # 鼠标释放操作
            utils.recorded_operations.append({
                'type': 'mouseup',      # 操作类型：鼠标释放
                'x': x,                 # 鼠标X坐标
                'y': y,                 # 鼠标Y坐标
                'button': str(button),  # 按钮类型（左键/右键）
                'timestamp': timestamp   # 时间戳
            })

# 键盘事件处理
# 功能：处理键盘按下事件
def on_press(key):
    """处理键盘按下事件"""
    # 首先检查是否需要停止录制
    # 检查Esc键
    if key == keyboard.Key.esc:
        # 按下Esc键，停止录制
        stop_recording()
        return
    
    # 检查是否正在录制
    if utils.is_recording:
        # 计算相对时间戳
        timestamp = time.time() - utils.recording_start_time
        
        # 处理修饰键（只更新状态，不记录为单独的按键操作）
        if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
            # 左Ctrl或右Ctrl键按下
            utils.modifier_keys['ctrl'] = True
            return  # 直接返回，不记录为单独操作
        elif key == keyboard.Key.shift_l or key == keyboard.Key.shift_r:
            # 左Shift或右Shift键按下
            utils.modifier_keys['shift'] = True
            return
        elif key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
            # 左Alt或右Alt键按下
            utils.modifier_keys['alt'] = True
            return
        elif key == keyboard.Key.cmd_l or key == keyboard.Key.cmd_r:
            # 左Win或右Win键按下
            utils.modifier_keys['win'] = True
            return
        
        # 检测当前按下的修饰键
        modifiers = []
        if utils.modifier_keys['ctrl']:
            modifiers.append('ctrl')
        if utils.modifier_keys['shift']:
            modifiers.append('shift')
        if utils.modifier_keys['alt']:
            modifiers.append('alt')
        if utils.modifier_keys['win']:
            modifiers.append('win')
        
        # 获取按键字符
        try:
            # 尝试获取普通字符键
            key_char = key.char
            # 处理控制字符（当有修饰键时）
            if modifiers and key_char and ord(key_char) < 32:
                # 如果是控制字符，转换为对应的字母（如 \x17 转换为 'w'）
                key_char = chr(ord('a') + ord(key_char) - 1)
        except AttributeError:
            # 对于特殊键（如方向键、功能键等），使用字符串表示
            key_char = str(key)
        
        # 构建组合键字符串
        if modifiers:
            # 如果有修饰键，构建形如 "ctrl+shift+c" 的字符串
            key_string = '+' .join(modifiers) + '+' + key_char
        else:
            # 如果没有修饰键，直接使用键字符
            key_string = key_char
        
        # 记录按键按下操作
        utils.recorded_operations.append({
            'type': 'keydown',        # 操作类型：按键按下
            'key': key_string,        # 完整的键字符串（包含修饰键）
            'modifiers': modifiers,    # 修饰键列表
            'base_key': key_char,      # 基础键（不包含修饰键）
            'timestamp': timestamp      # 时间戳
        })


def on_release(key):
    """处理键盘释放事件"""
    # 处理修饰键释放
    if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
        # 左Ctrl或右Ctrl键释放
        utils.modifier_keys['ctrl'] = False
        return  # 直接返回，不记录为单独操作
    elif key == keyboard.Key.shift_l or key == keyboard.Key.shift_r:
        # 左Shift或右Shift键释放
        utils.modifier_keys['shift'] = False
        return
    elif key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
        # 左Alt或右Alt键释放
        utils.modifier_keys['alt'] = False
        return
    elif key == keyboard.Key.cmd_l or key == keyboard.Key.cmd_r:
        # 左Win或右Win键释放
        utils.modifier_keys['win'] = False
        return
    
    # 检查是否正在录制
    if utils.is_recording:
        # 计算相对时间戳
        timestamp = time.time() - utils.recording_start_time
        
        # 检测当前仍按下的修饰键
        modifiers = []
        if utils.modifier_keys['ctrl']:
            modifiers.append('ctrl')
        if utils.modifier_keys['shift']:
            modifiers.append('shift')
        if utils.modifier_keys['alt']:
            modifiers.append('alt')
        if utils.modifier_keys['win']:
            modifiers.append('win')
        
        # 获取按键字符
        try:
            # 尝试获取普通字符键
            key_char = key.char
        except AttributeError:
            # 对于特殊键，使用字符串表示
            key_char = str(key)
        
        # 构建组合键字符串
        if modifiers:
            # 如果有修饰键，构建形如 "ctrl+shift+c" 的字符串
            key_string = '+' .join(modifiers) + '+' + key_char
        else:
            # 如果没有修饰键，直接使用键字符
            key_string = key_char
        
        # 记录按键释放操作
        utils.recorded_operations.append({
            'type': 'keyup',          # 操作类型：按键释放
            'key': key_string,        # 完整的键字符串（包含修饰键）
            'modifiers': modifiers,    # 修饰键列表
            'base_key': key_char,      # 基础键（不包含修饰键）
            'timestamp': timestamp      # 时间戳
        })

# 录制函数
# 功能：开始录制操作序列
def start_recording():
    """开始录制操作序列"""
    # 设置录制状态为 True
    utils.is_recording = True
    # 清空之前的操作序列
    utils.recorded_operations = []
    # 记录录制开始时间
    utils.recording_start_time = time.time()
    
    # 启动鼠标监听器
    # 创建鼠标监听器，绑定移动和点击事件处理函数
    mouse_listener = mouse.Listener(
        on_move=on_move,      # 鼠标移动事件处理
        on_click=on_click      # 鼠标点击事件处理
    )
    # 设置为守护线程，主程序退出时自动退出
    mouse_listener.daemon = True
    # 启动鼠标监听器
    mouse_listener.start()
    
    # 启动键盘监听器
    # 创建键盘监听器，绑定按下和释放事件处理函数
    keyboard_listener = keyboard.Listener(
        on_press=on_press,     # 键盘按下事件处理
        on_release=on_release  # 键盘释放事件处理
    )
    # 设置为守护线程
    keyboard_listener.daemon = True
    # 启动键盘监听器
    keyboard_listener.start()
    
    # 等待录制结束
    # 循环检查录制状态，直到录制被停止
    while utils.is_recording:
        # 短暂休眠，减少CPU占用，同时保持响应速度
        time.sleep(0.01)  # 10毫秒
    
    # 确保监听器停止
    try:
        # 停止鼠标监听器
        mouse_listener.stop()
        # 停止键盘监听器
        keyboard_listener.stop()
    except:
        # 捕获可能的异常，确保程序不会崩溃
        pass

# 停止录制函数
# 功能：停止录制操作序列
def stop_recording():
    """停止录制操作序列"""
    # 立即设置录制状态为 False
    utils.is_recording = False
    # 确保修饰键状态被重置
    # 防止修饰键状态残留影响后续操作
    utils.modifier_keys = {
        'ctrl': False,   # 重置Ctrl键状态
        'shift': False,  # 重置Shift键状态
        'alt': False,    # 重置Alt键状态
        'win': False     # 重置Win键状态
    }
    # 发送录制停止信号
    utils.recording_signals.stopped.emit()
    

