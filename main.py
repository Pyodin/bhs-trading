# coding: utf-8
import pathlib

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve
import sys

from AbstractTableModel import (
    PandasModelPersisted,
    PandasModeTotalWealth,
    PandasPerCategory,
)

# IMPORT GUI FILE
import resource_rc


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self)
        uic.loadUi("main.ui", self)

        self.info_path = pathlib.Path("account_info") / "account.csv"

        self.model = PandasModelPersisted(self.info_path)
        self.init_ui()

    def init_ui(self):
        def slideLeftMenu():
            width = self.leftMenuF.width()
            nextWidth = 0 if width == 200 else 200

            self.animation = QPropertyAnimation(self.leftMenuF, b"maximumWidth")
            self.animation.setDuration(250)
            self.animation.setStartValue(width)
            self.animation.setEndValue(nextWidth)
            self.animation.setEasingCurve(QEasingCurve.InOutQuart)
            self.animation.start()

        def load_account_info():
            self.tableView.setModel(self.model)
            self.update_displayed_data()

        def delete_row():
            if not self.tableView.selectedIndexes():
                return
            else:
                index = self.tableView.selectedIndexes()[0].row()
            self.model.removeRows(index)

        self.MenuBt.clicked.connect(slideLeftMenu)
        self.home_bt.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.page_2)
        ).
        

        load_account_info()
        self.model.dataChanged.connect(self.update_displayed_data)
        self.add_row_bt.clicked.connect(self.model.insertRows)
        self.del_row_bt.clicked.connect(delete_row)

    def update_displayed_data(self):
        model_2 = PandasModeTotalWealth(self.info_path)
        self.tableView_2.setModel(model_2)

        model_3 = PandasPerCategory(self.info_path)
        self.tableView_3.setModel(model_3)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
