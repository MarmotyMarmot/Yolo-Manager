import os.path
from colorsys import hsv_to_rgb

from numpy import ndarray
from PyQt6.QtGui import QPixmap, QImage


def q_pixmap_from_cv_img(cv_img: ndarray) -> QPixmap:
    """Convert numpy.ndarray to QPixmap
    :arg cv_img: cv2 image (numpy.ndarray) in BGR format
    :returns: PyQt6 QPixmap"""
    height, width, channel = cv_img.shape
    bytes_per_line = 3 * width
    q_image = QImage(cv_img.data, width, height, bytes_per_line, QImage.Format.Format_BGR888)
    return QPixmap.fromImage(q_image)


def notfound(string: str, not_val: str) -> int:
    """Return the first index in string where not_val character doesn't occur"""
    for ind, char in enumerate(string):
        if char != not_val:
            return ind


def max_string(list_of_strings: list[str]) -> int:
    """Returns maximum number from a list of numeric strings"""
    if len(list_of_strings) == 0:
        return 0
    try:
        return max(int(string) for string in list_of_strings)
    except ValueError:
        return 0


def rgb_to_bgr(rgb: list):
    """Converts RGB values to BGR"""
    return [rgb[2], rgb[1], rgb[0]]


def find_string_part_in_list(string_part: str, string_list: list) -> tuple:
    """Searches for substring in the list of strings.
     :returns (ind, string) if it exists, (-1, None) if it doesn't"""
    for ind, string in enumerate(string_list):
        if string_part in string:
            return ind, string
    return -1, None


def rgb_from_scale(value: int, scale: int, s: float = 0.95, v: float = 1):
    """Calculate appropriate RGB value from scale and value, based on the Hue value in HSV"""
    if scale == 0:
        hue = 0
    else:
        hue = value / scale

    rgb_normalized = hsv_to_rgb(hue, s, v)
    return [int(col * 255) for col in rgb_normalized]


def directory_checkout(directory: str):
    """Checks if directory exists and empties it, if it doesn't, creates it"""
    if os.path.isdir(directory):
        for file in os.listdir(directory):
            os.remove(f"{directory}/{file}")
    else:
        os.mkdir(directory)
