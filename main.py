# coding: utf-8
import itertools
import json
import pathlib
from collections import defaultdict

import pandas as pd
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QAbstractTableModel, Qt, QModelIndex
import sys

#IMPORT GUI FILE
import resource_rc


class PandasModel(QAbstractTableModel):
    """A model to interface a Qt view with pandas dataframe """

    def __init__(self, filename: pathlib.Path, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.fileName = filename
        self._dataframe = pd.read_csv(filename)

    def rowCount(self, parent=QModelIndex()) -> int:
        """ Override method from QAbstractTableModel

        Return row count of the pandas DataFrame
        """
        if parent == QModelIndex():
            return len(self._dataframe)

        return

    def columnCount(self, parent=QModelIndex()) -> int:
        """Override method from QAbstractTableModel

        Return column count of the pandas DataFrame
        """
        if parent == QModelIndex():
            return len(self._dataframe.columns)
        return 0

    def data(self, index: QModelIndex, role=Qt.ItemDataRole):
        """Override method from QAbstractTableModel

        Return data cell from the pandas DataFrame
        """
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            return str(self._dataframe.iloc[index.row(), index.column()])

        return None

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole
    ):
        """Override method from QAbstractTableModel

        Return dataframe index as vertical header data and columns as horizontal header data.
        """
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._dataframe.columns[section])

            if orientation == Qt.Vertical:
                return str(self._dataframe.index[section])

        return None

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            try:
                value = int(value)
            except ValueError:
                return False
            self._dataframe.iloc[index.row(), index.column()] = value
            self._dataframe.to_csv(self.fileName, index=False)
            return True
        return False

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self)
        uic.loadUi("main.ui", self)

        self.init_ui()
        self.init_home_page()
        self.load_account_info()

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
        self.home_bt.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_2))
        # self.add_row_bt.clicked.connect(self.add_new_row)
        # self.del_row_bt.clicked.connect(lambda: self.tableWidget_2.removeRow(self.tableWidget_2.currentRow()))

    def init_home_page(self):
        def update_total_table(_, col):
            if col >= 2:
                total_col = 0
                for i in range(self.tableWidget_2.rowCount()):
                    if self.tableWidget_2.item(i, col) and self.tableWidget_2.item(i, col).text().isdigit():
                        total_col += int(self.tableWidget_2.item(i, col).text())
                self.tableWidget.setItem(0, col-2, QtWidgets.QTableWidgetItem(str(total_col)))

        # self.tableWidget_2.cellChanged.connect(update_total_table)
        # self.load_account_info()

    def add_new_row(self):
        if not all([self.tableWidget_2.item(self.tableWidget_2.rowCount()-1, i) is None for i in range(self.tableWidget_2.columnCount())]) or self.tableWidget_2.rowCount()==0:
            self.tableWidget_2.insertRow(self.tableWidget_2.rowCount())
        else:
            return

    def load_account_info(self):
        model = PandasModel(pathlib.Path("account_info") / "account.csv")
        self.tableView.setModel(model)

        model = PandasModel(pathlib.Path("account_info") / "account.csv")
        self.tableView2.setModel(model)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
