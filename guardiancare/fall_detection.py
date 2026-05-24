"""Fall detection module using MediaPipe Pose.

This module provides real-time fall detection using a dual-signal approach:
1. Torso angle analysis (deviation from vertical)
2. Hip drop speed tracking (rapid vertical descent)

A fall is only detected when BOTH signals trigger simultaneously,
preventing false positives from normal movements like sitting or bending.
"""

import time
from datetime import datetime
from typing import Optional, Tuple, List

import cv2
import mediapipe as mp
import numpy as np

from config import (
    FALL_ANGLE_THRESHOLD,
    HIP_DROP_THRESHOLD,
    COOLDOWN_SECONDS,
    CAMERA_INDEX,
    AUTO_REGISTER_NAME,
    CAPTURE_FRAMES_COUNT,
    CAPTURE_INTERVAL_MS,
)

# MediaPipe setup
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Global state for cooldown tracking
_last_fall_time: Optional[float] = None


def calculate_torso_angle(landmarks: mp_pose.PoseLandmark) -> float:
    """Calculate the angle of the torso relative to vertical.

    Uses the midpoint of shoulders and midpoint of hips to determine
    the torso angle. Standing upright is ~0 degrees, lying flat is ~90 degrees.

    Args:
        landmarks: MediaPipe pose landmarks.

    Returns:
        Torso angle in degrees from vertical (0-90 range expected).
    """
    # Get shoulder midpoint
    left_shoulder = landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
    right_shoulder = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
    shoulder_mid = np.array([
        (left_shoulder.x + right_shoulder.x) / 2,
        (left_shoulder.y + right_shoulder.y) / 2
    ])

    # Get hip midpoint
    left_hip = landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
    right_hip = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP]
    hip_mid = np.array([
        (left_hip.x + right_hip.x) / 2,
        (left_hip.y + right_hip.y) / 2
    ])

    # Calculate vector from hip to shoulder
    torso_vector = shoulder_mid - hip_mid

    # Calculate angle from vertical (0, -1) vector
    # Vertical up is (0, -1) in normalized coordinates (y increases downward)
    vertical = np.array([0, -1])

    # Normalize torso vector
    torso_length = np.linalg.norm(torso_vector)
    if torso_length == 0:
        return 0.0

    torso_normalized = torso_vector / torso_length

    # Calculate angle using dot product
    dot_product = np.dot(torso_normalized, vertical)
    # Clamp to valid range for acos
    dot_product = np.clip(dot_product, -1.0, 1.0)
    angle_rad = np.arccos(dot_product)
    angle_deg = np.degrees(angle_rad)

    return angle_deg


def get_hip_position(landmarks: mp_pose.PoseLandmark) -> float:
    """Get the normalized y-position of the hip midpoint.

    Args:
        landmarks: MediaPipe pose landmarks.

    Returns:
        Normalized y-position (0-1 scale, where 1 is bottom of frame).
    """
    left_hip = landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
    right_hip = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP]
    return (left_hip.y + right_hip.y) / 2


def log_fall_event(angle: float, hip_y: float) -> None:
    """Log a fall event to the console (local mode - no database).

    Args:
        angle: The detected torso angle at time of fall.
        hip_y: The normalized hip y-position at time of fall.
    """
    print(f"📝 Fall logged locally — angle: {angle:.1f}°, hip_y: {hip_y:.3f}")


def detect_fall(
    angle: float,
    hip_y: float,
    prev_hip_y: Optional[float],
    current_time: float,
) -> Tuple[bool, str]:
    """Detect fall using dual-signal logic with cooldown.

    Args:
        angle: Current torso angle in degrees.
        hip_y: Current hip y-position (normalized 0-1).
        prev_hip_y: Previous hip y-position for drop calculation, or None.
        current_time: Current timestamp for cooldown check.

    Returns:
        Tuple of (fall_detected: bool, status_text: str).
    """
    global _last_fall_time

    # Check cooldown
    if _last_fall_time is not None:
        if current_time - _last_fall_time < COOLDOWN_SECONDS:
            return False, "OK"

    # Signal 1: Torso angle exceeds threshold
    angle_trigger = angle > FALL_ANGLE_THRESHOLD

    # Signal 2: Hip drop speed exceeds threshold
    hip_drop_trigger = False
    if prev_hip_y is not None:
        hip_drop = hip_y - prev_hip_y  # positive = moving down
        hip_drop_trigger = hip_drop > HIP_DROP_THRESHOLD

    # Both signals must trigger for fall detection
    if angle_trigger and hip_drop_trigger:
        _last_fall_time = current_time
        return True, "FALL"

    return False, "OK"


