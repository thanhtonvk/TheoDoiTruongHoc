import numpy as np
import cv2
from modules.SCRFD import SCRFD

class FaceDetector:
    def __init__(self, ctx_id=0, det_size=(640, 640)):
        self.ctx_id = ctx_id
        self.det_size = det_size
        self.model = SCRFD(model_file="models/scr_face_detector.onnx")
        self.model.prepare()

    def detect(
            self,
            np_image: np.ndarray,
            confidence_threshold=0.6,
    ):
        bboxes = []
        predictions = self.model.get(
            np_image, threshold=confidence_threshold, input_size=self.det_size)
        if len(predictions) != 0:
            for _, face in enumerate(predictions):
                bbox = face["bbox"]
                bbox = list(map(int, bbox))
                bboxes.append(bbox)
        return bboxes
