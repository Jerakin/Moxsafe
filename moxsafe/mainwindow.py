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
        self.card_list.setModel(self.list_template_model)
        self.card_list.clicked.connect(self.update_picture)

        self.save_snapshot_btn.clicked.connect(self.save_snapshot)

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
        self.moxsafe.add_version(deck, comment)
        self.list_template_model.removeRows(0, self.list_template_model.rowCount())
        for card in deck.mainboard:
            item = QtGui.QStandardItem(" ".join([str(c) for c in card]))
            self.list_template_model.appendRow(item)

    def save_snapshot(self):
        dialog = save_dialog.SaveDialog()
        dialog.add_deck_signal.connect(lambda: self._save_snapshot(dialog.lineEdit.text()))
        dialog.exec_()

    def update_list(self):
        deck_name = self.deckSwitch.currentText()
        deck = self.moxsafe.get_deck(next((x['id'] for x in self.moxsafe.index if x['name'] == deck_name)))
        self.list_template_model.removeRows(0, self.list_template_model.rowCount())
        for card in deck.mainboard:
            item = QtGui.QStandardItem(" ".join([str(c) for c in card]))
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
