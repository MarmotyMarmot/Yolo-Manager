import sys

from UI import LabellerUI
from PyQt6.QtWidgets import QApplication


def main():
    app = QApplication(sys.argv)
    # app.setStyleSheet("QPushButton{font-size: 26pt;}")
    window = LabellerUI()
    window.show()

    app.exec()


if __name__ == "__main__":
    main()