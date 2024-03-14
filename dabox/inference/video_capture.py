import threading
import time
from queue import Queue

import cv2


class VideoCapture:
    def __init__(self, name):
        self.name = name
        self.timeout_sec = 3

        self.q = Queue()
        t = threading.Thread(target=self._reader)
        t.daemon = True
        t.start()

    # read frames as soon as they are available, keeping only most recent one
    def _reader(self):
        while True:
            cap = cv2.VideoCapture(self.name)
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                if not self.q.empty():
                    try:
                        self.q.get_nowait()  # discard previous (unprocessed) frame
                    except Queue.Empty:
                        pass
                # Convert BGR to RGB
                image = frame[:, :, ::-1]
                self.q.put(image)
            cap.release()

            print(f"Waiting {self.timeout_sec} seconds before trying again...")
            time.sleep(self.timeout_sec)

    def read(self):
        return self.q.get()
