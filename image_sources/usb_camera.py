from image_sources.image_source import Camera
import cv2
from queue import Queue
from actors.message import Frame
from threading import Thread


class USBCamera(Camera):
    """
    USBCamera class which acquires images from USB camera
    """
    def __init__(self):
        super().__init__()
        self.usbcam = None              # Camera
        self.frame_count = None         # Frame Count
        self.fps = None                 # Camera FPS
        self.frame_queue = None         # Frames Queue
        self.height = None              # Camera Height
        self.width = None               # Camera Width
        self.source = None              # Camera Source
        self.caller_actor = None        # Caller actor variable
        self.is_acquiring = False       # Camera status
        self.acquisition_thread = None  # Thread variable

    def start_acquisition(self, src, caller_actor=None):
        """
        start_acquisition is used to start the acquisition of your camera
        :param src: source id
        :param caller_actor: Image acquisition actor
        :return: None
        """
        if not self.is_acquiring:
            print("Opening your camera")
            self.usbcam = cv2.VideoCapture(src)
            if self.usbcam is None or not self.usbcam.isOpened():
                print('Warning: unable to open video source: ', src)
            else:
                self.source = self.usbcam.getBackendName()
                self.caller_actor = caller_actor
                self.width = self.usbcam.get(cv2.CAP_PROP_FRAME_WIDTH)
                self.height = self.usbcam.get(cv2.CAP_PROP_FRAME_HEIGHT)
                self.fps = self.usbcam.get(cv2.CAP_PROP_FPS)
                self.frame_queue = Queue(maxsize=2*self.fps)
                if self.caller_actor is not None:
                    self.caller_actor.tell(Frame(frame_queue=self.frame_queue))
                self.is_acquiring = True
                self.acquisition_thread = Thread(target=self._acquire_frames)
                self.acquisition_thread.daemon = True
                self.acquisition_thread.start()

    def stop_acquisition(self):
        """
        stop_acquisition is used to stop the acquisition of your camera
        :return: None
        """
        print("Closing your camera")
        if self.is_acquiring:
            self.is_acquiring = False
            self.usbcam.release()

    def _acquire_frames(self):
        """
        acquire_frames is used to grab frames
        :return: None
        """
        while self.is_acquiring:
            ret, frame = self.usbcam.read()
            if not ret:
                break
            self.frame_queue.put(frame)