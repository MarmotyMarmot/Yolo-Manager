import yolov5

from label_tools import Label, label_from_coords, get_iou, average_label


class FineTuner:
    def __init__(self):
        """Class containing methods for fine-tuning YOLOv5 models."""
        self.model = None

    def set_model(self, model_path):
        """Setting model from path to be used in other methods"""
        self.model = yolov5.load(model_path)

    def average_detections(self,
                           image,
                           default_labels: list[Label],
                           score_threshold: float = 0.9,
                           iou_threshold: float = 0.9):
        """Averaging detections of model and already known labels"""
        if default_labels is []:
            return default_labels

        h, w, _ = image.shape
        detections_tensor = self.model(image).pred[0]
        for detection in detections_tensor.tolist():
            label = label_from_coords(detection[:2], detection[2:4], [w, h])
            score = detection[4]
            class_id = detection[5]

            if score > score_threshold:
                for ind, default_label in enumerate(default_labels):
                    if ((get_iou(label, default_label) > iou_threshold) and
                            (int(class_id) == int(default_label.class_number))):
                        default_labels[ind] = average_label(default_label, label)

        return default_labels

    def detect(self, image, class_dict, score_threshold: float = 0.9):
        """Run detection on image and return detected labels"""
        detections = []
        h, w, _ = image.shape
        detections_tensor = self.model(image).pred[0]
        for detection in detections_tensor.tolist():
            label = label_from_coords(detection[:2], detection[2:4], [w, h])
            score = detection[4]
            class_id = int(detection[5])

            label.class_number = str(class_id)
            label.class_name = class_dict[str(class_id)]

            if score > score_threshold:
                detections.append(label)

        return detections
