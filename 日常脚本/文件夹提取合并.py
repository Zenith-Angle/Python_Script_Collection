import sys
import os
import re
from shutil import move
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout,
    QLineEdit, QComboBox, QListWidget, QLabel,
    QFileDialog
)
from PyQt6.QtCore import Qt, QMimeData


class FolderList(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        mime_data: QMimeData = event.mimeData()
        if mime_data.hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        mime_data: QMimeData = event.mimeData()
        if mime_data.hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        mime_data: QMimeData = event.mimeData()
        if mime_data.hasUrls():
            for url in mime_data.urls():
                path = url.toLocalFile()
                if os.path.isdir(path):
                    self.addItem(path)


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('文件移动程序')
        self.setGeometry(100, 100, 600, 300)

        self.layout = QVBoxLayout()

        self.drag_label = QLabel('拖动待操作文件夹到此处', self)
        self.layout.addWidget(self.drag_label)

        self.folder_list = FolderList(self)
        self.layout.addWidget(self.folder_list)

        self.remove_folder_button = QPushButton('移除选中文件夹', self)
        self.remove_folder_button.clicked.connect(self.remove_folder)
        self.layout.addWidget(self.remove_folder_button)

        self.select_output_button = QPushButton('选择输出文件夹', self)
        self.select_output_button.clicked.connect(self.select_output_folder)
        self.layout.addWidget(self.select_output_button)

        self.output_folder_entry = QLineEdit(self)
        self.layout.addWidget(self.output_folder_entry)

        self.filter_layout = QVBoxLayout()
        self.filter_type_combo = QComboBox(self)
        self.filter_type_combo.addItems(['后缀', '包含', '全称', '正则表达式'])
        self.filter_entry = QLineEdit(self)
        self.filter_layout.addWidget(self.filter_type_combo)
        self.filter_layout.addWidget(self.filter_entry)

        self.layout.addLayout(self.filter_layout)

        self.move_files_button = QPushButton('移动文件', self)
        self.move_files_button.clicked.connect(self.move_files)
        self.layout.addWidget(self.move_files_button)

        self.output_folder = ""

        self.setLayout(self.layout)

    def remove_folder(self):
        for item in self.folder_list.selectedItems():
            self.folder_list.takeItem(self.folder_list.row(item))

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, '选择输出文件夹')
        if folder:
            self.output_folder = folder
            self.output_folder_entry.setText(folder)

    def move_files(self):
        self.output_folder = self.output_folder_entry.text()
        if self.folder_list.count() == 0 or not self.output_folder:
            print("输入和输出文件夹不能为空。")
            return

        filter_type = self.filter_type_combo.currentText()
        filter_text = self.filter_entry.text()

        # 转换筛选文本为正则表达式
        filter_regex = re.compile({
                                      '后缀': re.escape(filter_text) + '$',
                                      '包含': re.escape(filter_text),
                                      '全称': '^' + re.escape(filter_text) + '$',
                                      '正则表达式': filter_text,
                                  }[filter_type])

        for index in range(self.folder_list.count()):
            folder = self.folder_list.item(index).text()
            for root_dir, _, files in os.walk(folder):
                for file in files:
                    if filter_regex.search(file):
                        src = os.path.join(root_dir, file)
                        dst = os.path.join(self.output_folder, file)
                        if not os.path.exists(dst):
                            move(src, dst)
                            print(f'已将 {src} 移动到 {dst}')
                        else:
                            print(f'{dst} 已存在，未能移动 {src}')

        print("文件移动完成！")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec())
