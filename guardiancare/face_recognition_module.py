"""Face recognition module for GuardianCare.

This module provides face identification and registration using OpenCV's
LBPH face recognizer with in-memory storage (local mode - no database required).
"""

from typing import Optional, Dict, Any, List
import numpy as np
import cv2

from config import SIMILARITY_THRESHOLD

# In-memory storage for known faces
_face_images: List[np.ndarray] = []  # Grayscale face images for training
_face_labels: List[int] = []  # Integer labels corresponding to images
_face_data: Dict[int, Dict[str, Any]] = {}  # label -> {name, label_str, patient_id}
_next_label = 0

# OpenCV face detector (Haar cascade)
_face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# LBPH Face Recognizer
_recognizer = cv2.face.LBPHFaceRecognizer_create() if hasattr(cv2, 'face') else None

# Minimum face size for detection
MIN_FACE_SIZE = (100, 100)


def _detect_face(frame: np.ndarray) -> Optional[np.ndarray]:
    """Detect and extract face region from frame.

    Args:
        frame: OpenCV frame (numpy array in BGR format).

    Returns:
        Grayscale face image (resized to standard size) or None if no face detected.
    """
    global _face_cascade
    
    if _face_cascade is None:
        print("⚠️ Face cascade not available")
        return None
    
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detect faces
    faces = _face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=MIN_FACE_SIZE
    )
    
    if len(faces) == 0:
        return None
    
    # Get largest face
    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
    
    # Extract face region
    face_roi = gray[y:y+h, x:x+w]
    
    # Resize to standard size
    face_resized = cv2.resize(face_roi, (200, 200))
    
    return face_resized


def _retrain_recognizer() -> bool:
    """Retrain the LBPH recognizer with current face data.

    Returns:
        True if training succeeded, False otherwise.
    """
    global _recognizer, _face_images, _face_labels
    
    if _recognizer is None:
        if hasattr(cv2, 'face'):
            _recognizer = cv2.face.LBPHFaceRecognizer_create()
        else:
            print("⚠️ OpenCV face module not available")
            return False
    
    if len(_face_images) == 0:
        return False
    
    try:
        _recognizer.train(_face_images, np.array(_face_labels))
        return True
    except Exception as e:
        print(f"⚠️ Failed to train recognizer: {e}")
        return False


def identify_face(frame: np.ndarray) -> Optional[Dict[str, Any]]:
    """Identify a face in the given frame using LBPH recognizer.

    Detects face in frame and predicts identity using trained LBPH recognizer.

    Args:
        frame: OpenCV frame (numpy array in BGR format).

    Returns:
        Match dictionary with face_id, person_name, label, and confidence
        if a match is found, otherwise None.
    """
    global _recognizer, _face_data
    
    # Check if we have trained recognizer
    if _recognizer is None or len(_face_data) == 0:
        # Try to detect face anyway for feedback
        face_img = _detect_face(frame)
        if face_img is not None:
            print("❓ Unknown person detected (no registered faces)")
        else:
            print("❓ No face detected in frame")
        return None
    
    # Detect face
    face_img = _detect_face(frame)
    if face_img is None:
        print("❓ No face detected in frame")
        return None
    
    # Predict
    try:
        label, confidence = _recognizer.predict(face_img)
        
        # LBPH confidence: 0 = perfect match, 100 = very different
        # Convert to similarity score (0-1 scale)
        # Lower confidence = higher similarity
        similarity = max(0, 1 - (confidence / 100))
        
        # Debug: show actual values
        print(f"🔍 LBPH: label={label}, confidence={confidence:.1f}, similarity={similarity:.2f}")
        
        # Check if within threshold
        if similarity >= SIMILARITY_THRESHOLD and label in _face_data:
            face_info = _face_data[label]
            name = face_info.get("person_name", "Unknown")
            label_str = face_info.get("label_str", "visitor")
            
            conf_pct = int(similarity * 100)
            face_id = f"face_{label}"
            
            print(f"👤 Known person: {name} ({label_str}) — {conf_pct}% confidence")
            return {
                "face_id": face_id,
                "person_name": name,
                "label": label_str,
                "confidence": conf_pct,
                "similarity": similarity,
            }
        else:
            print("❓ Unknown person detected")
            return None
            
    except Exception as e:
        print(f"⚠️ Face recognition failed: {e}")
        return None


def register_face(
    frame: np.ndarray,
    person_name: str,
    label: str = "visitor",
    patient_id: Optional[str] = None,
) -> bool:
    """Register a new face to the local in-memory storage.

    Detects face in frame and adds to LBPH training data.

    Args:
        frame: OpenCV frame (numpy array in BGR format).
        person_name: Name of the person to register.
        label: Category label (e.g., "patient", "visitor", "caregiver").
        patient_id: Optional patient ID to associate with this face.

    Returns:
        True if registration succeeded, False otherwise.
    """
    global _face_images, _face_labels, _face_data, _next_label

    # Detect face
    face_img = _detect_face(frame)
    if face_img is None:
        print("❌ No face detected for registration")
        return False

    # Assign new label
    new_label = _next_label
    _next_label += 1
    
    # Store face data
    _face_images.append(face_img)
    _face_labels.append(new_label)
    _face_data[new_label] = {
        "person_name": person_name,
        "label_str": label,
        "patient_id": patient_id,
    }
    
    # Retrain recognizer
    if _retrain_recognizer():
        face_id = f"face_{new_label}"
        print(f"✅ Registered: {person_name} (ID: {face_id})")
        print(f"📊 Total registered faces: {len(_face_data)}")
        return True
    else:
        print("❌ Failed to train recognizer")
        return False


def get_registered_faces() -> Dict[int, Dict[str, Any]]:
    """Get all registered faces from local memory.

    Returns:
        Dictionary of all registered faces with their data.
    """
    return _face_data.copy()


def clear_registered_faces() -> None:
    """Clear all registered faces from memory."""
    global _face_images, _face_labels, _face_data, _next_label, _recognizer
    _face_images.clear()
    _face_labels.clear()
    _face_data.clear()
    _next_label = 0
    _recognizer = cv2.face.LBPHFaceRecognizer_create() if hasattr(cv2, 'face') else None
    print("🗑️ All registered faces cleared")


if __name__ == "__main__":
    # Standalone test mode
    from config import CAMERA_INDEX

    print("🧪 Running face recognition in standalone test mode (OpenCV LBPH)")
    print("Press 'i' to identify, 'r' to register, 'l' to list, 'c' to clear, 'q' to quit")

    cap = cv2.VideoCapture(CAMERA_INDEX)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Flip for mirror effect
        frame = cv2.flip(frame, 1)

        # Show frame
        cv2.imshow("Face Recognition Test (OpenCV LBPH)", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break
        elif key == ord("i"):
            print("🔍 Identifying face...")
            identify_face(frame)
        elif key == ord("r"):
            name = input("Enter name to register: ")
            if name.strip():
                label = input("Enter label (default 'visitor'): ").strip() or "visitor"
                register_face(frame, name, label)
        elif key == ord("l"):
            faces = get_registered_faces()
            print(f"📋 Registered faces ({len(faces)}):")
            for label, fdata in faces.items():
                print(f"  - face_{label}: {fdata['person_name']} ({fdata['label_str']})")
        elif key == ord("c"):
            clear_registered_faces()

    cap.release()
    cv2.destroyAllWindows()
