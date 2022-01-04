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

        self.deckSwitch.addItems([x['name'] for x in self.moxsafe.index])
        self.deckSwitch.currentIndexChanged.connect(self.update_list)

        self.list_template_model = QtGui.QStandardItemModel()
        self.list_template.setModel(self.list_template_model)

    def update_list(self):
        deck_name = self.deckSwitch.currentText()
        deck = self.moxsafe.get_deck(next((x['id'] for x in self.moxsafe.index if x['name'] == deck_name)))
        self.list_template_model.removeRows(0, self.list_template_model.rowCount())
        for card in deck.mainboard:
            item = QtGui.QStandardItem(" ".join(card))
            self.list_template_model.appendRow(item)

    def _add_deck(self, deck):
        _, deck_id = deck.split("/decks/")
        deck = moxfield.Deck(deck_id=deck_id)
        self.moxsafe.add_deck(deck)
        self.deckSwitch.addItem(deck.name)

    def add_deck(self):
        dialog = save_dialog.SaveDialog()
        dialog.add_deck_signal.connect(lambda: self._add_deck(dialog.lineEdit.text()))
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