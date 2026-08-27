# Musicom Radio Streamer
# Purpose: HTTP Stream for HQ Generative Music

import os
import time
import subprocess
from flask import Flask, Response

app = Flask(__name__)

# Paths
PROJECT_DIR = "/opt/data/projects/Styles/Folk/029-een-klein-meisje"
ENGINE_SCRIPT = os.path.join(PROJECT_DIR, "src/stream_engine.py")
MP3_PATH = os.path.join(PROJECT_DIR, "Audio/live_render.mp3")

@app.route("/")
def index():
    return "<h1>Musicom Personal Stream</h1><p>Running: Een Klein Meisje (Folk Algorithm)</p><audio controls autoplay src='/stream.mp3'></audio>"

@app.route("/stream.mp3")
def stream_audio():
    def generate():
        while True:
            subprocess.run(["python3", ENGINE_SCRIPT], check=True)
            with open(MP3_PATH, "rb") as f:
                yield f.read()
            time.sleep(60) 

    return Response(generate(), mimetype="audio/mpeg")

if __name__ == "__main__":
    # Internal port for tunnel or local network
    app.run(host="0.0.0.0", port=8001, threaded=True)
