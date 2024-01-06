from flask import Flask, render_template, request, send_from_directory, redirect, url_for, jsonify
import subprocess
import os
import torch
from TTS.api import TTS
from datetime import datetime
from werkzeug.utils import secure_filename
import re
import wave
import whisper


ALLOWED_EXTENSIONS = {'wav'}
ALLOWED_EXTENSIONS2 = {'wav', 'mp3', 'ogg','m4a'}
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'outputs'
from pydub import AudioSegment

device = "cuda" if torch.cuda.is_available() else "cpu"
whispermodel = whisper.load_model("large")
tts_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
global selected_file
global selected_lang
selected_file = "None"
selected_lang="pl"


def create_folders_if_not_exist():
    folders = ['voices', 'outputs', 'whisperaudios']

    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"Folder '{folder}' created.")


def allowed_file(filename, extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in extensions


@app.route('/upload_file', methods=['POST'])
def upload_file():
    try:
        uploaded_file = request.files['audio']
        if uploaded_file and allowed_file(uploaded_file.filename, ALLOWED_EXTENSIONS2):
            filename = secure_filename(uploaded_file.filename)
            file_path = os.path.join('voices', 'recordings', filename)
            uploaded_file.save(file_path)

            # Convert non-WAV files to WAV
            if filename.lower().endswith(('.mp3', '.ogg','.m4a')):
                audio = AudioSegment.from_file(file_path, format=filename.rsplit('.', 1)[1].lower())
                file_path = os.path.splitext(file_path)[0] + '.wav'
                audio.export(file_path, format='wav')

            return jsonify({'success': True, 'filename': file_path})
        else:
            raise Exception('Invalid file format')
    except Exception as e:
        print(str(e))
        return jsonify({'success': False, 'error': str(e)})


def save_audio(data):
    filename = os.path.join('whisperaudios', 'temp.wav')

    with open(filename, 'wb') as f:
        f.write(data)

    return filename

@app.route('/upload', methods=['POST'])
def upload():
    try:
        selected_lang = request.form.get('selected_language')
        audio_data = request.files['audio'].read()
        filename = save_audio(audio_data)
        print(selected_lang)
        result = whispermodel.transcribe(r"whisperaudios/temp.wav", language=selected_lang)
        print(result["text"])
        return jsonify({'success': True, 'text': result["text"]})
    except Exception as e:
        print(str(e))
        return jsonify({'success': False, 'error': str(e)})
    

def generate_tts_file(model_name, text, selected_lang):
    czas = datetime.now()
    date_time = czas.strftime("%d-%m-%Y_%H-%M-%S")
    result = re.sub(r".*\\", "", model_name)
    global tts_model, device
    tts_model.tts_to_file(text, speaker_wav="voices/"+model_name, language=selected_lang, file_path="outputs/"+date_time+"_"+result)


@app.route('/', methods=['GET', 'POST'])
def index():
    default_voice = request.form.get('selected_file', 'default_voice')
    default_language = request.form.get('selected_language', 'pl')

    if request.method == 'POST':
        text_input = request.form['text_input']
        selected_file = request.form['selected_file']
        selected_lang = request.form['selected_language']
        run_script(selected_file, text_input, selected_lang)
    else:
        text_input = ''
        selected_file = default_voice
        selected_lang = default_language

    voice_files = get_voice_files('voices', '.wav')
    audio_files = get_voice_files('outputs', '.wav')

    return render_template('index.html', voice_files=voice_files, audio_files=audio_files,
                           default_voice=default_voice, default_language=default_language, text_input=text_input)


def get_voice_files(folder, extension):
    folder_path = os.path.join(os.getcwd(), folder)
    files = []
    for root, dirs, filenames in os.walk(folder_path):
        for filename in filenames:
            if filename.endswith(extension):
                relative_path = os.path.relpath(os.path.join(root, filename), folder_path)
                files.append(relative_path)
    #return list(reversed(files))
    listakurwa = sorted(list(files), key=lambda x: x[:10])
    return reversed(listakurwa)


def run_script(selected_file, text_input,selected_lang):
    generate_tts_file(selected_file, text_input,selected_lang)

@app.route('/outputs/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return redirect(url_for('index'))
    else:
        return "File not found."



if __name__ == '__main__':
    try:
        #app.run(host = "172.26.4.97", port="16")

        app.run()
    except KeyboardInterrupt:
        print("Server terminated by user. Exiting...")
        sys.exit(0)
