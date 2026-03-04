#!/usr/bin/env python3
"""
Camera → n8n bridge
Forwards camera frames to an n8n webhook on demand, controlled via REST API.

REST API (default port 8080):
  GET  /health  — camera status and readiness
  POST /start   — begin streaming frames to n8n
  POST /stop    — stop streaming

Requires: pip3 install picamera2 opencv-python-headless numpy flask requests
"""

import time
import logging
import threading
import cv2
import requests
from datetime import datetime
from picamera2 import Picamera2
from flask import Flask, jsonify

# ── n8n config ────────────────────────────────────────────────
N8N_WEBHOOK_URL = (
    "http://n8n.truenas.zopilocal:5678/webhook/"
    "c9180df6-78b7-42d8-b3e8-c88b1854949c"
)

# ── Camera config ─────────────────────────────────────────────
RESOLUTION         = (1920, 1080)
PREVIEW_RESOLUTION = (640, 360)
CAPTURE_QUALITY    = 95
WARMUP_FRAMES      = 10

# ── Sender config ─────────────────────────────────────────────
SEND_INTERVAL = 0.2    # 5 fps
REST_PORT     = 8080

# ─────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

app = Flask(__name__)

_lock           = threading.Lock()
_camera_ready   = False
_last_lores_ts  = 0.0
_sending_active = False


def capture_jpeg(cam: Picamera2) -> bytes:
    frame = cam.capture_array("main")
    bgr   = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    _, jpeg = cv2.imencode(".jpg", bgr, [cv2.IMWRITE_JPEG_QUALITY, CAPTURE_QUALITY])
    return jpeg.tobytes()


def send_to_n8n(image_bytes: bytes) -> bool:
    ts = datetime.now().strftime("%Y%m%d_%H-%M-%S_%f")[:-3]
    try:
        resp = requests.post(
            N8N_WEBHOOK_URL,
            files={"image": (f"{ts}.jpg", image_bytes, "image/jpeg")},
            timeout=5,
        )
        resp.raise_for_status()
        log.info(f"→ n8n  {len(image_bytes) // 1024} KB  HTTP {resp.status_code}")
        return True
    except Exception as exc:
        log.error(f"n8n send failed: {exc}")
        return False


# ── REST endpoints ────────────────────────────────────────────

@app.route("/health", methods=["GET"])
def health():
    with _lock:
        ready   = _camera_ready
        last_ts = _last_lores_ts
        sending = _sending_active
    age = round(time.time() - last_ts, 2) if last_ts else None
    ok  = ready and age is not None and age < 2.0
    return jsonify({
        "status":                 "ok" if ok else "degraded",
        "camera_ready":           ready,
        "sending":                sending,
        "last_frame_age_seconds": age,
    })


@app.route("/start", methods=["POST"])
def start_sending():
    global _sending_active
    with _lock:
        _sending_active = True
    log.info("Sending STARTED")
    return jsonify({"sending": True})


@app.route("/stop", methods=["POST"])
def stop_sending():
    global _sending_active
    with _lock:
        _sending_active = False
    log.info("Sending STOPPED")
    return jsonify({"sending": False})


# ── Camera loop ───────────────────────────────────────────────

def camera_loop():
    global _camera_ready, _last_lores_ts

    cam = Picamera2()
    cam.configure(cam.create_still_configuration(
        main={"size": RESOLUTION, "format": "BGR888"},
        lores={"size": PREVIEW_RESOLUTION, "format": "YUV420"},
        buffer_count=2,
    ))
    cam.start()
    log.info(f"Camera started — main {RESOLUTION}, lores {PREVIEW_RESOLUTION}")

    log.info(f"Warming up ({WARMUP_FRAMES} frames)…")
    for _ in range(WARMUP_FRAMES):
        cam.capture_array("lores")
        time.sleep(0.1)

    with _lock:
        _camera_ready = True
    log.info("Camera ready — REST API is accepting requests.")

    last_send = 0.0

    try:
        while True:
            # Lightweight lores grab keeps health timestamp fresh (~10 fps)
            cam.capture_array("lores")
            now = time.time()

            with _lock:
                _last_lores_ts = now
                should_send = _sending_active

            if should_send and (now - last_send) >= SEND_INTERVAL:
                jpeg = capture_jpeg(cam)
                send_to_n8n(jpeg)
                last_send = now

            time.sleep(0.1)

    except Exception as exc:
        log.error(f"Camera loop crashed: {exc}")
    finally:
        cam.stop()
        log.info("Camera stopped.")


def main():
    threading.Thread(target=camera_loop, daemon=True, name="camera").start()
    log.info(f"REST API on http://0.0.0.0:{REST_PORT}")
    app.run(host="0.0.0.0", port=REST_PORT, use_reloader=False)


if __name__ == "__main__":
    main()
