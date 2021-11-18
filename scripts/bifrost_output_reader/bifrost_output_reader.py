"""
Description:
    Reads output attributes from a Bifrost graph and displays all of its data.

Author:
    Jason Labbe

Limitations:
    - Output port must have an active connection (can't create a port then unplug)
    - Unsupported types
        - char2, char3, char4
        - Matrices that aren't 4x4 and non-floating point types
        - Enums
        - Amino objects
        - Locations
        - Custom types except bool2, bool3, bool4
        - Any 3D arrays
"""

from PySide2 import QtCore
from PySide2 import QtWidgets

import maya.cmds as cmds

from bifrost_output_reader import utils
from bifrost_output_reader import custom_button
from bifrost_output_reader import data_view

from . import __version__, __version_info__


class OutputReader(QtWidgets.QWidget):

    def __init__(self, parent=None):
        self.bf_graph = None

        if parent is None:
            parent = utils.get_maya_window()
        super(self.__class__, self).__init__(parent=parent)

        self.setWindowFlags(QtCore.Qt.Window)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.setObjectName("outputReader")

        self.create_gui()
        self.get_attrs_from_selection()

    def create_gui(self):
        self.setStyleSheet("""
            QToolTip {
                background-color: rgb(30, 30, 30);
                color: rgb(235, 235, 235);
                border: 1px solid rgb(50, 50, 50);
                padding: 4px;
                font-weight: bold;
            }
            
            #valueLabel {
                font-weight: bold;
            }
        """)

        self.setWindowTitle("Bifrost Output Reader v{}".format(__version__))
        self.resize(900, 500)

        self.attrs_list = QtWidgets.QListWidget(parent=self)
        self.attrs_list.setAlternatingRowColors(True)
        self.attrs_list.itemSelectionChanged.connect(self.on_attrs_list_selection_changed)

        self.load_ports_button = custom_button.CustomButton("Load output ports", tooltip="Loads output ports from selected Bifrost graph", parent=self)
        self.load_ports_button.clicked.connect(self.on_load_ports_clicked)

        self.attrs_layout = utils.wrap_layout(
            [self.attrs_list, self.load_ports_button])

        self.attrs_groupbox = QtWidgets.QGroupBox("Ports", parent=self)
        self.attrs_groupbox.setLayout(self.attrs_layout)

        self.plug_type_label = QtWidgets.QLabel("Type:", parent=self)
        self.plug_type_label.setMinimumWidth(40)

        self.plug_type_value = QtWidgets.QLabel("n/a", parent=self)
        self.plug_type_value.setObjectName("valueLabel")
        self.plug_type_value.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)

        self.plug_type_layout = utils.wrap_layout(
            [self.plug_type_label, self.plug_type_value, "stretch"],
            QtCore.Qt.Horizontal)

        self.length_label = QtWidgets.QLabel("Length:", parent=self)
        self.length_label.setMinimumWidth(40)

        self.length_value = QtWidgets.QLabel("0", parent=self)
        self.length_value.setObjectName("valueLabel")
        self.length_value.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)

        self.length_layout = utils.wrap_layout(
            [self.length_label, self.length_value, "stretch"],
            QtCore.Qt.Horizontal)

        self.min_value_label = QtWidgets.QLabel("Min:", parent=self)
        self.min_value_label.setMinimumWidth(40)

        self.min_value = QtWidgets.QLabel("0", parent=self)
        self.min_value.setObjectName("valueLabel")
        self.min_value.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.min_value.setWordWrap(True)
        self.min_value.setCursor(QtCore.Qt.CursorShape.IBeamCursor)
        self.min_value.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)

        self.min_value_layout = utils.wrap_layout(
            [self.min_value_label, self.min_value],
            QtCore.Qt.Horizontal)

        self.max_value_label = QtWidgets.QLabel("Max:", parent=self)
        self.max_value_label.setMinimumWidth(40)

        self.max_value = QtWidgets.QLabel("0", parent=self)
        self.max_value.setObjectName("valueLabel")
        self.max_value.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.max_value.setWordWrap(True)
        self.max_value.setCursor(QtCore.Qt.CursorShape.IBeamCursor)
        self.max_value.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)

        self.max_value_layout = utils.wrap_layout(
            [self.max_value_label, self.max_value],
            QtCore.Qt.Horizontal)

        self.data_view = data_view.DataView(parent=self)
        self.data_view.table_model.plug_type_updated.connect(self.on_plug_type_updated)
        self.data_view.table_model.length_updated.connect(self.on_length_updated)
        self.data_view.table_model.min_value_updated.connect(self.on_min_value_updated)
        self.data_view.table_model.max_value_updated.connect(self.on_max_value_updated)

        self.refresh_data_button = custom_button.CustomButton("Refresh data", tooltip="Fetches current port's data", parent=self)
        self.refresh_data_button.clicked.connect(self.on_refresh_data_clicked)

        self.go_to_button = custom_button.CustomButton("Scroll to row", tooltip="Scrolls to a row of your choice", parent=self)
        self.go_to_button.clicked.connect(self.on_go_to_clicked)

        self.create_loc_button = custom_button.CustomButton(
            "Create locators", tooltip="Creates locators from selected cells\n(only supports vector3 and matrix types)", parent=self)
        self.create_loc_button.clicked.connect(self.on_create_loc_clicked)

        self.list_buttons_layout = utils.wrap_layout(
            [self.refresh_data_button, self.go_to_button, self.create_loc_button],
            QtCore.Qt.Horizontal)

        self.data_layout = utils.wrap_layout(
            [self.plug_type_layout, self.length_layout, self.min_value_layout, self.max_value_layout, self.data_view, self.list_buttons_layout])

        self.data_groupbox = QtWidgets.QGroupBox("Output Values", parent=self)
        self.data_groupbox.setLayout(self.data_layout)

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal, parent=self)
        self.splitter.addWidget(self.attrs_groupbox)
        self.splitter.addWidget(self.data_groupbox)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)

        self.main_layout = utils.wrap_layout(
            [self.splitter])
        self.setLayout(self.main_layout)

    def showEvent(self, event):
        self.splitter.setSizes([self.width() * 0.25, self.width() * 0.75])

    def display_error(self, msg, title="Error!"):
        cmds.confirmDialog(title=title, message=msg, button="OK", icon="critical")

    def get_attrs_from_selection(self):
        self.attrs_list.clear()
        self.bf_graph = None

        bf_graphs = cmds.listRelatives(cmds.ls(sl=True), shapes=True, type="bifrostGraphShape")
        if not bf_graphs:
            return
        self.bf_graph = bf_graphs[0]

        ports = utils.get_ports_from_bf_graph(self.bf_graph)
        for port in ports:
            item = QtWidgets.QListWidgetItem(port)
            item.setToolTip(port)
            item.setSizeHint(QtCore.QSize(1, 32))
            self.attrs_list.addItem(item)

    def fetch_data_from_selected_attr(self):
        items = self.attrs_list.selectedItems()

        if not items:
            self.data_view.clear_data()
            return

        plug_name = items[0].text()
        self.data_view.fill_data(self.bf_graph, plug_name)

    def on_load_ports_clicked(self):
        self.data_view.clear_data()
        self.get_attrs_from_selection()

    def on_attrs_list_selection_changed(self):
        self.fetch_data_from_selected_attr()

    def on_plug_type_updated(self, plug_type):
        self.plug_type_value.setText(plug_type)

        plug_color = utils.plug_colors.get(plug_type)
        if plug_color:
            self.plug_type_value.setStyleSheet(
                """
                QLabel {{
                    color: {plugColor};
                }}
            """.format(plugColor=plug_color.name()))
        else:
            self.plug_type_value.setStyleSheet("")

    def on_length_updated(self, length):
        self.length_value.setText(str(length))

    def on_min_value_updated(self, value):
        self.min_value.setText(str(value))

    def on_max_value_updated(self, value):
        self.max_value.setText(str(value))

    def on_refresh_data_clicked(self):
        self.fetch_data_from_selected_attr()

    def on_go_to_clicked(self):
        row, ok = QtWidgets.QInputDialog.getInt(self, "Go to row", "Row to scroll to:")
        if not ok:
            return

        self.data_view.scrollTo(
            self.data_view.table_model.index(row, 0),
            QtWidgets.QAbstractItemView.PositionAtCenter)
        self.data_view.selectRow(row)

    def on_create_loc_clicked(self):
        plug_type = self.data_view.table_model.plug_type
        if plug_type is None:
            return

        valid_plug_types = ["float3", "double3", "short3", "long3", "matrix"]
        if self.data_view.table_model.plug_type not in valid_plug_types:
            self.display_error("Can only create locators for the following plug types: {}".format(", ".join(valid_plug_types)))
            return

        indices = self.data_view.selectedIndexes()

        locs = []

        for index in indices:
            values = self.data_view.table_model.data(index, QtCore.Qt.EditRole)
            if values is not None:
                loc = cmds.spaceLocator()[0]

                if self.data_view.table_model.plug_type == "matrix":
                    cmds.xform(loc, ws=True, matrix=eval(values))
                else:
                    cmds.xform(loc, ws=True, t=eval(values))

                locs.append(loc)

        if locs:
            cmds.select(locs)


def launch():
    global tool
    tool = OutputReader()
    tool.show()
