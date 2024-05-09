from typing import Callable

from PyQt6.QtWidgets import  QPushButton


class LabelListButton(QPushButton):
    def __init__(self, text: str, parent, onClickFunc: Callable):
        super().__init__(text, parent)
        self.text = text
        self.onClickFunc = onClickFunc
        self.clicked.connect(self.onClick)

    def onClick(self):
        self.onClickFunc(self, self.text)


