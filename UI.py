import os

import cv2

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QScrollArea, QWidget, QFileDialog, \
    QCheckBox, QTableWidget, QTableWidgetItem, QSizePolicy, QHeaderView, QAbstractScrollArea
from customWidgets import InteractiveImage, LabelListButton


class LabellerUI(QDialog):
    def __init__(self):
        super().__init__()
        self.available_classes = []
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
        self.image_label.change_image(cv2.imread('test.png'))
        vertical_layout_middle.addWidget(self.image_label)

        vertical_layout_right = QVBoxLayout()
        vertical_layout_right.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.next_button = QPushButton("Next")
        self.prev_button = QPushButton("Previous")

        self.next_button.clicked.connect(self.next_image_and_labels)
        self.prev_button.clicked.connect(self.previous_image_and_labels)

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
        else:
            self.yaml_path = yaml_file[0]
            self.read_yaml()

        self.update_ui()

    def verify_database(self):
        print('DATABASE VERIFICATION')
        verify_flag = True
        if len(self.label_files) == 0:
            print('Nothing to verify')
        else:
            images_without_extension = [file[:file.index(".")] for file in self.image_files]
            for file in self.label_files:
                without_extension = file[:file.index(".")]
                if without_extension not in images_without_extension:
                    verify_flag = False
                    break

        if verify_flag:
            print('Let the user know that the database is valid')
        else:
            print('Let the user know that the database is invalid')

    def read_yaml(self):
        print('READING YAML FILE')

    def modify_classes(self):
        if self.yaml_path != '':
            self.yaml_editor = YAMLEditor(self.database_path, self.yaml_path, self.label_files)
            print('OPEN UP A DIALOG WHICH ALLOWS FOR AN EASIER YAML MODIFICATION')

    def next_image_and_labels(self):
        if not self.image_index >= len(self.image_files) - 1:
            self.image_index += 1
            self.update_ui()

    def previous_image_and_labels(self):
        if not self.image_index <= 0:
            self.image_index -= 1
            self.update_ui()

    def update_ui(self):
        self.read_image()
        self.read_labels()
        self.update_labels_list()

    def new_label(self, start_pos, end_pos):
        print(f"Received a new label of class {self.selected_class} at coordinates:\nLU {start_pos} RB {end_pos}")
        # Transform it to a label and add to self.active_labels, after that, just update the labels list and the UI

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
                print(f"{text} removed")


class YAMLEditor(QWidget):
    def __init__(self, database_path, yaml_path, labels_path):
        super().__init__()
        self.database_path = database_path
        self.yaml_path = yaml_path
        self.labels_path = labels_path

        self.yaml_header = None
        self.yolo_classes = None
        self.class_numbers_dict = dict()
        self.class_names_dict = dict()

        self.layout_setup()
        self.read_yaml()
        self.show()

    def read_yaml(self):
        self.yolo_classes = dict()
        with open(f"{self.database_path}/{self.yaml_path}", 'r') as yaml_file:
            yaml_contents = yaml_file.readlines()
            self.yaml_header = yaml_contents[:yaml_contents.index("names:\n") + 1]
            yaml_contents = yaml_contents[yaml_contents.index("names:\n") + 1:]
            for ind, yaml_line in enumerate(yaml_contents):
                number_and_class = yaml_line.strip().replace("\n", "")
                object_number, object_class = number_and_class.split(":")

                self.yolo_classes.update({object_number.strip(): object_class.strip()})
                row_count = self.yolo_table.rowCount()
                self.yolo_table.setRowCount(row_count + 1)

                object_number_item = QTableWidgetItem(object_number)
                object_number_item.setFlags(~Qt.ItemFlag.ItemIsEditable)
                object_class_item = QTableWidgetItem(object_class)
                object_class_item.setFlags(~Qt.ItemFlag.ItemIsEditable)

                self.yolo_table.setItem(row_count, 0, object_number_item)
                self.yolo_table.setItem(row_count, 1, object_class_item)
                self.yolo_table.setItem(row_count, 2, QTableWidgetItem(object_number))
                self.yolo_table.setItem(row_count, 3, QTableWidgetItem(object_class))

    def discard(self):
        self.close()

    def read_new_classes(self):
        for row in range(self.yolo_table.rowCount()):
            self.class_numbers_dict.update({self.yolo_table.item(row, 0).text(): self.yolo_table.item(row, 2).text()})
            self.class_names_dict.update({self.yolo_table.item(row, 1).text(): self.yolo_table.item(row, 3).text()})

    def overwrite_yaml(self):
        yaml_contents = []
        with open(f"{self.database_path}/{self.yaml_path}", 'r') as yaml_reader:
            yaml_contents = yaml_reader.readlines()
        yaml_contents = yaml_contents[yaml_contents.index("names:\n") + 1:]

        new_yaml_contents = []

        for line in yaml_contents:
            line_as_list = line.split(" ")
            line_as_list[0] = self.class_numbers_dict[line_as_list[0]]
            new_yaml_contents.append(" ".join(line_as_list))

        # print(yaml_contents)

    def overwrite_database(self):
        for label_file in self.labels_path:
            label_file_contents = []
            with open(f"{self.database_path}/{label_file}", 'r') as label_reader:
                label_file_contents = label_reader.readlines()

            new_label_file_contents = []
            for line in label_file_contents:
                line_as_list = line.split(" ")
                line_as_list[0] = self.class_numbers_dict[line_as_list[0]]
                new_label_file_contents.append(" ".join(line_as_list))

            with open(f"{self.database_path}/{label_file}", 'w') as label_writer:
                label_writer.writelines(new_label_file_contents)

    def overwrite(self):
        self.read_new_classes()
        # self.overwrite_database()
        self.overwrite_yaml()

    def layout_setup(self):
        box_layout = QVBoxLayout()

        button_layout = QHBoxLayout()
        self.overwrite_button = QPushButton("Overwrite")
        self.overwrite_button.clicked.connect(self.overwrite)
        button_layout.addWidget(self.overwrite_button)

        self.discard_button = QPushButton("Discard")
        self.discard_button.clicked.connect(self.discard)
        button_layout.addWidget(self.discard_button)

        box_layout.addLayout(button_layout)

        self.yolo_table = QTableWidget(0, 4)
        self.yolo_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.yolo_table.verticalHeader().setVisible(False)
        self.yolo_table.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        for header_ind, header_label in enumerate(
                ['Old class number', 'Old class name', "New class number", "New class name"]):
            header_item = QTableWidgetItem(header_label)
            header_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.yolo_table.setHorizontalHeaderItem(header_ind, header_item)

        box_layout.addWidget(self.yolo_table)
        self.setLayout(box_layout)
