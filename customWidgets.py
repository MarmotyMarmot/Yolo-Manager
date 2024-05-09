from typing import Callable

import cv2
import numpy

from PyQt6.QtWidgets import QLabel, QPushButton
from PyQt6.QtGui import QMouseEvent, QScrollEvent

from tools import q_pixmap_from_cv_img


class LabelListButton(QPushButton):
    def __init__(self, text: str, parent, onClickFunc: Callable):
        super().__init__(text, parent)
        self.text = text
        self.onClickFunc = onClickFunc
        self.clicked.connect(self.onClick)

    def onClick(self):
        self.onClickFunc(self, self.text)


class InteractiveImage(QLabel):
    """QLabel containing the image, used to easily determine the mouse click position in relation to the image"""

    def __init__(self, rect_drawn_handler: Callable):
        super().__init__()
        self.image = None
        self.temp_image = None
        self.rect_drawn_handler = rect_drawn_handler
        self.drawing_mode = False
        self.start_point = None

    def preprocess_image(self, image: numpy.ndarray):

        new_image_size = list(image.shape[:2])
        if image.shape[0] > self.size().height():
            new_image_size[1] = self.size().height()

        if image.shape[1] > self.size().width():
            new_image_size[0] = self.size().width()

        image_resized = cv2.resize(src=image, dsize=new_image_size)
        return image_resized
        # cv2.resize(image, )
        # q_pixmap_from_cv_img(preprocessed_image)

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

            if end_point[0] > self.temp_image.shape[1]:
                end_point[0] = self.temp_image.shape[1]

            if end_point[1] < 0:
                end_point[1] = 0

            if end_point[1] > self.temp_image.shape[0]:
                end_point[1] = self.temp_image.shape[0]

            self.rect_drawn_handler(self.start_point, end_point)
            # Clearing the temporary rectangle
            self.temp_image = self.image.copy()
            self.setPixmap(q_pixmap_from_cv_img(self.temp_image))
            self.start_point = None
            self.drawing_mode = False

    def change_image(self, image):
        self.image = self.preprocess_image(image)
        self.temp_image = self.image.copy()
        self.update_image()

    def update_image(self):
        self.setPixmap(q_pixmap_from_cv_img(self.image))

    def paint_rect(self, lu_corner, rb_corner, col):
        cv2.rectangle(self.image, lu_corner, rb_corner, col)
        self.update_image()
