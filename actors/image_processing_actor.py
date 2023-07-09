from actors import *
from actors.message import FrameProcess,ProcessFrame
from queue import Queue

class ImageProcessingActor(pykka.ThreadingActor):
    def __init__(self,caller_actor):
        super().__init__()
        self.sharpen_value = None
        self.caller_actor = caller_actor
        self.default_sharpness = None
        self.frame_queue = None
        self.thread_processor = None
        self.flag = None
        self.processed_queue = Queue(2)
        self.brightness_alpha = 1.0
        self.brightness_beta = 0.0
        self.is_alive = None
        self.default_param = False

    def on_receive(self, message):
        if isinstance(message, FrameProcess):
            self.frame_queue = message.frame_queue
            self.flag = message.flag
            self.thread_processor = Thread(target=self.process_frame_queue)
            self.thread_processor.start()

    def set_status(self):
        self.is_alive = self.flag.get()
        return self.is_alive

    def process_frame_queue(self):
        self.caller_actor.tell(ProcessFrame(frame_queue=self.processed_queue))
        self.is_alive = self.flag.get()
        while self.is_alive:
            if self.frame_queue.qsize()>0:
                self.frame_processor(self.frame_queue.get())
            if self.flag.qsize()>0:
                if not self.flag.get():
                    break
                    self.thread_processor.join()

    def frame_processor(self, frame):
        if not self.default_param:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blurred_frame = cv2.GaussianBlur(gray_frame, (5, 5), 0)
            sharpness = np.mean((gray_frame - blurred_frame) ** 2)
            self.default_sharpness = sharpness
            self.set_default(sharpness=sharpness)
            self.default_param = True
        frame = self.process_frame(frame)
        self.processed_queue.put(frame)

    def set_sharpen_value(self, sharpen_value):
        self.sharpen_value = sharpen_value

    def set_default(self,sharpness):
        self.set_sharpen_value(sharpen_value=sharpness)

    def process_frame(self, frame):
        if self.sharpen_value != self.default_sharpness:
            processed_frame = self.sharpen(frame, self.sharpen_value)
            return processed_frame
        else:
            return frame

    def sharpen(self, frame, sharpen_value):
        kernel = np.array([[-1,-1,-1], [-1,sharpen_value,-1], [-1,-1,-1]])
        sharpened_frame = cv2.filter2D(frame, -1, kernel)
        return sharpened_frame

    def display(self,frame):
        """
        display is used to display the video window
        :param frame: current frame that is acquired from camera
        :return: None
        """
        cv2.imshow("frame", frame)
        cv2.waitKey(1)

