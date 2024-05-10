import sys

from UI.labeller_ui import LabellerUI
from PyQt6.QtWidgets import QApplication


def main():
    app = QApplication(sys.argv)

    window = LabellerUI()
    window.show()

    app.exec()


if __name__ == "__main__":
    main()