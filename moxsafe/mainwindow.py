import logging as log
from PyQt5 import QtWidgets, uic, QtGui, QtCore
import sys
from pathlib import Path

import exception
import save_dialog
import moxfield
import moxsafe
import scryfall
import widgets


class MainWindow(QtWidgets.QMainWindow):
    ModernWindow = None

    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi(Path(__file__).parent.parent / "res" / 'window.ui', self)

        self.action_add_deck.triggered.connect(self.add_deck)
        self.moxsafe = moxsafe.Moxsafe()
        self.website = moxfield.Website()

        self.deckSwitch.addItem("")
        self.deckSwitch.addItems([x['name'] for x in self.moxsafe.index])
        self.deckSwitch.activated.connect(self.deck_dropdown_callback)

        self.version_switch.activated.connect(self.version_dropdown_callback)

        self.mainboard_card_list = widgets.CardList()
        self.commander_cards = widgets.CardList()
        self.sideboard_card_list = widgets.CardList()
        self.consider_card_list = widgets.CardList()

        self.commander_cards_model = QtGui.QStandardItemModel()
        self.commander_cards_model.setHorizontalHeaderLabels(["Commander"])
        self.commander_cards.setModel(self.commander_cards_model)
        self.commander_cards.clicked.connect(self.update_picture)
        self.commander_cards.verticalHeader().hide()
        self.commander_cards.horizontalHeader().setStretchLastSection(True)
        self.commander_cards.horizontalHeader().setSectionsClickable(False)
        self.commander_cards.setShowGrid(False)

        self.mainboard_card_list_model = QtGui.QStandardItemModel()
        self.mainboard_card_list_model.setHorizontalHeaderLabels(["Mainboard"])
        self.mainboard_card_list.setModel(self.mainboard_card_list_model)
        self.mainboard_card_list.clicked.connect(self.update_picture)
        self.mainboard_card_list.verticalHeader().hide()
        self.mainboard_card_list.horizontalHeader().setStretchLastSection(True)
        self.mainboard_card_list.horizontalHeader().setSectionsClickable(False)
        self.mainboard_card_list.setShowGrid(False)

        self.sideboard_card_list_model = QtGui.QStandardItemModel()
        self.sideboard_card_list_model.setHorizontalHeaderLabels(["Sideboard"])
        self.sideboard_card_list.setModel(self.sideboard_card_list_model)
        self.sideboard_card_list.clicked.connect(self.update_picture)
        self.sideboard_card_list.verticalHeader().hide()
        self.sideboard_card_list.horizontalHeader().setStretchLastSection(True)
        self.sideboard_card_list.horizontalHeader().setSectionsClickable(False)
        self.sideboard_card_list.setShowGrid(False)

        self.consider_card_list_model = QtGui.QStandardItemModel()
        self.consider_card_list_model.setHorizontalHeaderLabels(["Considering"])
        self.consider_card_list.setModel(self.consider_card_list_model)
        self.consider_card_list.clicked.connect(self.update_picture)
        self.consider_card_list.verticalHeader().hide()
        self.consider_card_list.horizontalHeader().setStretchLastSection(True)
        self.consider_card_list.horizontalHeader().setSectionsClickable(False)
        self.consider_card_list.setShowGrid(False)

        self.deck_history_model = QtGui.QStandardItemModel()
        self.deck_history.setModel(self.deck_history_model)
        self.deck_history.clicked.connect(self.version_list_callback)

        self.left_card_list_layout.insertWidget(0, self.mainboard_card_list)
        self.left_card_list_layout.insertWidget(0, self.commander_cards)
        self.right_card_list_layout.insertWidget(0, self.consider_card_list)
        self.right_card_list_layout.insertWidget(0, self.sideboard_card_list)

        self.commander_cards.hide()

        self.mainboard_card_list.hide()
        self.sideboard_card_list.hide()
        self.consider_card_list.hide()

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHorizontalStretch(1)

        self.mainboard_card_list.setSizePolicy(sizePolicy)
        self.sideboard_card_list.setSizePolicy(sizePolicy)
        self.consider_card_list.setSizePolicy(sizePolicy)

        self.save_snapshot_btn.clicked.connect(self.save_snapshot)
        self.new_version_btn.clicked.connect(self.add_version)
        self.restore_btn.clicked.connect(self.restore_version)

    def setup_list_widgets(self, deck):
        self.commander_cards.setVisible(bool(deck.commanders))
        self.mainboard_card_list.setVisible(bool(deck.mainboard))
        self.sideboard_card_list.setVisible(bool(deck.sideboard))
        self.consider_card_list.setVisible(bool(deck.considering))
        self.commander_cards.setFixedHeight(self.commander_cards.sizeHintForRow(0) *
                                            self.commander_cards_model.rowCount() +
                                            2 * self.commander_cards.frameWidth() +
                                            self.commander_cards.horizontalHeader().height() + 2)

    def get_deck(self, name, version_name=None, at_sha=None):
        version_name = version_name if version_name else "main"
        return self.moxsafe.get_deck(next((x['id'] for x in self.moxsafe.index if x['name'] == name)), version_name, at_sha)

    def _update_deck_list(self, deck):
        for card in deck.mainboard:
            item = QtGui.QStandardItem(" ".join([str(c) for c in card]))
            self.mainboard_card_list_model.appendRow(item)
        for card in deck.sideboard:
            item = QtGui.QStandardItem(" ".join([str(c) for c in card]))
            self.sideboard_card_list_model.appendRow(item)
        for card in deck.considering:
            item = QtGui.QStandardItem(" ".join([str(c) for c in card]))
            self.consider_card_list_model.appendRow(item)
        for card in deck.commanders:
            item = QtGui.QStandardItem(" ".join([str(c) for c in card]))
            self.commander_cards_model.appendRow(item)
        self.setup_list_widgets(deck)

    def _update_version_dropdown(self, deck, version_name=None):
        version_name = version_name if version_name else "main"
        self.version_switch.addItems([name for name in self.moxsafe.versions(deck)])
        self.version_switch.setCurrentText(version_name)

    def _update_version_list(self, deck, version_name=None):
        version_name = version_name if version_name else "main"
        history = self.moxsafe.version_history(deck, version_name)
        for sha, date, message in history:
            item = QtGui.QStandardItem(" ".join([date, message]))
            item.setData(sha, 1)
            self.deck_history_model.appendRow(item)

    def _clear_card_lists(self):
        self.commander_cards_model.removeRows(0, self.commander_cards_model.rowCount())
        self.mainboard_card_list_model.removeRows(0, self.mainboard_card_list_model.rowCount())
        self.sideboard_card_list_model.removeRows(0, self.sideboard_card_list_model.rowCount())
        self.consider_card_list_model.removeRows(0, self.consider_card_list_model.rowCount())

    def deck_dropdown_callback(self):
        deck_name = self.deckSwitch.currentText()
        self._clear_card_lists()
        self.deck_history_model.removeRows(0, self.deck_history_model.rowCount())
        self.version_switch.clear()
        if not deck_name:
            return

        deck = self.get_deck(deck_name)
        self._update_deck_list(deck)
        self._update_version_dropdown(deck)
        self._update_version_list(deck)

    def version_list_callback(self, index):
        deck_name = self.deckSwitch.currentText()
        self._clear_card_lists()
        if not deck_name:
            return
        if index.row() == 0:
            deck = self.get_deck(deck_name, version_name=self.version_switch.currentText())
        else:
            deck = self.get_deck(deck_name, at_sha=index.data(1))
        self._update_deck_list(deck)

    def version_dropdown_callback(self):
        deck_name = self.deckSwitch.currentText()
        version_name = self.version_switch.currentText()
        self._clear_card_lists()
        self.deck_history_model.removeRows(0, self.deck_history_model.rowCount())
        if not deck_name:
            return
        deck = self.get_deck(deck_name, version_name)
        self._update_deck_list(deck)
        self._update_version_list(deck, version_name)

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
        self.mainboard_card_list_model.removeRows(0, self.mainboard_card_list_model.rowCount())
        self.deck_history_model.removeRows(0, self.deck_history_model.rowCount())
        self._update_deck_list(deck)
        self._update_version_list(deck, based_on)

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
        deck = self.moxsafe.get_deck(next((x['id'] for x in self.moxsafe.index if x['name'] == deck_name)))
        self.moxsafe.add_version(deck, version_name)

        self.version_switch.blockSignals(True)
        self.version_switch.addItem(version_name)
        self.version_switch.setCurrentText(version_name)
        self.version_switch.blockSignals(False)

    def add_version(self):
        dialog = save_dialog.SaveDialog()
        dialog.add_deck_signal.connect(lambda: self._add_version(dialog.lineEdit.text()))
        dialog.exec_()

    def restore_version(self):
        specific_version = self.deck_history.selectedIndexes()
        deck_name = self.deckSwitch.currentText()

        if specific_version:
            sha = specific_version[0].data(1)
            deck = self.get_deck(deck_name, at_sha=sha)
        else:
            deck = self.get_deck(deck_name, version_name=self.version_switch.currentText())
        self.website.bulk_edit(deck)


def main():
    sys.excepthook = exception.ui_exception
    app = QtWidgets.QApplication(sys.argv)
    with (Path(__file__).parent.parent / "res" / "style.qss").open() as fh:
        app.setStyleSheet(fh.read())
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    log.getLogger().setLevel(log.INFO)

    main()
