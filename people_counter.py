import cv2
import cvlib as cv
from cvlib.object_detection import draw_bbox

# -------------------------------
# Path to your video
video_path = r"C:\Users\Tharushi Umayangana\Desktop\project1\pplwalk.mp4"

# Open video
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

# Line for counting (y-coordinate)
line_position = 300  # adjust this to your video frame
count_in = 0
count_out = 0

# Dictionary to track people by centroid
people_tracks = {}
person_id = 0

# Distance threshold to match centroids
DIST_THRESHOLD = 50

# -------------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (800, 600))  # optional resize

    # Detect people (cvlib auto-downloads YOLOv4-tiny if needed)
    bbox, labels, conf = cv.detect_common_objects(frame, model='yolov4-tiny')

    # Draw bounding boxes
    out = draw_bbox(frame, bbox, labels, conf)

    # Draw the counting line
    cv2.line(out, (0, line_position), (800, line_position), (0, 0, 255), 2)

    # Get current centroids of people
    current_centroids = []
    for i, label in enumerate(labels):
        if label == "person":
            x, y, w, h = bbox[i]
            cx = x + w // 2
            cy = y + h // 2
            current_centroids.append((cx, cy))

    # Match centroids to existing tracks
    new_people_tracks = {}
    for cx, cy in current_centroids:
        matched = False
        for pid, (prev_cx, prev_cy) in people_tracks.items():
            distance = ((cx - prev_cx) ** 2 + (cy - prev_cy) ** 2) ** 0.5
            if distance < DIST_THRESHOLD:
                new_people_tracks[pid] = (cx, cy)

                # Count logic
                if prev_cy < line_position <= cy:
                    count_in += 1
                elif prev_cy > line_position >= cy:
                    count_out += 1
                matched = True
                break

        if not matched:
            # New person detected
            person_id += 1
            new_people_tracks[person_id] = (cx, cy)

    people_tracks = new_people_tracks

    # Display counts
    cv2.putText(out, f"In: {count_in}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(out, f"Out: {count_out}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("People Counter", out)

    # Press 'q' to quit
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