def run_fall_detection(
    camera_lock=None,
    shared_cap=None,
    on_key_press=None,
) -> None:
    """Run the fall detection loop using webcam feed.

    Opens the webcam (or uses shared capture), processes frames with MediaPipe
    Pose, detects falls using dual-signal logic, and displays the feed with
    skeleton overlay and status.

    Args:
        camera_lock: Optional threading.Lock for shared camera access.
        shared_cap: Optional shared cv2.VideoCapture object.
        on_key_press: Optional callback function(key, frames) called when a key is pressed.
                      For 'r' key, passes list of captured frames.

    Press 'q' in the camera window to quit, 'r' to capture 10 frames for registration.
    """
    # Use shared capture or create new one
    if shared_cap is not None:
        cap = shared_cap
    else:
        cap = cv2.VideoCapture(CAMERA_INDEX)

    if not cap.isOpened():
        print("❌ Failed to open webcam")
        return

    prev_hip_y: Optional[float] = None
    capture_frames: List[np.ndarray] = []
    capture_start_time: Optional[float] = None
    
    print("🎥 Fall detection started (local mode - no database)")
    print(f"   Press R to auto-capture {CAPTURE_FRAMES_COUNT} frames for '{AUTO_REGISTER_NAME}'")

    while True:
        # Acquire lock if provided
        if camera_lock:
            camera_lock.acquire()

        try:
            ret, frame = cap.read()
        finally:
            if camera_lock:
                camera_lock.release()

        if not ret:
            print("❌ Failed to read frame from webcam")
            break

        # Flip frame for mirror effect
        frame = cv2.flip(frame, 1)

        # Convert to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb_frame)

        status = "OK"
        angle = 0.0
        hip_y = 0.0

        if results.pose_landmarks:
            landmarks = results.pose_landmarks

            # Calculate metrics
            angle = calculate_torso_angle(landmarks)
            hip_y = get_hip_position(landmarks)

            # Detect fall
            current_time = time.time()
            fall_detected, status = detect_fall(angle, hip_y, prev_hip_y, current_time)

            if fall_detected:
                print(f"🚨 FALL DETECTED — angle: {angle:.1f} degrees")
                log_fall_event(angle, hip_y)

            # Update previous hip position
            prev_hip_y = hip_y

            # Draw skeleton
            mp_drawing.draw_landmarks(
                frame,
                landmarks,
                mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2),
                connection_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=2),
            )

        # Draw status label
        color = (0, 0, 255) if status == "FALL" else (0, 255, 0)
        label = f"{status} — Angle: {angle:.1f}°"
        cv2.putText(
            frame,
            label,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2,
        )

        # Handle multi-frame capture mode
        current_time = time.time()
        
        # Check if we're in capture mode
        if capture_start_time is not None:
            # Check if it's time to capture next frame
            elapsed_ms = (current_time - capture_start_time) * 1000
            frames_to_capture = int(elapsed_ms / CAPTURE_INTERVAL_MS)
            
            # Capture frame if interval passed and we haven't captured enough
            if frames_to_capture > len(capture_frames) and len(capture_frames) < CAPTURE_FRAMES_COUNT:
                capture_frames.append(frame.copy())
                print(f"  📷 Captured frame {len(capture_frames)}/{CAPTURE_FRAMES_COUNT}")
            
            # Show countdown overlay
            remaining = CAPTURE_FRAMES_COUNT - len(capture_frames)
            cv2.putText(
                frame,
                f"CAPTURING: {remaining} remaining",
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 165, 255),  # Orange
                3,
            )
            
            # Check if capture complete
            if len(capture_frames) >= CAPTURE_FRAMES_COUNT:
                # Save first frame as timestamped image
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"registered_{timestamp}.jpg"
                cv2.imwrite(filename, capture_frames[0])
                print(f"  💾 Saved reference image: {filename}")
                
                # Trigger callback with all frames
                if on_key_press:
                    on_key_press("r", capture_frames)
                
                # Reset capture state
                capture_frames = []
                capture_start_time = None
                print(f"   Press R to auto-capture {CAPTURE_FRAMES_COUNT} frames for '{AUTO_REGISTER_NAME}'")
        
        # Display
        cv2.imshow("GuardianCare - Fall Detection", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        elif key == ord("r"):
            if capture_start_time is None and on_key_press:
                # Start capture mode
                capture_start_time = current_time
                capture_frames = []
                print(f"\n📸 Starting capture of {CAPTURE_FRAMES_COUNT} frames for '{AUTO_REGISTER_NAME}'...")
            elif capture_start_time is not None:
                print("⚠️ Already capturing frames, please wait...")

    # Cleanup
    if shared_cap is None:
        cap.release()
    cv2.destroyWindow("GuardianCare - Fall Detection")
    print("🛑 Fall detection stopped")


if __name__ == "__main__":
    # Standalone test mode
    print("🧪 Running fall detection in standalone test mode")
    run_fall_detection()
