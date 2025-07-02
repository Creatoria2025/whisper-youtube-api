from flask import Flask, request, jsonify
import openai
import yt_dlp
import os
import tempfile

app = Flask(__name__)
openai.api_key = os.environ["OPENAI_API_KEY"]

@app.route("/transcribe", methods=["POST"])
def transcribe():
    data = request.json
    url = data.get("url")
    if not url:
        return jsonify({"error": "Missing YouTube URL"}), 400

    with tempfile.TemporaryDirectory() as tmpdir:
        print("Current directory contents:", os.listdir(os.path.dirname(__file__)))
        cookie_path = os.path.join(os.path.dirname(__file__), 'cookies.txt')
        print("cookiefile path:", cookie_path)

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(tmpdir, '%(title)s.%(ext)s'),
            'cookiefile': cookie_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        audio_path = [f for f in os.listdir(tmpdir) if f.endswith(".mp3")][0]
        file_path = os.path.join(tmpdir, audio_path)

        with open(file_path, "rb") as f:
            transcript = openai.Audio.transcribe("whisper-1", f)

        return jsonify({
            "transcript": transcript["text"]
        })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
