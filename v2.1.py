import cv2
import mediapipe as mp
import pyautogui
import http.server
import socketserver
import threading
import os


mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

screenshot_path = "screenshot.png"
port = 8000  

def start_http_server():
    """Starts an HTTP server to share the screenshot."""
    os.makedirs("shared", exist_ok=True)
    if os.path.exists(screenshot_path):
        os.rename(screenshot_path, f"shared/{screenshot_path}")

    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"📡 Serving on port {port}. Access the file on your phone at: http://{get_ip_address()}:{port}/shared/{screenshot_path}")
        httpd.serve_forever()

def get_ip_address():
    """Get the IP address of the MacBook."""
    import socket
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)

cap = cv2.VideoCapture(0)
screenshot_taken = False
file_ready = False
server_started = False
reset_ready = False  # Ensures reset only happens AFTER sharing

def is_two_fingers_up(landmarks):
    """Detects if index and middle fingers are extended, while ring and pinky are curled."""
    index_up = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP].y < landmarks[mp_hands.HandLandmark.INDEX_FINGER_PIP].y
    middle_up = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y < landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y
    ring_down = landmarks[mp_hands.HandLandmark.RING_FINGER_TIP].y > landmarks[mp_hands.HandLandmark.RING_FINGER_PIP].y
    pinky_down = landmarks[mp_hands.HandLandmark.PINKY_TIP].y > landmarks[mp_hands.HandLandmark.PINKY_PIP].y
    
    return index_up and middle_up and ring_down and pinky_down

def is_fist(landmarks):
    """Detects a closed fist (all fingers curled)."""
    folded_fingers = sum(landmarks[finger].y > landmarks[mp_hands.HandLandmark.WRIST].y for finger in [
        mp_hands.HandLandmark.INDEX_FINGER_TIP,
        mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
        mp_hands.HandLandmark.RING_FINGER_TIP,
        mp_hands.HandLandmark.PINKY_TIP
    ])
    return folded_fingers == 4  # All fingers must be curled

def is_open_palm(landmarks):
    """Detects an open palm (all fingers extended)."""
    extended_fingers = sum(landmarks[finger].y < landmarks[mp_hands.HandLandmark.WRIST].y for finger in [
        mp_hands.HandLandmark.INDEX_FINGER_TIP,
        mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
        mp_hands.HandLandmark.RING_FINGER_TIP,
        mp_hands.HandLandmark.PINKY_TIP
    ])
    return extended_fingers == 4  # All fingers must be extended

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:

            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            landmarks = hand_landmarks.landmark

            # Gesture logic
            if not screenshot_taken and is_two_fingers_up(landmarks):  # ✌️ Two Fingers - Take Screenshot
                screenshot = pyautogui.screenshot()
                screenshot.save(screenshot_path)
                screenshot_taken = True
                file_ready = True
                reset_ready = False  # Reset is not allowed until sharing happens
                print("📸 Screenshot Taken!")

            elif file_ready and is_fist(landmarks):  # ✊ Closed Fist - Start Sharing
                if not server_started:
                    server_thread = threading.Thread(target=start_http_server, daemon=True)
                    server_thread.start()
                    server_started = True
                    reset_ready = True  # Now we allow resetting
                    print(f"✅ Screenshot Shared! Visit: http://{get_ip_address()}:{port}/shared/{screenshot_path}")

            elif reset_ready and is_open_palm(landmarks):  # 🖐️ Open Palm - Reset
                screenshot_taken = False
                file_ready = False
                server_started = False
                reset_ready = False  # Prevent multiple resets
                print("🔄 Screenshot Reset. You can take a new one.")

            # Display gesture instructions
            if not file_ready:
                gesture = "✌️ Two Fingers: Take Screenshot"
            elif server_started:
                gesture = "🖐️ Open Palm: Reset Screenshot"
            else:
                gesture = "✊ Closed Fist: Share Screenshot"

            cv2.putText(frame, gesture, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

    cv2.imshow("Gesture Recognition", frame)

    # Break loop with 'q' 
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
