import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableView, QHeaderView, QVBoxLayout

import pathlib
from AbstractTableModel import *


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.table = QtWidgets.QTableView()

        data = [
          [4, 9, 2],
          [1, 0, 0],
          [3, 5, 0],
          [3, 3, 2],
          [7, 8, 9],
        ]

        self.model = PandasModelPersisted(pathlib.Path("account_info") / "account.csv")
        self._delegate = ComboDelegate(self)

        self.table.setItemDelegateForColumn(1, self._delegate)
        self.table.setModel(self.model)
        self.setCentralWidget(self.table)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
