import sys

from qframelesswindow import AcrylicWindow
from mainwindow import Window
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QComboBox, QWidget, QLabel, QPushButton, QVBoxLayout, QLineEdit, QMessageBox, QDialog
from qframelesswindow import FramelessWindow
from PyQt5.QtCore import QTimer, QTime, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QPalette, QBrush
import os
import torch
import yaml
import cv2 as cv
from ultralytics import YOLO
from Yolov9.utils.torch_utils import select_device
from Yolov9.models.common import DetectMultiBackend
from Yolov9.API import runval
class ImageProcessingThread(QThread):
    update_progress = pyqtSignal(int)
    update_list_widget = pyqtSignal(list)

    def __init__(self, input_path, output_path, flag):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.flag = flag
        if flag == 'Yolov5':
            self.model = torch.hub.load('./Yolov5', 'custom', path='./Yolov5/best.pt', source='local')
        elif flag == 'Yolov8':
            self.model = YOLO("./Yolov8/best.pt")
        elif flag == 'Yolov9':
            self.device = select_device('')
            self.model = DetectMultiBackend('./Yolov9/best.pt', device=self.device)

    def run(self):
        # 获取文件夹内的所有文件名
        file_names = os.listdir(self.input_path)
        total_files = len(file_names)

        # 遍历每个文件名
        for i, file_name in enumerate(file_names):
            # 拼接完整的图片路径
            img_path = os.path.join(self.input_path, file_name)

            # 调用模型，得到结果
            if self.flag == 'Yolov9':
                results = runval(source=img_path, model=self.model)
            else:
                results = self.model(img_path)

            # 渲染结果
            if self.flag == 'Yolov8':
                frame = results[0].plot()
            elif self.flag == 'Yolov5':
                frame = results.render()[0]

            # 拼接完整的保存路径
            save_file = os.path.join(self.output_path, file_name)

            if self.flag == 'Yolov9':
                # 保存图片
                cv.imwrite(save_file, results)
            else:
                # 转换颜色空间
                bgr = cv.cvtColor(frame, cv.COLOR_RGB2BGR)
                # 保存图片
                cv.imwrite(save_file, bgr)

            # 更新进度条
            progress = int((i + 1) / total_files * 100)
            self.update_progress.emit(progress)

        # 更新listWidget
        self.update_list_widget.emit(file_names)

class MyMainWindow(Window):
    def __init__(self):
        super().__init__()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.Start.clicked.connect(self.start_processing)
        self.listWidget.itemClicked.connect(self.show_selected_image)

    def update_time(self):
        # 获取当前时间，并转换为00:00的格式
        current_time = QTime.currentTime()
        time_string = current_time.toString("hh:mm")

        # 设置Time标签的文本为当前时间
        self.Time.setText(time_string)

    def start_processing(self):
        # 获取输入和输出路径
        input_path = self.InputPath.text()
        output_path = self.OutputPath.text()

        # 创建并启动后台处理线程
        self.processing_thread = ImageProcessingThread(input_path, output_path, self.ComboBox.currentText())
        self.processing_thread.update_progress.connect(self.update_progress_bar)
        self.processing_thread.update_list_widget.connect(self.update_list_widget)
        self.processing_thread.start()

        # 禁用Start按钮
        self.Start.setEnabled(False)

    def update_progress_bar(self, value):
        # 更新进度条
        self.progressBar.setValue(value)

        # 当进度条到达100%时，恢复Start按钮状态
        if value == 100:
            self.Start.setEnabled(True)

    def update_list_widget(self, file_names):
        # 更新listWidget
        self.listWidget.clear()
        self.listWidget.addItems(file_names)

    def show_selected_image(self, item):
        # 获取选中的文件名
        selected_file = item.text()

        # 构造选中图片的路径
        selected_image_path = os.path.join(self.OutputPath.text(), selected_file)

        # 加载并在 ViewLabel QLabel 中显示图片
        pixmap = QPixmap(selected_image_path)
        self.ViewImg.setPixmap(pixmap)
        self.ViewImg.setScaledContents(True)



def main():
    app = QApplication(sys.argv)

    # 启动主程序
    main_window = MyMainWindow()
    main_window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()