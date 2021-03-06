import pandas as pd
from PyQt5.QtCore import Qt, QModelIndex, QAbstractItemModel, QSize


class TreeItem(object):
    def __init__(self, data: list, parent=None):
        self.parentItem = parent
        self.childItems = []
        self.itemData = data

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


class BaseTreemodel(QAbstractItemModel):
    def __init__(self, dataframe: pd.DataFrame, parent=None):
        QAbstractItemModel.__init__(self, parent)

        headers = dataframe.columns.drop(["Account"]).to_list()
        self.rootItem = TreeItem(headers)
        self.populateModel(dataframe)

    def columnCount(self, parent=QModelIndex()):
        return self.rootItem.columnCount()

    def data(self, index, role):
        if not index.isValid():
            return None

        if role == Qt.TextAlignmentRole:
            if index.column() > 1:
                return Qt.AlignVCenter | Qt.AlignHCenter

        if role != Qt.DisplayRole and role != Qt.EditRole:
            return None

        item = self.getItem(index)
        value = item.data(index.column())
        if value:
            return value
        else:
            return None

    def getItem(self, index):
        if index.isValid():
            item = index.internalPointer()
            if item:
                return item

        return self.rootItem

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            return Qt.AlignVCenter | Qt.AlignHCenter

        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.rootItem.data(section)

        return None

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

    def insertRows(self, position, rows, parent=QModelIndex()):
        parentItem = self.getItem(parent)
        self.beginInsertRows(parent, position, position + rows - 1)
        success = parentItem.insertChildren(position, self.rootItem.columnCount())
        self.endInsertRows()

        return success

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        childItem = self.getItem(index)
        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QModelIndex()

        return self.createIndex(parentItem.childNumber(), 0, parentItem)

    def populateModel(self, dataframe):
        pass

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

        self.update_df()

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

    def update_df(self, index, value):
        pass


class AccountTreeModel(BaseTreemodel):
    def __init__(self, dataframe: pd.DataFrame, parent=None):
        BaseTreemodel.__init__(self, dataframe, parent)

    def populateModel(self, dataframe):
        self.beginResetModel()

        grouped = dataframe.groupby("Account").sum()

        for row, account in enumerate(grouped.index):
            data = [account, ""] + grouped.loc[account].to_list()
            self.rootItem.insertChildren(
                self.rootItem.childCount(), data
            )

            for account_type in dataframe[dataframe["Account"] == account].iterrows():
                data = account_type[1].iloc[2:].to_list()
                data.insert(0, account_type[1]["Name"])
                self.rootItem.child(row).insertChildren(
                    self.rootItem.child(row).childCount(), data
                )

        self.endResetModel()

    def flags(self, index):
        if not index.isValid():
            return 0

        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def update_df(self, index, value):
        item = self.getItem(index)
        account, name = item.data(0), item.data(1)


class DetailTreeModel(BaseTreemodel):
    def __init__(self, dataframe: pd.DataFrame, parent=None):
        BaseTreemodel.__init__(self, dataframe, parent)

    def populateModel(self):
        self.beginResetModel()

        headers = self._dataframe.columns.drop("Account")
        self.rootItem = TreeItem(headers)

        self._dataframe = self._dataframe.groupby("Type").sum().transpose()
        self._dataframe["Total"] = self._dataframe.sum(axis=1)

        for i, type in enumerate(self._dataframe.columns):
            data = self._dataframe[type].to_list()
            data.insert(0, type)
            self.rootItem.insertChildren(self.rootItem.childCount(), data)

            evol = ["Evolution"] + (self._dataframe[type] - self._dataframe[type].shift(1)).to_list()
            percent = ["% portfollio"] + (self._dataframe[type] / self._dataframe["Total"] * 100).to_list()

            for lst in [evol, percent]:
                self.rootItem.child(i).insertChildren(
                    self.rootItem.child(i).childCount(), lst
                )

        self.endResetModel()

