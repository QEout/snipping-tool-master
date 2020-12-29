from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtCore import Qt, QPoint, QRect
import os

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"


class PictureWidget(QGraphicsScene):
    def __init__(self, image, brushColor, brushSize, brushStatus=[],backToBegin=False):
        print(backToBegin)
        self.brushSize = brushSize
        self.brushColor = brushColor
        self.brushStatus = brushStatus
        self.lastPoint = QPoint()
        self.backToBegin = backToBegin
        self.image = image
        self.pointlist = []
        super(PictureWidget, self).__init__()

    def drawForeground(self, painter: QtGui.QPainter, rect: QtCore.QRectF):
        rect = QRect(0, 0, self.image.width(), self.image.height())
        painter.drawPixmap(rect, self.image)

    def mousePressEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            self.lastPoint = event.scenePos()

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            if not self.backToBegin:
                self.pointlist.append(event.scenePos())
            painter = QPainter(self.image)
            painter.setPen(QPen(self.brushColor, self.brushSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawLine(self.lastPoint, event.scenePos())
            self.lastPoint = event.scenePos()
            self.update()

    def mouseReleaseEvent(self, event):
        if len(self.pointlist) > 0:
            self.brushStatus.append(self.pointlist)
        self.pointlist = []
        print('release')

    def change_color_size(self, new_color, new_size):
        self.brushColor = new_color
        self.brushSize = new_size

    def backToLastStep(self):
        if len(self.brushStatus) > 0:
            painter = QPainter(self.image)
            painter.setPen(QPen(self.brushColor, self.brushSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            self.brushStatus.pop()
            lineList = self.brushStatus
            for line in lineList:
                pos = 1
                for point in line:
                    painter.drawLine(point, line[pos])
                    # print(pos)
                    pos += 1
                    if pos == len(line):
                        break
