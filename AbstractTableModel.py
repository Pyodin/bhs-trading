# coding: utf-8
import itertools
import json
import pathlib
from collections import defaultdict

import pandas as pd
from PyQt5.QtCore import Qt, QModelIndex, QAbstractTableModel


class BasePandasModel(QAbstractTableModel):
    """A model to interface a Qt view with pandas dataframe"""

    _dataframe = pd.DataFrame()

    def rowCount(self, parent=QModelIndex()) -> int:
        """Override method from QAbstractTableModel

        Return row count of the pandas DataFrame
        """
        if parent == QModelIndex():
            return len(self._dataframe)
        return False

    def columnCount(self, parent=QModelIndex()) -> int:
        """Override method from QAbstractTableModel

        Return column count of the pandas DataFrame
        """
        if parent == QModelIndex():
            return len(self._dataframe.columns)
        return False

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


class PandasModelPersisted(BasePandasModel):
    """A model to interface a Qt view with pandas dataframe"""

    def __init__(self, filename: pathlib.Path, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.fileName = filename
        self._dataframe = pd.read_csv(filename)

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def setData(self, index, value, role) -> bool:
        if role == Qt.EditRole:
            try:
                value = int(value)
            except ValueError:
                pass
            self._dataframe.iloc[index.row(), index.column()] = value
            self._dataframe.to_csv(self.fileName, index=False)
            self.dataChanged.emit(index, index)
            return True
        return False

    def insertRows(self, position=0, rows=1, index=QModelIndex()):
        """
        Insert a row from the model.
        """

        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._dataframe = pd.concat(
            [self._dataframe, pd.DataFrame({i: [""] for i in self._dataframe.columns})],
            ignore_index=True,
        )
        self.endInsertRows()

        return True

    def removeRows(self, position, rows=1, index=QModelIndex()):
        """
        Remove a row from the model.
        """

        self.beginRemoveRows(QModelIndex(), position, position )
        self._dataframe.drop(position, axis=0, inplace=True)
        self.endRemoveRows()
        self._dataframe.to_csv(self.fileName, index=False)

        return True


class PandasModeTotalWealth(BasePandasModel):
    def __init__(self, filename: pathlib.Path, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.base_dataframe = pd.read_csv(filename)
        self.base_dataframe.drop(["Account", "Type"], axis=1, inplace=True)
        self._dataframe = pd.DataFrame()
        self._dataframe["Total"] = self.base_dataframe.sum(axis=0)
        self._dataframe["Evolution"] = (
            self._dataframe.Total.pct_change().mul(100).round(2)
        )

        self._dataframe = self._dataframe.transpose()


class PandasPerCategory(BasePandasModel):
    def __init__(self, filename: pathlib.Path, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self.base_dataframe = pd.read_csv(filename)
        self._dataframe = self.base_dataframe.groupby("Type").sum().transpose()
        total = self._dataframe.sum(axis=1)

        for col in self._dataframe.columns:
            self._dataframe[f"{col}_%"] = self._dataframe[col] / total * 100
            self._dataframe[f"{col}_Evolution"] = (
                self._dataframe[col].pct_change().mul(100).round(2)
            )

        self._dataframe = self._dataframe.round(2)
        self._dataframe = self._dataframe.transpose().sort_index()
