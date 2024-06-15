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

    # automatron = Automate(window)
    #
    # dataset_path = r"C:\Users\Antek\PycharmProjects\Yolo-Manager\base"
    # model_path = r"D:\tools\data\Studia\PBLA\datasets\best_test_dataset\test_dataset\test_dataset\training\best.pt"
    # automatron.start_ai(dataset_path, model_path)

    app.exec()


if __name__ == "__main__":
    main()
