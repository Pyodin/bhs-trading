import pathlib
import sys

import pandas as pd
from PyQt5.QtCore import Qt, QModelIndex, QAbstractItemModel, QSize
from PyQt5.QtWidgets import QTreeView, QApplication


class TreeItem(object):
    def __init__(self, data: list, parent=None):
        self.parentItem = parent
        self.itemData = data
        self.childItems = []

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def childNumber(self):
        if self.parentItem is not None:
            return self.parentItem.childItems.index(self)
        return 0

    def columnCount(self):
        return len(self.itemData)

    def data(self, column):
        return self.itemData[column]

    def insertChildren(self, position, columns):
        if position < 0 or position > len(self.childItems):
            return False

        item = TreeItem(columns, self)
        self.childItems.insert(position, item)

        return True

    def insertColumns(self, position, columns):
        if position < 0 or position > len(self.itemData):
            return False

        for column in range(columns):
            self.itemData.insert(position, None)

        for child in self.childItems:
            child.insertColumns(position, columns)

        return True

    def parent(self):
        return self.parentItem

    def removeChildren(self, position, count):
        if position < 0 or position + count > len(self.childItems):
            return False

        for row in range(count):
            self.childItems.pop(position)

        return True

    def removeColumns(self, position, columns):
        if position < 0 or position + columns > len(self.itemData):
            return False

        for column in range(columns):
            self.itemData.pop(position)

        for child in self.childItems:
            child.removeColumns(position, columns)

        return True

    def setData(self, column, value):
        if column < 0 or column >= len(self.itemData):
            return False

        self.itemData[column] = value

        return True


class mytreemodel(QAbstractItemModel):
    def __init__(self, dataframe: pd.DataFrame, parent=None):
        QAbstractItemModel.__init__(self, parent)

        self._dataframe = None

        headers = dataframe.drop(["Account", "Type"], axis=1).columns.to_list()
        self.rootItem = TreeItem(headers)

        self.setupModelData(dataframe)

    def columnCount(self, parent=QModelIndex()):
        return self.rootItem.columnCount()

    def data(self, index, role):
        if not index.isValid():
            return None

        if role != Qt.DisplayRole and role != Qt.EditRole:
            return None

        item = self.getItem(index)
        return item.data(index.column())

    # def flags(self, index):
    #     if not index.isValid():
    #         return 0
    #
    #     return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def getItem(self, index):
        if index.isValid():
            item = index.internalPointer()
            if item:
                return item
        return self.rootItem

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.SizeHintRole:
            return QSize(200, 39)

        if orientation == Qt.Horizontal:
            return str(self.rootItem.itemData[section])

        # if orientation == Qt.Vertical:
        #     return str(self.rootItem.itemData)

    def index(self, row, column, parent=QModelIndex()):
        if parent.isValid() and parent.column() != 0:
            return QModelIndex()

        parentItem = self.getItem(parent)
        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def insertColumns(self, position, columns, parent=QModelIndex()):
        self.beginInsertColumns(parent, position, position + columns - 1)
        success = self.rootItem.insertColumns(position, columns)
        self.endInsertColumns()

        return success

    # def insertRows(self, position, rows, parent=QModelIndex()):
    #     parentItem = self.getItem(parent)
    #     self.beginInsertRows(parent, position, position + rows - 1)
    #     success = parentItem.insertChildren(position, rows,
    #             self.rootItem.columnCount())
    #     self.endInsertRows()
    #
    #     return success

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        childItem = self.getItem(index)
        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QModelIndex()

        return self.createIndex(parentItem.childNumber(), 0, parentItem)

    def removeColumns(self, position, columns, parent=QModelIndex()):
        self.beginRemoveColumns(parent, position, position + columns - 1)
        success = self.rootItem.removeColumns(position, columns)
        self.endRemoveColumns()

        if self.rootItem.columnCount() == 0:
            self.removeRows(0, self.rowCount())

        return success

    def removeRows(self, position, rows, parent=QModelIndex()):
        parentItem = self.getItem(parent)

        self.beginRemoveRows(parent, position, position + rows - 1)
        success = parentItem.removeChildren(position, rows)
        self.endRemoveRows()

        return success

    def rowCount(self, parent=QModelIndex()):
        parentItem = self.getItem(parent)
        return parentItem.childCount()

    def setData(self, index, value, role=Qt.EditRole):
        if role != Qt.EditRole:
            return False

        item = self.getItem(index)
        result = item.setData(index.column(), value)

        if result:
            self.dataChanged.emit(index, index)

        return result

    def setHeaderData(self, section, orientation, value, role=Qt.EditRole):
        if role != Qt.EditRole or orientation != Qt.Horizontal:
            return False

        result = self.rootItem.setData(section, value)
        if result:
            self.headerDataChanged.emit(orientation, section, section)

        return result

    def setupModelData(self, df):
        # self._dataframe = df.groupby("Type").sum()
        _dataframe = df.groupby("Type").sum().transpose()
        _dataframe["Total"] = _dataframe.sum(axis=1)

        for i, type in enumerate(_dataframe.columns):
            self.rootItem.insertChildren(self.rootItem.childCount(), _dataframe[type].to_list())
            self.rootItem.child(self.rootItem.childCount()-1).insertChildren(0, _dataframe[type].to_list())

            _dataframe[f"{type}_Evolution"] = _dataframe[type] - _dataframe[type].shift(1)
            _dataframe[f"{type}_%"] = _dataframe[type] / _dataframe["Total"] * 100

            for j, new_type in enumerate([f"{type}_Evolution", f"{type}_%"]):
                d = _dataframe[new_type].to_list()
                print(i)
                self.rootItem.child(i).insertChildren(
                    self.rootItem.child(i).childCount(),
                    d)

            #     for l, new_col in enumerate(d):
            #         self.rootItem.child(
            #             self.rootItem.child(i).childCount() - 1
            #         ).setData(l, new_col)


if __name__ == '__main__':

    app = QApplication(sys.argv)

    info_path = pathlib.Path("account_info") / "account.csv"
    account_model = mytreemodel(pd.read_csv(info_path))

    treeView = QTreeView()
    treeView.setModel(account_model)

    treeView.show()
    sys.exit(app.exec_())
