"""GuardianCare main orchestrator - Windows-compatible threading.

MAIN THREAD: OpenCV loop (VideoCapture, imshow, waitKey, MediaPipe, fall detection)
BACKGROUND THREAD: Face recognition only (reads shared frame every 3s)

This architecture ensures OpenCV runs on the main thread on Windows,
preventing the silent failures that occur when cv2.imshow runs in background threads.
"""

import threading
import time
import math
from datetime import datetime
from typing import Optional, List

import cv2
import mediapipe as mp
import numpy as np

from face_recognition_module import identify_face, register_face
from config import (
    CAMERA_INDEX,
    AUTO_REGISTER_NAME,
    AUTO_REGISTER_LABEL,
    CAPTURE_FRAMES_COUNT,
    FALL_ANGLE_THRESHOLD,
    HIP_DROP_THRESHOLD,
    COOLDOWN_SECONDS,
    SIMILARITY_THRESHOLD,
    FALL_TRIGGERED,
)

# MediaPipe setup (main thread only)
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Shared frame for face recognition thread
_shared_frame: Optional[np.ndarray] = None
_frame_lock = threading.Lock()

# Fall detection cooldown
_last_fall_time: Optional[float] = None


def calculate_torso_angle(landmarks) -> tuple:
    """Calculate torso angle from vertical using atan2 method.
    
    Returns:
        Tuple of (angle_degrees, debug_info_dict)
    """
    # Get landmarks by enum value (more reliable)
    ls = landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
    rs = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
    lh = landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP.value]
    rh = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP.value]
    
    # Calculate midpoints (MediaPipe coords are 0.0-1.0 normalized)
    shoulder_mid_x = (ls.x + rs.x) / 2
    shoulder_mid_y = (ls.y + rs.y) / 2
    hip_mid_x = (lh.x + rh.x) / 2
    hip_mid_y = (lh.y + rh.y) / 2
    
    # Calculate angle using atan2
    # dx = horizontal difference, dy = vertical difference
    dx = abs(hip_mid_x - shoulder_mid_x)
    dy = abs(hip_mid_y - shoulder_mid_y)
    
    # atan2(dx, dy) gives angle from vertical
    # Standing: dx≈0, dy>0 → angle≈0°
    # Leaning: dx≈dy → angle≈45°
    # Lying: dy≈0, dx>0 → angle≈90°
    angle_rad = math.atan2(dx, dy)
    angle_deg = math.degrees(angle_rad)
    
    # Debug info with raw landmark values
    debug_info = {
        'ls': (ls.x, ls.y),
        'rs': (rs.x, rs.y),
        'lh': (lh.x, lh.y),
        'rh': (rh.x, rh.y),
        'shoulder_mid': (shoulder_mid_x, shoulder_mid_y),
        'hip_mid': (hip_mid_x, hip_mid_y),
        'dx': dx,
        'dy': dy,
        'hip_y': hip_mid_y,
    }
    
    return angle_deg, debug_info


def get_hip_position(landmarks) -> float:
    """Get normalized hip y-position (0-1 scale)."""
    left_hip = landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
    right_hip = landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP]
    return (left_hip.y + right_hip.y) / 2


def detect_fall(angle: float, hip_y: float, prev_hip_y: Optional[float]) -> bool:
    """Detect fall using dual-signal logic."""
    global _last_fall_time
    
    # Check cooldown
    if _last_fall_time is not None:
        if time.time() - _last_fall_time < COOLDOWN_SECONDS:
            return False
    
    # Signal 1: Torso angle exceeds threshold
    angle_trigger = angle > FALL_ANGLE_THRESHOLD
    
    # Signal 2: Hip drop speed exceeds threshold
    hip_drop_trigger = False
    if prev_hip_y is not None:
        hip_drop = hip_y - prev_hip_y  # positive = moving down
        hip_drop_trigger = hip_drop > HIP_DROP_THRESHOLD
    
    # Both signals must trigger
    if angle_trigger and hip_drop_trigger:
        _last_fall_time = time.time()
        # Set persistent global flag (imported from config)
        import config
        config.FALL_TRIGGERED = True
        return True
    return False


def face_recognition_thread() -> None:
    """Background thread: identify faces every 3 seconds.
    
    This thread NEVER touches cv2.imshow or cv2.waitKey.
    It only reads the shared frame protected by _frame_lock.
    """
    global _shared_frame
    
    print("👤 Face recognition thread started")
    
    while True:
        time.sleep(3)
        
        # Get shared frame copy
        with _frame_lock:
            if _shared_frame is None:
                continue
            frame = _shared_frame.copy()
        
        # Identify face (no OpenCV window operations here)
        match = identify_face(frame)
        if match:
            print(f"👤 Recognized: {match.get('person_name')} ({match.get('label')})")


