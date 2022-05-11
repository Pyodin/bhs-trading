
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.Qt import *

import sys


class TestModel(QAbstractTableModel):
    def __init__(self):
        QAbstractTableModel.__init__(self)

        # Here we keep the data
        self.display = []

    def rowCount(self, parent=QModelIndex()):
        return len(self.display)

    def columnCount(self, parent=QModelIndex()):
        return 1

    def setData(self, index, value, role=Qt.EditRole):
        '''
        Adjust the data (set it to value <value>) depending on the given index
        and role
        '''

        if role != Qt.EditRole:
            return False

        if index.isValid() and 0 <= index.row():
            print(f'[SET_DATA] DATA: {value} index row: {index.row()}; column{index.column()}')
            if index.column() == 0:
                self.display.append(value)
            else:
                return False

            print(f'data changed signal')
            # Let Qt know there's new data to be displayed
            self.dataChanged.emit(index, index)
            return True

        return False

    def flags(self, index):
        '''
        Set the item flags at the given index. Seems like we're implementing
        this function just to see ho it's done, as we manually adjust each
        tableView to have NoEditTriggers.
        '''
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemFlags(QAbstractTableModel.flags(self, index) | Qt.ItemIsEditable)

    def insertRows(self, position, rows=1, index=QModelIndex()):
        '''
        Insert a row from the model.
        '''

        self.beginInsertRows(QModelIndex(), position, position + rows - 1)

        self.endInsertRows()

        return True

    def removeRows(self, position, rows=1, index=QModelIndex()):
        '''
        Remove a row from the model.
        '''

        self.beginRemoveRows(QModelIndex(), position, position + rows - 1)

        print(self.display)

        print(f'Removing {rows} rows from {position} to {position + rows}')
        del self.display[position:position + rows]

        print(self.display)

        self.endRemoveRows()

        return True

    def insertColumns(self, column, count, parent):
        pass

    def removeColumns(self):
        pass

    def data(self, index, role=Qt.DisplayRole):

        if not index.isValid():
            return None

        if role != Qt.DisplayRole and role != Qt.EditRole:
            return None

        column = index.column()
        row = index.row()

        print(f'[DATA] Column: {column}; Row: {row}')

        if column == 0:
            return self.display[index.row()]
        else:
            return None

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            if section == 0:
                return 'Address'


class AppContext(ApplicationContext):
    def run(self):
        self.app.setStyle('Fusion')

        ui_file = self.get_resource("mainwindow.ui")
        self.file = QFile(ui_file)
        self.file.open(QFile.ReadOnly)
        self.loader = QUiLoader()
        self.window = self.loader.load(self.file)

        self.window.updateView.clicked.connect(self.onUpdateView)

        self.address_list = ['0x0800C000', '0x0800C004', '0x0800C008', '0x0800C00C', '0x0800C010', '0x0800C014']

        self.model = TestModel()

        first_index = self.model.createIndex(0, 0)

        self.model.setData(first_index, self.address_list[0], Qt.EditRole)

        self.window.tableView.setModel(self.model)
        self.window.tableView.show()

        print(self.model.rowCount())

        # Show the application to the user
        self.window.show()
        return self.app.exec_()

    def onUpdateView(self):
        current_rows = self.model.rowCount()

        print(f'Updating view, removing {current_rows} rows')
        self.model.removeRows(0, current_rows)

        current_rows = self.model.rowCount()
        print(f'Currently we have {current_rows} rows')

        row = 0
        for address in self.address_list:
            idx = self.model.createIndex(row, 0)
            self.model.setData(idx, address, Qt.EditRole)
            row += 1

        current_rows = self.model.rowCount()
        print(f'Currently we have {current_rows} rows')


if __name__ == '__main__':
    appctxt = AppContext()
    exit_code = appctxt.run()
    sys.exit(exit_code)