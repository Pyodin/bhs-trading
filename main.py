# coding: utf-8
import pathlib
import time

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve
import sys

from PyQt5.QtWidgets import QMessageBox

from AbstractTableModel import *
from ComboDelegate import *

# IMPORT GUI FILE
import resource_rc


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self)
        uic.loadUi("main.ui", self)

        self.info_path = pathlib.Path("account_info") / "account.csv"
        self.dataframe = pd.read_csv(self.info_path)

        self.account_model = PandasModelPersisted(self.dataframe.copy())
        self.evol_model = PandasModeTotalWealth(self.dataframe.copy())
        self.detail_model = PandasPerCategory(self.dataframe.copy())
        self.comboDelegate = ComboDelegate(self)

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

        self.MenuBt.clicked.connect(slideLeftMenu)

        # Three button
        self.add_row_bt.clicked.connect(self.account_model.insertRows)
        self.del_row_bt.clicked.connect(self.delete_row_from_model)
        self.save_bt.clicked.connect(self.save_df)

        # Model view component
        self.tableView.setModel(self.account_model)
        self.tableView_2.setModel(self.evol_model)
        self.tableView_3.setModel(self.detail_model)

        self.account_model.dataChanged.connect(self.customModelChanged)
        self.tableView.setItemDelegateForColumn(1, self.comboDelegate)

    def delete_row_from_model(self):
        # use currently
        if not self.tableView.selectedIndexes():
            return
        cpt = {index.row() for index in self.tableView.selectedIndexes()}
        self.account_model.removeRows(self.tableView.selectedIndexes()[0].row(), len(cpt))

    def customModelChanged(self):
        df = self.account_model.getMyModel()
        self.evol_model.resetMyModel(df)
        self.detail_model.resetMyModel(df)
        self.comboDelegate.model_updated()
        self.save_bt.setEnabled(True)

    def save_df(self):
        df = self.account_model.getMyModel()
        df.to_csv(self.info_path, index=False)
        self.save_bt.setEnabled(False)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
