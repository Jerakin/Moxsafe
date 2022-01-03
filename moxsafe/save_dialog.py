from PyQt5 import QtWidgets, uic, QtCore
from pathlib import Path


class SaveDialog(QtWidgets.QDialog):
    add_deck_signal = QtCore.pyqtSignal()

    def __init__(self):
        super(SaveDialog, self).__init__()
        uic.loadUi(Path(__file__).parent.parent / "res" / 'save_dialog.ui', self)
        self.ok_btn.clicked.connect(self.add)
        self.ok_btn.clicked.connect(self.close)
        self.show()

    def add(self):
        text = self.lineEdit.text()
        if text:  # and "www.moxfield.com/decks/" in text:
            self.add_deck_signal.emit()
