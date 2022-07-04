# coding: utf-8
import pathlib
import sys

import pandas as pd
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QStyledItemDelegate

from MyDelegates import ComboDelegate
from MyTreeModel import DetailTreeModel, AccountTreeModel

# IMPORT GUI FILE
import resource_rc


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self)
        uic.loadUi("ui_files/window.ui", self)

        self.info_path = pathlib.Path("account_info") / "account.csv"
        self.dataframe = pd.read_csv(self.info_path)

        self.account_model = AccountTreeModel(self.dataframe.copy())
        # self.detail_model = DetailTreeModel(self.dataframe.copy())

        self.comboDelegate = ComboDelegate(self)
        self.delegate = QStyledItemDelegate()

        self.init_ui()

    def init_ui(self):
        # Model view component
        self.treeView.setModel(self.account_model)
        # self.treeView.setItemDelegateForColumn(1, self.comboDelegate)
        # self.treeView.setItemDelegateForColumn(2, self.delegate)
        # self.treeView_2.setModel(self.detail_model)

        self.account_model.dataChanged.connect(self.customModelChanged)

    def customModelChanged(self):
        df = self.account_model.get_dataframe()
        df.to_csv(self.info_path, index=False)
        self.save_bt.setEnabled(False)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
