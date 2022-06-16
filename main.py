# coding: utf-8
import pathlib
import sys

import pandas as pd
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QStringListModel

from MyTableModel import PandasModel
from MyTreeModel import Treemodel
from MyDelegates import *

# IMPORT GUI FILE
import resource_rc


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self)
        uic.loadUi("main.ui", self)

        self.info_path = pathlib.Path("account_info") / "account.csv"
        self.dataframe = pd.read_csv(self.info_path)

        self.account_model = PandasModel(self.dataframe.copy())
        self.detail_model = Treemodel(self.dataframe.copy())

        self.comboDelegate = ComboDelegate(self)

        self.init_ui()

    def init_ui(self):
        # def slideLeftMenu():
        #     width = self.leftMenuF.width()
        #     nextWidth = 0 if width == 200 else 200
        #
        #     self.animation = QPropertyAnimation(self.leftMenuF, b"maximumWidth")
        #     self.animation.setDuration(250)
        #     self.animation.setStartValue(width)
        #     self.animation.setEndValue(nextWidth)
        #     self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        #     self.animation.start()


        # Three button
        # Init button
        self.add_row_bt.clicked.connect(self.account_model.insertRows)
        self.del_row_bt.clicked.connect(self.delete_row_from_model)
        self.save_bt.clicked.connect(self.save_df)

        # Model view component
        self.tableView.setModel(self.account_model)
        self.treeView.setModel(self.detail_model)

        self.account_model.dataChanged.connect(self.customModelChanged)
        self.tableView.setItemDelegateForColumn(1, self.comboDelegate)

        self.treeView.setColumnWidth(0, 200)

    def delete_row_from_model(self):
        # use currently
        if not self.tableView.selectedIndexes():
            return
        cpt = {index.row() for index in self.tableView.selectedIndexes()}
        self.account_model.removeRows(
            self.tableView.selectedIndexes()[0].row(), len(cpt)
        )

    def save_df(self):
        df = self.account_model.get_dataframe()
        df.to_csv(self.info_path, index=False)
        self.save_bt.setEnabled(False)

    def customModelChanged(self):
        df = self.account_model.get_dataframe()
        self.detail_model.setupModelData(df)
        self.save_bt.setEnabled(True)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
