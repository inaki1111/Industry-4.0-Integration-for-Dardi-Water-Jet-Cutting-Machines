import cv2

def find_camera_index():
    for i in range(10):
        cap = cv2.VideoCapture(i)
        if not cap.isOpened():
            continue
        ret, frame = cap.read()
        if ret:
            cap.release()
            return i
        cap.release()
    return None

camera_index = find_camera_index()

if camera_index is not None:
    print(f"Found camera at index {camera_index}")
else:
    print("No camera found.")
