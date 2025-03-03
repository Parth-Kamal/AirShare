import cv2
import mediapipe as mp
import pyautogui
import socket
import threading
import os
import time
from PIL import Image

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

screenshot_path = "screenshot.png"
PORT = 5001
receiving_mode = False
receive_thread = None
partner_ip = None  # Will store the partner's IP address

def get_ip_address():
    """Get the local IP address of the device."""
    try:
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)
    except Exception as e:
        print(f"Error getting IP address: {e}")
        return "127.0.0.1"

def send_screenshot():
    """Send screenshot to the stored partner IP address."""
    global partner_ip
    
    try:
        if not os.path.exists(screenshot_path):
            print("No screenshot found to send!")
            return
            
        if not partner_ip:
            print("No partner IP address configured. Use 'p' key to configure.")
            return

        print(f"Sending screenshot to {partner_ip}...")
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(5)  # 5 second timeout for connection
                    s.connect((partner_ip, PORT))
                    
                    # Send file size first
                    file_size = os.path.getsize(screenshot_path)
                    s.send(str(file_size).encode())
                    
                    # Wait for acknowledgment
                    s.recv(1024)
                    
                    # Send the file
                    with open(screenshot_path, 'rb') as f:
                        data = f.read(1024)
                        while data:
                            s.send(data)
                            data = f.read(1024)
                    
                    print(f"Screenshot sent successfully to {partner_ip}!")
                    return
                    
            except ConnectionRefusedError:
                if attempt < max_retries - 1:
                    print(f"Connection refused. Make sure the receiver is in receive mode. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print("Error: Receiver is not in receive mode. Ask them to use the open palm gesture (✋) first.")
            except Exception as e:
                print(f"Error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                
    except Exception as e:
        print(f"Error sending screenshot: {e}")

def start_receive_server():
    """Start the receive server in a separate thread."""
    global receiving_mode
    receiving_mode = True
    
    def receive_server():
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', PORT))
                s.settimeout(60)  # 60 second timeout (increased from 30)
                s.listen(1)
                print(f"\n📱 Ready to receive! Your IP address is: {get_ip_address()}")
                print("Waiting for incoming screenshots... (60 second timeout)")
                
                conn, addr = s.accept()
                with conn:
                    print(f"\nReceiving screenshot from {addr[0]}")
                    
                    # Receive file size first
                    file_size = int(conn.recv(1024).decode())
                    conn.send(b"ACK")
                    
                    # Receive the file
                    received_data = b""
                    while len(received_data) < file_size:
                        data = conn.recv(1024)
                        if not data:
                            break
                        received_data += data
                    
                    # Save the received screenshot
                    with open("received_screenshot.png", 'wb') as f:
                        f.write(received_data)
                    
                    print("✅ Screenshot received successfully!")
                    # Automatically open the received screenshot
                    try:
                        img = Image.open("received_screenshot.png")
                        img.show()
                    except Exception as e:
                        print(f"Error opening received image: {e}")
                    
        except socket.timeout:
            print("\n⏰ Receive mode timed out. Use open palm gesture (✋) to start receiving again.")
        except Exception as e:
            print(f"\n❌ Error receiving screenshot: {e}")
        finally:
            global receiving_mode
            receiving_mode = False
    
    return threading.Thread(target=receive_server, daemon=True)

def configure_partner_ip():
    """Configure the partner's IP address."""
    global partner_ip
    partner_ip = input("\n🔄 Enter your partner's IP address: ")
    print(f"Partner IP set to: {partner_ip}")
    return partner_ip    

def detect_gestures():
    """Detects hand gestures for taking, sending, and receiving screenshots."""
    global receive_thread, receiving_mode, partner_ip
    
    # Try different camera indices
    for camera_index in [0, 1, -1]:
        try:
            print(f"Trying to open camera {camera_index}")
            cap = cv2.VideoCapture(camera_index)
            
            if not cap.isOpened():
                print(f"Failed to open camera {camera_index}")
                continue
                
            print(f"Successfully opened camera {camera_index}")
            break
        except Exception as e:
            print(f"Error opening camera {camera_index}: {e}")
            continue
    else:
        print("Error: Could not open any camera")
        return

    # Configure partner IP at startup
    print(f"\n📱 Your IP address is: {get_ip_address()}")
    partner_ip = configure_partner_ip()

    screenshot_taken = False
    
    print("\n👋 Gesture Controls:")
    print("✌  Two Fingers to take a screenshot")
    print("✊  Closed Fist to send screenshot to pre-configured IP")
    print("✋  Open Palm to enter receive mode (60 second timeout)")
    print("Press 'p' to change partner IP address")
    print("Press 'q' to quit\n")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Couldn't read frame from camera")
                break

            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            try:
                result = hands.process(rgb_frame)
            except Exception as e:
                print(f"Error processing frame: {e}")
                continue

            if result.multi_hand_landmarks:
                for hand_landmarks in result.multi_hand_landmarks:
                    try:
                        mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                        
                        landmarks = hand_landmarks.landmark
                        thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP].y
                        index_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP].y
                        middle_tip = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y
                        ring_tip = landmarks[mp_hands.HandLandmark.RING_FINGER_TIP].y
                        pinky_tip = landmarks[mp_hands.HandLandmark.PINKY_TIP].y

                        # Gesture: Two Fingers Up (Take Screenshot)
                        if (index_tip < thumb_tip and middle_tip < thumb_tip and
                            ring_tip > index_tip and pinky_tip > index_tip and not screenshot_taken):
                            try:
                                screenshot = pyautogui.screenshot()
                                screenshot.save(screenshot_path)
                                screenshot_taken = True
                                print("\n📸 Screenshot taken!")
                                time.sleep(1)
                            except Exception as e:
                                print(f"Error taking screenshot: {e}")
                        
                        # Gesture: Closed Fist (Send Screenshot)
                        elif (index_tip > thumb_tip and middle_tip > thumb_tip and
                              ring_tip > thumb_tip and pinky_tip > thumb_tip and screenshot_taken):
                            send_screenshot()
                            screenshot_taken = False
                        
                        # Gesture: Open Palm (Receive Screenshot)
                        elif (index_tip < thumb_tip and middle_tip < thumb_tip and
                              ring_tip < thumb_tip and pinky_tip < thumb_tip and not receiving_mode):
                            receive_thread = start_receive_server()
                            receive_thread.start()
                            
                    except Exception as e:
                        print(f"Error processing hand landmarks: {e}")
                        continue

            # Add status text and IP info to the frame
            status_text = "Ready"
            if screenshot_taken:
                status_text = "Screenshot taken - Ready to send"
            elif receiving_mode:
                status_text = "Receiving mode active"
            
            cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Display connection info
            ip_text = f"Your IP: {get_ip_address()}"
            partner_text = f"Partner: {partner_ip if partner_ip else 'Not set'}"
            cv2.putText(frame, ip_text, (10, frame.shape[0] - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(frame, partner_text, (10, frame.shape[0] - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            cv2.imshow("AirShare - Gesture Recognition", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('p'):
                partner_ip = configure_partner_ip()

    except Exception as e:
        print(f"Unexpected error: {e}")
    
    finally:
        print("\nCleaning up...")
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    detect_gestures()