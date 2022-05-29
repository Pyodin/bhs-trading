# coding: utf-8
import numpy
import pandas as pd
from PyQt5.QtCore import Qt, QModelIndex, QAbstractTableModel, QSize


class BasePandasModel(QAbstractTableModel):
    """A model to interface a Qt view with pandas dataframe"""

    def __init__(self, dataframe: pd.DataFrame, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self._dataframe = dataframe

    def rowCount(self, parent=QModelIndex()) -> int:
        if parent == QModelIndex():
            return len(self._dataframe)
        return False

    def columnCount(self, parent=QModelIndex()) -> int:
        if parent == QModelIndex():
            return len(self._dataframe.columns)
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
        self.endInsertRows()

        return True

    def removeRows(self, position, rows=1, index=QModelIndex()):
        """
        Remove a row from the model.
        """

        self.beginRemoveRows(QModelIndex(), position, position + rows - 1)
        self._dataframe.drop(range(position, position + rows), axis=0, inplace=True)
        self.endRemoveRows()

        return True

    def data(self, index: QModelIndex, role=Qt.ItemDataRole):
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            data = self._dataframe.iloc[index.row(), index.column()]
            if data:
                if isinstance(data, numpy.float_):
                    return str(data.round(2))
                return str(data)
        return None

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

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ):
        if role == Qt.SizeHintRole:
            return QSize(200, 39)

        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            return str(self._dataframe.columns[section])

        if orientation == Qt.Vertical:
            return str(self._dataframe.index[section])

    def getMyModel(self):
        return self._dataframe

    def resetMyModel(self, df):
        self.beginResetModel()
        self.transformDataframe(df)
        self.endResetModel()

    def transformDataframe(self, df):
        pass


class PandasModelPersisted(BasePandasModel):
    """A model to interface a Qt view with pandas dataframe"""

    def __init__(self, dataframe: pd.DataFrame):
        BasePandasModel.__init__(self, dataframe)

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable


class PandasModeTotalWealth(BasePandasModel):
    def __init__(self, dataframe: pd.DataFrame):
        BasePandasModel.__init__(self, dataframe)
        self.transformDataframe(dataframe)

    def transformDataframe(self, df):
        dataframe = df.drop(["Account", "Type"], axis=1)
        self._dataframe = pd.DataFrame()

        self._dataframe["Total"] = dataframe.sum(axis=0)
        self._dataframe["Evolution"] = self._dataframe["Total"].diff()
        self._dataframe["Evolution_%"] = self._dataframe["Evolution"] / self._dataframe["Total"].shift(1) * 100

        self._dataframe = self._dataframe.transpose().fillna(0)


class PandasPerCategory(BasePandasModel):
    def __init__(self, dataframe: pd.DataFrame):
        BasePandasModel.__init__(self, dataframe)
        self.transformDataframe(dataframe)

    def transformDataframe(self, df):
        dataframe = df.replace(False, 0)
        self._dataframe = dataframe.groupby("Type").sum().transpose()
        total_per_month = self._dataframe.sum(axis=1)

        for col in self._dataframe.columns:
            self._dataframe[f"{col}_Evolution"] = self._dataframe[col] - self._dataframe[col].shift(1)
            self._dataframe[f"{col}_%"] = self._dataframe[col] / total_per_month * 100

        self._dataframe = self._dataframe.transpose().sort_index().fillna(0)


