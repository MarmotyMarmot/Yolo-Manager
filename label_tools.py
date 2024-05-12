from typing import Self


class Label:
    """Class for storing labels and loading them from different formats"""

    def __init__(self, class_name: str, class_number: str, x_center: float, y_center: float, width: float, height: float):
        self.class_name = class_name
        self.class_number = class_number
        self.x_center = x_center
        self.y_center = y_center
        self.width = width
        self.height = height


def label_from_yolo_v5(yolo_v5_label: str, class_name: str = "") -> Label:
    """Creates a new label from yolo_v5 label.
    :arg yolo_v5_label: label in format - class_number x_center y_center width height.
    :arg class_name: literal class name, for example - Plane.
    :returns: Instance of a Label class."""
    label_params = []

    yolo_v5_label_split = yolo_v5_label.replace("\n", "").split(" ")

    yolo_v5_label_class_number = yolo_v5_label_split[0]
    yolo_v5_label_coords = [float(param) for param in yolo_v5_label_split[1:]]

    return Label(class_name, yolo_v5_label_class_number, *yolo_v5_label_coords)


def yolo_v5_from_label(label: Label) -> str:
    """Creates a yolo_v5 label from a label.
    :arg label: instance of a Label class.
    :returns: yolo_v5 label."""
    return f"{label.class_number} {label.x_center} {label.y_center} {label.width} {label.height}"


def label_from_coords(lu_corner: list[int, int], rb_corner: list[int, int],
                      image_size: list[int, int]) -> Label:
    """Creates a new label from rectangle coordinates and image size. Created label is nameless!
    :arg lu_corner: left upper corner coordinates.
    :arg rb_corner: right lower corner coordinates.
    :arg image_size: width and height of image in pixels.
    :returns: Instance of a Label class."""
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

    return Label("", "", x_center, y_center, width, height)


def coords_from_label(label: Label, image_size: list[int, int]) -> tuple[tuple[int, int], tuple[int, int]]:
    """Creates rectangular coordinates and from yolo_v5 label.
    :arg label: instance of a Label class.
    :arg image_size: width and height of image in pixels.
    :returns: Coordinates of left upper corner and right bottom corner."""
    lu_corner = (int(image_size[0] * (label.x_center - label.width / 2)),
                 int(image_size[1] * (label.y_center - label.height / 2)))
    rb_corner = (int(image_size[0] * (label.x_center + label.width / 2)),
                 int(image_size[1] * (label.y_center + label.height / 2)))
    return lu_corner, rb_corner