def register_frames_thread(frames: List[np.ndarray]) -> None:
    """Background thread: register multiple frames.
    
    Args:
        frames: List of frames to register under AUTO_REGISTER_NAME.
    """
    print(f"\n📝 Registering {len(frames)} frames for '{AUTO_REGISTER_NAME}'...")
    
    success_count = 0
    for i, frame in enumerate(frames):
        success = register_face(frame, AUTO_REGISTER_NAME, AUTO_REGISTER_LABEL)
        if success:
            success_count += 1
            print(f"  ✅ Frame {i+1}/{len(frames)}")
        else:
            print(f"  ❌ Frame {i+1}/{len(frames)} - no face")
    
    print(f"✅ Registered {success_count}/{len(frames)} frames for '{AUTO_REGISTER_NAME}'")


def main() -> None:
    """Main entry point - OpenCV runs entirely on main thread."""
    global _shared_frame, _last_fall_time
    
    print("🚀 GuardianCare monitoring started")
    print("Press Q to quit | Press R to capture 10 frames for registration")
    print(f"Angle threshold: {FALL_ANGLE_THRESHOLD}° | Hip drop: {HIP_DROP_THRESHOLD}")
    print("-" * 50)
    
    # Initialize camera (MAIN THREAD)
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("❌ Failed to open webcam")
        return
    
    # Start face recognition background thread
    face_thread = threading.Thread(target=face_recognition_thread, daemon=True)
    face_thread.start()
    
    # State variables
    prev_hip_y: Optional[float] = None
    frame_counter = 0
    capture_frames: List[np.ndarray] = []
    capturing = False
    
    # Main OpenCV loop (NEVER in a background thread on Windows)
    print("🎥 Starting main video loop...")
    
    while True:
        # Read frame
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to read frame")
            break
        
        # Mirror effect
        frame = cv2.flip(frame, 1)
        
        # Update shared frame for face recognition thread
        with _frame_lock:
            _shared_frame = frame.copy()
        
        # MediaPipe pose processing
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb_frame)
        
        status = "OK"
        angle = 0.0
        hip_y = 0.0
        
        if results.pose_landmarks:
            landmarks = results.pose_landmarks
            
            # Calculate metrics
            angle, debug_info = calculate_torso_angle(landmarks)
            hip_y = debug_info['hip_y']  # Use hip midpoint from angle calculation
            
            # Fall detection
            if detect_fall(angle, hip_y, prev_hip_y):
                print(f"� FALL DETECTED — angle: {angle:.1f}°")
            
            prev_hip_y = hip_y
            
            # Draw skeleton
            mp_drawing.draw_landmarks(
                frame,
                landmarks,
                mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2),
                connection_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=2),
            )
        
        # Debug: print angle and raw landmarks every 30 frames
        frame_counter += 1
        if frame_counter % 30 == 0 and results.pose_landmarks:
            d = debug_info
            print(f"[DEBUG] Frame {frame_counter}:")
            print(f"  Raw landmarks: LS=({d['ls'][0]:.3f},{d['ls'][1]:.3f}) RS=({d['rs'][0]:.3f},{d['rs'][1]:.3f})")
            print(f"                   LH=({d['lh'][0]:.3f},{d['lh'][1]:.3f}) RH=({d['rh'][0]:.3f},{d['rh'][1]:.3f})")
            print(f"  Midpoints: shoulder=({d['shoulder_mid'][0]:.3f},{d['shoulder_mid'][1]:.3f}) hip=({d['hip_mid'][0]:.3f},{d['hip_mid'][1]:.3f})")
            print(f"  dx={d['dx']:.3f}, dy={d['dy']:.3f}, angle={angle:.1f}°, hip_y={hip_y:.3f}")
        
        # Draw status label based on FALL_TRIGGERED flag
        import config
        if config.FALL_TRIGGERED:
            # Bold red alert when fall detected
            cv2.putText(frame, "FALL DETECTED!", (50, 80), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 4)
        else:
            # Normal green status
            cv2.putText(frame, f"OK | Angle: {angle:.1f}°", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Handle frame capture for registration
        if capturing:
            capture_frames.append(frame.copy())
            remaining = CAPTURE_FRAMES_COUNT - len(capture_frames)
            cv2.putText(
                frame,
                f"CAPTURING: {remaining}",
                (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 165, 255),
                3,
            )
            
            if len(capture_frames) >= CAPTURE_FRAMES_COUNT:
                # Save reference image
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"registered_{timestamp}.jpg"
                cv2.imwrite(filename, capture_frames[0])
                print(f"� Saved: {filename}")
                
                # Start registration in background thread
                reg_thread = threading.Thread(
                    target=register_frames_thread,
                    args=(capture_frames,),
                    daemon=True
                )
                reg_thread.start()
                
                capture_frames = []
                capturing = False
        
        # Display (MAIN THREAD ONLY on Windows)
        cv2.imshow("GuardianCare - Fall Detection", frame)
        
        # Handle keyboard (MAIN THREAD)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        elif key == ord("r") and not capturing:
            capturing = True
            capture_frames = []
            print(f"\n📸 Capturing {CAPTURE_FRAMES_COUNT} frames for '{AUTO_REGISTER_NAME}'...")
    
    # Cleanup (MAIN THREAD)
    cap.release()
    cv2.destroyAllWindows()
    print("🛑 GuardianCare stopped")


if __name__ == "__main__":
    main()
