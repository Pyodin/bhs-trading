# coding: utf-8
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve
import sys

#IMPORT GUI FILE
import resource_rc

# MAIN WINDOW CLASS
class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self)
        uic.loadUi("main.ui", self)

        self.MenuBt.clicked.connect(self.slideLeftMenu)

    def slideLeftMenu(self):

        width = self.leftMenuF.width()
        nextWidth = 0 if width == 200 else 200

        self.animation = QPropertyAnimation(self.leftMenuF, b"maximumWidth")
        self.animation.setDuration(250)
        self.animation.setStartValue(width)
        self.animation.setEndValue(nextWidth)
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        self.animation.start()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
