#!/usr/bin/env python3
# 打包脚本，用于将Python代码打包成Windows的exe可执行文件

import os
import sys
import shutil
import subprocess

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# 输出目录
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "dist")
# 临时目录
BUILD_DIR = os.path.join(PROJECT_ROOT, "build")


def clean_build():
    """清理之前的构建文件"""
    print("清理之前的构建文件...")
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    if os.path.exists(BUILD_DIR):
        shutil.rmtree(BUILD_DIR)
    if os.path.exists(os.path.join(PROJECT_ROOT, "main.spec")):
        os.remove(os.path.join(PROJECT_ROOT, "main.spec"))
    if os.path.exists(os.path.join(PROJECT_ROOT, "PcDesktopAutomation.spec")):
        os.remove(os.path.join(PROJECT_ROOT, "PcDesktopAutomation.spec"))
    print("清理完成！")


def install_dependencies():
    """安装依赖"""
    print("安装依赖...")
    requirements_file = os.path.join(PROJECT_ROOT, "requirements.txt")
    if os.path.exists(requirements_file):
        # 使用 --user 参数安装到用户目录
        subprocess.run([sys.executable, "-m", "pip", "install", "--user", "-r", requirements_file], check=True)
    else:
        print("未找到requirements.txt文件，使用默认依赖")
        subprocess.run([sys.executable, "-m", "pip", "install", "--user", "PyQt5", "pynput", "pyautogui", "pyinstaller"], check=True)
    print("依赖安装完成！")


def find_python_exe():
    """查找正确的Python解释器"""
    # 尝试使用当前Python解释器
    python_exe = sys.executable
    print(f"使用Python解释器: {python_exe}")
    
    # 检查是否是Microsoft Store版本的Python
    if "WindowsApps" in python_exe and "PythonSoftwareFoundation" in python_exe:
        print("警告：检测到Microsoft Store版本的Python，可能会遇到模块访问问题")
        # 尝试查找用户本地安装的Python解释器
        import os
        local_python = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Python", "Python39", "python.exe")
        if os.path.exists(local_python):
            print(f"找到本地Python解释器: {local_python}")
            return local_python
        print("未找到本地Python解释器，将尝试直接使用pyinstaller可执行文件")
    
    return python_exe


