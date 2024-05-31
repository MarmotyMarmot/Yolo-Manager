import os
import random
import shutil

import cv2

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QScrollArea, QWidget, QFileDialog, \
    QCheckBox, QSizePolicy, QSpinBox

from UI.yaml_editor import YAMLEditor
from UI.small_custom_widgets import LabelListButton, StringSpinBox, ProportionSpinBox
from UI.interactive_image import InteractiveImage

from tools import max_string, rgb_to_bgr, rgb_from_scale, directory_checkout, find_string_part_in_list

from label_tools import Label, label_from_yolo_v5, yolo_v5_from_label


class LabellerUI(QDialog):
    def __init__(self):
        # TODO docstring and comments
        super().__init__()
        self.available_classes = dict()
        self.selected_class = 0
        self.active_labels = []
        self.visible_class_count = dict()
        self.tmp_dir = 'tmp'
        self.database_path = ''
        self.yaml_path = ''
        self.image_files = []
        self.label_files = []
        self.image_index = 0
        self.clipboard = None
        self.labels_exists = False
        self.dataset_loaded_flag = False

        self.setWindowTitle("YOLO Manager")
        self.layout_setup()
        self.show()

    def layout_setup(self):
        # TODO docstring and comments
        screen_size = QGuiApplication.primaryScreen().size()
        self.setStyleSheet('background-color: rgb(228, 219, 255);')
        horizontal_layout = QHBoxLayout()

        # Left part setup
        vertical_widget_left = QWidget()
        vertical_widget_left.setStyleSheet('background-color: rgb(192, 173, 255);')
        vertical_layout_left = QVBoxLayout()
        vertical_widget_left.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        vertical_layout_left.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.read_database_button = QPushButton("Read database")
        self.read_database_button.setStyleSheet("background-color: rgb(0, 255, 0);")
        self.read_database_button.clicked.connect(self.select_database)

        self.verify_database_button = QPushButton("Verify database")
        self.verify_database_button.clicked.connect(self.verify_database)

        self.modify_classes_button = QPushButton("Modify classes")
        self.modify_classes_button.clicked.connect(self.modify_classes)

        self.dataset_proportions = ProportionSpinBox()
        self.prepare_for_training_button = QPushButton("Prepare for training")
        self.prepare_for_training_button.clicked.connect(self.prepare_for_training)

        self.class_spin_box = StringSpinBox()
        self.class_spin_box.setStyleSheet("background-color: rgb(228, 219, 255);")

        self.labels_on_checkbox = QCheckBox("Show labels")
        self.save_on_change_checkbox = QCheckBox("Save on change")
        self.lock_editing_checkbox = QCheckBox("Enable edition")
        self.labels_on_checkbox.setChecked(True)
        self.labels_on_checkbox.checkStateChanged.connect(self.toggle_editing)

        vertical_layout_left.addWidget(self.read_database_button)
        vertical_layout_left.addWidget(self.verify_database_button)
        vertical_layout_left.addWidget(self.modify_classes_button)
        vertical_layout_left.addLayout(self.dataset_proportions)
        vertical_layout_left.addWidget(self.prepare_for_training_button)
        vertical_layout_left.addWidget(QLabel("Class"))
        vertical_layout_left.addWidget(self.class_spin_box)
        vertical_layout_left.addWidget(self.labels_on_checkbox)
        vertical_layout_left.addWidget(self.save_on_change_checkbox)
        vertical_layout_left.addWidget(self.lock_editing_checkbox)

        # Middle part setup
        vertical_widget_middle = QWidget()
        vertical_widget_middle.setStyleSheet('background-color: rgb(228, 219, 255);')
        vertical_layout_middle = QVBoxLayout()
        self.image_label = InteractiveImage(self.new_label)
        self.image_label.setFixedSize(int(screen_size.width() / 2), int(screen_size.height() / 2))
        self.image_label.change_image(cv2.imread('UI/test.png'))
        vertical_layout_middle.addWidget(self.image_label)

        # Right part setup
        vertical_widget_right = QWidget()
        vertical_widget_right.setStyleSheet('background-color: rgb(192, 173, 255);')
        vertical_widget_right.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        vertical_layout_right = QVBoxLayout()
        vertical_layout_right.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.save_button = QPushButton("Save")
        self.next_button = QPushButton("Next")
        self.prev_button = QPushButton("Previous")
        self.copy_button = QPushButton("Copy")
        self.paste_button = QPushButton("Paste")

        self.save_button.clicked.connect(self.save_labels)
        self.next_button.clicked.connect(self.next_image_and_labels)
        self.prev_button.clicked.connect(self.previous_image_and_labels)
        self.copy_button.clicked.connect(self.copy_labels)
        self.paste_button.clicked.connect(self.paste_labels)

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

        vertical_layout_right.addWidget(self.copy_button)
        vertical_layout_right.addWidget(self.paste_button)

        vertical_widget_left.setLayout(vertical_layout_left)
        vertical_widget_middle.setLayout(vertical_layout_middle)
        vertical_widget_right.setLayout(vertical_layout_right)

        horizontal_layout.addWidget(vertical_widget_left)
        horizontal_layout.addWidget(vertical_widget_middle)
        horizontal_layout.addWidget(vertical_widget_right)

        self.setLayout(horizontal_layout)

    def resizeEvent(self, event):
        # TODO docstring and comments
        new_size = self.size()
        self.image_label.setFixedSize(int(new_size.width() / 1.5), int(new_size.height() / 1.1))

        if self.database_path != '':
            self.update_ui()

    def toggle_editing(self):
        # TODO docstring
        self.lock_editing_checkbox.setEnabled(self.labels_on_checkbox.isChecked())

    def select_database(self):
        self.database_path = QFileDialog.getExistingDirectory(self, "Select Database Directory")
        if not self.database_path == '':
            self.read_database()

    def read_database(self):
        # TODO docstring and comments
        self.setEnabled(True)
        self.yaml_editor = None
        self.clipboard = None

        if len(self.image_files) != 0:
            print('WARN USER ABOUT CHANGING AND SAVING THE OLD DATABASE')

        self.available_classes = dict()

        self.dataset_loaded_flag = True
        self.read_database_button.setStyleSheet("")
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

        class_names_in_order = []
        for key in range(len(self.available_classes.keys())):
            class_names_in_order.append(self.available_classes[f"{key}"])

        self.class_spin_box.set_strings(class_names_in_order)
        self.class_spin_box.setValue(0)

        self.update_ui()

    def verify_database(self):
        # TODO docstring and comments
        if self.dataset_loaded_flag:
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
                        # verification of labels FOR YOLOv5, NOT UNIVERSAL,
                        # CHANGE IF DATABASE VERIFIER WILL BE IMPLEMENTED
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
                print(
                    f'Let the user know that the database is invalid and the {invalid_files} are causing the problems')

    def prepare_for_training(self):
        """Dividing the dataset according to the desired proportions and copying it into the selected directory"""
        if self.dataset_loaded_flag:
            # Get the relative paths saved in the yaml file
            with open(f"{self.database_path}/{self.yaml_path}", "r") as yaml_reader:
                yaml_contents = yaml_reader.readlines()
            _, train_path_line = find_string_part_in_list("train:", yaml_contents)
            _, val_path_line = find_string_part_in_list("val:", yaml_contents)
            train_images_path = train_path_line[train_path_line.index(":") + 1:train_path_line.index("#")].strip()
            val_images_path = val_path_line[val_path_line.index(":") + 1:val_path_line.index("#")].strip()

            train_labels_path = train_images_path.replace("images", "labels")
            val_labels_path = val_images_path.replace("images", "labels")

            # Ask user to point to the output directory
            training_directory = QFileDialog.getExistingDirectory(self, "Select Training Dataset Directory")

            train_images_full_path = os.path.join(training_directory, str(train_images_path))
            train_labels_full_path = os.path.join(training_directory, str(train_labels_path))
            val_images_full_path = os.path.join(training_directory, str(val_images_path))
            val_labels_full_path = os.path.join(training_directory, str(val_labels_path))

            directory_checkout(training_directory)
            directory_checkout(os.path.join(training_directory, "images"))
            directory_checkout(os.path.join(training_directory, "labels"))
            directory_checkout(train_images_full_path)
            directory_checkout(train_labels_full_path)
            directory_checkout(val_images_full_path)
            directory_checkout(val_labels_full_path)

            train_prop, val_prop = self.dataset_proportions.get_proportions()

            number_of_train_images = int(train_prop * len(self.image_files))

            image_files = self.image_files.copy()
            random.shuffle(image_files)

            train_images = image_files[:number_of_train_images]
            val_images = image_files[number_of_train_images:]

            for train_image in train_images:
                shutil.copy(os.path.join(self.database_path, str(train_image)),
                            os.path.join(train_images_full_path, str(train_image)))

                labels_name = f"{train_image[:train_image.index('.')]}.txt"
                labels_path = os.path.join(self.database_path, labels_name)

                if os.path.exists(labels_path):
                    shutil.copy(labels_path, os.path.join(train_labels_full_path, labels_name))

            for val_image in val_images:
                shutil.copy(os.path.join(self.database_path, str(val_image)),
                            os.path.join(val_images_full_path, str(val_image)))

                labels_name = f"{val_image[:val_image.index('.')]}.txt"
                labels_path = os.path.join(self.database_path, labels_name)

                if os.path.exists(labels_path):
                    shutil.copy(labels_path, os.path.join(val_labels_full_path, labels_name))

    def read_yaml(self):
        """Reading available classes from yaml file"""
        with open(f"{self.database_path}/{self.yaml_path}", 'r') as yaml_file:
            yaml_contents = yaml_file.readlines()
            yaml_contents = yaml_contents[yaml_contents.index("names:\n") + 1:]
            for yaml_line in yaml_contents:
                number_and_class = yaml_line.strip().replace("\n", "")
                object_number, object_class = number_and_class.split(": ")
                self.available_classes.update({object_number: object_class})

    def modify_classes(self):
        """Opening yaml editor and suspending the main window"""
        if self.yaml_path != '':
            self.yaml_editor = YAMLEditor(self.database_path, self.yaml_path, self.label_files, self.read_database)
            self.setEnabled(False)

    def closeEvent(self, a0):
        """Closing the window and the yaml editor if opened"""
        if isinstance(self.yaml_editor, YAMLEditor):
            self.yaml_editor.close()
        self.close()

    def next_image_and_labels(self):
        """Switching to the next image and label, saving if requested"""
        if not self.image_index >= len(self.image_files) - 1:
            if self.save_on_change_checkbox.isChecked():
                self.save_labels()
            self.image_index += 1
            self.update_ui()

    def previous_image_and_labels(self):
        """Switching to the previous image and label, saving if requested"""
        if not self.image_index <= 0:
            if self.save_on_change_checkbox.isChecked():
                self.save_labels()
            self.image_index -= 1
            self.update_ui()

    def save_labels(self):
        """Saving active labels to labels file, if active labels is empty, deletes labels file"""
        if self.dataset_loaded_flag:
            print('OVERWRITING LABELS')
            image_name = self.image_files[self.image_index]
            labels_path = os.path.join(self.database_path, f"{image_name[:image_name.index('.')]}.txt")
            if self.labels_exists:
                if len(self.active_labels) == 0:
                    os.remove(labels_path)
                else:
                    with open(labels_path, 'w') as labels_writer:
                        labels_writer.writelines([yolo_v5_from_label(label) for label in self.active_labels])

    def update_ui(self):
        """Reading the image with labels and loading them into UI"""
        if self.dataset_loaded_flag:
            self.read_image()
            self.read_labels()
            self.update_labels_list()
            self.paint_labels()

    def copy_labels(self):
        if self.dataset_loaded_flag:
            self.clipboard = self.active_labels

    def paste_labels(self):
        if self.dataset_loaded_flag and (self.clipboard is not None):
            self.active_labels += self.clipboard
            self.update_labels_list()
            self.paint_labels()

    def new_label(self, label: Label):
        """Adding a label to the displayed picture"""
        if self.dataset_loaded_flag:
            if self.lock_editing_checkbox.isChecked():
                label.class_number = str(self.class_spin_box.value())
                label.class_name = self.available_classes[str(self.class_spin_box.value())]
                self.active_labels.append(label)
                self.update_labels_list()
                self.paint_labels()

    def paint_labels(self):
        """Painting the active labels on the displayed image"""
        if self.labels_on_checkbox.isChecked():
            for label in self.active_labels:
                max_class_number = max_string(list(self.available_classes.keys()))
                rgb_col = rgb_from_scale(int(label.class_number), max_class_number)

                self.image_label.paint_rect_from_label(label, rgb_to_bgr(rgb_col))

    def read_image(self):
        """Reading image from path"""
        self.image_label.change_image(cv2.imread(os.path.join(self.database_path, self.image_files[self.image_index])))

    def read_labels(self):
        """Reading the labels, based on displayed image"""
        image_name = self.image_files[self.image_index]
        labels_name = f"{image_name[:image_name.index('.')]}.txt"

        if labels_name in self.label_files:
            with open(os.path.join(self.database_path, labels_name), 'r') as labels_file:
                labels = [label_from_yolo_v5(label, self.available_classes[label.split(" ")[0]]) for label in
                          labels_file.readlines()]
                self.active_labels = labels
                self.labels_exists = True
        else:
            self.labels_exists = False

        self.visible_class_count = dict()

    def update_visible_class_count(self, class_number: str, increment: bool = True) -> int:
        """Incrementing or decrementing the number of visible objects assigned to each class
        :arg class_number class number
        :arg increment should increment or decrement
        :return: number of objects of this class"""

        if class_number in list(self.visible_class_count.keys()):
            if increment:
                self.visible_class_count.update({class_number: self.visible_class_count[class_number] + 1})
            else:
                self.visible_class_count.update({class_number: self.visible_class_count[class_number] - 1})
        else:
            self.visible_class_count.update({class_number: 1})

        return self.visible_class_count[class_number]

    def update_labels_list(self):
        """Updating the labels list displayed on the right side of the UI"""
        for child in self.label_list_widget.children():
            if type(child) is not QVBoxLayout:
                child.deleteLater()

        for label in self.active_labels:
            class_count = self.update_visible_class_count(label.class_number)

            text = f"{label.class_name} {class_count}"

            class_number = max_string(list(self.available_classes.keys()))
            rgb_col = rgb_from_scale(int(label.class_number), class_number)
            self.label_list_container.addWidget(
                LabelListButton(text, label, rgb_col, self.label_list_widget, self.label_clicked))

    def label_clicked(self, widget, label):
        """Deleting the clicked label"""
        if self.lock_editing_checkbox.isChecked():
            widget.close()
            if label in self.active_labels:
                self.update_visible_class_count(label.class_number, increment=False)
                self.active_labels.remove(label)
                self.image_label.clear_labels()
                self.paint_labels()
