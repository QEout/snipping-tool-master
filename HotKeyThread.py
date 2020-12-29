# ''
# 另开一个线程用于捕捉全局热键，以防止主线程堵塞导致假死
# 具体逻辑如下:
# 1、注册一个全局热键，callback为self.start()，即启动线程；
# 2、线程启动后，通过run()函数发送一个信号；
# 3、信号对应的槽函数为具体要执行的内容，在这里的目的是隐藏|弹出后台窗口。
# '''
from PyQt5 import QtCore
from PyQt5.QtCore import QThread, pyqtSignal
from system_hotkey import SystemHotkey


class HotKeyThread(QThread, SystemHotkey):
    trigger = pyqtSignal()

    def __init__(self, UI):
        self.ui = UI
        super(HotKeyThread, self).__init__()
        self.register(('control', 'x'), callback=lambda x: self.start())
        self.trigger.connect(self.hotKeyEvent)

    def run(self):
        self.trigger.emit()

    def hotKeyEvent(self):
        self.ui.gotion_event()

    def quitThread(self):
        self.unregister(('control', 'x'))
        self.quit()
        print('good')