def find_pyinstaller():
    """查找pyinstaller可执行文件"""
    import os
    import subprocess
    
    # 尝试直接运行pyinstaller
    try:
        result = subprocess.run(["pyinstaller", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("找到pyinstaller可执行文件")
            return "pyinstaller"
    except FileNotFoundError:
        pass
    
    # 尝试从pip安装路径查找
    pip_path = os.path.join(os.environ.get("LOCALAPPDATA", ""), "packages", "PythonSoftwareFoundation.Python.3.9_qbz5n2kfra8p0", "LocalCache", "local-packages", "Python39", "Scripts", "pyinstaller.exe")
    if os.path.exists(pip_path):
        print(f"从pip安装路径找到pyinstaller: {pip_path}")
        return pip_path
    
    # 尝试其他可能的路径
    possible_paths = [
        os.path.join(os.environ.get("APPDATA", ""), "Python", "Python39", "Scripts", "pyinstaller.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Python", "Python39", "Scripts", "pyinstaller.exe")
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"找到pyinstaller: {path}")
            return path
    
    print("未找到pyinstaller可执行文件")
    return None


def build_exe():
    """构建exe可执行文件"""
    print("开始构建exe可执行文件...")
    
    # 确保所有的spec文件都被清理干净
    for spec_file in ["main.spec", "PcDesktopAutomation.spec"]:
        spec_path = os.path.join(PROJECT_ROOT, spec_file)
        if os.path.exists(spec_path):
            print(f"删除旧的spec文件: {spec_path}")
            os.remove(spec_path)
    
    # 尝试方法1: 使用Python模块方式
    print("尝试方法1: 使用Python模块方式")
    python_exe = find_python_exe()
    
    # 使用绝对路径来指定main.py文件
    main_py_path = os.path.abspath(os.path.join(PROJECT_ROOT, "main.py"))
    
    build_command = [
        python_exe,
        "-m", "pyinstaller",
        "--name", "PcDesktopAutomation",
        "--onefile",
        "--windowed",
        "--add-data", f"{os.path.join(PROJECT_ROOT, 'styles.css')};.",
        main_py_path
    ]
    
    print(f"执行命令: {' '.join(build_command)}")
    
    try:
        subprocess.run(build_command, cwd=PROJECT_ROOT, check=True)
        print("exe可执行文件构建完成！")
        print(f"可执行文件位于: {os.path.join(OUTPUT_DIR, 'PcDesktopAutomation.exe')}")
        return
    except subprocess.CalledProcessError as e:
        print(f"方法1失败: {e}")
    
    # 尝试方法2: 不使用 --windowed 参数
    print("\n尝试方法2: 不使用 --windowed 参数")
    build_command_no_windowed = [
        python_exe,
        "-m", "pyinstaller",
        "--name", "PcDesktopAutomation",
        "--onefile",
        "--add-data", f"{os.path.join(PROJECT_ROOT, 'styles.css')};.",
        main_py_path
    ]
    
    print(f"执行命令: {' '.join(build_command_no_windowed)}")
    
    try:
        subprocess.run(build_command_no_windowed, cwd=PROJECT_ROOT, check=True)
        print("exe可执行文件构建完成！")
        print(f"可执行文件位于: {os.path.join(OUTPUT_DIR, 'PcDesktopAutomation.exe')}")
        return
    except subprocess.CalledProcessError as e:
        print(f"方法2失败: {e}")
    
    # 尝试方法3: 直接使用pyinstaller可执行文件
    print("\n尝试方法3: 直接使用pyinstaller可执行文件")
    pyinstaller_exe = find_pyinstaller()
    
    if pyinstaller_exe:
        build_command_direct = [
            pyinstaller_exe,
            "--name", "PcDesktopAutomation",
            "--onefile",
            "--windowed",
            "--add-data", f"{os.path.join(PROJECT_ROOT, 'styles.css')};.",
            main_py_path
        ]
        
        print(f"执行命令: {' '.join(build_command_direct)}")
        
        try:
            subprocess.run(build_command_direct, cwd=PROJECT_ROOT, check=True)
            print("exe可执行文件构建完成！")
            print(f"可执行文件位于: {os.path.join(OUTPUT_DIR, 'PcDesktopAutomation.exe')}")
            return
        except subprocess.CalledProcessError as e:
            print(f"方法3失败: {e}")
    else:
        print("未找到pyinstaller可执行文件")
    
    # 尝试方法4: 直接使用pyinstaller可执行文件（无窗口）
    print("\n尝试方法4: 直接使用pyinstaller可执行文件（无窗口）")
    if pyinstaller_exe:
        build_command_direct_no_windowed = [
            pyinstaller_exe,
            "--name", "PcDesktopAutomation",
            "--onefile",
            "--add-data", f"{os.path.join(PROJECT_ROOT, 'styles.css')};.",
            main_py_path
        ]
        
        print(f"执行命令: {' '.join(build_command_direct_no_windowed)}")
        
        try:
            subprocess.run(build_command_direct_no_windowed, cwd=PROJECT_ROOT, check=True)
            print("exe可执行文件构建完成！")
            print(f"可执行文件位于: {os.path.join(OUTPUT_DIR, 'PcDesktopAutomation.exe')}")
            return
        except subprocess.CalledProcessError as e:
            print(f"方法4失败: {e}")
    
    print("所有构建方法均失败！")
    print("\n建议：")
    print("1. 安装完整版本的Python（非Microsoft Store版本）")
    print("2. 以管理员身份运行此脚本")
    print("3. 确保pyinstaller已正确安装: pip install pyinstaller")
    raise Exception("无法构建exe可执行文件")


def create_distribution():
    """创建分发目录"""
    print("创建分发目录...")
    
    # 确保dist目录存在
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    # 复制README.txt到dist目录
    readme_src = os.path.join(PROJECT_ROOT, "README.txt")
    readme_dst = os.path.join(OUTPUT_DIR, "README.txt")
    if os.path.exists(readme_src):
        shutil.copy2(readme_src, readme_dst)
        print("已复制README.txt到分发目录")
    
    # 创建sequences目录
    sequences_dir = os.path.join(OUTPUT_DIR, "sequences")
    if not os.path.exists(sequences_dir):
        os.makedirs(sequences_dir)
        print("已创建sequences目录")
    
    # 创建logs目录
    logs_dir = os.path.join(OUTPUT_DIR, "logs")
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
        print("已创建logs目录")
    
    print("分发目录创建完成！")


def main():
    """主函数"""
    try:
        print("=====================================")
        print("桌面操作自动重放工具 - 打包脚本")
        print("=====================================")
        
        # 清理构建
        clean_build()
        
        # 安装依赖
        install_dependencies()
        
        # 构建exe
        build_exe()
        
        # 创建分发目录
        create_distribution()
        
        print("=====================================")
        print("打包完成！")
        print(f"可执行文件: {os.path.join(OUTPUT_DIR, 'PcDesktopAutomation.exe')}")
        print("=====================================")
        
    except Exception as e:
        print(f"打包过程中出现错误: {e}")
        print("\n注意：如果构建失败，可能需要以下步骤：")
        print("1. 确保使用的是完整安装的Python版本，而非Microsoft Store版本")
        print("2. 确保所有依赖都已正确安装")
        print("3. 尝试以管理员身份运行此脚本")
        sys.exit(1)


if __name__ == "__main__":
    main()
