# TODO: Convert this file into a test file

# file source: https://projects.raspberrypi.org/en/projects/getting-started-with-picamera/6

import time

from picamera2 import Picamera2

picam2 = Picamera2()
video_config = picam2.create_video_configuration()
picam2.configure(video_config)

picam2.start_and_record_video("testvid.mp4", show_preview=False)
time.sleep(10)
picam2.stop_recording()
