from PySide2 import QtGui
from PySide2 import QtWidgets


class CustomButton(QtWidgets.QPushButton):

    def __init__(self, caption, tooltip=None, parent=None):
        super(CustomButton, self).__init__(caption, parent)
        self.setMouseTracking(True)
        self.is_pressed = False
        self.tooltip_msg = tooltip

    def mousePressEvent(self, event):
        super(CustomButton, self).mousePressEvent(event)
        self.is_pressed = True

    def mouseMoveEvent(self, event):
        if self.tooltip_msg is not None and not self.is_pressed:
            widget = self.parent()
            if widget is None:
                widget = self

            QtWidgets.QToolTip.hideText()

            QtWidgets.QToolTip.showText(
                QtGui.QCursor.pos(),
                self.tooltip_msg,
                widget,
                self.rect()
            )

    def leaveEvent(self, event):
        self.is_pressed = False
        QtWidgets.QToolTip.hideText()
