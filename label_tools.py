import copy
from typing import Self, Tuple, List


class Label:
    """Class for storing labels and loading them from different formats"""

    def __init__(self, class_name: str, class_number: str, x_center: float, y_center: float, width: float,
                 height: float):
        self.class_name = class_name
        self.class_number = class_number
        self.x_center = x_center
        self.y_center = y_center
        self.width = width
        self.height = height


def get_iou(label1: Label, label2: Label) -> float:
    bb1 = rectangle_from_label(label1)
    bb2 = rectangle_from_label(label2)

    intersect_w = min(bb1[1][0], bb2[1][0]) - max(bb1[0][0], bb1[0][0])
    intersect_h = min(bb1[1][1], bb2[1][1]) - max(bb1[0][1], bb2[0][1])

    if intersect_w <= 0 or intersect_h <= 0:
        return 0

    intersect_a = intersect_w * intersect_h

    bb1_area = (bb1[1][0] - bb1[0][0]) * (bb1[1][1] - bb1[0][1])
    bb2_area = (bb2[1][0] - bb2[0][0]) * (bb2[1][1] - bb2[0][1])

    union_area = bb1_area + bb2_area - intersect_a

    return intersect_a / union_area


def rectangle_from_label(label: Label) -> tuple[list[float], list[float]]:
    lu_corner = [label.x_center - label.width / 2, label.y_center - label.height / 2]
    br_corner = [label.x_center + label.width / 2, label.y_center + label.height / 2]
    return lu_corner, br_corner


def average_label(label1: Label, label2: Label) -> Label:
    averaged_label = copy.copy(label1)
    averaged_label.x_center = (min(label1.x_center, label2.x_center) +
                               (max(label1.x_center, label2.x_center) - min(label1.x_center, label2.x_center)) / 2)
    averaged_label.y_center = (min(label1.y_center, label2.y_center) +
                               (max(label1.y_center, label2.y_center) - min(label1.y_center, label2.y_center)) / 2)
    averaged_label.width = (min(label1.width, label2.width) +
                            (max(label1.width, label2.width) - min(label1.width, label2.width)) / 2)
    averaged_label.height = (min(label1.height, label2.height) +
                             (max(label1.height, label2.height) - min(label1.height, label2.height)) / 2)

    return averaged_label


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
    return f"{label.class_number} {label.x_center} {label.y_center} {label.width} {label.height}\n"


def label_from_coords(lu_corner: list[int, int], rb_corner: list[int, int],
                      image_size: list) -> Label:
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
