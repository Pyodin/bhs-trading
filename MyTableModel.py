# coding: utf-8
import pandas as pd
import random
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QModelIndex, QAbstractTableModel, QSize


class PandasModel(QAbstractTableModel):
    """A model to interface a Qt view with pandas dataframe"""

    def __init__(self, dataframe: pd.DataFrame, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self._dataframe = dataframe

    def columnCount(self, parent=QModelIndex()) -> int:
        if parent == QModelIndex():
            return len(self._dataframe.columns)
        return False

    def data(self, index: QModelIndex, role=Qt.ItemDataRole):
        if not index.isValid():
            return None

        value = self._dataframe.iloc[index.row()][index.column()]
        if role == Qt.TextAlignmentRole:
            if isinstance(value, str):
                return Qt.AlignVCenter | Qt.AlignLeft
            else:
                return Qt.AlignVCenter | Qt.AlignHCenter

        if role == Qt.BackgroundRole:
            if index.column() == 0:
                return QtGui.QColor("#9f9f9f")

        if role == Qt.DisplayRole:
            if value:
                if isinstance(value, str):
                    return value
                else:
                    return str(value.round(2))
        return None

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ):
        if role == Qt.SizeHintRole:
            return QSize(200, 30)

        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._dataframe.columns[section])
            if orientation == Qt.Vertical:
                return str(self._dataframe.index[section])

        return None

    def get_dataframe(self):
        return self._dataframe

    def insertRows(self, position=0, rows=1, index=QModelIndex()):
        """
        Insert a row from the model.
        """

        self.beginInsertRows(index, self.rowCount(), self.rowCount() + rows - 1)
        self._dataframe = pd.concat(
            [self._dataframe, pd.DataFrame({i: [0] for i in self._dataframe.columns})],
            ignore_index=True,
        )
        self.endInsertRows()

        return True

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def rowCount(self, parent=QModelIndex()) -> int:
        if parent == QModelIndex():
            return len(self._dataframe)
        return False

    def removeRows(self, position, rows=1, index=QModelIndex()):
        """
        Remove a row from the model.
        """

        self.beginRemoveRows(QModelIndex(), position, position + rows - 1)
        self._dataframe.drop(range(position, position + rows), axis=0, inplace=True)
        self.endRemoveRows()

        return True

    def setData(
        self, index: QModelIndex, value, role: int = Qt.ItemDataRole.EditRole
    ) -> bool:
        if role == Qt.EditRole:
            if index.column() > 1:
                try:
                    value = int(value)
                except ValueError:
                    return False
            self._dataframe.iloc[index.row(), index.column()] = value
            self.dataChanged.emit(index, index)
            return True
        return False
