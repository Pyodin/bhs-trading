from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys


class Window(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Python ")

        self.setGeometry(100, 100, 600, 400)

        self.UiComponents()

        self.show()

    def UiComponents(self):
        self.combo_box = QComboBox(self)

        self.combo_box.setGeometry(200, 150, 150, 30)

        geek_list = ["Sayian", "Super Saiyan", "Super Sayian 2"]

        self.combo_box.addItems(geek_list)

        edit = QLineEdit(self)

        self.combo_box.setLineEdit(edit)


App = QApplication(sys.argv)

window = Window()

sys.exit(App.exec()) 