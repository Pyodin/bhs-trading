
from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtWidgets import QComboBox, QLineEdit, QStyledItemDelegate


class ComboDelegate(QStyledItemDelegate):
    """
    A delegate to add QComboBox in every cell of the given column
    """

    def __init__(self, parent):
        super(ComboDelegate, self).__init__(parent)
        self.parent = parent
        self.columns = list(set(self.parent.account_model.getMyModel().Type.to_list()))

    def createEditor(self, parent, option, index):
        combobox = QComboBox(parent)
        return combobox

    def setEditorData(self, editor, index):
        editor.addItems(self.columns)
        edit = QLineEdit(self.parent)
        editor.setLineEdit(edit)
        value = index.data()
        editor.setCurrentText(value)

    def setModelData(self, editor, model, index=QModelIndex()):
        value = editor.currentText()
        model.setData(index, value, Qt.EditRole)

    def model_updated(self):
        self.columns = list(set(self.parent.account_model.getMyModel().Type.to_list()))

#
# if __name__ == '__main__':
#     import sys
#     import pathlib
#     import pandas as pd
#     from AbstractTableModel import *
#     from PyQt5.QtWidgets import QItemDelegate, QComboBox, QLineEdit, QTableView, QApplication
#
#     app = QApplication(sys.argv)
#
#     info_path = pathlib.Path("account_info") / "account.csv"
#     account_model = PandasModelPersisted(pd.read_csv(info_path))
#
#     tableView = QTableView()
#     tableView.setModel(account_model)
#
#     delegate = ComboDelegate(app)
#
#     tableView.setItemDelegateForColumn(1, delegate)
#     tableView.resizeRowsToContents()
#
#     tableView.show()
#     sys.exit(app.exec_())
