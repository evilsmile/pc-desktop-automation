import json
import os
import utils

# 保存序列
def save_sequence(name):
    if not name:
        return False, '序列名称不能为空'
    
    # 确保sequences目录存在
    if not os.path.exists(utils.sequences_dir):
        os.makedirs(utils.sequences_dir)
    
    # 保存到内存
    utils.sequences[name] = utils.recorded_operations
    utils.current_sequence = name
    
    # 保存到文件
    try:
        with open(os.path.join(utils.sequences_dir, f'{name}.json'), 'w', encoding='utf-8') as f:
            json.dump(utils.recorded_operations, f, ensure_ascii=False, indent=2)
        return True, f'序列 "{name}" 已保存'
    except Exception as e:
        return False, f'保存失败: {str(e)}'

# 加载序列
def load_sequence(name):
    if not name:
        return False, '序列名称不能为空'
    
    # 从内存加载
    if name in utils.sequences:
        utils.recorded_operations = utils.sequences[name]
        utils.current_sequence = name
        return True, f'序列 "{name}" 已加载'
    
    # 从文件加载
    try:
        with open(os.path.join(utils.sequences_dir, f'{name}.json'), 'r', encoding='utf-8') as f:
            utils.recorded_operations = json.load(f)
        utils.sequences[name] = utils.recorded_operations
        utils.current_sequence = name
        return True, f'序列 "{name}" 已从文件加载'
    except Exception as e:
        return False, f'加载失败: {str(e)}'

# 删除序列
def delete_sequence(name):
    if not name:
        return False, '序列名称不能为空'
    
    # 从内存删除
    if name in utils.sequences:
        del utils.sequences[name]
    
    # 从文件删除
    try:
        if os.path.exists(os.path.join(utils.sequences_dir, f'{name}.json')):
            os.remove(os.path.join(utils.sequences_dir, f'{name}.json'))
        
        # 如果当前序列被删除，清空当前序列
        if utils.current_sequence == name:
            utils.current_sequence = ""
        
        return True, f'序列 "{name}" 已删除'
    except Exception as e:
        return False, f'删除失败: {str(e)}'

# 加载所有序列
def load_all_sequences():
    utils.sequences = {}
    
    # 从文件系统加载所有序列
    if os.path.exists(utils.sequences_dir):
        for filename in os.listdir(utils.sequences_dir):
            if filename.endswith('.json'):
                name = filename[:-5]  # 移除.json后缀
                try:
                    with open(os.path.join(utils.sequences_dir, filename), 'r', encoding='utf-8') as f:
                        utils.sequences[name] = json.load(f)
                except:
                    pass
    return list(utils.sequences.keys())

# 修改序列名称
def rename_sequence(old_name, new_name):
    if not old_name:
        return False, '旧序列名称不能为空'
    if not new_name:
        return False, '新序列名称不能为空'
    if old_name == new_name:
        return False, '新名称与旧名称相同'
    
    # 检查旧序列是否存在
    if old_name not in utils.sequences:
        # 尝试从文件加载
        try:
            with open(os.path.join(utils.sequences_dir, f'{old_name}.json'), 'r', encoding='utf-8') as f:
                utils.sequences[old_name] = json.load(f)
        except:
            return False, f'序列 "{old_name}" 不存在'
    
    # 获取序列内容
    sequence_content = utils.sequences[old_name]
    
    # 从内存中删除旧名称的序列
    del utils.sequences[old_name]
    
    # 将序列保存为新名称
    utils.sequences[new_name] = sequence_content
    
    # 如果当前序列是被修改的序列，更新当前序列名称
    if utils.current_sequence == old_name:
        utils.current_sequence = new_name
    
    # 从文件系统中删除旧文件
    try:
        old_file = os.path.join(utils.sequences_dir, f'{old_name}.json')
        if os.path.exists(old_file):
            os.remove(old_file)
        
        # 将序列保存为新文件
        with open(os.path.join(utils.sequences_dir, f'{new_name}.json'), 'w', encoding='utf-8') as f:
            json.dump(sequence_content, f, ensure_ascii=False, indent=2)
        
        return True, f'序列已从 "{old_name}" 重命名为 "{new_name}"'
    except Exception as e:
        # 如果文件操作失败，恢复内存中的旧序列
        utils.sequences[old_name] = sequence_content
        if utils.current_sequence == new_name:
            utils.current_sequence = old_name
        return False, f'重命名失败: {str(e)}'
