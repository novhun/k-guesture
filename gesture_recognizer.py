import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks.python import vision
from mediapipe import tasks

class GestureRecognizer:
    def __init__(self):
        # Initialize the HandLandmarker using the new Tasks API
        # Using verified import paths for Tasks API
        base_options = tasks.BaseOptions(model_asset_path='hand_landmarker.task')
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=1,
            min_hand_detection_confidence=0.7,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.landmarker = vision.HandLandmarker.create_from_options(options)
        
        # Hand connections for drawing (legacy HAND_CONNECTIONS)
        self.connections = [
            (0, 1), (1, 2), (2, 3), (3, 4), # Thumb
            (0, 5), (5, 6), (6, 7), (7, 8), # Index
            (0, 9), (9, 10), (10, 11), (11, 12), # Middle
            (0, 13), (13, 14), (14, 15), (15, 16), # Ring
            (0, 17), (17, 18), (18, 19), (19, 20), # Pinky
            (5, 9), (9, 13), (13, 17) # Palm
        ]

    def process_frame(self, frame):
        """
        Processes a BGR frame, returns the processed frame (with landmarks drawn)
        and the list of landmarks if a hand is detected.
        """
        # Convert BGR to RGB (MediaPipe Image)
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)

        # Process landmarks
        detection_result = self.landmarker.detect(mp_image)

        landmarks_list = None

        if detection_result.hand_landmarks:
            for hand_landmarks in detection_result.hand_landmarks:
                # Draw landmarks manually since drawing_utils is missing
                h, w, _ = frame.shape
                for i, lm in enumerate(hand_landmarks):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)

                for connection in self.connections:
                    start_idx, end_idx = connection
                    start_lm = hand_landmarks[start_idx]
                    end_lm = hand_landmarks[end_idx]
                    start_pos = (int(start_lm.x * w), int(start_lm.y * h))
                    end_pos = (int(end_lm.x * w), int(end_lm.y * h))
                    cv2.line(frame, start_pos, end_pos, (0, 255, 0), 2)
                
                # Extract landmarks for comparison
                landmarks_list = self.extract_landmarks(hand_landmarks)
                break # Only process the first hand found

        return frame, landmarks_list

    def extract_landmarks(self, hand_landmarks):
        """
        Extracts landmarks into a flat list, normalizes them relative to the wrist (landmark 0),
        and scales them by the maximum distance to be scale-invariant.
        """
        landmarks = []
        for lm in hand_landmarks:
            landmarks.append([lm.x, lm.y, lm.z])
            
        landmarks = np.array(landmarks)
        
        # Normalize relative to wrist (index 0)
        base = landmarks[0]
        landmarks = landmarks - base
        
        # Scale to max distance
        max_dist = np.max(np.linalg.norm(landmarks, axis=1))
        if max_dist > 0:
            landmarks = landmarks / max_dist
            
        return landmarks.flatten().tolist()

    def compare_gestures(self, current_landmarks, stored_gestures, threshold=0.5):
        """
        Compare current normalized landmarks to stored gestures.
        Returns the best matching gesture dict or None.
        """
        if not current_landmarks or not stored_gestures:
            return None

        current = np.array(current_landmarks)
        
        best_match = None
        best_distance = float('inf')

        for gesture in stored_gestures:
            stored = np.array(gesture['landmarks'])
            
            # Ensure same length
            if len(current) != len(stored):
                continue
                
            # Euclidean distance
            distance = np.linalg.norm(current - stored)
            
            if distance < best_distance:
                best_distance = distance
                best_match = gesture

        if best_distance < threshold:
            return best_match
            
        return None
    def draw_landmarks_on_black_canvas(self, hand_landmarks_list, width=300, height=300):
        """
        Draws the landmarks onto a black background for a clean 'finger style' thumbnail.
        hand_landmarks_list: a flattened list of 63 floats (normalized coordinates).
        """
        # Create black canvas
        canvas = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Reshape to (21, 3)
        landmarks = np.array(hand_landmarks_list).reshape(21, 3)
        
        # Since landmarks are normalized relative to wrist and scaled, 
        # we need to map them back to a visible range in the center of the canvas.
        # We'll put the wrist (0,0) in the center.
        center_x, center_y = width // 2, height // 2
        scale = min(width, height) * 0.4
        
        coords = []
        for i in range(21):
            lx, ly = landmarks[i][0], landmarks[i][1]
            # Invert Y for drawing (OpenCV Y increases downwards)
            px = int(center_x + lx * scale)
            py = int(center_y + ly * scale)
            coords.append((px, py))
            cv2.circle(canvas, (px, py), 4, (0, 255, 0), -1)
            
        for connection in self.connections:
            start_idx, end_idx = connection
            cv2.line(canvas, coords[start_idx], coords[end_idx], (255, 255, 255), 2)
            
        return canvas
