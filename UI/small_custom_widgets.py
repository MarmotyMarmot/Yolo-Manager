from typing import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QPushButton, QSpinBox, QHBoxLayout, QLabel, QToolBar, QVBoxLayout, QMessageBox

from label_tools import Label


class LabelListButton(QPushButton):
    """QPushButton with easily customizable background colour"""
    def __init__(self, text: str, label: Label, background_col, parent, onClickFunc: Callable):
        super().__init__(text, parent)
        self.text = text
        self.label = label
        self.setStyleSheet(f"background-color:rgb({','.join([str(col) for col in background_col])})")
        self.onClickFunc = onClickFunc
        self.clicked.connect(self.on_click)

    def on_click(self):
        self.onClickFunc(self, self.label)


class StringSpinBox(QSpinBox):
    # TODO docstring and comments
    def __init__(self, strings: list):
        super().__init__()
        self._strings = None
        self._values = None
        self.set_strings(strings)

    def set_strings(self, strings):
        strings = list(strings)
        self._strings = tuple(strings)
        self._values = dict(zip(strings, range(len(strings))))
        self.setRange(0, len(strings) - 1)

    def textFromValue(self, value):
        return self._strings[value]


class ProportionSpinBox(QHBoxLayout):
    def __init__(self, max_val: int = 100):
        """Layout with two dependent Spin boxes for selecting proportions"""
        super().__init__()
        self.max_val = max_val
        self.changing = False
        self.proportions = (0.8, 0.2)

        self.left_spin = QSpinBox()
        self.right_spin = QSpinBox()

        self.left_spin.lineEdit().setReadOnly(True)
        self.right_spin.lineEdit().setReadOnly(True)

        self.left_spin.setRange(0, self.max_val)
        self.right_spin.setRange(0, self.max_val)

        self.left_spin.setValue(int(self.max_val * 0.8))
        self.right_spin.setValue(int(self.max_val * 0.2))

        self.left_spin.valueChanged.connect(self.left_value_changed)
        self.right_spin.valueChanged.connect(self.right_value_changed)

        self.addWidget(self.left_spin)
        self.addWidget(self.right_spin)

    def left_value_changed(self, value):
        """Changes the right spin box value so the sum of the both spin boxes does not exceed the max_val"""
        if not self.changing:
            self.changing = True
            self.right_spin.setValue(self.max_val - value)
            self.changing = False
            self.proportions = (int(self.left_spin.value() / self.max_val), int(self.right_spin.value() / self.max_val))

    def right_value_changed(self, value):
        """Changes the left spin box value so the sum of the both spin boxes does not exceed the max_val"""
        if not self.changing:
            self.changing = True
            self.right_spin.setValue(self.max_val - value)
            self.changing = False
            self.proportions = (int(self.left_spin.value() / self.max_val), int(self.right_spin.value() / self.max_val))

    def get_proportions(self):
        return self.proportions


class SwitchButton(QHBoxLayout):
    def __init__(self, name: str, toggle_func: Callable, button_states: list[str], bool_mode: bool = True):
        """QPushButton that switches between the list values on click"""
        super().__init__()
        self.bool_mode = bool_mode
        self.toggle_func = toggle_func
        self.button_states = button_states

        self.button_state_ind = 0

        self.toggle_button = QPushButton(self.button_states[0])
        self.toggle_button.clicked.connect(self.toggled)

        self.addWidget(QLabel(name))
        self.addWidget(self.toggle_button)

    def toggled(self):
        """Switches the value, calls the toggle_func"""
        if self.button_state_ind < len(self.button_states) - 1:
            self.button_state_ind += 1
        else:
            self.button_state_ind = 0

        if self.bool_mode:
            ans = self.button_state_ind != 0
            self.toggle_func(ans)
        else:
            self.toggle_func(self.button_states[self.button_state_ind])

        self.toggle_button.setText(self.button_states[self.button_state_ind])


class ZoomTool(QVBoxLayout):
    def __init__(self, zoom_handler: Callable):
        """Layout containing + and - buttons to zoom in/out"""
        super().__init__()
        self.zoom_handler = zoom_handler
        self.zoom_level = 1
        self.active = False

        self.title_label = QLabel("Zoom")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.decrement_button = QPushButton("-")
        self.decrement_button.clicked.connect(self.decrement)

        self.zoom_level_label = QLabel("100 %")
        self.zoom_level_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.increment_button = QPushButton("+")
        self.increment_button.clicked.connect(self.increment)

        self.button_container = QHBoxLayout()
        self.button_container.addWidget(self.decrement_button)
        self.button_container.addWidget(self.zoom_level_label)
        self.button_container.addWidget(self.increment_button)

        self.addWidget(self.title_label)
        self.addLayout(self.button_container)

    def increment(self):
        """Increments the value by 0.1, calls the zoom_handler"""
        if self.active:
            self.zoom_level += 0.1
            self.zoom_level_label.setText(f"{int(self.zoom_level * 100)} %")
            self.zoom_handler(self.zoom_level)

    def decrement(self):
        """Decrements the value by 0.1, calls the zoom_handler"""
        if self.zoom_level > 0.2 and self.active:
            self.zoom_level -= 0.1
            self.zoom_level_label.setText(f"{int(self.zoom_level * 100)} %")
            self.zoom_handler(self.zoom_level)

    def set_zoom(self, zoom):
        self.zoom_level = zoom
        self.zoom_level_label.setText(f"{int(self.zoom_level * 100)} %")


class Notify:
    def __init__(self, parent, text: str, title: str = 'Notification'):
        """Creates a small window with notification and blocks all other windows"""
        QMessageBox.information(parent, title, text)
