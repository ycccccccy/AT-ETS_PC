import asyncio
import subprocess
import sys
import os
import json
import time
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel, QCheckBox, \
    QListWidget, QListWidgetItem, QMessageBox
from PyQt5.QtGui import QFontDatabase, QFont, QTextCursor, QIcon, QMovie
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from bs4 import BeautifulSoup
from win10toast import ToastNotifier


class ScanThread(QThread):
    finished = pyqtSignal()

    def __init__(self, window):
        super().__init__()
        self.window = window

    def run(self):
        self.window.update_folder_list()
        self.finished.emit()  # 发送完成信号

class CheckVersionThread(QThread):
    versionChecked = pyqtSignal(str)
    downloadLink = pyqtSignal(str)

    def __init__(self, app_id, current_version):
        super().__init__()
        self.app_id = app_id
        self.current_version = current_version

    async def download_file_async(self, url, filename):
        try:
            response = await asyncio.to_thread(requests.get, url, stream=True)
            response.raise_for_status()
            self.notify("下载更新", "正在下载更新")
            with open(filename, 'wb') as fd:
                for chunk in response.iter_content(chunk_size=8192):
                    fd.write(chunk)
            self.notify("下载更新", "下载完成，即将更新!")

            # 在这里执行更新的操作，例如启动更新程序
            subprocess.Popen(["start", os.path.join("..", "update.exe")], shell=True)
        except requests.exceptions.RequestException as e:
            self.notify("下载更新", f"出现错误: {str(e)}")

    def notify(self, title, message):
        toaster = ToastNotifier()
        toaster.show_toast(title, message)



    def run(self):
        try:
            self.notify("更新", "正在检查更新🤔")
            response = requests.get('https://ycccccccy.github.io/app-versioncheck/')
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                version_div = soup.find(id=self.app_id)
                if version_div:
                    version = version_div.text
                    if version != self.current_version:
                        self.notify("更新", "正在下载最新版本！")
                        download_link = f"https://d.kstore.space/download/8128/FK-ETS-x64-{version}.zip"
                        asyncio.run(self.download_file_async(download_link, "update.zip"))
                    else:
                        self.notify("更新", "当前已是最新版本")
                else:
                    self.notify("更新", "啊啊啊，检查更新失败了...")
        except Exception as e:
            self.notify("更新", "啊啊啊，检查更新失败了...")


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AT-ETS")
        self.resize(1024, 620)
        self.setWindowOpacity(0.9)
        self.setWindowIcon(QIcon('icon.ico'))

        self.layout = QVBoxLayout(self)

        # 创建一个新的水平布局，用于包含标题栏和加载动画
        self.top_layout = QHBoxLayout()
        self.layout.addLayout(self.top_layout)

        self.title_bar = QWidget(self)
        self.title_layout = QHBoxLayout(self.title_bar)
        self.top_layout.addWidget(self.title_bar)

        # 加载字体文件
        self.font_id = QFontDatabase.addApplicationFont('Fonts/MiSans-Light.ttf')
        self.font_families = QFontDatabase.applicationFontFamilies(self.font_id)
        self.font_family = self.font_families[0] if self.font_families else "Helvetica"



        self.home_button = QPushButton("主页", self.title_bar)
        self.home_button.setFont(QFont(self.font_family, 12))
        self.title_layout.addWidget(self.home_button)

        self.only_one_answer = QCheckBox("只显示一个答案", self.title_bar)
        self.only_one_answer.setFont(QFont(self.font_family, 12))
        self.title_layout.addWidget(self.only_one_answer)

        self.print_keywords = QCheckBox("显示关键词", self.title_bar)
        self.print_keywords.setFont(QFont(self.font_family, 12))
        self.title_layout.addWidget(self.print_keywords)
        self.title_layout.addStretch()

        self.text_area = QTextEdit(self)
        self.text_area.setFont(QFont(self.font_family, 14))
        self.layout.addWidget(self.text_area)

        self.folder_list = QListWidget(self)
        self.folder_list.setFont(QFont(self.font_family, 14))
        self.folder_list.setFrameShape(QListWidget.NoFrame)
        self.layout.addWidget(self.folder_list)

        self.appdata_path = os.getenv('APPDATA')
        self.base_path = os.path.join(self.appdata_path, '74656D705F74656D705F74656D705F74002')

        #加载GIF动画
        self.loading_movie = QMovie("loading.gif")
        self.loading_label = QLabel(self)
        self.loading_label.setMovie(self.loading_movie)
        self.loading_label.hide()
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.top_layout.addWidget(self.loading_label)


        self.scan_thread = ScanThread(self)
        self.scan_thread.finished.connect(self.on_scan_finished)

        self.folder_list.itemClicked.connect(self.on_folder_clicked)
        self.home_button.clicked.connect(self.on_home_clicked)

        self.check_version_thread = CheckVersionThread("FKETS-windwos-version", "2.0.3")
        self.check_version_thread.versionChecked.connect(self.on_version_checked)
        self.check_version_thread.downloadLink.connect(self.on_download_link_received)
        self.check_version_thread.start()

        self.show()
        self.on_home_clicked()

    def notify(self, title, message):
        toaster = ToastNotifier()
        toaster.show_toast(title, message)

    def on_version_checked(self, message):
        self.notify("更新", message)

    def on_download_link_received(self, link):
        self.download_file_async(link, "update.zip")

    async def download_file_async(self, url, filename):
        try:
            response = await asyncio.to_thread(requests.get, url, stream=True)
            response.raise_for_status()
            self.notify("下载更新", "正在下载更新")
            with open(filename, 'wb') as fd:
                for chunk in response.iter_content(chunk_size=8192):
                    fd.write(chunk)
            self.notify("下载更新", "下载完成，即将更新!")

            # 执行更新
            subprocess.Popen(["start", os.path.join("..", "update.exe")], shell=True)
        except requests.exceptions.RequestException as e:
            self.notify("下载更新", f"出现错误: {str(e)}")



    def on_folder_clicked(self, item):
        folder_name = item.text().split(' ')[0]  # 从列表项中获取文件夹名
        self.get_result(folder_name)

    def on_home_clicked(self):
        self.title_bar.hide()
        self.text_area.hide()
        self.folder_list.hide()
        self.loading_label.show()
        self.loading_movie.start()
        self.scan_thread.start()

    def on_scan_finished(self):
        self.loading_movie.stop()
        self.loading_label.hide()
        self.title_bar.show()
        self.folder_list.show()

    def get_result(self, folder_name):
        self.text_area.clear()
        file_count = len([name for name in os.listdir(os.path.join(self.base_path, folder_name)) if
                          name.startswith('content0001000')])
        if file_count == 3:
            titles = self.A()
        elif file_count == 7:
            titles = self.B()
        else:
            self.text_area.setText("这似乎不是正常模考试题，请重新选择吧")
            self.text_area.setAlignment(Qt.AlignCenter)
            self.text_area.show()
            self.folder_list.hide()
            return
        error_count = 0
        for i in range(2, len(titles) + 2):
            file_name = f'content0001000{i}'
            file_path = os.path.join(self.base_path, folder_name, file_name, 'content.json')
            self.text_area.append(f'{titles[i - 2]}:\n')
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if 'question' in data['info']:
                    questions = data['info']['question']
                    for j, question in enumerate(questions):
                        self.text_area.append(f'角色扮演 {j + 1} :\n')
                        for k, answer in enumerate(question['std']):
                            answer_value = answer["value"].replace('</p><p>', ' ')
                            self.text_area.append(f'{k + 1}. {answer_value}\n')
                            if self.print_keywords.isChecked() and 'keywords' in question:
                                keywords = question["keywords"].replace('|', ', ')
                                self.text_area.append(f'关键词: {keywords}\n')
                            if self.only_one_answer.isChecked():
                                break
                else:
                    self.text_area.append('\n')
                    for k, answer in enumerate(data['info']['std']):
                        answer_value = answer["value"].replace('</p><p>', ' ')
                        self.text_area.append(f'{k + 1}. {answer_value}\n')
                        if self.only_one_answer.isChecked():
                            break
                self.text_area.append('')
            except Exception as e:
                self.text_area.append("获取错误")
                error_count += 1
        if error_count == len(titles):
            self.text_area.setText("这似乎不是正常模考试题，请重新选择吧")
            self.text_area.setAlignment(Qt.AlignCenter)
        self.text_area.moveCursor(QTextCursor.Start)
        self.text_area.show()
        self.folder_list.hide()


    def A(self):
        return ['角色扮演', '故事复述']

    def B(self):
        return ['听选信息1', '听选信息2', '听选信息3', '回答问题', '短文复述', '提问']

    def update_folder_list(self):
        folders = [(name, os.path.getmtime(os.path.join(self.base_path, name))) for name in os.listdir(self.base_path)
                   if name.isdigit()]
        folders.sort(key=lambda x: x[1], reverse=True)  # 按创建时间从新到旧排序
        self.folder_list.clear()
        for folder, mtime in folders:
            mtime_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))
            item = QListWidgetItem(f'{folder.ljust(20)} {mtime_str.rjust(20)}')
            item.setTextAlignment(Qt.AlignLeft)
            self.folder_list.addItem(item)




app = QApplication(sys.argv)
window = MainWindow()
sys.exit(app.exec_())
