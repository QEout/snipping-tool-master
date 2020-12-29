import sys
import time
from os.path import basename
import numpy as np
from PIL import ImageGrab
from PyQt5.QtCore import QPoint, Qt, QRegExp
from PyQt5.QtWidgets import QAction, QApplication, QPushButton, QMenu, QFileDialog, QMainWindow
from PyQt5.QtGui import QPixmap, QImage, QRegExpValidator
from PyQt5 import QtCore, QtWidgets
import SnippingTool
import cv2
from PictureWidget import PictureWidget
import os

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"


class Menu(QMainWindow):
    default_title = "工业识图"
    EXPORTS = ['.xls', '.txt']
    COLORS = ['red', 'black', 'blue', 'green', 'yellow']
    SIZES = [1, 3, 5, 7, 9, 50]
    IDENTIFIERS = ['文字识别', '数字识别', '文档识别', '试卷识别']

    # numpy_image is the desired image we want to display given as a numpy array.
    def __init__(self, numpy_image=None, backToBegin=False, snip_number=None, start_position=(300, 300, 350, 250)):
        super().__init__()
        self.yImage = numpy_image
        self.snip_number = snip_number
        self.backToBegin = backToBegin
        # MainWindow.setObjectName("MainWindow")
        # --------------------------------------------------------------------
        self.setStyleSheet("font-family: \"Microsoft YaHei\";\n"
                           "font-size:16px;\n"
                           "")

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        spacerItem = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        spacerItem1 = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        self.gridLayout.addItem(spacerItem1, 1, 8, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        self.gridLayout.addItem(spacerItem2, 3, 8, 1, 1)
        self.gridLayout.addItem(spacerItem, 5, 8, 1, 1)

        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 4, 1, 1)

        # 条件选择器
        self.conditionPick = QtWidgets.QComboBox(self.centralwidget)
        self.conditionPick.setObjectName("conditionPick")
        self.conditionPick.addItem("")
        self.conditionPick.addItem("")
        self.conditionPick.addItem("")
        self.conditionPick.addItem("")
        self.gridLayout.addWidget(self.conditionPick, 2, 1, 1, 1)

        # 条件编辑
        self.conditionEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.conditionEdit.setStyleSheet("border-radius:3px;\n"
                                         "background-color:rgb(220, 218, 214);\n"
                                         "color:white;\n"
                                         "font-weight:bold;\n"
                                         "font-size:20px;")
        self.conditionEdit.setText("")
        self.conditionEdit.setObjectName("conditionEdit")
        self.gridLayout.addWidget(self.conditionEdit, 2, 2, 1, 6)

        # 开始位置
        self.start_x = QtWidgets.QLineEdit(self.centralwidget)
        self.start_x.setStyleSheet("border-radius:3px;")
        self.start_x.setText(str(start_position[0]))
        self.start_x.setValidator(QRegExpValidator(QRegExp("[0-9]+$")))
        self.start_x.setObjectName("start_x")
        self.gridLayout.addWidget(self.start_x, 0, 1, 1, 1)
        self.start_y = QtWidgets.QLineEdit(self.centralwidget)
        self.start_y.setStyleSheet("border-radius:3px;")
        self.start_y.setText(str(start_position[1]))
        self.start_y.setValidator(QRegExpValidator(QRegExp("[0-9]+$")))
        self.start_y.setObjectName("start_y")
        self.gridLayout.addWidget(self.start_y, 0, 2, 1, 1)

        # 结束位置
        self.over_x = QtWidgets.QLineEdit(self.centralwidget)
        self.over_x.setStyleSheet("border-radius:3px;")
        self.over_x.setObjectName("over_x")
        self.over_x.setValidator(QRegExpValidator(QRegExp("[0-9]+$")))
        self.over_x.setText(str(start_position[2]))
        self.gridLayout.addWidget(self.over_x, 0, 5, 1, 1)
        self.gridLayout.addWidget(self.line, 0, 3, 1, 1)
        self.over_y = QtWidgets.QLineEdit(self.centralwidget)
        self.over_y.setStyleSheet("border-radius:3px;")
        self.over_y.setObjectName("over_y")
        self.over_y.setText(str(start_position[3]))
        self.over_y.setValidator(QRegExpValidator(QRegExp("[0-9]+$")))
        self.gridLayout.addWidget(self.over_y, 0, 6, 1, 1)

        # 开始按钮
        self.startButton = QtWidgets.QPushButton(self.centralwidget)
        self.startButton.setStyleSheet("\n"
                                       "background-color: #07c160;\n"
                                       "    border-radius: 3px;\n"
                                       "    padding:5px;\n"
                                       "color:white;")
        self.startButton.setAutoDefault(False)
        self.startButton.setDefault(False)
        self.startButton.setFlat(False)
        self.startButton.setObjectName("startButton")
        self.gridLayout.addWidget(self.startButton, 4, 6, 1, 2)

        # 测试按钮
        self.testButton = QtWidgets.QPushButton(self.centralwidget)
        self.testButton.setStyleSheet("background-color: #ff9800;\n"
                                      "    border-radius: 3px;\n"
                                      "    padding:5px;\n"
                                      "color:white;")
        self.testButton.setObjectName("testButton")
        self.gridLayout.addWidget(self.testButton, 4, 2, 1, 4)

        # 停止按钮
        self.stopButton = QtWidgets.QPushButton(self.centralwidget)
        self.stopButton.setStyleSheet("background-color:#f73131;\n"
                                      "    border-radius: 3px;\n"
                                      "    padding:5px;\n"
                                      "color:white;")
        self.stopButton.setObjectName("stopButton")
        self.gridLayout.addWidget(self.stopButton, 4, 0, 1, 2)

        # 手动取点
        self.getBySelf = QtWidgets.QPushButton(self.centralwidget)
        self.getBySelf.setObjectName("getBySelf")
        self.gridLayout.addWidget(self.getBySelf, 0, 7, 1, 1)
        self.getBySelf.clicked.connect(lambda action: self.get_by_self())

        # 控制台
        self.consoleArea = QtWidgets.QTextBrowser(self.centralwidget)
        self.consoleArea.setStyleSheet("")
        self.consoleArea.setObjectName("consoleArea")
        self.gridLayout.addWidget(self.consoleArea, 7, 3, 1, 5)

        # 图像界面
        self.graphicsView = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsView.setObjectName("graphicsView")
        self.gridLayout.addWidget(self.graphicsView, 7, 0, 1, 3)
        self.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar()
        self.statusbar.setObjectName("statusbar")
        self.retranslate_ui(self)
        QtCore.QMetaObject.connectSlotsByName(self)

        # --------------------------------------------------------------------
        self.brushSize = 3
        self.brushColor = Qt.red
        self.lastPoint = QPoint()
        self.total_snips = 0
        self.title = Menu.default_title

        new_snip_action = QAction('屏幕取点', self)
        new_snip_action.setShortcut('Ctrl+N')
        new_snip_action.setStatusTip('Ctrl+N')
        new_snip_action.triggered.connect(self.new_image_window)
        # 识别设置
        identifier_button = QPushButton("识别设置")
        # identifier_button.setText('文档')
        identifierMenu = QMenu()
        for identifier in Menu.IDENTIFIERS:
            identifierMenu.addAction(identifier)
        identifier_button.setMenu(identifierMenu)
        identifierMenu.triggered.connect(lambda action: change_identifier(action.text()))
        # Brush export
        brush_export_button = QPushButton("导出设置")
        exportMenu = QMenu()
        for export in Menu.EXPORTS:
            exportMenu.addAction(export)
        brush_export_button.setMenu(exportMenu)
        exportMenu.triggered.connect(lambda action: change_brush_export(action.text()))

        # Brush color
        brush_color_button = QPushButton("绘图刷")
        colorMenu = QMenu()
        for color in Menu.COLORS:
            colorMenu.addAction(color)
        brush_color_button.setMenu(colorMenu)
        colorMenu.triggered.connect(lambda action: change_brush_color(action.text()))
        brush_color_button = QPushButton("绘图刷")
        colorMenu = QMenu()
        for color in Menu.COLORS:
            colorMenu.addAction(color)
        brush_color_button.setMenu(colorMenu)
        colorMenu.triggered.connect(lambda action: change_brush_color(action.text()))
        # Brush Size
        brush_size_button = QPushButton("尺寸")
        sizeMenu = QMenu()
        for size in Menu.SIZES:
            sizeMenu.addAction("{0}px".format(str(size)))
        brush_size_button.setMenu(sizeMenu)
        sizeMenu.triggered.connect(lambda action: change_brush_size(action.text()))

        def change_brush_color(new_color):
            brush_color_button.setText(new_color)
            self.brushColor = eval("Qt.{0}".format(new_color.lower()))
            self.scene.change_color_size(self.brushColor, self.brushSize)

        def change_brush_size(new_size):
            brush_size_button.setText(new_size)
            self.brushSize = int(''.join(filter(lambda x: x.isdigit(), new_size)))
            self.scene.change_color_size(self.brushColor, self.brushSize)

        def change_brush_export(new_export):
            brush_export_button.setText(new_export)
            # self.brushExport = eval("Qt.{0}".format(new_export.lower()))

        def change_identifier(new_type):
            identifier_button.setText(new_type)
            # self.brushExport = eval("Qt.{0}".format(new_export.lower()))

        # Save
        save_action = QAction('保存', self)
        save_action.setShortcut('Ctrl+S')
        save_action.setStatusTip('Ctrl+S')
        save_action.triggered.connect(self.save_file)
        # 自动保存
        auto_save_action = QAction('自动保存', self)
        auto_save_action.setStatusTip('自动保存的图片位于根目录screenshot')
        auto_save_action.triggered.connect(self.auto_save)
        # Exit
        exit_window = QAction('退出', self)
        exit_window.setShortcut('Ctrl+Q')
        exit_window.setStatusTip('Ctrl+Q')
        exit_window.triggered.connect(self.close)
        # self.printf('ss')
        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(new_snip_action)
        self.toolbar.addAction(save_action)
        self.toolbar.addAction(auto_save_action)
        self.toolbar.addWidget(identifier_button)
        self.toolbar.addWidget(brush_export_button)
        self.toolbar.addWidget(brush_color_button)
        self.toolbar.addWidget(brush_size_button)
        self.toolbar.addAction(exit_window)
        self.snippingTool = SnippingTool.SnippingWidget()
        # self.setGeometry(*start_position)
        # print(self.snippingTool.begin)
        # From the second initialization, both arguments will be valid
        if numpy_image is not None and snip_number is not None:
            self.image = self.convert_numpy_img_to_qpixmap(numpy_image)
            self.nonePic = False
        # self.change_and_set_title("Snip #{0}".format(snip_number))
        else:
            self.image = QPixmap("background.PNG")
            self.nonePic = True
            self.change_and_set_title(Menu.default_title)
        self.scene = PictureWidget(self.image, self.brushColor, self.brushSize, [], self.backToBegin)  # 创建场景
        self.scene.addPixmap(self.image)
        self.graphicsView.setScene(self.scene)
        self.show()
        self.printf('程序初始化成功')
        # self.check_web()

    # snippingTool.start() will open a new window, so if this is the first snip, close the first wind
    def contextMenuEvent(self, event):
        if not self.nonePic:
            self.reloadPicture()

    def reloadPicture(self):
        self.image = self.convert_numpy_img_to_qpixmap(self.yImage)
        self.scene = PictureWidget(self.image, self.brushColor, self.brushSize, self.scene.brushStatus,
                                   self.backToBegin)  # 创建场景
        self.scene.backToLastStep()
        self.scene.addPixmap(self.image)
        self.graphicsView.setScene(self.scene)
        self.update()

    def new_image_window(self):
        self.printf('正在截屏...')
        self.printf('按Q退出')
        self.total_snips += 1
        self.snippingTool.start()
        time.sleep(1)
        self.close()

    def printf(self, myStr):
        self.cursor = self.consoleArea.textCursor()
        self.consoleArea.append(str(myStr))  # 在指定的区域显示提示信息
        self.consoleArea.moveCursor(self.cursor.End)  # 光标移到最后，这样就会自动显示出来
        QtWidgets.QApplication.processEvents()  # 一定加上这个功能，不然有卡顿

    def retranslate_ui(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        # MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label_2.setText(_translate("MainWindow", "起始位置"))
        self.stopButton.setText(_translate("MainWindow", "停止"))
        self.conditionPick.setItemText(0, _translate("MainWindow", "包含"))
        self.conditionPick.setItemText(1, _translate("MainWindow", "不包含"))
        self.conditionPick.setItemText(2, _translate("MainWindow", "等于"))
        self.conditionPick.setItemText(3, _translate("MainWindow", "不等于"))
        self.label_3.setText(_translate("MainWindow", "选择条件"))
        self.label.setText(_translate("MainWindow", "结束位置"))
        self.getBySelf.setText(_translate("MainWindow", "手动取点"))
        self.startButton.setText(_translate("MainWindow", "开始"))
        self.testButton.setText(_translate("MainWindow", "测试"))
        self.consoleArea.setHtml(_translate("MainWindow",
                                            "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                                            "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                                            "p, li { white-space: pre-wrap; }\n"
                                            "</style></head><body style=\" font-family:\'Microsoft YaHei\'; font-size:16px; font-weight:400; font-style:normal;\">\n"
                                            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'SimSun\'; font-size:9pt;\"></span></p></body></html>"))
        self.setStatusBar(self.statusbar)

    def get_by_self(self):
        self.showMinimized()
        x1 = min(int(self.start_x.text()), int(self.over_x.text()))
        y1 = min(int(self.start_y.text()), int(self.over_y.text()))
        x2 = max(int(self.start_x.text()), int(self.over_x.text()))
        y2 = max(int(self.start_y.text()), int(self.over_y.text()))
        bbox = (x1, y1, x2, y2)
        img = ImageGrab.grab(bbox)
        # print(img)
        img = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)
        self.yImage = img
        self.reloadPicture()
        self.nonePic = False
        self.showNormal()

    def save_file(self):
        file_path, name = QFileDialog.getSaveFileName(self, "保存图片", self.title, "PNG Image file (*.png)")
        if file_path:
            self.image.save(file_path)
            self.change_and_set_title(basename(file_path))
            print(self.title, 'Saved')

    def check_web(self):
        exit_code = os.system('ping aip.baidubce.com')
        if exit_code != 0:
            self.printf('网络连接错误')

    def auto_save(self):
        file_path, name = QFileDialog.getSaveFileName(self, "Save file", self.title, "PNG Image file (*.png)")
        if file_path:
            self.image.save(file_path)
            self.change_and_set_title(basename(file_path))
            print(self.title, 'Saved')

    def change_and_set_title(self, new_title):
        self.title = new_title
        self.setWindowTitle(self.title)

    # TODO exit application when we exit all windows
    def closeEvent(self, event):
        event.accept()

    @staticmethod
    def convert_numpy_img_to_qpixmap(np_img):
        height, width, channel = np_img.shape
        bytesPerLine = 3 * width
        return QPixmap(QImage(np_img.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainMenu = Menu(QMainWindow())
    # mainMenu.resize(943, 505)
    sys.exit(app.exec_())
