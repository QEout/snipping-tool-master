import sys
import time
from os.path import basename
import numpy as np
from PIL import ImageGrab
from PyQt5.QtCore import QPoint, Qt, QRegExp
from PyQt5.QtMultimedia import QSound
from PyQt5.QtWidgets import QAction, QApplication, QPushButton, QMenu, QFileDialog, QMainWindow, QWidget, QSizePolicy
from PyQt5.QtGui import QPixmap, QImage, QRegExpValidator, QIcon, QDesktopServices
from PyQt5 import QtCore, QtWidgets
from aip import AipOcr
import xlwt
import SnippingTool
import cv2

from HotKeyThread import HotKeyThread
from PictureWidget import PictureWidget
import os
import PyQt5.QtCore as qc

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
settings = qc.QSettings("config.ini", qc.QSettings.IniFormat)
biao = xlwt.Workbook()
worksheet = biao.add_sheet('sheet1')


class Menu(QMainWindow):
    default_title = "工业识图"
    EXPORTS = ['.xls', '.txt']
    COLORS = ['white', 'black', 'blue', 'green', 'red']
    SIZES = [3, 1, 5, 7, 9, 50]
    IDENTIFIERS = ['文字识别', '数字识别', '文档识别', '试卷识别']

    # numpy_image is the desired image we want to display given as a numpy array.
    def __init__(self, numpy_image=None, backToBegin=False, snip_number=None, start_position=(300, 300, 350, 250)):
        super().__init__()
        self.yImage = numpy_image
        self.snip_number = snip_number
        self.backToBegin = backToBegin

        # 初始化配置
        settings.setIniCodec("UTF-8")
        self.windowOnTop = int(settings.value("TOOLCONFIG/window_onTop"))
        self.brushSize = settings.value("TOOLCONFIG/sizes_config")
        self.brushColorStr = settings.value("TOOLCONFIG/colors_config")
        self.brushColor = eval('Qt.{0}'.format(self.brushColorStr))
        self.export = settings.value("TOOLCONFIG/exports_config")
        self.identify = settings.value("TOOLCONFIG/identifies_config")
        self.autoSave = int(settings.value("TOOLCONFIG/auto_save_config"))
        self.readNum = 0
        self.endMusic = QSound('source/ding.wav')
        # 初始化识图
        APP_ID = settings.value("READCONFIG/appId")
        API_KEY = settings.value("READCONFIG/apiKey")
        SECRET_KEY = settings.value("READCONFIG/secretKey")
        self.client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
        # MainWindow.setObjectName("MainWindow")
        # --------------------------------------------------------------------
        self.setStyleSheet("font-family: \"Microsoft YaHei\";\n"
                           "font-size:16px;\n"
                           )

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
                                         "background-color:#b6b6b6;\n"
                                         "color:white;\n"
                                         "padding:2px;\n"
                                         "font-weight:bold;\n"
                                         "font-size:18px;")
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
        self.startButton.setStyleSheet("QPushButton{border-radius:3px;\n"
                                       "background-color:#b6b6b6;\n"
                                       "color:white;\n"
                                       "padding:5px;\n"
                                       "font-weight:bold;}\n"
                                       ":hover{background-color:#4caf50;}"
                                       )
        self.startButton.setAutoDefault(False)
        self.startButton.setDefault(False)
        self.startButton.setFlat(False)
        self.startButton.setObjectName("startButton")
        self.startButton.clicked.connect(self.start_reading)
        self.gridLayout.addWidget(self.startButton, 4, 6, 1, 2)

        # 测试按钮
        self.testButton = QtWidgets.QPushButton(self.centralwidget)
        self.testButton.setStyleSheet("QPushButton{border-radius:3px;\n"
                                      "background-color:#b6b6b6;\n"
                                      "color:white;\n"
                                      "padding:5px;\n"
                                      "font-weight:bold;}\n"
                                      ":hover{background-color:#ff9800}"
                                      )
        self.testButton.setObjectName("testButton")
        self.testButton.clicked.connect(self.start_testing)
        self.gridLayout.addWidget(self.testButton, 4, 2, 1, 4)

        # 停止按钮
        self.stopButton = QtWidgets.QPushButton(self.centralwidget)
        self.stopButton.setStyleSheet("QPushButton{border-radius:3px;\n"
                                      "background-color:#b6b6b6;\n"
                                      "color:white;\n"
                                      "padding:5px;\n"
                                      "font-weight:bold;}\n"
                                      ":hover{background-color:#f44336}"
                                      )
        self.stopButton.setObjectName("stopButton")
        self.stopButton.clicked.connect(self.stop_task)
        self.gridLayout.addWidget(self.stopButton, 4, 0, 1, 2)

        # 手动取点
        self.getBySelf = QtWidgets.QPushButton(self.centralwidget)
        self.getBySelf.setObjectName("getBySelf")
        self.gridLayout.addWidget(self.getBySelf, 0, 7, 1, 1)
        self.getBySelf.clicked.connect(lambda action: self.get_by_self())

        # 控制台
        self.consoleArea = QtWidgets.QTextBrowser(self.centralwidget)
        self.consoleArea.setObjectName("consoleArea")
        self.gridLayout.addWidget(self.consoleArea, 7, 3, 1, 5)
        # self.consoleArea.acceptRichText(True)
        self.consoleArea.setOpenLinks(False)
        self.consoleArea.anchorClicked.connect(self.open_file)
        # 图像界面
        self.graphicsView = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsView.setObjectName("graphicsView")
        self.gridLayout.addWidget(self.graphicsView, 7, 0, 1, 3)
        self.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar()
        self.statusbar.setObjectName("statusbar")
        self.translate_ui(self)
        QtCore.QMetaObject.connectSlotsByName(self)

        # --------------------------------------------------------------------
        # self.brushSize = 3
        # self.brushColor = Qt.red

        self.lastPoint = QPoint()
        self.total_snips = 0
        self.title = Menu.default_title

        new_snip_action = QAction('屏幕取点', self)
        new_snip_action.setShortcut('Ctrl+N')
        new_snip_action.setStatusTip('Ctrl+N')
        new_snip_action.triggered.connect(self.new_image_window)

        # 识别设置
        identifier_button = QPushButton("识别设置")
        identifier_button.setStatusTip('当前：' + self.identify)
        identifierMenu = QMenu()
        for identifier in Menu.IDENTIFIERS:
            identifierMenu.addAction(identifier)
        identifier_button.setMenu(identifierMenu)
        identifierMenu.triggered.connect(lambda action: change_identifier(action.text()))

        # Brush export
        brush_export_button = QPushButton("导出设置")
        brush_export_button.setStatusTip('当前：' + self.export)
        exportMenu = QMenu()
        for export in Menu.EXPORTS:
            exportMenu.addAction(export)
        brush_export_button.setMenu(exportMenu)
        exportMenu.triggered.connect(lambda action: change_brush_export(action.text()))

        # Brush color
        brush_color_button = QPushButton("绘图刷")
        brush_color_button.setStatusTip('当前：' + self.brushColorStr)
        colorMenu = QMenu()
        for color in Menu.COLORS:
            colorMenu.addAction(color)
        brush_color_button.setMenu(colorMenu)
        colorMenu.triggered.connect(lambda action: change_brush_color(action.text()))

        # Brush Size
        brush_size_button = QPushButton("尺寸")
        brush_size_button.setStatusTip('当前：' + self.brushSize + 'px')
        sizeMenu = QMenu()
        for size in Menu.SIZES:
            sizeMenu.addAction("{0}px".format(str(size)))
        brush_size_button.setMenu(sizeMenu)
        sizeMenu.triggered.connect(lambda action: change_brush_size(action.text()))

        def change_brush_color(new_color):
            brush_color_button.setText(new_color)
            self.brushColor = eval("Qt.{0}".format(new_color.lower()))
            settings.setValue("TOOLCONFIG/colors_config", new_color)
            brush_color_button.setStatusTip('当前：' + new_color)
            self.scene.change_color_size(self.brushColor, self.brushSize)

        def change_brush_size(new_size):
            brush_size_button.setText(new_size)
            self.brushSize = int(''.join(filter(lambda x: x.isdigit(), new_size)))
            settings.setValue("TOOLCONFIG/size_config", self.brushSize)
            brush_size_button.setStatusTip('当前：' + new_size)
            self.scene.change_color_size(self.brushColor, self.brushSize)

        def change_brush_export(new_export):
            brush_export_button.setText(new_export)
            self.export = new_export
            settings.setValue("TOOLCONFIG/exports_config", self.export)
            identifier_button.setStatusTip('当前：' + self.identify)
            # self.brushExport = eval("Qt.{0}".format(new_export.lower()))

        def change_identifier(new_type):
            self.identify = new_type
            settings.setValue("TOOLCONFIG/identifies_config", self.identify)
            identifier_button.setText(new_type)
            identifier_button.setStatusTip('当前：' + self.identify)
            # self.brushExport = eval("Qt.{0}".format(new_export.lower()))

        def window_onTop():
            if self.windowOnTop == 0:
                self.windowOnTop = 1
                self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
                onTop_action.setIcon(QIcon("source/onTop_a.png"))
            else:
                self.windowOnTop = 0
                self.setWindowFlags(QtCore.Qt.Widget)
                onTop_action.setIcon(QIcon("source/onTop.png"))
            settings.setValue("TOOLCONFIG/window_onTop", self.windowOnTop)
            self.show()

        # Save
        save_action = QAction('保存', self)
        save_action.setShortcut('Ctrl+S')
        save_action.setStatusTip('保存的图片位于根目录screenshot')
        save_action.triggered.connect(self.save_file)

        # 自动保存
        # def auto_save():
        #     print(self.autoSave)
        #     if self.autoSave == 0:
        #         self.autoSave = 1
        #         open_file_action.setText("自动保存√")
        #     else:
        #         self.autoSave = 0
        #         open_file_action.setText("自动保存")
        #     settings.setValue("TOOLCONFIG/auto_save_config", self.autoSave)
        # 文件打开识别

        open_file_action = QAction('打开文件', self)
        open_file_action.setStatusTip('只支持图片格式')
        open_file_action.triggered.connect(self.open_file)

        # Exit
        exit_window = QAction('退出', self)
        exit_window.setShortcut('Ctrl+Q')
        exit_window.setStatusTip('Ctrl+Q')
        exit_window.triggered.connect(self.close)

        # 窗口置顶
        onTop_action = QAction(self)
        if self.windowOnTop == 1:
            onTop_action.setIcon(QIcon("source/onTop_a.png"))
            self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        else:
            onTop_action.setIcon(QIcon("source/onTop.png"))
        onTop_action.setShortcut('Ctrl+Q')
        onTop_action.setStatusTip('Ctrl+Q')
        onTop_action.triggered.connect(window_onTop)

        # self.printf('ss')
        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(new_snip_action)
        self.toolbar.addAction(open_file_action)
        self.toolbar.addAction(save_action)

        self.toolbar.addWidget(identifier_button)
        self.toolbar.addWidget(brush_export_button)
        self.toolbar.addWidget(brush_color_button)
        self.toolbar.addWidget(brush_size_button)
        self.toolbar.addAction(exit_window)
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.toolbar.addWidget(spacer)
        self.toolbar.addAction(onTop_action)
        self.snippingTool = SnippingTool.SnippingWidget()
        # self.setGeometry(*start_position)
        # print(self.snippingTool.begin)
        # From the second initialization, both arguments will be valid
        if numpy_image is not None and snip_number is not None:
            self.image = self.convert_numpy_img_to_qpixmap(numpy_image)
            self.nonePic = False
        # self.change_and_set_title("Snip #{0}".format(snip_number))
        else:
            self.image = QPixmap("source/background.png")
            self.nonePic = True
            self.change_and_set_title(Menu.default_title)
        self.scene = PictureWidget(self.image, self.brushColor, self.brushSize, [], self.backToBegin)  # 创建场景
        self.scene.addPixmap(self.image)
        self.graphicsView.setScene(self.scene)
        self.hotKey = HotKeyThread(self)
        self.show()
        self.printf('程序初始化成功')
        # self.check_web()

    # 函数区

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
        self.hotKey.quitThread()
        self.total_snips += 1
        self.snippingTool.start()
        self.close()

    def closeEvent(self, event):
        sys.exit(app.exec_())

    # def get_file_content(filePath):
    #     with open(filePath, 'rb') as fp:
    #         return fp.read()

    def gotion_event(self):
        self.get_by_self(True)
        self.start_reading()

    def start_reading(self):
        self.printf('开始识图...')
        # 获得当前时间时间戳
        now = int(time.time())  # 这是时间戳
        # 转换为其他日期格式,如:"%Y-%m-%d %H:%M:%S"
        timeArray = time.localtime(now)
        nowTime = time.strftime("%m%d%H%M", timeArray)
        self.image.save(os.path.join('screenshots', nowTime + str(self.readNum) + ".png"))
        self.printf("screenshots/%s.png" % (nowTime + str(self.readNum)), 1)
        # # 获取图片的二进制数据
        with open("screenshots/%s.png" % (nowTime + str(self.readNum)), 'rb') as fp:
            image = fp.read()
        """ 调用通用文字识别（高精度版） """
        text = self.client.basicAccurate(image)
        textList = text['words_result']
        self.printf('识别结果：' + str(textList))
        num1 = 0
        lastResult = []
        for i in textList:
            if 'C' in i['words']:
                print('过滤词：' + i['words'])
            else:
                worksheet.write(self.readNum, num1, i['words'])
                biao.save('export/export.xls')
                lastResult.append(i['words'])
                num1 += 1
        self.readNum += 1
        self.printf(str(lastResult))
        self.endMusic.play()

        self.printf("")

    def start_testing(self):
        self.printf('开始测试...')

    def stop_task(self):
        self.printf('任务已停止')

    def printf(self, myStr, type=0):
        # self.cursor()= self.consoleArea.textCursor()
        if type == 0:
            self.consoleArea.append(str(myStr))  # 在指定的区域显示提示信息
        # fileLink
        if type == 1:
            self.consoleArea.append("<a href=\"%s\">%s</a>" % (myStr, myStr))
        # self.consoleArea.moveCursor(self.cursor.End)  # 光标移到最后，这样就会自动显示出来
        QtWidgets.QApplication.processEvents()  # 一定加上这个功能，不然有卡顿



    def translate_ui(self, MainWindow):
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

    def get_by_self(self, custom=False):
        print(not custom)
        if self.start_x.text() == '':
            self.start_x.setText('0')
        if self.over_x.text() == '':
            self.over_x.setText('0')
        if self.start_y.text() == '':
            self.start_y.setText('0')
        if self.over_y.text() == '':
            self.over_y.setText('0')
        x1 = min(int(self.start_x.text()), int(self.over_x.text()))
        y1 = min(int(self.start_y.text()), int(self.over_y.text()))
        x2 = max(int(self.start_x.text()), int(self.over_x.text()))
        y2 = max(int(self.start_y.text()), int(self.over_y.text()))
        bbox = (x1, y1, x2, y2)
        if x1 == x2 or y1 == y2:
            self.printf('无法找到取点区域，位置点构成了直线，请检查')
            return
        self.showMinimized()
        img = ImageGrab.grab(bbox)
        # print(img)
        img = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)
        self.yImage = img
        self.reloadPicture()
        self.nonePic = False
        if not custom:
            self.showNormal()

    def save_file(self):
        # 获得当前时间时间戳
        now = int(time.time())  # 这是时间戳
        # 转换为其他日期格式,如:"%Y-%m-%d %H:%M:%S"
        timeArray = time.localtime(now)
        nowTime = time.strftime("%m%d%H%M", timeArray)
        file_path, name = QFileDialog.getSaveFileName(self, "保存图片", nowTime, "PNG Image file (*.png)")
        if file_path:
            self.image.save(file_path)
            self.change_and_set_title(basename(file_path))
            print(self.title, 'Saved')

    def open_file(self):
        filename = QFileDialog.getOpenFileName(self, 'open file', '')
        with open(filename[0], 'r') as fp:
            image = fp.read()

    def check_web(self):
        exit_code = os.system('ping aip.baidubce.com')
        if exit_code != 0:
            self.printf('网络连接错误')

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
    sys.exit(app.exec_())
