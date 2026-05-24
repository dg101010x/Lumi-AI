"""GuardianCare configuration constants.

All tuning parameters for fall detection, face recognition,
and webcam settings are centralized here.
"""

# Fall detection tuning
FALL_ANGLE_THRESHOLD = 25    # degrees from vertical (adjusted for overhead camera)
HIP_DROP_THRESHOLD = 0.02    # normalized 0-1 scale, frame-to-frame hip y-position drop
COOLDOWN_SECONDS = 10        # seconds between fall alerts to prevent spam

# Global state
FALL_TRIGGERED = False       # Persistent flag set when fall is detected

# Face recognition tuning
SIMILARITY_THRESHOLD = 0.4   # 0=strict, 1=loose; lowered for LBPH recognizer

# Auto-registration settings (no input() blocking)
AUTO_REGISTER_NAME = "Patient"   # Name used when pressing R key
AUTO_REGISTER_LABEL = "patient"  # Label for registered faces
CAPTURE_FRAMES_COUNT = 10        # Number of frames to capture per registration
CAPTURE_INTERVAL_MS = 100        # Milliseconds between frame captures

# Webcam settings
CAMERA_INDEX = 0             # 0 = default laptop webcam
