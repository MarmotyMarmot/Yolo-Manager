from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QPushButton, QWidget, QTableWidget, QTableWidgetItem, QHeaderView, \
    QAbstractScrollArea
from PyQt6.QtCore import Qt

from tools import notfound


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

        self.setWindowTitle("YAML Editor")
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
                object_number, object_class = number_and_class.split(": ")

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
            line_as_list = line.strip().replace("\n", "").split(": ")
            space_num = notfound(line, " ")

            if line_as_list[0] in self.class_numbers_dict.keys():
                line_as_list[0] = self.class_numbers_dict[line_as_list[0]]

            if line_as_list[1] in self.class_names_dict.keys():
                line_as_list[1] = self.class_names_dict[line_as_list[1]]

            new_yaml_contents.append(space_num * " " + ": ".join(line_as_list) + "\n")

        with open(f"{self.database_path}/{self.yaml_path}", 'w') as yaml_writer:
            yaml_writer.writelines(self.yaml_header)
            yaml_writer.writelines(new_yaml_contents)

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
