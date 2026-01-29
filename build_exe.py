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
    return python_exe


def build_exe():
    """构建exe可执行文件"""
    print("开始构建exe可执行文件...")
    
    # 获取Python解释器
    python_exe = find_python_exe()
    
    # 构建命令
    build_command = [
        python_exe,
        "-m", "pyinstaller",
        "--name", "WindowsDesktopAutomation",
        "--onefile",
        "--windowed",
        "main.py"
    ]
    
    print(f"执行命令: {' '.join(build_command)}")
    
    # 执行构建命令
    try:
        subprocess.run(build_command, cwd=PROJECT_ROOT, check=True)
    except subprocess.CalledProcessError as e:
        print(f"构建失败，尝试使用其他方法...")
        # 尝试不使用 --windowed 参数
        build_command_no_windowed = [
            python_exe,
            "-m", "pyinstaller",
            "--name", "WindowsDesktopAutomation",
            "--onefile",
            "main.py"
        ]
        print(f"执行命令: {' '.join(build_command_no_windowed)}")
        subprocess.run(build_command_no_windowed, cwd=PROJECT_ROOT, check=True)
    
    print("exe可执行文件构建完成！")
    print(f"可执行文件位于: {os.path.join(OUTPUT_DIR, 'WindowsDesktopAutomation.exe')}")


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
        print("Windows桌面自动化工具 - 打包脚本")
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
        print(f"可执行文件: {os.path.join(OUTPUT_DIR, 'WindowsDesktopAutomation.exe')}")
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
