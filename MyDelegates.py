from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtWidgets import QComboBox, QLineEdit, QStyledItemDelegate


class BorderDelegate(QStyledItemDelegate):
    def __init__(self, parent):
        super(BorderDelegate, self).__init__(parent)
        self.parent = parent

    def paint(self, painter, option, index):
        painter.setPen(Qt.red)
        rect = option.rect

        if index.column() == 0:
            painter.drawLine(rect.topLeft(), rect.bottomLeft())

        if index.column() == index.model().columnCount() - 1:
            painter.drawLine(rect.topRight(), rect.bottomRight())


class ComboDelegate(QStyledItemDelegate):
    """
    A delegate to add QComboBox in every cell of the given column
    """

    def __init__(self, parent):
        super(ComboDelegate, self).__init__(parent)
        self.parent = parent
        self.columns = list(
            set(self.parent.account_model.get_dataframe().Type.to_list())
        )

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
        self.columns = list(
            set(self.parent.account_model.get_dataframe().Type.to_list())
        )
