import cv2
import numpy as np

video_path = r"C:\Users\Tharushi Umayangana\Desktop\project1\pplwalk.mp4"
cfg = r"C:\Users\Tharushi Umayangana\Desktop\project1\yolov4-tiny.cfg"
weights = r"C:\Users\Tharushi Umayangana\Desktop\project1\yolov4-tiny.weights"
names = r"C:\Users\Tharushi Umayangana\Desktop\project1\coco.names"

# Load YOLO
net = cv2.dnn.readNet(weights, cfg)
with open(names, "r") as f:
    classes = [line.strip() for line in f.readlines()]

cap = cv2.VideoCapture(video_path)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    height, width, _ = frame.shape
    blob = cv2.dnn.blobFromImage(frame, 1/255, (416,416), swapRB=True, crop=False)
    net.setInput(blob)
    layer_names = net.getUnconnectedOutLayersNames()
    outputs = net.forward(layer_names)

    # Draw bounding boxes for 'person' class only
    for outp in outputs:
        for detection in outp:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if classes[class_id] == 'person' and confidence > 0.5:
                center_x = int(detection[0]*width)
                center_y = int(detection[1]*height)
                w = int(detection[2]*width)
                h = int(detection[3]*height)
                x = int(center_x - w/2)
                y = int(center_y - h/2)
                cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 2)

    cv2.imshow("People Detection", frame)
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
