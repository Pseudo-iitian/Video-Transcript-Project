import os
from flask import Flask, render_template, request
from youtube_transcript_api import YouTubeTranscriptApi as yta
from pytube import YouTube
import whisper
import time

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def home():
    start_time = time.time()  # Record the start time
    transcript = ' '

    if request.method == "POST":
        # Check if a YouTube video link is provided
        if 'link' in request.form:
            video_link = request.form['link']
            idx = video_link.find("=")

            if idx != -1:
                video_id = video_link[idx + 1:]

                try:
                    # Download the video
                    yt = YouTube(video_link)
                    stream = yt.streams.get_by_itag(139)

                    # Save the video with a unique name
                    video_path = f"downloads/{video_id}.mp4"
                    stream.download('downloads', f"{video_id}.mp4")

                    # Transcribe the video using Whisper
                    model = whisper.load_model("base")
                    result = model.transcribe(video_path)
                    transcript = result['text']

                except Exception as e:
                    print(f"Error: {str(e)}")

        # Check if a video file is uploaded
        elif 'video_file' in request.files:
            video_file = request.files['video_file']

            try:
                # Save the uploaded video with a unique name
                video_path = os.path.join("uploads", video_file.filename)
                video_file.save(video_path)

                # Transcribe the video using Whisper
                model = whisper.load_model("base")
                result = model.transcribe(video_path)
                transcript = result['text']

            except Exception as e:
                print(f"Error: {str(e)}")

        # Check if an audio file is uploaded
        elif 'audio_file' in request.files:
            audio_file = request.files['audio_file']

            try:
                # Save the uploaded audio with a unique name
                audio_path = os.path.join("uploads", audio_file.filename)
                audio_file.save(audio_path)

                # Transcribe the audio using Whisper
                model = whisper.load_model("base")
                result = model.transcribe(audio_path)
                transcript = result['text']

            except Exception as e:
                print(f"Error: {str(e)}")
    end_time = time.time()
    execution_time = end_time - start_time
    # print(f"Execution Time: {execution_time} seconds")
    return render_template('index.html', transcript=transcript,execution_time=execution_time)

if __name__ == "__main__":
    os.makedirs("downloads", exist_ok=True)  # Create a folder to store downloaded videos
    os.makedirs("uploads", exist_ok=True)  # Create a folder to store uploaded files
    app.run(debug=True)