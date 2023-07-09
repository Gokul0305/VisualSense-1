from queue import Queue
from actors import *
from actors.image_processing_actor import ImageProcessingActor
from actors.image_acquisition_actor import ImageAcquisitionActor
from actors.message import StopAcquisition,StartAcquisition, Frame, FrameProcess, FpsGetter, ProcessFrame, GetQueue


class ControllerActor(pykka.ThreadingActor):
    def __init__(self):
        super().__init__()

        self.processed_queue = Queue()

        # Create the child actors
        self.fps_cal = FpsGetter()
        self.is_alive = None
        self.thread_display = None
        self.frame_queue = None
        self.flag = Queue(1)
        self.image_acquisition_actor = ImageAcquisitionActor.start(camera_type="usb",caller_actor=self.actor_ref)
        self.processing_actor = ImageProcessingActor.start(caller_actor=self.actor_ref)

    def on_receive(self, message):
        if isinstance(message, StartAcquisition):
            print("Started Acq")
            self.is_alive = self.image_acquisition_actor.ask(StartAcquisition(src=0))
            self.flag.put(self.is_alive)

        elif isinstance(message,StopAcquisition):
            self.is_alive = self.image_acquisition_actor.ask(StopAcquisition())
            self.thread_display.join()
            self.flag.put(self.is_alive)

        elif isinstance(message, Frame):
            self.frame_queue = message.frame_queue
            self.processing_actor.tell(FrameProcess(frame_queue=self.frame_queue,flag=self.flag))

        elif isinstance(message, ProcessFrame):
            self.processed_queue = message.frame_queue

        elif isinstance(message, GetQueue):
            return self.processed_queue

    def process_frame_queue(self):
        while self.is_alive:
            if self.processed_queue.qsize()>0:
                self.fps_cal.run_fps()
                fps = self.fps_cal.get_fps()
                processed_frame = cv2.putText(self.processed_queue.get(), "Fps : "+str(int(fps)), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8 , (255,255,255), 3)
                self.display(frame=processed_frame)
            if not self.is_alive:
                break

    def display(self,frame):
        """
        display is used to display the video window
        :param frame: current frame that is acquired from camera
        :return: None
        """
        cv2.imshow("frame", frame)
        cv2.waitKey(1)


if __name__ == '__main__':
    controller = ControllerActor.start()
    controller.tell(StartAcquisition(src=0))
    time.sleep(50)
    controller.tell(StopAcquisition())
    pykka.ActorRegistry.stop_all()

