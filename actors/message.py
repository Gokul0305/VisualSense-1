from actors import *
from queue import Queue
class StartAcquisition:
    """
    StartAcquisition is message class to start acquisition
    """
    def __init__(self, src):
        """
        :param src: camera_id
        """
        self.src = src

class GetQueue:
    pass

class Frame:
    """
    Frame is message class which stores ImageQueue
    """
    def __init__(self,frame_queue):
        """
        :param frame_queue: it is a frame
        """
        self.frame_queue = frame_queue

class FrameProcess:
    def __init__(self, frame_queue, flag):
        self.frame_queue = frame_queue
        self.flag = flag

class ProcessFrame:
    def __init__(self, frame_queue):
        self.frame_queue = frame_queue


class CamParams:
    def __init__(self,fps=None, height=None, width=None):
        self.fps = fps

class StopAcquisition:
    pass

class FpsGetter:
    def __init__(self):
        self.frame_count = 0
        self.start_time = time.time()
        self.fps = 0
        self.elapsed_time = None

    def get_fps(self):
        return self.fps

    def run_fps(self):
        self.frame_count += 1
        self.elapsed_time = time.time() - self.start_time
        if self.elapsed_time > 1.0:
            fps = self.frame_count / self.elapsed_time
            self.fps = fps
            self.frame_count = 0
            self.start_time = time.time()


