# 导入时间模块，用于处理延迟
import time
# 导入 pyautogui 模块，用于执行鼠标和键盘操作
import pyautogui
# 导入工具模块，用于访问全局变量和信号
import utils

# 播放操作
# 功能：执行录制的操作序列
def play_operations():
    """执行录制的操作序列"""
    # 设置播放状态为 True
    utils.is_playing = True
    # 初始化当前循环次数为 0
    current_loop = 0
    
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
                        # 播放速度 > 1.0 时，延迟减少（播放加速）
                        # 播放速度 < 1.0 时，延迟增加（播放减速）
                        adjusted_delay = delay / utils.playback_speed
                        # 执行延迟
                        time.sleep(adjusted_delay)
                        # 打印延迟信息
                        utils.logger.info(f"原始延迟: {delay:.3f}秒, 调整后: {adjusted_delay:.3f}秒, 速度: {utils.playback_speed}倍")
                
                # 执行操作
                try:
                    # 根据操作类型执行相应的操作
                    if op['type'] == 'mousemove':
                        # 鼠标移动操作
                        # 将鼠标移动到指定坐标 (op['x'], op['y'])
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
                        # 键盘按键操作
                        # 检查是否为组合键
                        if 'modifiers' in op and op['modifiers']:
                            # 处理组合键
                            try:
                                # 打印组合键信息
                                
                                # 处理基础键格式：将'Key.tab'转换为'tab'等pyautogui可识别的格式
                                base_key = op['base_key']
                                if base_key.startswith('Key.'):
                                    # 移除'Key.'前缀，提取实际键名
                                    base_key = base_key[4:]  # 'Key.tab' -> 'tab'
                                
                                # 构建热键列表：修饰键 + 处理后的基础键
                                hotkey_list = op['modifiers'] + [base_key]
                                utils.logger.info(f"组合键执行 {hotkey_list}")
                                
                                # 执行组合键
                                pyautogui.hotkey(*hotkey_list)
                                time.sleep(0.1)  # 短延时，确保组合键生效
                                
                                # 打印执行成功信息
                                utils.logger.info(f"组合键执行成功")
                            except Exception as e:
                                # 捕获组合键执行异常
                                utils.logger.error(f"组合键执行失败: {e}")
                        else:
                            # 处理非组合键（特殊键或普通键）
                            # 特殊键映射
                            # 优化：使用通用的键名转换方法处理特殊键
                            key = op['key']
                            if key.startswith('Key.'):
                                # 移除'Key.'前缀，提取实际键名
                                press_key = key[4:]  # 'Key.space' -> 'space'
                                
                                # 处理特殊映射：如'page_up' -> 'pageup'
                                key_mappings = {
                                    'page_up': 'pageup',
                                    'page_down': 'pagedown'
                                }
                                if press_key in key_mappings:
                                    press_key = key_mappings[press_key]
                                
                                # 执行按键操作
                                pyautogui.press(press_key)
                            else:
                                # 处理普通键
                                try:
                                    # 打印普通键信息
                                    utils.logger.info(f"执行普通键: {op['key']}")
                                    # 执行按键操作
                                    pyautogui.press(op['key'])
                                except Exception as e:
                                    # 捕获普通键执行异常
                                    utils.logger.error(f"普通键执行失败: {e}")
                except pyautogui.FailSafeException:
                    # 捕获安全机制异常
                    # 当用户将鼠标移动到屏幕角落时，pyautogui 会触发 FailSafeException
                    # 这是一个安全机制，允许用户在紧急情况下停止自动化操作
                    utils.logger.warning("检测到安全机制触发")
                    # 设置播放状态为 False，停止播放
                    utils.is_playing = False
                    # 弹出提示框：播放结束
                    pyautogui.alert(text='播放已结束', title='提示', button='确定')
                    
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
            
            # 检查是否需要继续循环
            # 当未开启循环且当前循环次数达到最大循环次数时，跳出循环
            if not utils.is_looping and current_loop >= utils.max_loop_count:
                break
    
    finally:
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
