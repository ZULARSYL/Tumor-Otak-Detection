from flask import Flask, request, send_file, render_template, jsonify, Response
import os
import subprocess
import shutil
import cv2
from ultralytics import YOLO

app = Flask(__name__)
model = YOLO('model.pt')
streaming = False

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/process-image', methods=['POST'])

def process_image():
    if 'image' not in request.files:
        return 'No file uploaded.', 400

    file = request.files['image']
    filename = file.filename
    filepath = os.path.join('uploads', filename)
    os.makedirs('uploads', exist_ok=True)
    file.save(filepath)

    # Bersihkan runs/detect/predict dulu
    shutil.rmtree('runs/detect/predict', ignore_errors=True)

    # Run YOLO command
    command = f'yolo task=detect mode=predict model=model.pt source="{filepath}"'
    subprocess.run(command, shell=True)

    # Cek hasil output sesuai nama file upload
    output_dir = 'runs/detect/predict'
    output_file = os.path.join(output_dir, filename)

    if not os.path.exists(output_file):
        # fallback: ambil file terakhir
        output_files = [f for f in os.listdir(output_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
        if not output_files:
            return 'No output file found.', 500
        output_file = os.path.join(output_dir, output_files[-1])

    # Kirim file hasil
    return send_file(output_file, as_attachment=True)

def generate_frames():
    global streaming
    cap = cv2.VideoCapture(0)

    while streaming:
        success, frame = cap.read()
        if not success:
            break

        # Run YOLO detection
        results = model(frame)
        annotated_frame = results[0].plot()

        # Encode frame to JPEG
        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        frame_bytes = buffer.tobytes()

        # Yield frame in multipart stream
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()
if __name__ == "__main__":
    app.run(debug=True)
