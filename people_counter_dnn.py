import cv2
import numpy as np

#------------database connect---
import pyodbc
from datetime import datetime

# Connect to SQL Server
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=Tharushi\\SQLEXPRESS;'  
    'DATABASE=PeopleCounterDB;'
    'Trusted_Connection=yes;'
)
cursor = conn.cursor()

# Example counts
count_in = 5
count_out = 2
timestamp = datetime.now()  # current timestamp

# Insert into SQL Server
cursor.execute(
    "INSERT INTO PeopleCount (Timestamp, CountIn, CountOut) VALUES (?, ?, ?)",
    (timestamp, count_in, count_out)
)
conn.commit()

cursor.close()
conn.close()


# -------------------------------
# Paths
video_path = r"C:\Users\Tharushi Umayangana\Desktop\project1\pplwalk.mp4"
cfg = r"C:\Users\Tharushi Umayangana\Desktop\project1\yolov4-tiny.cfg"
weights = r"C:\Users\Tharushi Umayangana\Desktop\project1\yolov4-tiny.weights"
names = r"C:\Users\Tharushi Umayangana\Desktop\project1\coco.names"

# -------------------------------
# Load YOLO
net = cv2.dnn.readNet(weights, cfg)
with open(names, "r") as f:
    classes = [line.strip() for line in f.readlines()]

# -------------------------------
# Open video
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

# Counting line
line_position = 300
count_in = 0
count_out = 0

# Track people by centroid
people_tracks = {}
person_id = 0
DIST_THRESHOLD = 50

# -------------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (800, 600))
    height, width = frame.shape[:2]

    # YOLO detection
    blob = cv2.dnn.blobFromImage(frame, 1/255, (416,416), swapRB=True, crop=False)
    net.setInput(blob)
    layer_names = net.getUnconnectedOutLayersNames()
    outputs = net.forward(layer_names)

    # Collect centroids of detected people
    current_centroids = []
    for outp in outputs:
        for detection in outp:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if classes[class_id] == "person" and confidence > 0.5:
                cx = int(detection[0]*width)
                cy = int(detection[1]*height)
                w = int(detection[2]*width)
                h = int(detection[3]*height)
                x = int(cx - w/2)
                y = int(cy - h/2)
                current_centroids.append((cx, cy))
                # Draw box
                cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 2)

    # Draw counting line
    cv2.line(frame, (0, line_position), (800, line_position), (0,0,255), 2)

    # Match centroids to tracks
    new_tracks = {}
    for cx, cy in current_centroids:
        matched = False
        for pid, (prev_cx, prev_cy) in people_tracks.items():
            distance = ((cx - prev_cx)**2 + (cy - prev_cy)**2)**0.5
            if distance < DIST_THRESHOLD:
                new_tracks[pid] = (cx, cy)
                # Count logic
                if prev_cy < line_position <= cy:
                    count_in += 1
                elif prev_cy > line_position >= cy:
                    count_out += 1
                matched = True
                break
        if not matched:
            person_id += 1
            new_tracks[person_id] = (cx, cy)

    people_tracks = new_tracks

    # Display counts
    cv2.putText(frame, f"In: {count_in}", (10,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
    cv2.putText(frame, f"Out: {count_out}", (10,100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

    # Show frame
    cv2.imshow("People Counter", frame)
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
