import logging as log
from PyQt5 import QtWidgets, uic, QtGui, QtCore
import sys
from pathlib import Path

from moxsafe import exception
from moxsafe import save_dialog
from moxsafe import moxfield


class MainWindow(QtWidgets.QMainWindow):
    ModernWindow = None

    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi(Path(__file__).parent.parent / "res" / 'window.ui', self)

        self.action_add_deck.triggered.connect(self.add_deck)

    def _add_deck(self, deck):
        _, deck_id = deck.split("/decks/")
        deck = moxfield.Deck(deck_id=deck_id)

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