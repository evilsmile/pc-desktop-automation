# 导入时间模块，用于处理延迟
import time
# 导入 pyautogui 模块，用于执行鼠标和键盘操作
import pyautogui
# 从 pynput 库导入键盘监听器
from pynput import keyboard
# 导入工具模块，用于访问全局变量和信号
import utils

# 键盘事件处理函数
# 功能：处理播放时的键盘事件，按esc键停止播放
def on_play_press(key):
    """处理播放时的键盘按下事件"""
    # 检查是否按下了Esc键
    if key == keyboard.Key.esc:
        # 按下Esc键，停止播放
        stop_playback()
        # 弹出提示框：播放已停止
        #pyautogui.alert(text='播放已停止', title='提示', button='确定')
        return

# 播放操作
# 功能：执行录制的操作序列
def play_operations():
    """执行录制的操作序列"""
    # 设置播放状态为 True
    utils.is_playing = True
    # 初始化当前循环次数为 0
    current_loop = 0
    
    # 启动键盘监听器
    keyboard_listener = keyboard.Listener(
        on_press=on_play_press  # 键盘按下事件处理
    )
    # 设置为守护线程
    keyboard_listener.daemon = True
    # 启动键盘监听器
    keyboard_listener.start()
    
    # 异常处理块，确保即使出现错误也能正确清理状态
    try:
        # 主循环：控制播放过程
        # 循环条件：
        # 1. utils.is_playing 为 True（未被停止）
        # 2. 未开启循环时：current_loop < 1（只播放一遍）
        # 3. 开启循环时：current_loop < utils.max_loop_count（按设置的次数循环）
        while utils.is_playing and ((utils.is_looping == False and current_loop < 1) or (utils.is_looping and current_loop < utils.max_loop_count)):
            # 遍历操作序列中的每个操作
            for i, op in enumerate(utils.recorded_operations):
                # 检查是否应该停止播放
                if not utils.is_playing:
                    # 如果播放被停止，跳出循环
                    break
                
                # 计算延迟时间（从第二个操作开始）
                if i > 0:
                    # 获取前一个操作
                    prev_op = utils.recorded_operations[i-1]
                    # 计算两个操作之间的时间差
                    delay = op['timestamp'] - prev_op['timestamp']
                    # 如果时间差大于0（有延迟）
                    if delay > 0:
                        # 根据播放速度调整延迟时间
                        # 播放速度 > 1.0 时，延迟减少（播放加速），播放速度 < 1.0 时，延迟增加（播放减速）
                        adjusted_delay = delay / utils.playback_speed
                        # 执行延迟
                        time.sleep(adjusted_delay)
                        # 打印延迟信息
                        utils.logger.info(f"原始延迟: {delay:.3f}秒, 调整后: {adjusted_delay:.3f}秒, 速度: {utils.playback_speed}倍")


                # 执行操作
                try:
                    # 根据操作类型执行相应的操作
                    
                    # 将鼠标移动到指定坐标 (op['x'], op['y'])
                    if op['type'] == 'mousemove':
                        pyautogui.moveTo(op['x'], op['y'])
                    
                    elif op['type'] == 'mousedown':
                        # 鼠标按下操作
                        if 'left' in op['button']:
                            # 左键按下
                            pyautogui.mouseDown(x=op['x'], y=op['y'], button='left')
                        elif 'right' in op['button']:
                            # 右键按下
                            pyautogui.mouseDown(x=op['x'], y=op['y'], button='right')
                    
                    elif op['type'] == 'mouseup':
                        # 鼠标释放操作
                        if 'left' in op['button']:
                            # 左键释放
                            pyautogui.mouseUp(x=op['x'], y=op['y'], button='left')
                        elif 'right' in op['button']:
                            # 右键释放
                            pyautogui.mouseUp(x=op['x'], y=op['y'], button='right')
                    
                    elif op['type'] == 'keydown':
                        # 键盘按键按下操作
                        try:
                            # 处理基础键格式：将'Key.tab'转换为'tab'等pyautogui可识别的格式
                            base_key = op['base_key']
                            if base_key.startswith('Key.'):
                                # 移除'Key.'前缀，提取实际键名
                                base_key = base_key[4:]  # 'Key.tab' -> 'tab'
                            
                            # 处理特殊映射：如'page_up' -> 'pageup'
                            key_mappings = {
                                'page_up': 'pageup',
                                'page_down': 'pagedown'
                            }
                            if base_key in key_mappings:
                                base_key = key_mappings[base_key]
                            
                            # 按下所有修饰键
                            for mod in op.get('modifiers', []):
                                # 将修饰键统一转换为pyautogui可识别的格式
                                press_mod = mod
                                if press_mod in ['win', 'cmd']:
                                    press_mod = 'win'
                                utils.logger.info(f"按下修饰键: {press_mod}")
                                pyautogui.keyDown(press_mod)
                                time.sleep(0.05)  # 短暂延时确保键被按下
                            
                            # 按下基础键
                            utils.logger.info(f"按下基础键: {base_key}")
                            pyautogui.keyDown(base_key)
                            time.sleep(0.05)  # 短暂延时确保键被按下
                            
                            utils.logger.info(f"按键按下成功: {op['key']}")
                        except Exception as e:
                            # 捕获按键执行异常
                            utils.logger.error(f"按键按下失败: {e}")
                    elif op['type'] == 'keyup':
                        # 键盘按键释放操作
                        try:
                            # 处理基础键格式：将'Key.tab'转换为'tab'等pyautogui可识别的格式
                            base_key = op['base_key']
                            if base_key.startswith('Key.'):
                                # 移除'Key.'前缀，提取实际键名
                                base_key = base_key[4:]  # 'Key.tab' -> 'tab'
                            
                            # 处理特殊映射：如'page_up' -> 'pageup'
                            key_mappings = {
                                'page_up': 'pageup',
                                'page_down': 'pagedown'
                            }
                            if base_key in key_mappings:
                                base_key = key_mappings[base_key]
                            
                            # 释放基础键
                            utils.logger.info(f"释放基础键: {base_key}")
                            pyautogui.keyUp(base_key)
                            time.sleep(0.05)  # 短暂延时确保键被释放
                            
                            # 释放所有修饰键（按反向顺序）
                            for mod in reversed(op.get('modifiers', [])):
                                # 将修饰键统一转换为pyautogui可识别的格式
                                press_mod = mod
                                if press_mod in ['win', 'cmd']:
                                    press_mod = 'win'
                                utils.logger.info(f"释放修饰键: {press_mod}")
                                pyautogui.keyUp(press_mod)
                                time.sleep(0.05)  # 短暂延时确保键被释放
                            
                            utils.logger.info(f"按键释放成功: {op['key']}")
                        except Exception as e:
                            # 捕获按键执行异常
                            utils.logger.error(f"按键释放失败: {e}")
                except pyautogui.FailSafeException:
                    # 捕获安全机制异常
                    # 当用户将鼠标移动到屏幕角落时，pyautogui 会触发 FailSafeException
                    # 这是一个安全机制，允许用户在紧急情况下停止自动化操作
                    utils.logger.warning("检测到安全机制触发")
                    # 设置播放状态为 False，停止播放
                    utils.is_playing = False
                    
                    # 跳出当前循环
                    break
                except Exception as e:
                    # 捕获其他异常
                    # 处理执行操作时可能出现的其他错误
                    utils.logger.error(f"执行操作时出错: {e}")
                    # 继续执行下一个操作，不中断整个播放过程
                    continue
            
            # 增加循环计数
            # 更新全局循环计数（用于UI显示）
            utils.loop_count += 1
            # 更新当前函数内的循环计数（用于控制循环条件）
            current_loop += 1
            
    
    finally:
        # 停止键盘监听器
        try:
            keyboard_listener.stop()
        except:
            pass
        
        utils.logger.info(f"播放结束")
        # 无论播放是否正常完成，都会执行的清理工作
        # 设置播放状态为 False，确保播放已停止
        utils.is_playing = False
        # 播放完成，发送信号给UI，通知其恢复窗口
        # 这会触发 ui.py 中的 on_playback_completed 方法
        utils.playback_signals.completed.emit()

# 停止播放
# 功能：停止正在进行的播放操作
def stop_playback():
    """停止正在进行的播放操作"""
    # 设置播放状态为 False
    # 这会导致 play_operations 函数中的循环条件不满足，从而停止播放
    utils.is_playing = False
