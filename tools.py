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
