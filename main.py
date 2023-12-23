import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel, QCheckBox
from PyQt5.QtGui import QFontDatabase, QFont, QTextCursor
from PyQt5.QtCore import Qt
import json
import os

def get_result(func):
    # 清空文本框
    text_area.clear()

    # 执行获取部分
    appdata_path = os.getenv('APPDATA')
    base_path = os.path.join(appdata_path, '74656D705F74656D705F74656D705F74002')
    folder_name = ''
    latest_mtime = 0
    for name in os.listdir(base_path):
        if name.isdigit():
            folder_path = os.path.join(base_path, name)
            mtime = os.path.getmtime(folder_path)
            if mtime > latest_mtime:
                latest_mtime = mtime
                folder_name = name

    titles = func()
    for i in range(2, len(titles) + 2):
        file_name = f'content0001000{i}'
        file_path = os.path.join(base_path, folder_name, file_name, 'content.json')
        text_area.append(f'{titles[i - 2]}:\n')
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if 'question' in data['info']:
                questions = data['info']['question']
                for j, question in enumerate(questions):
                    text_area.append(f'问题 {j + 1} 标准答案:\n')
                    for k, answer in enumerate(question['std']):
                        text_area.append(f'{k + 1}. {answer["value"]}\n')
                        if only_one_answer.isChecked():
                            break
            else:
                text_area.append('标准答案:\n')
                for k, answer in enumerate(data['info']['std']):
                    text_area.append(f'{k + 1}. {answer["value"]}\n')
                    if only_one_answer.isChecked():
                        break
            text_area.append('')
        except Exception as e:
            text_area.append("获取错误")

    # 将光标移动到文本的开头
    text_area.moveCursor(QTextCursor.Start)

def A():
    return ['角色扮演', '故事复述']

def B():
    return ['听选信息1', '听选信息2', '听选信息3', '回答问题', '短文复述', '提问']

# 创建应用实例
app = QApplication(sys.argv)

# 加载字体文件
font_id = QFontDatabase.addApplicationFont('Fonts/MiSans-Light.ttf') #暂时不用这个，安装有点小问题
font_families = QFontDatabase.applicationFontFamilies(font_id)
font_family = font_families[0] if font_families else "Helvetica"

# 创建主窗口
window = QWidget()
window.setWindowTitle("AT-ETS")
window.resize(1024, 620)
window.setWindowOpacity(0.9)  # 设置窗口为半透明

# 创建垂直布局
layout = QVBoxLayout(window)

# 创建标题控制栏
title_bar = QWidget(window)
title_layout = QHBoxLayout(title_bar)
layout.addWidget(title_bar)

# 创建固定文字
label = QLabel("选项：", title_bar)
font = QFont(font_family, 12)  # 设置字体为Helvetica，字体大小为18
label.setFont(font)
title_layout.addWidget(label)

# 创建开关
only_one_answer = QCheckBox("只显示一个答案", title_bar)
only_one_answer.setFont(QFont(font_family, 12))  # 设置字体大小为18
title_layout.addWidget(only_one_answer)

# 在标题控制栏中添加弹性空间
title_layout.addStretch()

# 创建文本框，并设置其字体和大小随窗口大小变化
text_area = QTextEdit(window)
text_area.setFont(QFont(font_family, 14))
layout.addWidget(text_area)

# 创建一个框架来放置按钮，并设置其大小随窗口大小变化
button_frame = QWidget(window)
layout.addWidget(button_frame)
button_layout = QHBoxLayout(button_frame)

# 创建按钮A，并设置其大小随窗口大小变化
button_A = QPushButton("获取高中模考答案", button_frame)
button_A.clicked.connect(lambda: get_result(A))
button_A.setFont(QFont(font_family, 18))  # 设置字体大小为18
button_layout.addWidget(button_A)

# 创建按钮B，并设置其大小随窗口大小变化
button_B = QPushButton("获取初中模考答案", button_frame)
button_B.clicked.connect(lambda: get_result(B))
button_B.setFont(QFont(font_family, 18))  # 设置字体大小为18
button_layout.addWidget(button_B)

# 显示窗口
window.show()

# 运行主循环
sys.exit(app.exec_())
