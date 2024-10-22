import sys
import os
import time
from moviepy.editor import VideoFileClip
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QPushButton, QFileDialog, QSpinBox, QProgressBar,
                               QListWidget, QListView, QTreeView, QAbstractItemView)
from PySide6.QtCore import Qt, QThread, Signal
import imageio


class DroppableListWidget(QListWidget):
    directoriesDropped = Signal(list)  # 信号：拖放的文件夹列表

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            # 检查是否有文件夹被拖入
            for url in event.mimeData().urls():
                if os.path.isdir(url.toLocalFile()):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if os.path.isdir(url.toLocalFile()):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            directories = []
            for url in event.mimeData().urls():
                dir_path = url.toLocalFile()
                if os.path.isdir(dir_path) and dir_path not in directories:
                    directories.append(dir_path)
            if directories:
                self.directoriesDropped.emit(directories)
                event.acceptProposedAction()
                return
        event.ignore()


class VideoProcessorThread(QThread):
    progress = Signal(int)
    finished = Signal()
    detail_progress = Signal(str)  # 用于传递当前的处理状态
    time_update = Signal(str)  # 用于传递时间信息

    total_frames = 0
    frames_processed = 0
    paused = False
    stop_requested = False

    def __init__(self, directories, num_segments):
        super().__init__()
        self.directories = directories
        self.num_segments = num_segments
        self.start_time = None

    def run(self):
        self.start_time = time.time()  # 记录开始时间
        video_extensions = ('.mp4', '.mpv', '.avi', '.mov', '.mkv')
        videos = []

        # 获取所有视频文件并记录所属文件夹
        for directory in self.directories:
            for root, _, files in os.walk(directory):
                for f in files:
                    if f.lower().endswith(video_extensions):
                        video_path = os.path.join(root, f)
                        folder_mod_time = os.path.getmtime(root)
                        videos.append((video_path, folder_mod_time))

        # 按文件夹修改时间排序，从旧到新
        videos.sort(key=lambda x: x[1])

        # 计算总的帧数
        total_videos = len(videos)
        self.total_frames = total_videos * self.num_segments
        self.frames_processed = 0

        for video_info in videos:
            if self.stop_requested:
                break

            while self.paused:
                self.msleep(100)  # 暂停时休眠，避免占用CPU

            video_path = video_info[0]
            filename = os.path.basename(video_path)
            video_name = os.path.splitext(filename)[0]
            save_folder = os.path.join(os.path.dirname(video_path),
                                       f"{video_name}_ScreenShot")
            os.makedirs(save_folder, exist_ok=True)
            try:
                clip = VideoFileClip(video_path)
                duration = clip.duration
                segment_times = [duration * i / (self.num_segments + 1) for i in
                                 range(1, self.num_segments + 1)]
                for idx_frame, t in enumerate(segment_times):
                    if self.stop_requested:
                        break

                    while self.paused:
                        self.msleep(100)  # 暂停时休眠，避免占用CPU

                    frame = clip.get_frame(t)
                    image_name = f"{video_name}_{idx_frame + 1}.jpg"
                    image_path = os.path.join(save_folder, image_name)

                    # 将图片保存为JPEG格式，限制大小不超过1MB
                    quality = 95
                    imageio.imwrite(image_path, frame, format='JPEG', quality=quality)
                    # 如果图片大小超过1MB，降低质量重新保存
                    while os.path.getsize(image_path) > 1024 * 1024 and quality > 10:
                        quality -= 5
                        imageio.imwrite(image_path, frame, format='JPEG', quality=quality)

                    self.frames_processed += 1
                    progress_value = int(self.frames_processed / self.total_frames * 100)
                    self.progress.emit(progress_value)
                    self.detail_progress.emit(
                        f"正在处理：{filename} ({self.frames_processed}/{self.total_frames})")

                    # 计算已消耗时间和预计剩余时间
                    elapsed_time = time.time() - self.start_time
                    if self.frames_processed > 0:
                        estimated_total_time = elapsed_time / self.frames_processed * self.total_frames
                        remaining_time = estimated_total_time - elapsed_time
                    else:
                        remaining_time = 0

                    # 格式化时间为 hh:mm:ss
                    elapsed_str = self.format_time(elapsed_time)
                    remaining_str = self.format_time(remaining_time)
                    time_info = f"已消耗时间: {elapsed_str} / 预计剩余时间: {remaining_str}"
                    self.time_update.emit(time_info)
                clip.close()
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                continue
        self.finished.emit()

    def format_time(self, seconds):
        seconds = int(seconds)
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def stop(self):
        self.stop_requested = True
        self.paused = False  # 如果正在暂停，解除暂停以便线程退出


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('视频截图提取器')
        self.directories = []
        self.num_segments = 10
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 选择输入文件夹按钮
        self.dir_button = QPushButton('选择文件夹')
        self.dir_button.clicked.connect(self.select_directories)
        layout.addWidget(self.dir_button)

        # 显示已选择的文件夹列表（使用DroppableListWidget）
        self.dir_list_widget = DroppableListWidget()
        self.dir_list_widget.directoriesDropped.connect(self.add_directories)
        layout.addWidget(self.dir_list_widget)

        # 删除选中按钮
        self.delete_button = QPushButton('删除选中')
        self.delete_button.clicked.connect(self.delete_selected_directories)
        layout.addWidget(self.delete_button)

        # 选择分段数
        segments_layout = QHBoxLayout()
        self.segments_label = QLabel('分段数:')
        self.segments_spinbox = QSpinBox()
        self.segments_spinbox.setValue(10)
        self.segments_spinbox.setRange(1, 1000)  # 设置范围为1-1000
        # 如果您更喜欢分开设置最小值和最大值，可以使用以下两行代替上面一行：
        # self.segments_spinbox.setMinimum(1)
        # self.segments_spinbox.setMaximum(1000)
        self.segments_spinbox.setFixedHeight(45)
        segments_layout.addWidget(self.segments_label)
        segments_layout.addWidget(self.segments_spinbox)
        layout.addLayout(segments_layout)

        # 详细进度
        self.detail_progress_label = QLabel('')
        layout.addWidget(self.detail_progress_label)

        # 时间预计条
        self.time_label = QLabel('')
        # 使用水平布局将时间标签放置在进度条的右端
        time_layout = QHBoxLayout()
        time_layout.addStretch()  # 添加弹性空间将时间标签推到右端
        time_layout.addWidget(self.time_label)
        layout.addLayout(time_layout)

        # 进度条
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # 底部按钮布局
        button_layout = QHBoxLayout()
        self.start_button = QPushButton('开始处理')
        self.start_button.clicked.connect(self.start_processing)
        self.start_button.setEnabled(False)
        button_layout.addWidget(self.start_button)

        # 暂停、继续、结束按钮
        self.pause_button = QPushButton('暂停')
        self.pause_button.clicked.connect(self.pause_processing)
        self.pause_button.setVisible(False)
        button_layout.addWidget(self.pause_button)

        self.resume_button = QPushButton('继续')
        self.resume_button.clicked.connect(self.resume_processing)
        self.resume_button.setVisible(False)
        button_layout.addWidget(self.resume_button)

        self.stop_button = QPushButton('结束')
        self.stop_button.clicked.connect(self.stop_processing)
        self.stop_button.setVisible(False)
        button_layout.addWidget(self.stop_button)

        layout.addLayout(button_layout)

        # 设置布局
        self.setLayout(layout)
        self.setFixedSize(500, 600)  # 调整窗口高度以适应新添加的时间标签

        # 设置样式表，使界面更美观
        self.setStyleSheet("""
            QWidget {
                font-size: 14px;
            }
            QPushButton {
                background-color: #5DADE2;
                color: white;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #3498DB;
            }
            QProgressBar {
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #5DADE2;
            }
            QSpinBox {
                height: 45px;
                font-size: 16px;
            }
            QLabel {
                font-size: 14px;
            }
        """)

    def add_directories(self, directories):
        added = False
        for dir_path in directories:
            if dir_path not in self.directories:
                self.directories.append(dir_path)
                self.dir_list_widget.addItem(dir_path)
                added = True
        if added and self.directories:
            self.start_button.setEnabled(True)

    def select_directories(self):
        # 创建自定义的QFileDialog，允许多选文件夹
        dialog = QFileDialog()
        dialog.setWindowTitle('选择输入文件夹')
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        dialog.setOption(QFileDialog.ShowDirsOnly, True)

        # 获取文件树视图并设置选择模式为多选
        file_view = dialog.findChild(QListView, 'listView')

        if not file_view:
            file_view = dialog.findChild(QTreeView)

        if file_view:
            file_view.setSelectionMode(QAbstractItemView.MultiSelection)

        if dialog.exec():
            directories = dialog.selectedFiles()
            self.add_directories(directories)

    def delete_selected_directories(self):
        selected_items = self.dir_list_widget.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            dir_path = item.text()
            if dir_path in self.directories:
                self.directories.remove(dir_path)
            self.dir_list_widget.takeItem(self.dir_list_widget.row(item))
        if not self.directories:
            self.start_button.setEnabled(False)

    def start_processing(self):
        if not self.directories:
            self.detail_progress_label.setText('请先选择输入文件夹!')
            return
        self.num_segments = self.segments_spinbox.value()
        self.progress_bar.setValue(0)
        self.detail_progress_label.setText('')
        self.time_label.setText('')
        self.thread = VideoProcessorThread(self.directories, self.num_segments)
        self.thread.progress.connect(self.update_progress)
        self.thread.detail_progress.connect(self.update_detail_progress)
        self.thread.time_update.connect(self.update_time)
        self.thread.finished.connect(self.processing_finished)
        self.thread.start()
        self.start_button.setVisible(False)
        self.pause_button.setVisible(True)
        self.pause_button.setEnabled(True)
        self.dir_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        self.segments_spinbox.setEnabled(False)

    def pause_processing(self):
        if self.thread and self.thread.isRunning():
            self.thread.pause()
            self.pause_button.setVisible(False)
            self.resume_button.setVisible(True)
            self.stop_button.setVisible(True)

    def resume_processing(self):
        if self.thread:
            self.thread.resume()
            self.pause_button.setVisible(True)
            self.resume_button.setVisible(False)
            self.stop_button.setVisible(False)

    def stop_processing(self):
        if self.thread:
            self.thread.stop()
            self.resume_button.setEnabled(False)
            self.stop_button.setEnabled(False)
            self.pause_button.setEnabled(False)
            self.detail_progress_label.setText('正在停止，请稍候...')
            self.time_label.setText('')

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_detail_progress(self, text):
        self.detail_progress_label.setText(text)

    def update_time(self, time_info):
        self.time_label.setText(time_info)

    def processing_finished(self):
        self.start_button.setEnabled(True)
        self.start_button.setVisible(True)
        self.pause_button.setVisible(False)
        self.resume_button.setVisible(False)
        self.stop_button.setVisible(False)
        self.progress_bar.setValue(100)
        self.detail_progress_label.setText('处理完成!')
        self.time_label.setText('已消耗时间: 00:00:00 / 预计剩余时间: 00:00:00')
        self.dir_button.setEnabled(True)
        self.delete_button.setEnabled(True)
        self.segments_spinbox.setEnabled(True)
        # 清空已选择的文件夹列表
        self.directories.clear()
        self.dir_list_widget.clear()
        self.start_button.setText('开始处理')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
