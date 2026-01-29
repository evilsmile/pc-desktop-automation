import sys

# 导入拆分后的模块
from utils import init_utils
from ui import MainWindow
from PyQt5.QtWidgets import QApplication

# 初始化工具函数
init_utils()

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        import utils
        utils.logger.error(f"错误: {e}")
        import traceback
        traceback.print_exc()
        input("按Enter键退出...")
