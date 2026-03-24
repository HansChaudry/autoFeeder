import time
import subprocess
import os
import signal
from dataclasses import dataclass

@dataclass
class Processes:
    stream: subprocess.Popen | None = None
    record: subprocess.Popen | None = None

class cameraHandler:
    stream_cmd = []
    stream_recording_cmd = []
    streamWasOpen = True

    cameraProcesses:Processes

    def __init__(self) -> None:
        self.stream_cmd = [
            "bash", "-c",
            f"""
            rpicam-vid -t 0 --width 1280 --height 720 --framerate 30 \
            --codec h264 --profile baseline --inline --nopreview -o - 2>/dev/null |
            ffmpeg -fflags nobuffer -flags low_delay -f h264 -i - \
            -c copy -rtsp_transport tcp -f rtsp \
            {os.getenv("streamURL")} 2>/dev/null
            """
        ]

        self.stream_recording_cmd = [
            "bash", "-c",
            f"""
            ffmpeg -rtsp_transport tcp -i {os.getenv("streamURL")} \
            -c copy -t 8 /home/clover/autoFeeder/media/lastFeeding.mp4 -y  2>/dev/null&& \
            ~/aistor-binaries/mc cp /home/clover/autoFeeder/media/lastFeeding.mp4 hansololabMinio/tank-videos/lastFeeding.mp4
            """
        ]
        self.cameraProcesses = Processes()
        self.streamWasOpen = True

    # Record Video
    def recordVideo(self):
        if self.cameraProcesses.stream == None:
            self.startStream()
            self.streamWasOpen = False
            time.sleep(5)
        
        self.cameraProcesses.record = subprocess.Popen(
            self.stream_recording_cmd,
            preexec_fn=os.setsid  # creates new process group
        )

        print("Recording started successfully")

    # Stop recording video
    def stopRecordVideo(self):
        if self.cameraProcesses.record:
            try:
                print(f"Stopping stream PID {self.cameraProcesses.record.pid}")

                # Send SIGTERM to entire process group
                os.killpg(os.getpgid(self.cameraProcesses.record.pid), signal.SIGTERM)

                # Give it time to exit cleanly
                self.cameraProcesses.record.wait(timeout=3)

            except subprocess.TimeoutExpired:
                print("Force killing process group")
                os.killpg(os.getpgid(self.cameraProcesses.record.pid), signal.SIGKILL)

            except Exception as e:
                print("Error stopping stream:", e)

        self.cameraProcesses.record = None

    # Start stream
    def startStream(self):
        if self.cameraProcesses.stream:
            print("Stream already running")
            return
        
        self.cameraProcesses.stream = subprocess.Popen(
            self.stream_cmd,
            preexec_fn=os.setsid  # creates new process group
        )

        self.streamWasOpen = True
        print("Stream started successfully")

    # End stream
    def stopStream(self):
        if self.cameraProcesses.stream:
            try:
                print(f"Stopping stream. PID: {self.cameraProcesses.stream.pid}")

                # Send SIGTERM to entire process group
                os.killpg(os.getpgid(self.cameraProcesses.stream.pid), signal.SIGTERM)

                # Give it time to exit cleanly
                self.cameraProcesses.stream.wait(timeout=3)

                print("Stream stopped successfully")

            except subprocess.TimeoutExpired:
                print("Force killing process group")
                os.killpg(os.getpgid(self.cameraProcesses.stream.pid), signal.SIGKILL)

            except Exception as e:
                print("Error stopping stream:", e)

        self.cameraProcesses.stream = None

    # Clean up on app close
    def cleanUp(self):
        self.stopRecordVideo()
        self.stopStream()
