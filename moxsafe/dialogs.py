from PyQt5 import QtWidgets, uic, QtCore, QtGui
from pathlib import Path

import moxsafe


with (Path(__file__).parent.parent / "res" / "style.qss").open() as fh:
    STYLESHEET = fh.read()


class SaveDialog(QtWidgets.QDialog):
    add_deck_signal = QtCore.pyqtSignal()

    def __init__(self):
        super(SaveDialog, self).__init__()
        uic.loadUi(Path(__file__).parent.parent / "res" / 'save_dialog.ui', self)
        self.setStyleSheet(STYLESHEET)

        self.ok_btn.clicked.connect(self.add)
        self.cancel_btn.clicked.connect(self.close)

        exit_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Esc"), self)
        exit_shortcut.activated.connect(self.close)
        accept_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+Enter"), self)
        accept_shortcut.activated.connect(self.add)

        self.show()

    def add(self):
        text = self.lineEdit.text()
        if text:
            self.add_deck_signal.emit()
        self.close()


class SettingsDialog(QtWidgets.QDialog):
    accepted_settings_signal = QtCore.pyqtSignal(str)
    deck_deleted_signal = QtCore.pyqtSignal(str)

    def __init__(self):
        super(SettingsDialog, self).__init__()
        uic.loadUi(Path(__file__).parent.parent / "res" / 'deck_settings.ui', self)
        self.setStyleSheet(STYLESHEET)

        self.cancel_btn.clicked.connect(self.close)
        self.ok_btn.clicked.connect(self.ok)
        self.delete_btn.clicked.connect(self.delete)
        self.refresh_name_btn.clicked.connect(self.refresh)

        exit_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Esc"), self)
        exit_shortcut.activated.connect(self.close)
        self.moxsafe = moxsafe.Moxsafe()
        self._deck_data = {"id": None, "name": None}
        self.deck = None
        self.show()

    def set_deck(self, deck):
        self.deck = deck
        self.name_lbl.setText(self.deck.name)
        self.url_lbl.setOpenExternalLinks(True)
        url = f'https://www.moxfield.com/decks/{self.deck.id}'
        self.url_lbl.setText(f'<a href="{url}"><span style="color:#c999e6;">{url}</a>')

    def refresh(self):
        self.deck.load_from_id(self.deck.id)
        self._deck_data["name"] = self.deck.name
        self.name_lbl.setText(self.deck.name)

    def delete(self):
        msg_box = QtWidgets.QMessageBox()
        msg_box.setIcon(QtWidgets.QMessageBox.Warning)
        msg_box.setText(f"Deleting {self.deck.name}, this can not be undone")
        msg_box.setWindowTitle("Warning")
        msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)

        return_value = msg_box.exec()
        if return_value == QtWidgets.QMessageBox.Ok:
            self.moxsafe.delete(self.deck)
            self.deck_deleted_signal.emit(self.deck.id)
            self.close()

    def ok(self):
        self.moxsafe.update_index(self.deck, self._deck_data)
        self.accepted_settings_signal.emit(self.deck.id)
        self.close()
