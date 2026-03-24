import RPi.GPIO as GPIO
import time
from handlers.cameraHandler import cameraHandler

class feederHandler:
    CONTROL_PINS = [31, 29, 23, 21]

    @staticmethod
    def setup():
        for pin in feederHandler.CONTROL_PINS:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, 0)

    @staticmethod
    def feedClover(camera:cameraHandler):
        halfstep_seq = [
            [1,0,0,0],
            [1,1,0,0],
            [0,1,0,0],
            [0,1,1,0],
            [0,0,1,0],
            [0,0,1,1],
            [0,0,0,1],
            [1,0,0,1]
        ]
        
        camera.recordVideo()

        for _ in range(256):
            for halfstep in range(8):
                for pin in range(4):
                    GPIO.output(
                        feederHandler.CONTROL_PINS[pin],
                        bool(halfstep_seq[halfstep][pin])
                    )
                time.sleep(0.001)

        time.sleep(1)

        for _ in range(256):
            for halfstep in range(7, -1, -1):
                for pin in range(4):
                    GPIO.output(
                        feederHandler.CONTROL_PINS[pin],
                        bool(halfstep_seq[halfstep][pin])
                    )
                time.sleep(0.001)
        
        for pin in feederHandler.CONTROL_PINS:
            GPIO.output(pin, 0)



