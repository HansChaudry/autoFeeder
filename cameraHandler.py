from helpers import servoHelper
import time
from picamera2 import Picamera2, Preview


class cameraHandler:
    def __init__(self) -> None:
        self.piCam2 = Picamera2()

        video_config = self.piCam2.create_video_configuration()
        self.piCam2.configure(video_config)

        servoHelper.testServo()
        pass

    def recordVideo(self, fileName: str, duration: int):
        try:
            self.piCam2.start_and_record_video(fileName, show_preview=False)
            time.sleep(duration + 2)
            self.piCam2.stop_recording()
        except Exception as e:
            print("An exception occured while recording: ", e)

    def takePicture(self, fileName: str):
        try:
            self.piCam2.start_preview(Preview.NULL)
            self.piCam2.start()
            time.sleep(2)
            self.piCam2.capture_file(fileName)
            self.piCam2.close()
        except Exception as e:
            print("An exception occured while capturing picture ", e)
