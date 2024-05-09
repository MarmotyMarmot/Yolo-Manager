import os
import cv2

from colorsys import hsv_to_rgb
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QScrollArea, QWidget, QFileDialog, \
    QCheckBox

from UI.yaml_editor import YAMLEditor
from UI.small_custom_widgets import LabelListButton
from UI.interactive_image import InteractiveImage

from tools import max_string


class LabellerUI(QDialog):
    def __init__(self):
        super().__init__()
        self.available_classes = dict()
        self.selected_class = 0
        self.active_labels = []
        self.tmp_dir = 'tmp'
        self.database_path = ''
        self.yaml_path = ''
        self.image_files = []
        self.label_files = []
        self.image_index = 0

        self.setWindowTitle("Labeller")
        self.layout_setup()
        self.show()

    def layout_setup(self):
        screen_size = QGuiApplication.primaryScreen().size()
        horizontal_layout = QHBoxLayout()

        vertical_layout_left = QVBoxLayout()
        vertical_layout_left.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.read_dtbs_button = QPushButton("Read database")
        self.read_dtbs_button.clicked.connect(self.read_database)

        self.verify_dtbs_button = QPushButton("Verify database")
        self.verify_dtbs_button.clicked.connect(self.verify_database)

        self.modify_classes_button = QPushButton("Modify classes")
        self.modify_classes_button.clicked.connect(self.modify_classes)

        self.save_on_change_checkbox = QCheckBox("Save on change")
        self.lock_editing_checkbox = QCheckBox("Enable edition")

        vertical_layout_left.addWidget(self.read_dtbs_button)
        vertical_layout_left.addWidget(self.verify_dtbs_button)
        vertical_layout_left.addWidget(self.modify_classes_button)
        vertical_layout_left.addWidget(self.save_on_change_checkbox)
        vertical_layout_left.addWidget(self.lock_editing_checkbox)

        vertical_layout_middle = QVBoxLayout()
        self.image_label = InteractiveImage(self.new_label)
        self.image_label.setFixedSize(int(screen_size.width() / 2), int(screen_size.height() / 2))
        self.image_label.change_image(cv2.imread('UI/test.png'))
        vertical_layout_middle.addWidget(self.image_label)

        vertical_layout_right = QVBoxLayout()
        vertical_layout_right.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.save_button = QPushButton("Save")
        self.next_button = QPushButton("Next")
        self.prev_button = QPushButton("Previous")

        self.save_button.clicked.connect(self.save_labels)
        self.next_button.clicked.connect(self.next_image_and_labels)
        self.prev_button.clicked.connect(self.previous_image_and_labels)

        vertical_layout_right.addWidget(self.save_button)
        vertical_layout_right.addWidget(self.next_button)
        vertical_layout_right.addWidget(self.prev_button)

        vertical_layout_right.addWidget(QLabel('Active Labels'))

        self.label_list_widget = QWidget()
        self.label_list_container = QVBoxLayout()
        self.label_list_container.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.label_list_widget.setLayout(self.label_list_container)

        label_list_scroll = QScrollArea()
        label_list_scroll.setWidgetResizable(True)
        label_list_scroll.setWidget(self.label_list_widget)

        vertical_layout_right.addWidget(label_list_scroll)

        horizontal_layout.addLayout(vertical_layout_left)
        horizontal_layout.addLayout(vertical_layout_middle)
        horizontal_layout.addLayout(vertical_layout_right)

        self.setLayout(horizontal_layout)

    def read_database(self):
        print('READING DATABASE')
        if len(self.image_files) != 0:
            print('WARN USER ABOUT CHANGING AND SAVING THE OLD DATABASE')

        self.database_path = QFileDialog.getExistingDirectory(self, "Select Database Directory")
        all_files = os.listdir(self.database_path)
        self.image_files = [file for file in all_files if
                            file.endswith('.png') or file.endswith('.jpg') or file.endswith('.jpeg')]
        self.label_files = [file for file in all_files if file.endswith('.txt')]
        yaml_file = [file for file in all_files if file.endswith('.yaml')]

        if len(yaml_file) > 1:
            print('More than one .yaml file found')
        elif len(yaml_file) == 0:
            print("No .yaml file found")
            max_class_number = 0
            for label_file in self.label_files:
                with open(f"{self.database_path}/{label_file}", "r") as label_reader:
                    labels = label_reader.readlines()
                    for label in labels:
                        if int(label.split(" ")[0]) > max_class_number:
                            max_class_number = int(label.split(" ")[0])

            for class_number in range(max_class_number):
                self.available_classes.update({f"{class_number}": f"{class_number}"})

        else:
            self.yaml_path = yaml_file[0]
            self.read_yaml()

        self.update_ui()

    def verify_database(self):
        print('DATABASE VERIFICATION')
        verify_flag = True
        invalid_files = []
        if len(self.label_files) == 0:
            print('Nothing to verify')
        else:
            images_without_extension = [file[:file.index(".")] for file in self.image_files]
            for file in self.label_files:
                with open(f"{self.database_path}/{file}", "r") as label_reader:
                    label_contents = label_reader.readlines()

                for line in label_contents:
                    line_as_list = line.replace("\n", "").split(" ")
                    if len(line_as_list) != 5:
                        verify_flag = False
                        invalid_files.append(file)

                    for number in line_as_list:
                        try:
                            float(number)
                        except ValueError:
                            try:
                                int(number)
                            except ValueError:
                                verify_flag = False
                                invalid_files.append(file)

                without_extension = file[:file.index(".")]
                if without_extension not in images_without_extension:
                    verify_flag = False
                    invalid_files.append(file)

        if verify_flag:
            print('Let the user know that the database is valid')
        else:
            print(f'Let the user know that the database is invalid and the {invalid_files} are causing the problems')

    def read_yaml(self):
        with open(f"{self.database_path}/{self.yaml_path}", 'r') as yaml_file:
            yaml_contents = yaml_file.readlines()
            yaml_contents = yaml_contents[yaml_contents.index("names:\n") + 1:]
            for yaml_line in yaml_contents:
                number_and_class = yaml_line.strip().replace("\n", "")
                object_number, object_class = number_and_class.split(": ")
                self.available_classes.update({object_number: object_class})

    def modify_classes(self):
        if self.yaml_path != '':
            self.yaml_editor = YAMLEditor(self.database_path, self.yaml_path, self.label_files)

    def next_image_and_labels(self):
        if not self.image_index >= len(self.image_files) - 1:
            self.save_labels()
            self.image_index += 1
            self.update_ui()

    def previous_image_and_labels(self):
        if not self.image_index <= 0:
            self.save_labels()
            self.image_index -= 1
            self.update_ui()

    def save_labels(self):
        print('OVERWRITING LABELS')

    def update_ui(self):
        self.read_image()
        self.read_labels()
        self.update_labels_list()
        self.paint_labels()

    def new_label(self, x_center, y_center, width, height):
        self.active_labels.append(f"{self.selected_class} {x_center} {y_center} {width} {height}")
        self.update_labels_list()
        self.paint_labels()

    def paint_labels(self):
        for label in self.active_labels:
            label_class = int(label.split(" ")[0])
            class_number = max_string(list(self.available_classes.keys()))
            if class_number == 0:
                hue = 0
            else:
                hue = label_class / class_number

            rgb_normalized = hsv_to_rgb(hue, 0.95, 1)
            rgb_col = [int(col * 255) for col in rgb_normalized]
            self.image_label.paint_rect_from_label(label, rgb_col)

    def read_image(self):
        self.image_label.change_image(cv2.imread(f"{self.database_path}/{self.image_files[self.image_index]}"))

    def read_labels(self):
        image_name = self.image_files[self.image_index]
        labels_name = f"{image_name[:image_name.index('.')]}.txt"

        if labels_name in self.label_files:
            with open(f"{self.database_path}/{labels_name}", 'r') as labels_file:
                labels = [label.replace("\n", "") for label in labels_file.readlines()]
                self.active_labels = labels
        else:
            print('There is no txt file, make one')

    def update_labels_list(self):
        for child in self.label_list_widget.children():
            if type(child) is not QVBoxLayout:
                child.deleteLater()

        for label in self.active_labels:
            self.label_list_container.addWidget(LabelListButton(label, self.label_list_widget, self.label_clicked))

    def label_clicked(self, widget, text):
        if self.lock_editing_checkbox.isChecked():
            widget.close()
            if text in self.active_labels:
                self.active_labels.remove(text)
                self.image_label.clear_labels()
                self.paint_labels()
