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

    cameraProcesses:Processes

    def __init__(self) -> None:
        self.stream_cmd = [
            "bash", "-c",
            f"""
            rpicam-vid -t 0 --width 1280 --height 720 --framerate 30 \
            --codec h264 --profile baseline --inline -o - |
            ffmpeg -fflags nobuffer -flags low_delay -f h264 -i - \
            -c copy -rtsp_transport tcp -f rtsp \
            {os.getenv("streamURL")}
            """
        ]

        self.stream_recording_cmd = [
            "bash", "-c",
            f"""
            ffmpeg -rtsp_transport tcp -i {os.getenv("streamURL")} \
            -c copy -t 10 /home/clover/autoFeeder/media/lastFeeding.mp4 -y && \
            ~/aistor-binaries/mc cp /home/clover/autoFeeder/media/lastFeeding.mp4 hansololabMinio/tank-videos/lastFeeding.mp4
            """
        ]
        self.cameraProcesses = Processes()

    # TODO:
    # [x] Record while streaming
    # [x]  Record while not streaming

    # Record Video
    def recordVideo(self):
        streamWasOpen = True

        if self.cameraProcesses.stream == None:
            streamWasOpen = False
            self.startStream()
            time.sleep(6)
        
        self.cameraProcesses.record = subprocess.Popen(
            self.stream_recording_cmd,
            preexec_fn=os.setsid  # creates new process group
        )
        
        self.cameraProcesses.record.wait()

        if not streamWasOpen:
            self.stopStream()

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

    # End stream
    def stopStream(self):
        if self.cameraProcesses.stream:
            try:
                print(f"Stopping stream PID {self.cameraProcesses.stream.pid}")

                # Send SIGTERM to entire process group
                os.killpg(os.getpgid(self.cameraProcesses.stream.pid), signal.SIGTERM)

                # Give it time to exit cleanly
                self.cameraProcesses.stream.wait(timeout=3)

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