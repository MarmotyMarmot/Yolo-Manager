from typing import Self


class Label:
    """Class for storing labels and loading them from different formats"""

    def __init__(self, class_name, x_center, y_center, width, height):
        self.class_name = class_name
        self.x_center = x_center
        self.y_center = y_center
        self.width = width
        self.height = height


class LabelLoader:
    """Loader for Label class"""
    def label_from_yolo_v5(self, yolo_v5_label: str, class_name: str = None) -> Label:
        """Creates a new label from yolo_v5 label.
        :arg yolo_v5_label: label in format - class_number x_center y_center width height.
        :arg class_name: literal class name, for example - Plane.
        :return: Instance of a Label class."""
        label_params = []
        if class_name is None:
            label_params = class_name, *yolo_v5_label.split(" ")[1:]
        else:
            label_params = "", *yolo_v5_label.split(" ")[1:]

        return Label(*label_params)

    def label_from_coords(self, lu_corner: list[int, int], rb_corner: list[int, int],
                          image_size: list[int, int]) -> Label:
        """Creates a new label from rectangle coordinates and image size. Created label is nameless!
        :arg lu_corner: left upper corner coordinates.
        :arg rb_corner: right lower corner coordinates.
        :arg image_size: width and height of image in pixels.
        :return: Instance of a Label class."""
        pix_width = abs(rb_corner[0] - lu_corner[0])
        pix_height = abs(rb_corner[1] - lu_corner[1])

        if rb_corner[0] >= lu_corner[0]:
            x_center = round((lu_corner[0] + pix_width / 2) / image_size[0], 6)
        else:
            x_center = round((rb_corner[0] + pix_width / 2) / image_size[0], 6)

        if rb_corner[1] >= lu_corner[1]:
            y_center = round((lu_corner[1] + pix_height / 2) / image_size[1], 6)
        else:
            y_center = round((rb_corner[1] + pix_height / 2) / image_size[1], 6)

        width = round(pix_width / image_size[0], 6)
        height = round(pix_height / image_size[1], 6)

        return Label("", x_center, y_center, width, height)
