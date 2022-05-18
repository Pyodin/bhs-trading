# coding: utf-8
import math
import pathlib

import pandas as pd
from PyQt5.QtCore import Qt, QModelIndex, QAbstractTableModel, QSize
import numpy
from PyQt5.QtWidgets import QItemDelegate, QComboBox, QLineEdit


class ComboDelegate(QItemDelegate):
    """
    A delegate to add QComboBox in every cell of the given column
    """

    def __init__(self, parent):
        super(ComboDelegate, self).__init__(parent)
        self.parent = parent

    def createEditor(self, parent, option, index):
        combobox = QComboBox(parent)
        version_list = [index.data(), "0"]
        combobox.addItems(version_list)
        edit = QLineEdit()
        edit.setText(index.data())
        combobox.setLineEdit(edit)
        return combobox

    def setEditorData(self, editor, index):
        editor.blockSignals(True)
        editor.setCurrentIndex(index.row())
        editor.blockSignals(False)


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

        if index.row() >= len(self._dataframe):
            return None

        if role == Qt.DisplayRole:
            data = self._dataframe.iloc[index.row(), index.column()]
            if isinstance(data, numpy.float64):
                if math.isnan(data):
                    return ""
            return str(self._dataframe.iloc[index.row(), index.column()])
        return None

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ):
        """Override method from QAbstractTableModel

        Return dataframe index as vertical header data and columns as horizontal header data.
        """

        if role == Qt.SizeHintRole:
            return QSize(200, 39)

        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            return str(self._dataframe.columns[section])

        if orientation == Qt.Vertical:
            return str(self._dataframe.index[section])


class PandasModelPersisted(BasePandasModel):
    """A model to interface a Qt view with pandas dataframe"""

    def __init__(self, dataframe: pd.DataFrame, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self._dataframe = dataframe

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def setData(
        self, index: QModelIndex, value, role: int = Qt.ItemDataRole.EditRole
    ) -> bool:
        if role == Qt.EditRole:
            self._dataframe.iloc[index.row(), index.column()] = value
            self._dataframe.to_csv(self.fileName, index=False)
            self.dataChanged.emit(index, index)
            return True
        return False

    def insertRows(self, position=0, rows=1, index=QModelIndex()):
        """
        Insert a row from the model.
        """

        self.beginInsertRows(index, self.rowCount(), self.rowCount() + rows - 1)
        self._dataframe = pd.concat(
            [self._dataframe, pd.DataFrame({i: [0] for i in self._dataframe.columns})],
            ignore_index=True,
        )
        self._dataframe.to_csv(self.fileName, index=False)
        self.endInsertRows()

        return True

    def removeRows(self, position, rows=1, index=QModelIndex()):
        """
        Remove a row from the model.
        """

        self.beginRemoveRows(QModelIndex(), position, position + rows - 1)
        self._dataframe.drop(range(position, position + rows), axis=0, inplace=True)
        self._dataframe.to_csv(self.fileName, index=False)
        self.endRemoveRows()

        return True


class PandasModeTotalWealth(BasePandasModel):
    def __init__(self, dataframe: pd.DataFrame, parent=None):
        QAbstractTableModel.__init__(self, parent)
        dataframe.drop(["Account", "Type"], axis=1, inplace=True)

        self._dataframe = pd.DataFrame()
        self._dataframe["Total"] = dataframe.sum(axis=0)
        self._dataframe["Evolution"] = self._dataframe["Total"].diff()
        self._dataframe["Evolution_%"] = (
            self._dataframe.Total.pct_change().mul(100).round(2)
        )

        self._dataframe = self._dataframe.transpose()


class PandasPerCategory(BasePandasModel):
    def __init__(self, dataframe: pd.DataFrame, parent=None):
        QAbstractTableModel.__init__(self, parent)

        self._dataframe = dataframe.groupby("Type").sum().transpose()
        total = self._dataframe.sum(axis=1)

        for col in self._dataframe.columns:
            self._dataframe[f"{col}_Evolution"] = (
                self._dataframe[col].pct_change().mul(100).round(2)
            )
            self._dataframe[f"{col}_%"] = self._dataframe[col] / total * 100

        self._dataframe = self._dataframe.round(2)
        self._dataframe = self._dataframe.transpose().sort_index()
