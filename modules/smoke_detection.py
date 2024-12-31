from ultralytics import YOLO
import cv2
import numpy as np
personDetection = YOLO('models/yolo11m.pt')
smokeDetection = YOLO('models/smoke.pt')

def predictPerson(image):
    personResult = personDetection.predict(image,verbose= False)[0].boxes
    cls = personResult.cls.cpu().detach().numpy().astype('int')
    personBoxes = personResult.xyxy.cpu().detach().numpy().astype('int')
    personBoxes = np.array([personBoxes[i] for i in range(len(cls)) if cls[i]==0])
    return personBoxes
def predictSmoke(image,personBoxes):
    final_result = []
    for person_box in personBoxes:
        xmin1,ymin1,xmax1,ymax1 = person_box
        crop = image[ymin1:ymax1,xmin1:xmax1]
        smokeResult = smokeDetection.predict(crop,verbose = False)[0].boxes
        smoke_boxes = smokeResult.xyxy.cpu().detach().numpy().astype('int')
        smoke_scores = smokeResult.conf.cpu().detach().numpy()
        for smoke_box, smoke_score in zip(smoke_boxes, smoke_scores):
            xmin2,ymin2,xmax2,ymax2 = smoke_box
            w = xmax2-xmin2
            h = ymax2-ymin2
            xmin = xmin1+xmin2
            xmax = xmin+w
            ymin = ymin1+ymin2
            ymax = ymin+h
            final_result.append(((xmin,ymin,xmax,ymax), smoke_score))
    return final_result