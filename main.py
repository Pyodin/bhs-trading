# coding: utf-8
import pathlib

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve
import sys

from AbstractTableModel import *

# IMPORT GUI FILE
import resource_rc


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self)
        uic.loadUi("main.ui", self)

        self.info_path = pathlib.Path("account_info") / "account.csv"
        dataframe = pd.read_csv(self.info_path)

        self.model = PandasModelPersisted(dataframe)
        self.comboDelegate = ComboDelegate(self)
        self.init_ui()
        self.populate_ui()

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

        self.MenuBt.clicked.connect(slideLeftMenu)
        self.home_bt.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.page_2)
        )

        self.model.dataChanged.connect(self.update_displayed_data)
        self.add_row_bt.clicked.connect(self.model.insertRows)
        self.del_row_bt.clicked.connect(self.delete_row_from_model)

    def populate_ui(self):
        self.tableView.setModel(self.model)
        self.tableView.setItemDelegateForColumn(1, self.comboDelegate)
        self.update_displayed_data()

    def update_displayed_data(self):

        model_2 = PandasModeTotalWealth(self.info_path)
        self.tableView_2.setModel(model_2)
        # self.tableView_2.verticalHeader().setSectionResizeMode(1, 300)

        model_3 = PandasPerCategory(self.info_path)
        self.tableView_3.setModel(model_3)

    def delete_row_from_model(self):
        if not self.tableView.selectedIndexes():
            return
        cpt = {index.row() for index in self.tableView.selectedIndexes()}
        self.model.removeRows(self.tableView.selectedIndexes()[0].row(), len(cpt))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
