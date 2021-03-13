from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets

import utils


class DataView(QtWidgets.QTableView):

    def __init__(self, parent=None):
        QtWidgets.QTableView.__init__(self, parent=parent)

        self.table_model = DataModel(parent=self)
        self.setModel(self.table_model)
        self.setShowGrid(True)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.verticalHeader().setDefaultSectionSize(25)

    def paintEvent(self, paint_event):
        if self.model().rowCount(self.rootIndex()) == 0:
            if len(self.table_model.values) > 0:
                msg = "This port has empty data"
            else:
                msg = "<- Load ports from selected Bifrost graph"

            qp = QtGui.QPainter(self.viewport())
            if not qp.isActive():
                qp.begin(self)

            font_family = self.fontInfo().family()

            rect = paint_event.rect()
            rect.setLeft(10)
            rect.setRight(rect.right() - 10)

            qp.setPen(QtGui.QColor(255, 255, 255))
            qp.setFont(QtGui.QFont(font_family, 15))
            qp.drawText(rect, QtCore.Qt.AlignCenter | QtCore.Qt.TextWordWrap, msg)
            qp.end()

        QtWidgets.QTableView.paintEvent(self, paint_event)

    def clear_data(self):
        self.table_model.clear_data()

    def fill_data(self, bf_graph, plug_name):
        self.table_model.get_data(bf_graph, plug_name)

        for i in range(len(self.table_model.values)):
            self.resizeColumnToContents(i)


class DataModel(QtCore.QAbstractTableModel):

    plug_type_updated = QtCore.Signal(str)
    length_updated = QtCore.Signal(int)
    min_value_updated = QtCore.Signal(str)
    max_value_updated = QtCore.Signal(str)

    def __init__(self, parent=None):
        super(DataModel, self).__init__(parent)
        self.values = []
        self.rows = 0
        self.columns = 0
        self.plug_type = None

        temp_widget = QtWidgets.QWidget()
        self.bg_color = temp_widget.palette().color(QtGui.QPalette.Active, QtGui.QPalette.Base)
        self.bg_alt_color = self.bg_color.lighter(115)
        temp_widget.deleteLater()

    def rowCount(self, parent):
        return self.rows

    def columnCount(self, parent):
        return self.columns

    def data(self, index, role):
        if not index.isValid():
            return

        row = index.row()
        column = index.column()

        if role == QtCore.Qt.DisplayRole:
            if column < len(self.values) and row < len(self.values[column]):
                return "  {}  ".format(self.values[column][row])
        elif role == QtCore.Qt.EditRole:
            if column < len(self.values) and row < len(self.values[column]):
                return str(self.values[column][row])
        elif role == QtCore.Qt.ToolTipRole:
            if column < len(self.values) and row < len(self.values[column]):
                return str(self.values[column][row])
        elif role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignVCenter
        elif role == QtCore.Qt.BackgroundColorRole:
            if row % 2 == 0:
                return self.bg_color
            else:
                return self.bg_alt_color
        elif role == QtCore.Qt.ForegroundRole:
            if utils.plug_colors.get(self.plug_type):
                return utils.plug_colors[self.plug_type]

        return

    def headerData(self, index, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Vertical:
                return index
            else:
                return "Array {}".format(index)
        elif role == QtCore.Qt.TextAlignmentRole:
            if orientation == QtCore.Qt.Vertical:
                return QtCore.Qt.AlignCenter
            else:
                return QtCore.Qt.AlignLeft

    def flags(self, index):
        flags = super(DataModel, self).flags(index)
        return flags | QtCore.Qt.ItemIsEditable

    def clear_data(self, emit_signals=True):
        if emit_signals:
            self.layoutAboutToBeChanged.emit()

        self.values = []
        self.columns = 0
        self.rows = 0
        self.plug_type = None
        self.plug_type_updated.emit("n/a")
        self.length_updated.emit(0)
        self.min_value_updated.emit("0")
        self.max_value_updated.emit("0")

        if emit_signals:
            self.layoutChanged.emit()

    def get_data(self, bf_graph, plug_name):
        self.layoutAboutToBeChanged.emit()

        data_dict = utils.extract_data_from_port(bf_graph, plug_name)

        if data_dict:
            self.values = data_dict["data"]
            if self.values:
                self.rows = max([len(v) for v in self.values])

            self.columns = len(self.values)

            self.plug_type = data_dict["plugType"]
            self.plug_type_updated.emit(self.plug_type)
            self.length_updated.emit(data_dict["dataLength"])
            self.min_value_updated.emit(str(data_dict["minValue"]))
            self.max_value_updated.emit(str(data_dict["maxValue"]))
        else:
            self.clear_data(emit_signals=False)

        self.layoutChanged.emit()
