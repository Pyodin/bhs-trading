# coding: utf-8
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve
import sys

# ----------------------------------
# IMPORT GUI FILE
# ----------------------------------

# ----------------------------------
# IMPORT RESOURCE FILE
# ----------------------------------

# ----------------------------------
# MAIN WINDOW CLASS
class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self)
        uic.loadUi("main.ui", self)

# ----------------------------------


# ----------------------------------
# EXECUTE APP


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
# ----------------------------------