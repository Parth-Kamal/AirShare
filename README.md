# AirShare : Gesture-Controlled File Transfer System

AirShare is an AI-driven, touch-free file-sharing web application that allows users to transfer files between devices using hand gestures, eliminating the need for physical interaction. It leverages OpenCV and MediaPipe for gesture recognition and transfers files wirelessly over Wi-Fi/LAN.

## Why AirShare?
- Physical interaction required for file selection and sharing.
- Dependency on external applications (Google Drive, WhatsApp, etc.).
- Security risks in traditional file-sharing methods.
- Need for a faster, touchless, and intuitive file transfer solution.

## Features
- Gesture-based file transfer.
- Supports multiple file types.
- Fast and secure.
- Cross-platform compatibility.
- No additional hardware required (just a webcam for gesture detection).
- Instant responses.

## How It Works
1. The camera captures hand gestures and detects movement using OpenCV + MediaPipe.
2. Recognizes specific gestures for selecting and sending files.
3. Establishes a wireless connection via Wi-Fi Direct or WebSockets.
4. Encrypts and transmits the file securely to the recipient.
5. No need for a mouse, keyboard, or touchscreen.

## Huawei's Hand Gesture Sharing System
Huawei, in its Mate 70 series, launched a hand gesture picture-sharing feature that allows users to take screenshots and share them with other Huawei models using hand gestures (closed fist and open palm). However, this feature is limited to Huawei devices.

### How AirShare Stands Out:
- **Cross-platform compatibility**: Works on any device with a camera and network connectivity.
- **Enhanced security**: Requires verification code confirmation for file sharing.

## Three-Way Share
1. **Laptop to Laptop**
   - Two methods:
     - One PC acts as a receiver and the other as a sender; both need to share a verification code or IP address for file transferring.
     - Both PCs can act as receivers or senders, similar to Huawei's feature.
2. **Laptop to Phone**
   - Currently, this feature is in a basic stage, allowing screenshots to be sent to a phone when the script runs.
3. **Phone to Laptop**
   - This feature will be available in the future.

##FlowChart 

<img width="689" alt="image" src="https://github.com/user-attachments/assets/f4fb5e1d-af29-4dff-acf1-db258627cf77" />



## Installation Guide
### Prerequisites
- **Python 3.x**
- Required libraries: OpenCV, MediaPipe, PyAutoGUI, Socket, Threading, OS, Time, PIL, Flask (for backend)
- **Wi-Fi Direct module**
- **WebSockets**

## Usage Instructions
1. Launch the web application and grant camera access.
2. Use the following gestures:
   - **Peace symbol** (two index fingers) to take screenshots.
   - **Closed fist** to send the file.
   - **Open palm** to receive the file.
3. The recipient accepts the file, and the transfer is completed.

---
### Future Enhancements
- Improved phone-to-laptop file transfer.
- Optimized laptop-to-phone sharing.
- Additional gesture-based controls for enhanced user experience.

AirShare aims to revolutionize file sharing with an AI-driven, secure, and intuitive system. Stay tuned for updates!

