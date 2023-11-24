from googletrans import Translator, LANGUAGES
import os
from flask import Flask, render_template, request
from youtube_transcript_api import YouTubeTranscriptApi as yta
from pytube import YouTube
import whisper
import time

app = Flask(__name__)

class LanguageTranslator:
    def __init__(self):
        self.translator = Translator()

    def translate_to_english(self, text):
        # Detect the source language of the text
        detected_language = self.translator.detect(text).lang

        # Translate the text to English
        translated_text = self.translator.translate(text, src=detected_language, dest='en').text

        return translated_text

translator_instance = LanguageTranslator()

def get_language_code(text):
    # Add code to detect the language of the text
    # For simplicity, you can use a language detection library or service
    # For example, you could use the langdetect library: https://pypi.org/project/langdetect/
    # Install it using: pip install langdetect
    from langdetect import detect
    return detect(text)
    
def get_youtube_transcript(video_id):
    try:
        transcript = yta.get_transcript(video_id)
        text = ' '.join([entry['text'] for entry in transcript])
        return text
    except Exception as e:
        print(f"Error getting YouTube transcript: {str(e)}")
        return None

def translate_to_english(text, target_language='en'):
    translator = Translator()

    # Detect the source language of the text
    detected_language = translator.detect(text).lang

    # Translate the text to English
    translated_text = translator.translate(text, src=detected_language, dest=target_language).text

    return translated_text

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
                youtube_transcript = get_youtube_transcript(video_id)
                if youtube_transcript:
                    # Detect the language of the transcript
                    original_language = get_language_code(youtube_transcript)

                    if original_language != 'en':
                        # Translate the transcript to English
                        transcript = translator_instance.translate_to_english(youtube_transcript)
                    else:
                        transcript = youtube_transcript
                else:
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