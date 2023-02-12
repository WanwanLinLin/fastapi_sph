# encoding:utf-8
import os

CURRENT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 静态文件存放路径
Static_PATH = os.path.join(CURRENT_PATH, "static")

if __name__ == '__main__':
    print(CURRENT_PATH)