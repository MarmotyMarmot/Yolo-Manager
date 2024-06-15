import asyncio
import os

import cv2

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QGuiApplication, QIcon
from PyQt6.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QScrollArea, QWidget, QFileDialog, \
    QCheckBox, QSizePolicy, QMessageBox, QSpinBox

from UI.yaml_editor import YAMLEditor
from UI.small_custom_widgets import LabelListButton, StringSpinBox, ProportionSpinBox, SwitchButton, ZoomTool, Notify
from UI.interactive_image import InteractiveImage

from tools import max_string, rgb_to_bgr, rgb_from_scale
from dataset_tools import (dataset_checkout, get_images_and_labels, get_available_classes_and_yaml,
                           prepare_dataset_for_training)

from label_tools import Label, label_from_yolo_v5, yolo_v5_from_label
from fine_tuner import FineTuner


class LabellerUI(QDialog):
    def __init__(self):
        """Main window of the YOLO Manager"""
        super().__init__()
        self.available_classes = dict()
        self.selected_class = 0
        self.active_labels = []
        self.visible_class_count = dict()
        self.tmp_dir = 'tmp'
        self.dataset_path = ''
        self.yaml_path = ''
        self.image_files = []
        self.label_files = []
        self.image_index = 0
        self.clipboard = None
        self.labels_exists = False
        self.dataset_loaded_flag = False
        self.fine_tune_mode = False
        self.yaml_editor = None
        self.fine_tuner = FineTuner()

        self.setWindowTitle("YOLO Manager")
        self.setWindowIcon(QIcon(os.path.join("resources", "YOLO-Manager_LOGO.ico")))
        self.layout_setup()
        self.show()

    def layout_setup(self):
        """Sets up the UI"""
        screen_size = QGuiApplication.primaryScreen().size()
        self.setStyleSheet('background-color: rgb(228, 219, 255);')
        horizontal_layout = QHBoxLayout()

        # Left part setup
        vertical_widget_left = QWidget()
        vertical_widget_left.setStyleSheet('background-color: rgb(192, 173, 255);')
        vertical_layout_left = QVBoxLayout()
        vertical_widget_left.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        vertical_layout_left.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.read_dataset_button = QPushButton("Read dataset")
        self.read_dataset_button.setStyleSheet("background-color: rgb(0, 255, 0);")
        self.read_dataset_button.clicked.connect(self.select_dataset)

        self.verify_dataset_button = QPushButton("Verify dataset")
        self.verify_dataset_button.clicked.connect(self.validate_dataset)

        self.modify_classes_button = QPushButton("Modify classes")
        self.modify_classes_button.clicked.connect(self.modify_classes)

        self.training_proportions_label = QLabel("Training Proportions")
        self.dataset_proportions = ProportionSpinBox()
        self.prepare_for_training_button = QPushButton("Prepare for training")
        self.prepare_for_training_button.clicked.connect(self.prepare_for_training)

        self.class_spin_box = StringSpinBox(["0"])
        self.class_spin_box.setStyleSheet("background-color: rgb(228, 219, 255);")

        self.labels_on_checkbox = QCheckBox("Show labels")
        self.save_on_change_checkbox = QCheckBox("Save on change")
        self.lock_editing_checkbox = QCheckBox("Enable edition")
        self.labels_on_checkbox.setChecked(True)
        self.labels_on_checkbox.checkStateChanged.connect(self.toggle_editing)

        self.select_model_button = QPushButton("Select model")
        self.fine_tune_button = QPushButton("Fine tune")
        self.fine_tune_all_button = QPushButton("Fine tune all")
        # self.fine_tune_all_button.setEnabled(False)
        self.fine_tune_switch = SwitchButton("Mode", self.toggle_fine_tune, ["Average", "Overwrite"])

        vertical_layout_left.addWidget(self.read_dataset_button)
        vertical_layout_left.addWidget(self.verify_dataset_button)
        vertical_layout_left.addWidget(self.modify_classes_button)
        vertical_layout_left.addWidget(QLabel(""))

        vertical_layout_left.addWidget(self.training_proportions_label)
        vertical_layout_left.addLayout(self.dataset_proportions)
        vertical_layout_left.addWidget(self.prepare_for_training_button)
        vertical_layout_left.addWidget(QLabel(""))

        vertical_layout_left.addWidget(QLabel("Class"))
        vertical_layout_left.addWidget(self.class_spin_box)
        vertical_layout_left.addWidget(QLabel(""))

        vertical_layout_left.addWidget(self.labels_on_checkbox)
        vertical_layout_left.addWidget(self.save_on_change_checkbox)
        vertical_layout_left.addWidget(self.lock_editing_checkbox)
        vertical_layout_left.addWidget(QLabel(""))

        vertical_layout_left.addWidget(QLabel("AI"))
        vertical_layout_left.addWidget(self.select_model_button)
        self.select_model_button.clicked.connect(self.select_model)
        vertical_layout_left.addWidget(self.fine_tune_button)
        self.fine_tune_button.clicked.connect(self.fine_tune_current)
        vertical_layout_left.addWidget(self.fine_tune_all_button)
        self.fine_tune_all_button.clicked.connect(self.fine_tune_all)

        vertical_layout_left.addLayout(self.fine_tune_switch)

        # Middle part setup
        vertical_widget_middle = QWidget()
        vertical_widget_middle.setStyleSheet('background-color: rgb(228, 219, 255);')
        vertical_layout_middle = QVBoxLayout()
        self.image_label = InteractiveImage(self.new_label, self.zoom)
        self.image_label.setFixedSize(int(screen_size.width() / 2), int(screen_size.height() / 2))
        vertical_layout_middle.addWidget(self.image_label)

        # Right part setup
        vertical_widget_right = QWidget()
        vertical_widget_right.setStyleSheet('background-color: rgb(192, 173, 255);')
        vertical_widget_right.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        vertical_layout_right = QVBoxLayout()
        vertical_layout_right.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.image_name_label = QLabel("Image name")
        self.image_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        image_index_label_cont = QHBoxLayout()
        image_index_label = QLabel("Image Index")
        image_index_label.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum)
        image_index_label_cont.addWidget(image_index_label)
        self.image_index_spinbox = QSpinBox(self)
        self.image_index_spinbox.setEnabled(False)
        self.image_index_spinbox.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum)
        self.image_index_spinbox.setAlignment(Qt.AlignmentFlag.AlignRight)
        image_index_label_cont.addWidget(self.image_index_spinbox)
        self.image_quantity_label = QLabel(" / 0")
        self.image_quantity_label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        image_index_label_cont.addWidget(self.image_quantity_label)

        self.save_button = QPushButton("Save")
        self.next_button = QPushButton("Next")
        self.prev_button = QPushButton("Previous")

        self.zoom_tool = ZoomTool(self.zoom)

        self.copy_button = QPushButton("Copy Labels")
        self.paste_button = QPushButton("Paste Labels")

        self.image_index_spinbox.valueChanged.connect(self.image_index_spinbox_changed)
        self.save_button.clicked.connect(self.save_labels)
        self.next_button.clicked.connect(self.next_image_and_labels)
        self.prev_button.clicked.connect(self.previous_image_and_labels)
        self.copy_button.clicked.connect(self.copy_labels)
        self.paste_button.clicked.connect(self.paste_labels)

        vertical_layout_right.addWidget(self.image_name_label)
        vertical_layout_right.addLayout(image_index_label_cont)
        vertical_layout_right.addWidget(self.save_button)
        vertical_layout_right.addWidget(self.next_button)
        vertical_layout_right.addWidget(self.prev_button)
        vertical_layout_right.addWidget(QLabel(""))
        vertical_layout_right.addWidget(QLabel('Active Labels'))

        self.label_list_widget = QWidget()
        self.label_list_container = QVBoxLayout()
        self.label_list_container.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.label_list_widget.setLayout(self.label_list_container)

        label_list_scroll = QScrollArea()
        label_list_scroll.setWidgetResizable(True)
        label_list_scroll.setWidget(self.label_list_widget)

        vertical_layout_right.addWidget(label_list_scroll)
        vertical_layout_right.addWidget(QLabel(""))

        vertical_layout_right.addWidget(self.copy_button)
        vertical_layout_right.addWidget(self.paste_button)

        vertical_layout_right.addWidget(QLabel(""))
        vertical_layout_right.addLayout(self.zoom_tool)

        vertical_widget_left.setLayout(vertical_layout_left)
        vertical_widget_middle.setLayout(vertical_layout_middle)
        vertical_widget_right.setLayout(vertical_layout_right)

        horizontal_layout.addWidget(vertical_widget_left)
        horizontal_layout.addWidget(vertical_widget_middle)
        horizontal_layout.addWidget(vertical_widget_right)

        self.setLayout(horizontal_layout)

    def resizeEvent(self, event):
        """Adjust the image label to the new window size"""
        new_size = self.size()
        self.image_label.setFixedSize(int(new_size.width() / 1.5), int(new_size.height() / 1.1))

        if self.dataset_path != '':
            self.update_ui()

    def closeEvent(self, event):
        """Closing the window and the yaml editor if opened"""
        answer = QMessageBox.question(self, 'Confirmation',
                                      'All unsaved changes will be lost, do still you want to quit?',
                                      QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        if answer == QMessageBox.StandardButton.Cancel:
            event.ignore()
        elif answer == QMessageBox.StandardButton.Ok:
            if isinstance(self.yaml_editor, YAMLEditor):
                self.yaml_editor.close()
            event.accept()

    def keyPressEvent(self, event):
        match event.key():
            case Qt.Key.Key_A:
                self.previous_image_and_labels()
            case Qt.Key.Key_D:
                self.next_image_and_labels()
            case Qt.Key.Key_S:
                self.save_labels()
            case Qt.Key.Key_C:
                self.copy_labels()
            case Qt.Key.Key_V:
                self.paste_labels()
            case Qt.Key.Key_Plus:
                self.zoom(-1, True)
            case Qt.Key.Key_Underscore:
                self.zoom(-1, False)
            case Qt.Key.Key_Escape:
                self.close()

    def toggle_editing(self):
        self.lock_editing_checkbox.setEnabled(self.labels_on_checkbox.isChecked())
        self.update_ui()

    def toggle_fine_tune(self, fine_tune_mode):
        self.fine_tune_mode = fine_tune_mode

    def select_dataset(self):
        """Lets the user select a dataset"""
        self.dataset_path = QFileDialog.getExistingDirectory(self, "Select the dataset directory")
        if not self.dataset_path == '':
            self.read_dataset()
        else:
            Notify(self, "To read the dataset, choose its directory")

    def read_dataset(self):
        """Reads the dataset into the UI from self.dataset_path"""
        self.setEnabled(True)
        self.yaml_editor = None
        self.clipboard = None

        if len(self.image_files) != 0:
            print('WARN USER ABOUT CHANGING AND SAVING THE OLD DATASET')

        self.available_classes = dict()

        self.dataset_loaded_flag = True
        self.image_label.interactive_mode = True
        self.zoom_tool.active = True
        self.read_dataset_button.setStyleSheet("")

        self.image_files, self.label_files = get_images_and_labels(self.dataset_path)
        self.yaml_path, self.available_classes = get_available_classes_and_yaml(self.dataset_path)

        if self.yaml_path is not None:
            self.read_yaml()

        class_names_in_order = []
        for key in range(len(self.available_classes.keys())):
            class_names_in_order.append(self.available_classes[f"{key}"])

        self.class_spin_box.set_strings(class_names_in_order)
        self.class_spin_box.setValue(0)

        self.image_name_label.setText(self.image_files[self.image_index])

        self.image_index_spinbox.setRange(0, len(self.image_files) - 1)
        self.image_index_spinbox.setEnabled(True)
        self.image_quantity_label.setText(f"/ {len(self.image_files) - 1}")

        self.update_ui()

    def validate_dataset(self):
        """Validates the dataset and gives feedback to the user"""
        if self.dataset_loaded_flag:
            verify_flag, invalid_files = dataset_checkout(self.dataset_path)

            if verify_flag:
                Notify(self, 'Dataset valid')
            else:
                Notify(self, f'Dataset invalid, fix :\n{invalid_files}')

    def prepare_for_training(self):
        """Asks the user to point to the destination folder and copies the divided dataset into given folder"""
        if self.dataset_loaded_flag:
            # Ask user to point to the output directory
            training_directory = QFileDialog.getExistingDirectory(self, "Select Training Dataset Directory")
            train_prop, val_prop = self.dataset_proportions.get_proportions()
            prepare_dataset_for_training(self.dataset_path, training_directory, self.yaml_path, train_prop)

    def read_yaml(self):
        """Reading available classes from yaml file"""
        with open(f"{self.dataset_path}/{self.yaml_path}", 'r') as yaml_file:
            yaml_contents = yaml_file.readlines()
            yaml_contents = yaml_contents[yaml_contents.index("names:\n") + 1:]
            for yaml_line in yaml_contents:
                number_and_class = yaml_line.strip().replace("\n", "")
                object_number, object_class = number_and_class.split(": ")
                self.available_classes.update({object_number: object_class})

    def modify_classes(self):
        """Opening yaml editor and suspending the main window"""
        if self.yaml_path != '':
            self.yaml_editor = YAMLEditor(self.dataset_path, self.yaml_path, self.label_files, self.read_dataset)
            self.setEnabled(False)
        else:
            Notify(self, '.yaml file not found')

    def image_index_spinbox_changed(self):
        if self.save_on_change_checkbox.isChecked():
            self.save_labels()
        self.image_index = self.image_index_spinbox.value()
        self.image_name_label.setText(self.image_files[self.image_index])
        self.update_ui()

    def next_image_and_labels(self):
        """Switching to the next image and label, saving if requested"""
        if not self.image_index >= len(self.image_files) - 1:
            if self.save_on_change_checkbox.isChecked():
                self.save_labels()
            self.image_index += 1
            self.image_index_spinbox.setValue(self.image_index)
            self.image_name_label.setText(self.image_files[self.image_index])
            self.update_ui()
            return True
        else:
            return False

    def previous_image_and_labels(self):
        """Switching to the previous image and label, saving if requested"""
        if not self.image_index <= 0:
            if self.save_on_change_checkbox.isChecked():
                self.save_labels()
            self.image_index -= 1
            self.image_index_spinbox.setValue(self.image_index)
            self.image_name_label.setText(self.image_files[self.image_index])
            self.update_ui()
            return True
        else:
            return False

    def save_labels(self):
        """Saving active labels to labels file, if active labels is empty, deletes labels file"""
        if self.dataset_loaded_flag:
            image_name = self.image_files[self.image_index]
            labels_path = os.path.join(self.dataset_path, f"{image_name[:image_name.index('.')]}.txt")
            if self.labels_exists:
                if len(self.active_labels) == 0:
                    os.remove(labels_path)
                else:
                    with open(labels_path, 'w') as labels_writer:
                        labels_writer.writelines([yolo_v5_from_label(label) for label in self.active_labels])

    def update_ui(self):
        """Reads the image with labels and loads them into the UI"""
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
        """Reads image from a path"""
        self.image_label.change_image(cv2.imread(os.path.join(self.dataset_path, self.image_files[self.image_index])))

    def read_labels(self):
        """Reading the labels, based on displayed image"""
        image_name = self.image_files[self.image_index]
        labels_name = f"{image_name[:image_name.index('.')]}.txt"

        if labels_name in self.label_files:
            with open(os.path.join(self.dataset_path, labels_name), 'r') as labels_file:
                labels = [label_from_yolo_v5(label, self.available_classes[label.split(" ")[0]]) for label in
                          labels_file.readlines()]
                self.active_labels = labels
                self.labels_exists = True
        else:
            self.labels_exists = False

        self.visible_class_count = dict()

    def select_model(self):
        """Lets the user select the dataset"""
        model_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select model file",
            "${HOME}",
            "Model Files (*.pt)",
        )
        if model_path is not '':
            self.fine_tuner.set_model(model_path)
        else:
            Notify(self, 'Select the model to use it')

    def fine_tune_current(self):
        """Fine-tunes the labels on the current image"""
        if self.fine_tuner.model is not None and self.lock_editing_checkbox.isChecked():
            if not self.fine_tune_mode:
                self.active_labels = self.fine_tuner.average_detections(self.image_label.ori_image, self.active_labels)
            else:
                self.active_labels = self.fine_tuner.detect(self.image_label.ori_image, self.available_classes)
            self.read_image()
            self.update_labels_list()
            self.paint_labels()
            return True
        else:
            return False

    def fine_tune_all(self):
        """At the moment, this function does nothing"""
        print(f'FINE TUNING ALL IN {self.dataset_path}')
        while self.image_index < len(self.image_files) - 1:
            self.fine_tune_current()
            self.image_index += 1
            self.update_ui()
            self.update()
            print('Iter')
            print(self.image_index)

    def update_visible_class_count(self, class_number: str, increment: bool = True) -> int:
        """Incrementing or decrementing the number of visible objects assigned to each class
        :return: the number of objects of this class"""

        if class_number in list(self.visible_class_count.keys()):
            if increment:
                self.visible_class_count.update({class_number: self.visible_class_count[class_number] + 1})
            else:
                self.visible_class_count.update({class_number: self.visible_class_count[class_number] - 1})
        else:
            self.visible_class_count.update({class_number: 1})

        return self.visible_class_count[class_number]

    def update_labels_list(self):
        """Updating the label list displayed on the right side of the UI"""
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

    def zoom(self, zoom: float, incr=True):
        """Change the zoom level in the image label"""
        if self.dataset_loaded_flag:

            match zoom:
                case self.zoom_tool.zoom_level:  # Zooming using zoom_tool
                    self.image_label.zoom_changed(zoom)
                case self.image_label.zoom_factor:  # Zooming using image_label
                    self.zoom_tool.set_zoom(zoom)
                case _:  # Zooming using keyboard
                    if incr:
                        self.zoom_tool.increment()
                    else:
                        self.zoom_tool.decrement()

            self.paint_labels()
