from typing import Callable

import cv2
import numpy

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QMouseEvent

from tools import q_pixmap_from_cv_img

from label_tools import label_from_coords, coords_from_label


class InteractiveImage(QLabel):
    """QLabel containing the image, used to easily determine the mouse click position in relation to the image"""

    def __init__(self, rect_drawn_handler: Callable):
        # TODO docstring and comments
        super().__init__()
        self.ori_image = None
        self.image = None
        self.temp_image = None
        self.rect_drawn_handler = rect_drawn_handler
        self.drawing_mode = False
        self.start_point = None
        self.image_size = [0, 0]  # [width, height]
        self.setAlignment(Qt.AlignmentFlag.AlignTop)

    def preprocess_image(self, image: numpy.ndarray):
        # TODO docstring and comments
        new_image_height, new_image_width = list(image.shape[:2])

        if new_image_height > self.size().height():
            new_image_width = int(new_image_width / (new_image_height / self.size().height()))
            new_image_height = self.size().height()

        if new_image_width > self.size().width():
            new_image_height = int(new_image_height / (new_image_width / self.size().width()))
            new_image_width = self.size().width()

        image_resized = cv2.resize(src=image, dsize=(new_image_width, new_image_height))
        self.image_size = new_image_width, new_image_height
        return image_resized

    def mousePressEvent(self, mouse_event: QMouseEvent):
        """Overriding the default mousePressEvent, collecting the mouse press position and turning on the drawing
        mode"""
        self.start_point = mouse_event.pos().x(), mouse_event.pos().y()
        self.drawing_mode = True

    def mouseMoveEvent(self, mouse_event: QMouseEvent):
        """Overriding the default mouseMoveEvent, showing the rectangle drawn so far"""
        if self.drawing_mode:
            mouse_position = mouse_event.pos().x(), mouse_event.pos().y()

            # Clearing the temporary rectangle
            self.temp_image = self.image.copy()

            # Paint a temporary rectangle
            cv2.rectangle(self.temp_image, self.start_point, mouse_position, (0, 0, 255))
            self.setPixmap(q_pixmap_from_cv_img(self.temp_image))

    def mouseReleaseEvent(self, mouse_event: QMouseEvent):
        """Overriding the default mouseReleaseEvent, collecting the drawn rectangular coordinates and turning off the
        drawing mode"""
        if self.drawing_mode:
            end_point = [mouse_event.pos().x(), mouse_event.pos().y()]

            # If rectangle was released out of the image boundaries
            if end_point[0] < 0:
                end_point[0] = 0

            if end_point[0] > self.image_size[0]:
                end_point[0] = self.image_size[0]

            if end_point[1] < 0:
                end_point[1] = 0

            if end_point[1] > self.image_size[1]:
                end_point[1] = self.image_size[1]

            self.rect_drawn_handler(label_from_coords(self.start_point, end_point, self.image_size))
            # Clearing the temporary rectangle
            self.temp_image = self.image.copy()
            self.setPixmap(q_pixmap_from_cv_img(self.temp_image))
            self.start_point = None
            self.drawing_mode = False

    def clear_labels(self):
        # TODO docstring
        self.image = self.ori_image.copy()
        self.update_image()

    def change_image(self, image):
        # TODO docstring
        self.ori_image = self.preprocess_image(image)
        self.image = self.ori_image.copy()
        self.temp_image = self.ori_image.copy()
        self.update_image()

    def update_image(self):
        # TODO docstring
        self.setPixmap(q_pixmap_from_cv_img(self.image))

    def paint_rect_from_label(self, label, col):
        # TODO docstring
        lu_corner, rb_corner = coords_from_label(label, self.image_size)

        cv2.rectangle(self.image, lu_corner, rb_corner, col)
        cv2.putText(self.image, label.class_name, lu_corner, 1, 1, col, 1)
        self.update_image()
