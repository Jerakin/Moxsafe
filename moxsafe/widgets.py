from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QListView


class CardList(QListView):
    def __init__(self):
        self.uses_fixed_size = False
        super(CardList, self).__init__()

    def sizeHint(self):
        s = QSize()
        s.setWidth(self.sizeHintForColumn(0) + self.verticalScrollBar().width() + 2 * self.frameWidth())
        s.setHeight(self.model().rowCount() * self.sizeHintForRow(0) + 2 * self.frameWidth())
        return s
