import logging as log
from PyQt5 import QtWidgets, uic, QtGui, QtCore
import sys
from pathlib import Path

import exception
import save_dialog
import moxfield
import moxsafe
import scryfall


class MainWindow(QtWidgets.QMainWindow):
    ModernWindow = None

    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi(Path(__file__).parent.parent / "res" / 'window.ui', self)

        self.action_add_deck.triggered.connect(self.add_deck)
        self.moxsafe = moxsafe.Moxsafe()

        self.deckSwitch.addItem("")
        self.deckSwitch.addItems([x['name'] for x in self.moxsafe.index])
        self.deckSwitch.currentIndexChanged.connect(self.deck_dropdown_callback)

        self.version_switch.currentIndexChanged.connect(self.version_dropdown_callback)

        self.card_list_model = QtGui.QStandardItemModel()
        self.card_list.setModel(self.card_list_model)
        self.card_list.clicked.connect(self.update_picture)

        self.save_snapshot_btn.clicked.connect(self.save_snapshot)
        self.new_version_btn.clicked.connect(self.add_version)

    def get_deck(self, name, version_name):
        version_name = version_name if version_name else "main"
        return self.moxsafe.get_deck(next((x['id'] for x in self.moxsafe.index if x['name'] == name)), version_name)

    def _update_deck_list(self, deck):
        for card in deck.mainboard:
            item = QtGui.QStandardItem(" ".join([str(c) for c in card]))
            self.card_list_model.appendRow(item)

    def _update_version_dropdown(self, deck, version_name):
        version_name = version_name if version_name else "main"
        self.version_switch.blockSignals(True)
        self.version_switch.addItems([name for name in self.moxsafe.versions(deck)])
        self.version_switch.setCurrentText(version_name)
        self.version_switch.blockSignals(False)

    def deck_dropdown_callback(self):
        deck_name = self.deckSwitch.currentText()
        version_name = self.version_switch.currentText()
        self.card_list_model.removeRows(0, self.card_list_model.rowCount())
        if not deck_name:
            self.version_switch.clear()
            return

        deck = self.get_deck(deck_name, version_name)
        self._update_deck_list(deck)
        self._update_version_dropdown(deck, version_name)

    def version_dropdown_callback(self):
        deck_name = self.deckSwitch.currentText()
        version_name = self.version_switch.currentText()
        self.card_list_model.removeRows(0, self.card_list_model.rowCount())

        deck = self.get_deck(deck_name, version_name)
        self._update_deck_list(deck)

    def update_picture(self, index):
        item_text = index.data()
        _, *name = item_text.split(" ")
        image_path = scryfall.get_image(" ".join(name))

        image = QtGui.QImage(image_path.as_posix())
        pixmap = QtGui.QPixmap.fromImage(image)
        pixmap_image = QtGui.QPixmap(pixmap)

        self.card_image.setPixmap(pixmap_image)
        self.card_image.setMaximumSize(250, int(250*(pixmap_image.height()/pixmap_image.width())))
        self.card_image.setScaledContents(True)
        self.card_image.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

    def _save_snapshot(self, comment):
        deck_name = self.deckSwitch.currentText()
        deck = self.moxsafe.get_deck(next((x['id'] for x in self.moxsafe.index if x['name'] == deck_name)))
        based_on = self.version_switch.currentText()

        self.moxsafe.add_snapshot(deck, comment, based_on)
        self.card_list_model.removeRows(0, self.card_list_model.rowCount())
        for card in deck.mainboard:
            item = QtGui.QStandardItem(" ".join([str(c) for c in card]))
            self.card_list_model.appendRow(item)

    def save_snapshot(self):
        dialog = save_dialog.SaveDialog()
        dialog.add_deck_signal.connect(lambda: self._save_snapshot(dialog.lineEdit.text()))
        dialog.exec_()

    def _add_deck(self, deck):
        _, deck_id = deck.split("/decks/")
        deck = moxfield.Deck(deck_id=deck_id)
        self.moxsafe.add_deck(deck)
        self.deckSwitch.addItem(deck.name)

    def add_deck(self):
        dialog = save_dialog.SaveDialog()
        dialog.add_deck_signal.connect(lambda: self._add_deck(dialog.lineEdit.text()))
        dialog.exec_()

    def _add_version(self, version_name):
        deck_name = self.deckSwitch.currentText()
        based_on = self.version_switch.currentText()
        deck = self.moxsafe.get_deck(next((x['id'] for x in self.moxsafe.index if x['name'] == deck_name)))
        self.moxsafe.add_version(deck, based_on, version_name)

        self.version_switch.blockSignals(True)
        self.version_switch.addItem(version_name)
        self.version_switch.setCurrentText(version_name)
        self.version_switch.blockSignals(False)

    def add_version(self):
        dialog = save_dialog.SaveDialog()
        dialog.add_deck_signal.connect(lambda: self._add_version(dialog.lineEdit.text()))
        dialog.exec_()


def main():
    sys.excepthook = exception.ui_exception
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    log.getLogger().setLevel(log.INFO)

    main()
