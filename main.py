from feederHandler import feederHandler
from cameraHandler import cameraHandler
import time
import os
from dotenv import load_dotenv
import paho.mqtt.client as paho
import threading

camera = cameraHandler()


def message_handling(client, userdata, msg):
    """Callback function for when a message is received."""
    print("Message received on topic:", msg.topic)

    # Setting up recordVideo to execute indepently
    recordVideoThread = threading.Thread(
        daemon=True, target=camera.recordVideo, args=("testVid.mp4", 10)
    )
    recordVideoThread.start()

    # Camera start up time buffer
    time.sleep(2)

    feederHandler.feedClover()


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker!")
    else:
        print("Failed to connect to broker!")


def on_disconnect(client, userdata, rc):
    print("Disconnected from broker!")


def main():
    load_dotenv()
    time.sleep(1)

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

            print("Press CTRL+C to exit...")

            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Exiting...")
            if client is not None:
                client.loop_stop()
                client.disconnect()


if __name__ == "__main__":
    main()
else:
    print("main.py is being imported")
