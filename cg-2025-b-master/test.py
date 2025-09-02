import numpy as np
from PIL import Image
from PyQt5 import QtCore  # 导入QtCore模块

print("numpy版本:", np.__version__)
print("Pillow版本:", Image.__version__)
print("PyQt5版本:", QtCore.qVersion())  # 通过QtCore调用qVersion()
print("所有库均安装成功！")