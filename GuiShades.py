from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtCore import QDateTime, Qt, QTimer, QThread, pyqtSignal, QRectF, QPoint, QSize
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *
import cv2
from PIL import Image
import numpy as np
from os import walk
from Shades import ColorShades



class WidgetGallery(QDialog):
    shades_thread_signal = pyqtSignal(list)

    def __init__(self, parent=None):
        super(WidgetGallery, self).__init__(parent)

        self.originalPalette = QApplication.palette()
        # self.setMouseTracking(True)

        styleComboBox = QComboBox()
        styleComboBox.addItems(QStyleFactory.keys())
        self.create_parameter_groupbox()
        # self.createCanvasBox_2()

        topLayout = QHBoxLayout()
        self.input_img_groupbox = self.create_input_image_groupbox()
        self.output_img_groupbox = self.create_ouput_image_groupbox()
        self.parameterGroupBox.setFixedWidth(400)
        mainLayout = QGridLayout()
        mainLayout.addLayout(topLayout, 0, 0, 1, 2)
        mainLayout.addWidget(self.parameterGroupBox, 0, 0)
        mainLayout.addWidget(self.input_img_groupbox, 0, 1)
        mainLayout.addWidget(self.output_img_groupbox, 0, 2)

        # mainLayout.addWidget(self.canvasGroupBox_2, 1, 2)
        self.connect_signals()
        self.init_variables()
        self.changeStyle('Fusion')
        self.setLayout(mainLayout)

    def changeStyle(self, styleName):
        QApplication.setStyle(QStyleFactory.create(styleName))

    def connect_signals(self):
        self.openfile_dialog_btn.clicked.connect(self.openfile_dialog)

    def init_variables(self):
        self.current_img_path = 'E:\Work\StructureTranferProject\Makalu\Colors Extracted from Swing and Weave Designs and Enlarged\Color_12.Large.jpg'
        self.current_img = np.array(Image.open(self.current_img_path))
        self.render_image(self.current_img, self.input_scene)
        self.choosed_color_list = []
        self.colorShadesObj = ColorShades()

    def create_parameter_groupbox(self):
        self.parameterGroupBox = QGroupBox("Parameters")

        self.process_image_btn = QPushButton("Process Image")
        self.openfile_dialog_btn = QPushButton('Open Image')

        self.color_list_view = QListWidget()
        self.shades_lbl = QLabel()
        self.time_label = QLabel()

        layout = QGridLayout()
        layout.addWidget(self.openfile_dialog_btn, 0 , 0, 2, 0)
        layout.addWidget(self.color_list_view, 2, 0)
        layout.addWidget(self.shades_lbl, 3, 0)
        layout.addWidget(self.process_image_btn, 10, 0, 2, 0)
        layout.addWidget(self.time_label, 11,0,2,0)

        self.parameterGroupBox.setLayout(layout)

    def create_input_image_groupbox(self):
        groupbox = QGroupBox('Input')
        layout = QVBoxLayout()
        self.input_scene = QGraphicsScene()
        self.input_view = QGraphicsView(self.input_scene)
        self.input_view.mousePressEvent = self.get_coordinate
        layout.addWidget(self.input_view)
        groupbox.setLayout(layout)
        return groupbox

    def create_ouput_image_groupbox(self):
        groupbox = QGroupBox('Output')
        layout = QVBoxLayout()
        self.output_scene = QGraphicsScene()
        self.output_view = QGraphicsView(self.output_scene)
        layout.addWidget(self.output_view)
        groupbox.setLayout(layout)
        return groupbox

    def get_coordinate(self, event):
        pos = self.input_view.mapToScene(event.pos())
        x = int(pos.x())
        y = int(pos.y())
        print(x, y)
        itm = QListWidgetItem(str(self.current_img[y, x]))
        itm.setIcon(QIcon(self.create_tile(self.current_img[y, x])))
        self.color_list_view.addItem(itm)
        self.choosed_color_list.append(tuple(self.current_img[y, x]))
        hsv_img = Image.fromarray(self.current_img).convert('HSV')
        choosed_hsv = hsv_img.getpixel((x,y))
        shades_img, shades_array = self.colorShadesObj.create_shades_of_color(choosed_hsv, 'a')
        self.shades_lbl.setPixmap(QPixmap(self.numpy_to_pixmap(shades_img)))
        self.colorShadesObj.replicate_image_with_new_shades(shades_array, self.current_img)
        print('finised')

    def openfile_dialog(self):
        filename = QFileDialog.getOpenFileName(self, "Select Image")
        if filename[0] != '':
            print(filename)
            self.current_img_path = filename[0]
            self.current_img = np.asarray(Image.open(self.current_img_path).convert('RGB'))
            # self.input_scene = QImage(filename[0])
            self.render_image(self.current_img, self.input_scene)

    def render_image(self, img, place_holder):
        place_holder.clear()
        height, width, channel = img.shape
        bytesPerLine = 3 * width
        qImg = QImage(img.data, width, height, bytesPerLine, QImage.Format_RGB888)
        pixmap = QPixmap(qImg)
        place_holder.addPixmap(pixmap)

    def create_tile(self, array):
        img = np.zeros((32, 32, 3), dtype='uint8')
        img[:, :, 0] = array[0]
        img[:, :, 1] = array[1]
        img[:, :, 2] = array[2]
        return QPixmap(self.numpy_to_pixmap(img))

    def numpy_to_pixmap(self, img):
        height, width, channel = img.shape
        bytesPerLine = 3 * width
        qImg = QImage(img.data, width, height, bytesPerLine, QImage.Format_RGB888)
        return qImg

    @QtCore.pyqtSlot(list)
    def worker_thread_complete(self, returned_list):
        print('finished')
        output_img = np.asarray(Image.open(returned_list[0]).convert('RGB'))
        self.render_image(output_img, self.output_scene)
        self.time_label.setText('Inpainting Time = '+str(returned_list[1]))

class WorkerThread(QThread):

    shades_thread_signal = pyqtSignal(list)
    def __init__(self, parent=None):
        super(WorkerThread, self).__init__(parent)
        self.image_to_process = None
        self.image_path = ''
        self.parameter_list = None

    @QtCore.pyqtSlot()
    def run(self):
        return_list = []

        print('still in thread')
        self.shades_thread_signal.emit(return_list)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    gallery = WidgetGallery()
    screen = app.primaryScreen()
    h = screen.size().height()
    w = screen.size().width()
    gallery = WidgetGallery()
    gallery.setFixedSize(screen.size().width()-50, screen.size().height()-100)
    gallery.show()
    sys.exit(app.exec_())
