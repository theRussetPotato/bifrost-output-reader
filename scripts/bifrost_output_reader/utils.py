import shiboken2
from operator import itemgetter

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

import maya.cmds as cmds
import maya.OpenMayaUI as OpenMayaUI


array_types = [
    "TdataCompound",
    "float2",
    "float3",
    "double2",
    "double3",
    "long2",
    "long3",
    "short2",
    "short3"]

int_color = QtGui.QColor(98, 207, 217)
float_color = QtGui.QColor(130, 217, 159)
vector_color = QtGui.QColor(168, 217, 119)

plug_colors = {
    "char": int_color,
    "short": int_color,
    "short2": vector_color,
    "short3": vector_color,
    "long": int_color,
    "long2": vector_color,
    "long3": vector_color,
    "long long int": int_color,
    "TdataCompound": vector_color,
    "float": float_color,
    "float2": vector_color,
    "float3": vector_color,
    "double": float_color,
    "double2": vector_color,
    "double3": vector_color,
    "bool": QtGui.QColor(230, 153, 99),
    "matrix": QtGui.QColor(222, 117, 110),
    "string": QtGui.QColor(217, 190, 108)
}


def get_maya_window():
    maya_win_pointer = OpenMayaUI.MQtUtil.mainWindow()
    return shiboken2.wrapInstance(long(maya_win_pointer), QtWidgets.QWidget)


def wrap_layout(widgets, orientation=QtCore.Qt.Vertical, parent=None):
    if orientation == QtCore.Qt.Horizontal:
        new_layout = QtWidgets.QHBoxLayout()
    else:
        new_layout = QtWidgets.QVBoxLayout()

    for widget in widgets:
        if widget == "stretch":
            new_layout.addStretch()
        elif widget == "splitter":
            frame = QtWidgets.QFrame(parent=parent)
            frame.setStyleSheet("QFrame {background-color: rgb(50, 50, 50);}")

            if orientation == QtCore.Qt.Vertical:
                frame.setFixedHeight(2)
            else:
                frame.setFixedWidth(2)

            new_layout.addWidget(frame)
        elif type(widget) == int:
            new_layout.addSpacing(widget)
        else:
            if QtCore.QObject.isWidgetType(widget):
                new_layout.addWidget(widget)
            else:
                new_layout.addLayout(widget)

    return new_layout


def get_ports_from_bf_graph(bf_graph):
    invalid_attrs = ["message", "mesh", "dirtyFlag"]
    invalid_attr_types = ["bifData"]
    attrs = cmds.listAttr(bf_graph, hasData=True, userDefined=True, readOnly=True) or []

    ports = []

    for attr in sorted(attrs):
        if attr in invalid_attrs or "." in attr:
            continue

        if cmds.attributeQuery(attr, node=bf_graph, listParent=True):
            continue

        if cmds.getAttr("{}.{}".format(bf_graph, attr), type=True) in invalid_attr_types:
            continue

        ports.append(attr)

    return ports


def extract_data_from_port(bf_graph, plug_name):
    data = []
    plug_type = None

    if not cmds.attributeQuery(plug_name, node=bf_graph, exists=True):
        return

    plug = "{}.{}".format(bf_graph, plug_name)
    try:
        cmds.getAttr(plug)  # Force output to pull data for access.
    except:
        pass

    attr_type = cmds.getAttr(plug, type=True)
    if attr_type == "bifData":
        return

    # Determine if it's a 2D array.
    sub_multi_plug = None
    for sub_plug in cmds.listAttr(plug)[1:]:
        sub_plug_name = sub_plug.split(".")[-1]
        if cmds.attributeQuery(sub_plug_name, node=bf_graph, multi=True):
            sub_multi_plug = sub_plug_name
            break

    is_multi_plug = cmds.attributeQuery(plug_name, node=bf_graph, multi=True)
    array_size = cmds.getAttr(plug, size=True)

    if sub_multi_plug:
        for index in range(array_size):
            values = []
            sub_array_size = cmds.getAttr("{}[{}].{}".format(plug, index, sub_multi_plug), size=True)
            for sub_index in range(sub_array_size):
                if plug_type is None:
                    plug_type = cmds.getAttr("{}[{}].{}[{}]".format(plug, index, sub_multi_plug, sub_index), type=True)
                raw_value = cmds.getAttr("{}[{}].{}[{}]".format(plug, index, sub_multi_plug, sub_index))
                value = serialize_data(raw_value, plug_type)
                values.append(value)
            data.append(values)
    else:
        if is_multi_plug:
            values = []
            for index in range(array_size):
                if plug_type is None:
                    plug_type = cmds.getAttr("{}[{}]".format(plug, index), type=True)
                value = serialize_data(cmds.getAttr("{}[{}]".format(plug, index)), plug_type)
                values.append(value)
            data.append(values)
        else:
            plug_type = attr_type
            value = serialize_data(cmds.getAttr(plug), plug_type)
            data.append([value])

    data_length = 0
    min_value = 0
    max_value = 0

    if len(data[0]):
        data_length = len(data[0])

        if type(data[0][0]) == tuple:
            min_value = []
            max_value = []
            tuple_length = len(data[0][0])

            for i in range(tuple_length):
                min_value.append(min(data[0], key=itemgetter(i))[i])
                max_value.append(max(data[0], key=itemgetter(i))[i])

            min_value = tuple(min_value)
            max_value = tuple(max_value)
        else:
            min_value = min(data[0])
            max_value = max(data[0])

    return {
        "data": data,
        "plugType": plug_type,
        "dataLength": data_length,
        "minValue": min_value,
        "maxValue": max_value
    }


def serialize_data(data, data_type):
    if data_type in array_types:
        value = data[0]
    else:
        value = data

    if type(value) == list:
        value = tuple(value)

    return value
