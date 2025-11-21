import RPi.GPIO as GPIO
import time

class feederHandler:
    @staticmethod
    def feedClover(): 
      GPIO.setmode(GPIO.BOARD)
      control_pins = [7,11,13,15]

      for pin in control_pins:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, 0)

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

      for i in range(int(512/2)):
        for halfstep in range(8):
          for pin in range(4):
            GPIO.output(control_pins[pin], bool(halfstep_seq[halfstep][pin]))
          time.sleep(0.001)

      time.sleep(3)

      for i in range(int(512/2)):
        for halfstep in range(7, -1, -1):
          for pin in range(4):
            GPIO.output(control_pins[pin], bool(halfstep_seq[halfstep][pin]))
          time.sleep(0.001)

      GPIO.cleanup()