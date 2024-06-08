from typing import Callable

import cv2
from numpy import ndarray

from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtWidgets import QLabel, QWidget
from PyQt6.QtGui import QMouseEvent
from matplotlib.backend_bases import MouseButton

from tools import q_pixmap_from_cv_img

from label_tools import Label, label_from_coords, coords_from_label


class InteractiveImage(QLabel):
    """QLabel containing the image, used to easily determine the mouse click position in relation to the image,
    allows for zooming"""

    def __init__(self, rect_drawn_handler: Callable, zoom_handler: Callable):
        super().__init__()
        self.ori_image = None
        self.image = None
        self.temp_image = None
        self.rect_drawn_handler = rect_drawn_handler
        self.zoom_handler = zoom_handler
        self.drawing_mode = False
        self.interactive_mode = False
        self.start_point = None
        self.image_size = [0, 0]  # [width, height]
        self.zoom_factor = 1

        self.setAlignment(Qt.AlignmentFlag.AlignTop)

    def preprocess_image(self, image: ndarray):
        """Resize the image to fit inside the label"""
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
        if mouse_event.button() is Qt.MouseButton.LeftButton and self.interactive_mode:
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
        if self.drawing_mode and (mouse_event.button() is Qt.MouseButton.LeftButton):
            end_point = [mouse_event.pos().x(), mouse_event.pos().y()]

            # If rectangle was released out of the image boundaries
            if end_point[0] < 0:
                end_point[0] = 0

            if end_point[0] > self.image_size[0] * self.zoom_factor:
                end_point[0] = self.image_size[0] * self.zoom_factor
                print('X too large')

            if end_point[1] < 0:
                end_point[1] = 0

            if end_point[1] > self.image_size[1] * self.zoom_factor:
                end_point[1] = self.image_size[1] * self.zoom_factor
                print('Y too large')

            s_point_translate = [int(self.start_point[0] / self.zoom_factor),
                                 int(self.start_point[1] / self.zoom_factor)]
            e_point_translate = [int(end_point[0] / self.zoom_factor), int(end_point[1] / self.zoom_factor)]

            self.rect_drawn_handler(label_from_coords(s_point_translate, e_point_translate, self.image_size))
            # Clearing the temporary rectangle
            self.temp_image = self.image.copy()
            self.setPixmap(q_pixmap_from_cv_img(self.temp_image))
            self.start_point = None
            self.drawing_mode = False

    def wheelEvent(self, event):
        """Reacts to the scroll-wheel event, zooms in or out depending on the direction"""
        if self.interactive_mode:
            zoom = self.zoom_factor
            if event.angleDelta().y() > 0:
                zoom += 0.1
            else:
                if self.zoom_factor > 0.2:
                    zoom -= 0.1

            # a0.position()
            self.zoom_changed(zoom)
            self.zoom_handler(self.zoom_factor)

    def zoom_changed(self, zoom: float):
        """Resizes the image based on the zoom factor"""
        self.zoom_factor = zoom
        img = self.ori_image.copy()
        h, w = img.shape[:2]
        self.image = cv2.resize(src=img, dsize=(int(w * zoom), int(h * zoom)))
        self.update_image()

    def clear_labels(self):
        """Recover the original image without annotations"""
        self.image = self.ori_image.copy()
        self.update_image()

    def change_image(self, image: ndarray):
        """Load a new image into the label"""
        self.ori_image = self.preprocess_image(image)
        self.image = self.ori_image.copy()
        self.temp_image = self.ori_image.copy()
        self.update_image()

    def update_image(self):
        """Change image to the content of self.image"""
        self.setPixmap(q_pixmap_from_cv_img(self.image))

    def paint_rect_from_label(self, label: Label, col: tuple):
        """Paint an annotation based on the label"""
        lu_corner, rb_corner = coords_from_label(label, self.image_size)

        lu_corner = (int(lu_corner[0] * self.zoom_factor), int(lu_corner[1] * self.zoom_factor))
        rb_corner = (int(rb_corner[0] * self.zoom_factor), int(rb_corner[1] * self.zoom_factor))

        cv2.rectangle(self.image, lu_corner, rb_corner, col)
        cv2.putText(self.image, label.class_name, lu_corner, 1, 1, col, 1)
        self.update_image()
