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
