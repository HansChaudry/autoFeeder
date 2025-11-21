import RPi.GPIO as GPIO
import time


def testServo():
    duty = 90 / 18 + 2
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(40, GPIO.OUT)
    pwm = GPIO.PWM(40, 50)
    pwm.start(0)

    GPIO.output(40, True)
    pwm.ChangeDutyCycle(90 / 18 + 2)
    time.sleep(1)
    pwm.ChangeDutyCycle(0)
    time.sleep(1)
    pwm.ChangeDutyCycle(0 / 18 + 2)
    time.sleep(1)
    pwm.ChangeDutyCycle(0)
    time.sleep(1)
    pwm.ChangeDutyCycle(45 / 18 + 2)
    time.sleep(1)
    pwm.ChangeDutyCycle(0)
    time.sleep(1)
    GPIO.output(40, False)
    pwm.stop()
    GPIO.cleanup()
