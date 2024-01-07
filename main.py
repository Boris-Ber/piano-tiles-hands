import cv2
import mediapipe as mp
import numpy as np
from math import hypot

TOUCH_DIST = 30
FINGER_PAIRS = [
    [(0, 0), (0, 2)],
    [(0, 0), (0, 1)],
    [(1, 0), (1, 1)],
    [(1, 0), (1, 2)]
]


def get_distance(p1, p2) -> float:
    """Returns distance between two points"""
    return hypot(p1[0] - p2[0], p1[1] - p2[1])


def calculate(landmarks) -> list:
    """Returns list of distances between fingers"""
    return [get_distance(landmarks[pair[0]], landmarks[pair[1]]) for pair in FINGER_PAIRS]


handsDetector = mp.solutions.hands.Hands(static_image_mode=False,
                                         max_num_hands=2,
                                         min_detection_confidence=0.85)
cap = cv2.VideoCapture(0)
while cap.isOpened():
    # Read a frame and check if the video is over
    ret, frame = cap.read()
    if cv2.waitKey(1) & 0xFF == ord('q') or not ret:
        break

    # Prepare the image and recognize hands
    flipped = np.fliplr(frame)
    flippedRGB = cv2.cvtColor(flipped, cv2.COLOR_BGR2RGB)
    results = handsDetector.process(flippedRGB)

    if results.multi_handedness is not None and len(results.multi_handedness) == 2:
        # If 2 hands are detected, calculate the coordinates of fingertips
        fingers_landmarks = np.zeros((2, 3, 2), dtype=int)
        hand_index = [0, 0]
        for hand_id in range(2):
            hand = 'Right' in str(results.multi_handedness[hand_id])
            hand_index[hand] = hand_id
        for hand_id in range(2):
            for finger in [4, 8, 12]:
                x_tip = int(results.multi_hand_landmarks[hand_id].landmark[finger].x *
                            flippedRGB.shape[1])
                y_tip = int(results.multi_hand_landmarks[hand_id].landmark[finger].y *
                            flippedRGB.shape[0])
                fingers_landmarks[hand_index[hand_id], int(finger // 4) - 1] = [x_tip, y_tip]
                cv2.circle(flippedRGB, (x_tip, y_tip), 10, (0, 0, 255), -1)

        # Calculate distances between fingers and detect touches
        dist = calculate(fingers_landmarks)
        control = [False] * 4
        for i in range(4):
            pair = FINGER_PAIRS[i]
            if dist[i] < TOUCH_DIST:
                color = (0, 255, 0)
                control[i] = True
            else:
                color = (255, 0, 0)
            cv2.line(flippedRGB, fingers_landmarks[pair[0]], fingers_landmarks[pair[1]], color, 3)

    # Show the image
    res_image = cv2.cvtColor(flippedRGB, cv2.COLOR_RGB2BGR)
    cv2.imshow("Hands", res_image)

handsDetector.close()
