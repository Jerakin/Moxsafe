from PyQt5 import QtWidgets, uic, QtCore, QtGui
from pathlib import Path


class SaveDialog(QtWidgets.QDialog):
    add_deck_signal = QtCore.pyqtSignal()

    def __init__(self):
        super(SaveDialog, self).__init__()
        uic.loadUi(Path(__file__).parent.parent / "res" / 'save_dialog.ui', self)
        self.ok_btn.clicked.connect(self.add)
        self.cancel_btn.clicked.connect(self.close)
        self.show()
        exit_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Esc"), self)
        exit_shortcut.activated.connect(self.close)
        accept_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+Enter"), self)
        accept_shortcut.activated.connect(self.add)

    def add(self):
        text = self.lineEdit.text()
        if text:
            self.add_deck_signal.emit()
