from handlers.feederHandler import feederHandler
from handlers.cameraHandler import cameraHandler
import time
import os
from dotenv import load_dotenv
import paho.mqtt.client as paho
import threading
import RPi.GPIO as GPIO
import requests


camera = cameraHandler()
led_pins = [5, 7]
GPIO.setmode(GPIO.BOARD)

def initiate_pins():
    for pin in led_pins:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, False)
    
    feederHandler.setup()


def cleanUp_pins():
    GPIO.cleanup()


def message_handling(client, userdata, msg):
    """Callback function for when a message is received."""
    print("Message received on topic:", msg.topic)

    # # Setting up recordVideo to execute indepently
    # recordVideoThread = threading.Thread(
    #     daemon=True, target=camera.recordVideo, args=("testVid.mp4", 10)
    # )
    # recordVideoThread.start()

    # # Camera start up time buffer
    # time.sleep(2)
    if(msg.topic == str(os.getenv("inTopic"))):
        print("feeding")
        feederHandler.feedClover(camera)
    elif(msg.topic == "cloverFeeder/stream"):
        if(msg.payload.decode("utf-8") == "start"):
            camera.startStream()
        elif(msg.payload.decode("utf-8") == "stop"):
            camera.cleanUp()


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker!")
        GPIO.output(led_pins[1], True)
    else:
        print("Failed to connect to broker!")


def on_disconnect(client, userdata, rc):
    print("Disconnected from broker!")
    GPIO.output(led_pins[1], False)


def internet_connection():
    try:
        response = requests.get("https://www.github.com", timeout=5)
        return True
    except requests.ConnectionError:
        print("No network connection. Trying again in 6 seconds...")
        return False


def main():
    load_dotenv()
    time.sleep(1)

    initiate_pins()

    while not internet_connection():
        GPIO.output(led_pins[0], True)
        time.sleep(0.5)
        GPIO.output(led_pins[0], False)
        time.sleep(0.5)

    client = paho.Client()

    if client is not None:
        try:
            # Setup MQTT
            client.on_connect = on_connect
            client.on_message = message_handling
            client.on_disconnect = on_disconnect

            host = os.getenv("HOSTNAME")
            port = os.getenv("PORT")
            if host is not None and port is not None:
                client.connect(str(host), int(port))

            client.loop_start()

            client.subscribe(str(os.getenv("inTopic")))
            client.subscribe(str(os.getenv("streamTopic")))

            print("Press CTRL+C to exit...")

            # camera.startStream()

            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Exiting...")
        except Exception as e:
            print(f"Unexpected error: {e}")
        finally:
            if client is not None:
                client.loop_stop()
                client.disconnect()
            camera.cleanUp()
            cleanUp_pins()


if __name__ == "__main__":
    main()
else:
    print("main.py is being imported")
