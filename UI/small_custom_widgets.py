from typing import Callable

from PyQt6.QtWidgets import QPushButton, QSpinBox

from label_tools import Label


class LabelListButton(QPushButton):
    # TODO docstring and comments
    def __init__(self, text: str, label: Label, background_col, parent, onClickFunc: Callable):
        super().__init__(text, parent)
        self.text = text
        self.label = label
        self.setStyleSheet(f"background-color:rgb({','.join([str(col) for col in background_col])})")
        self.onClickFunc = onClickFunc
        self.clicked.connect(self.onClick)

    def onClick(self):
        self.onClickFunc(self, self.label)


class StringSpinBox(QSpinBox):
    # TODO docstring and comments
    def __init__(self, strings: list = ["0"]):
        super().__init__()
        self.set_strings(strings)

    def set_strings(self, strings):
        strings = list(strings)
        self._strings = tuple(strings)
        self._values = dict(zip(strings, range(len(strings))))
        self.setRange(0, len(strings) - 1)

    def textFromValue(self, value):
        return self._strings[value]
