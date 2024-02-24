import sys
import os
import json
import time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel, QCheckBox, QListWidget, QListWidgetItem
from PyQt5.QtGui import QFontDatabase, QFont, QTextCursor, QIcon
from PyQt5.QtCore import Qt

def get_result(folder_name):
    text_area.clear()
    file_count = len([name for name in os.listdir(os.path.join(base_path, folder_name)) if name.startswith('content0001000')])
    if file_count == 3:
        titles = A()
    elif file_count == 7:
        titles = B()
    else:
        text_area.setText("这似乎不是正常模考试题，请重新选择吧")
        text_area.setAlignment(Qt.AlignCenter)
        text_area.show()
        folder_list.hide()
        return
    error_count = 0
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
            error_count += 1
    if error_count == len(titles):
        text_area.setText("这似乎不是正常模考试题，请重新选择吧")
        text_area.setAlignment(Qt.AlignCenter)
    text_area.moveCursor(QTextCursor.Start)
    text_area.show()
    folder_list.hide()

def A():
    return ['角色扮演', '故事复述']

def B():
    return ['听选信息1', '听选信息2', '听选信息3', '回答问题', '短文复述', '提问']

def update_folder_list():
    folders = [(name, os.path.getmtime(os.path.join(base_path, name))) for name in os.listdir(base_path) if name.isdigit()]
    folders.sort(key=lambda x: x[1], reverse=True)  # 按创建时间从新到旧排序
    folder_list.clear()
    for folder, mtime in folders:
        mtime_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))
        item = QListWidgetItem(f'{folder.ljust(20)} {mtime_str.rjust(20)}')
        item.setTextAlignment(Qt.AlignLeft)
        folder_list.addItem(item)

app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle("AT-ETS")
window.resize(1024, 620)
window.setWindowOpacity(0.9)
# 设置窗口图标
window.setWindowIcon(QIcon('icon.ico'))

layout = QVBoxLayout(window)
title_bar = QWidget(window)
title_layout = QHBoxLayout(title_bar)
layout.addWidget(title_bar)

# 加载字体文件
font_id = QFontDatabase.addApplicationFont('Fonts/MiSans-Light.ttf')
font_families = QFontDatabase.applicationFontFamilies(font_id)
font_family = font_families[0] if font_families else "Helvetica"

label = QLabel("选项：", title_bar)
font = QFont(font_family, 12)
label.setFont(font)
title_layout.addWidget(label)

only_one_answer = QCheckBox("只显示一个答案", title_bar)
only_one_answer.setFont(QFont(font_family, 12))
title_layout.addWidget(only_one_answer)

home_button = QPushButton("主页", title_bar)
home_button.setFont(QFont(font_family, 12))
title_layout.addWidget(home_button)

title_layout.addStretch()

text_area = QTextEdit(window)
text_area.setFont(QFont(font_family, 14))
layout.addWidget(text_area)

folder_list = QListWidget(window)
folder_list.setFont(QFont(font_family, 14))
folder_list.setFrameShape(QListWidget.NoFrame)  # 去掉边框
layout.addWidget(folder_list)

appdata_path = os.getenv('APPDATA')
base_path = os.path.join(appdata_path, '74656D705F74656D705F74656D705F74002')

def on_folder_clicked(item):
    folder_name = item.text().split(' ')[0]  # 从列表项中获取文件夹名
    get_result(folder_name)

folder_list.itemClicked.connect(on_folder_clicked)

def on_home_clicked():
    text_area.hide()
    update_folder_list()
    folder_list.show()

home_button.clicked.connect(on_home_clicked)

window.show()
on_home_clicked()

sys.exit(app.exec_())
