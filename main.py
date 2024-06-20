import pathlib
import sys
import asyncio

from UI.labeller_ui import LabellerUI
from PyQt6.QtWidgets import QApplication

from tests import Automate


def main():
    if sys.platform == 'win32':
        pathlib.PosixPath = pathlib.WindowsPath

    app = QApplication(sys.argv)

    window = LabellerUI()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
