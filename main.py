# This is a sample Python script.
import fnmatch
import json
import os
from datetime import datetime

import cv2
import numpy as np
from mutagen.mp3 import MP3
from pyAudioAnalysis import audioBasicIO
import wave
from pydub import AudioSegment
import eyed3
import numpy
import ffmpeg

import pyaudio
import speech_recognition as sr
import sounddevice as sd
from cvzone.HandTrackingModule import HandDetector


from flask import Flask, render_template, jsonify, redirect, url_for, request, Response


# if __name__ == '__main__':
#     app = QApplication([])
#     window = QWidget()
#     window.setWindowTitle("Music player")
#     window.setGeometry(500, 500, 1000, 600)
#     with open('colours.json') as f:
#         data = json.load(f)
#     #print(data["home_backround"])
#     window.setStyleSheet("background-color:" + data["home_background"])
#
#     layout = QVBoxLayout()
#     list_widget = QListWidget()
#     layout.addWidget(list_widget)
#     layout.setContentsMargins(0, 0, 0, 0)
#     layout.setSpacing(0)
#     list_widget.setStyleSheet("background-color:" + data["list_colour"])
#     pattern = "*.mp3"
#     i = 0
#     for root, dirs, files in os.walk("C:/Users/eiorg/Desktop/FacultateAn4Sem2/IOC/Proiect/music"):
#         for filename in fnmatch.filter(files,pattern):
#             list_widget.insertItem(i, filename)
#             print(filename)
#             i=i+1
#
#     window.setLayout(layout)
#     window.show()
#     sys.exit(app.exec())
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
from tensorflow.python.keras.models import model_from_json

from function import mp_hands, mediapipe_detection, extract_keypoints, actions

app = Flask(__name__)
song = 0

information = []
i = 0
songs = []
text = "None"
letter = None

for root, dirs, files in os.walk("C:/Users/eiorg/Desktop/FacultateAn4Sem2/IOC/Proiect/static/music"):
    for filename in fnmatch.filter(files, "*.mp3"):
        songs.append(filename)
        full_path = os.path.join(root, filename)

        my_root = "../" + full_path.split("C:/Users/eiorg/Desktop/FacultateAn4Sem2/IOC/Proiect/")[1].replace("\\","/")
        my_path = os.path.join(my_root )
        # print("MY PATH " + my_path)

        modified_time = os.path.getmtime(full_path)
        formatted_time = datetime.fromtimestamp(modified_time).strftime('%Y-%m-%d')
        post_date = datetime.strptime(formatted_time, '%Y-%m-%d').date()
        today = datetime.now().date()
        days_ago = (today-post_date).days
        if filename.__contains__("-"):
            sng = filename.split("-")[1]
            artist = filename.split("-")[0]
        else:
            sng = filename
            artist = "Theme song"
        if sng.__contains__(".mp3"):
            sng = sng.split(".mp3")[0].strip()
        information.append([i, sng, artist, str(days_ago) + " days ago","not_playing", my_path])
        i = i + 1

# @app.route('/')
# def index():
#     return render_template('index.html')

cap = cv2.VideoCapture(0)


def gen_frames():
    # detector = HandDetector(maxHands=1)
    # while True:
    #     success, frame = cap.read()
    #     if not success:
    #         break
    #     else:
    #         imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    #         hands, img = detector.findHands(imgRGB)
    #         ret, buffer = cv2.imencode('.jpg', cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
    #         frame = buffer.tobytes()
    #
    #         # if hands:
    #         #     hand = hands[0]
    #         #     x,y,w,h = hand['bbox']
    #         #     imgCrop = img[y:y+h,x:x+w]
    #         #     ret, buffer = cv2.imencode('.jpg', imgCrop)
    #         #     hand_frame = buffer.tobytes()
    #             # yield (b'--frame\r\n'
    #             #        b'Content-Type: image/jpeg\r\n\r\n' + hand_frame + b'\r\n')
    #
    #         yield (b'--frame\r\n'
    #                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    json_file = open("model.json", "r")
    model_json = json_file.read()
    json_file.close()
    model = model_from_json(model_json)
    model.load_weights("model.h5")
    global text

    colors = []
    for i in range(0, 20):
        colors.append((245, 117, 16))
    print(len(colors))

    def prob_viz(res, actions, input_frame, colors, threshold):
        output_frame = input_frame.copy()
        for num, prob in enumerate(res):
            cv2.rectangle(output_frame, (0, 60 + num * 40), (int(prob * 100), 90 + num * 40), colors[num], -1)
            cv2.putText(output_frame, actions[num], (0, 85 + num * 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2,
                        cv2.LINE_AA)

        return output_frame

    # 1. New detection variables
    sequence = []
    sentence = []
    accuracy = []
    predictions = []
    threshold = 0.8
    global letter

    cap = cv2.VideoCapture(0)
    # cap = cv2.VideoCapture("https://192.168.43.41:8080/video")
    # Set mediapipe model
    with mp_hands.Hands(
            model_complexity=0,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5) as hands:
        while cap.isOpened():

            # Read feed
            ret, frame = cap.read()

            # Make detections
            cropframe = frame[40:400, 0:300]
            # print(frame.shape)
            frame = cv2.rectangle(frame, (0, 40), (300, 400), 255, 2)
            # frame=cv2.putText(frame,"Active Region",(75,25),cv2.FONT_HERSHEY_COMPLEX_SMALL,2,255,2)
            image, results = mediapipe_detection(cropframe, hands)
            # print(results)

            # Draw landmarks
            # draw_styled_landmarks(image, results)
            # 2. Prediction logic
            keypoints = extract_keypoints(results)
            sequence.append(keypoints)
            sequence = sequence[-30:]

            try:
                if len(sequence) == 30:
                    res = model.predict(np.expand_dims(sequence, axis=0))[0]
                    print(actions[np.argmax(res)])
                    text = actions[np.argmax(res)]
                    predictions.append(np.argmax(res))

                    # 3. Viz logic
                    if np.unique(predictions[-10:])[0] == np.argmax(res):
                        if res[np.argmax(res)] > threshold:
                            if len(sentence) > 0:
                                if actions[np.argmax(res)] != sentence[-1]:
                                    sentence.append(actions[np.argmax(res)])
                                    accuracy.append(str(res[np.argmax(res)] * 100))
                            else:
                                sentence.append(actions[np.argmax(res)])
                                accuracy.append(str(res[np.argmax(res)] * 100))

                    if len(sentence) > 1:
                        sentence = sentence[-1:]
                        accuracy = accuracy[-1:]

                    # Viz probabilities
                    # frame = prob_viz(res, actions, frame, colors,threshold)
            except Exception as e:
                # print(e)
                pass
            cv2.putText(frame, "Output: -" + ' '.join(sentence) + ''.join(accuracy), (3, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            letter = sentence
            ret, buffer = cv2.imencode('.jpg', cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            # cv2.rectangle(frame, (0, 0), (300, 40), (245, 117, 16), -1)
            # cv2.putText(frame, "Output: -" + ' '.join(sentence) + ''.join(accuracy), (3, 30),
            #             cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            #
            # # Show to screen
            # cv2.imshow('OpenCV Feed', frame)


            # yield (b'--frame\r\n'
            #         b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

            # Break gracefully
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()






@app.route('/record_camera')
def record_camera():
    global text
    global information
    return render_template('record_camera.html', information=information, text=text)

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/colors')
def get_colors():
    with open('colours.json', 'r') as f:
        colors = json.load(f)
    return jsonify(colors)


def get_playlists():
    with open("music/description.json", 'r') as f:
        playlists = json.load(f)
    return jsonify(playlists)
@app.route('/set_song')
def init_song():
    global song
    song = request.args.get('song')
    print("am setat " + song)
    return "OK"

@app.route("/")
def collections():
    global information
    global song
    with open('description.json', 'r') as f:
        playlists = json.load(f)
    # playlists = jsonify(playlists)
    pattern = "*.mp3"
    songs = []
    for root, dirs, files in os.walk("C:/Users/eiorg/Desktop/FacultateAn4Sem2/IOC/Proiect/music"):
        for filename in fnmatch.filter(files, pattern):
            songs.append(filename)
    patternImg = "*.*"
    images = []
    for root, dirs, files in os.walk("static/images/playlists"):
        for filename in fnmatch.filter(files, patternImg):
            images.append(filename)
    name_of_playlists = []
    for root, dirs, files in os.walk("music"):
        for dir in dirs:
            name_of_playlists.append(dir)
    artists = set()
    for songg in songs:
        if songg.__contains__(' - '):
            artists.add(songg.split(" - ")[0])
    print(songs)
    print(artists)
    print("!!!!!!!!!!!!! " + str(information[10][1]))
    return render_template('collections.html', songs=songs, images=images, playlists=playlists,
                           name_of_playlists=name_of_playlists, artists=sorted(artists), song=song,
                           information=information)


@app.route('/current_song')
def current_song():
    global information
    global song
    print(str(information))
    return [information[int(song)][1], information[int(song)][5]]

@app.route('/current_text')
def current_text():
    global text
    found = []
    found.append(text)
    for info in information:
        if info[1].lower().__contains__(text.lower()) or info[2].lower().__contains__(text.lower()):
            found.append([info[0], info[1], info[2], info[3], info[4], info[5]])
    print("La found am " + str(found))
    return found
@app.route('/curre')
@app.route('/songs')
def songs():
    global information
    global songs
    global song
    songs = []
    for root, dirs, files in os.walk("C:/Users/eiorg/Desktop/FacultateAn4Sem2/IOC/Proiect/static/music"):
        for filename in fnmatch.filter(files, "*.mp3"):
            songs.append(filename)
    print(str(information))
    return render_template('songs.html', songs=songs, information=information, song=song)


@app.route('/page/<parameter>')
def page(parameter):
    # return f'The parameter is : {parameter}'
    pattern = "*.mp3"
    patternImg = "*.jpg"
    global song
    songs = []
    global information
    images = []
    informatio = []
    i = 0
    match parameter:
        case 'hits':
            pathh = "C:/Users/eiorg/Desktop/FacultateAn4Sem2/IOC/Proiect/music/hits"
        case 'new_music':
            pathh = "C:/Users/eiorg/Desktop/FacultateAn4Sem2/IOC/Proiect/music/new_music"
        case "old_but_gold":
            pathh = "C:/Users/eiorg/Desktop/FacultateAn4Sem2/IOC/Proiect/music/old_but_gold"
        case "our_top_picks":
            pathh = "C:/Users/eiorg/Desktop/FacultateAn4Sem2/IOC/Proiect/music/our_top_picks"
        case "party":
            pathh = "C:/Users/eiorg/Desktop/FacultateAn4Sem2/IOC/Proiect/music/party"
        case "power_music":
            pathh = "C:/Users/eiorg/Desktop/FacultateAn4Sem2/IOC/Proiect/music/power_music"
        case "relaxing_music":
            pathh = "C:/Users/eiorg/Desktop/FacultateAn4Sem2/IOC/Proiect/music/relaxing_music"
        case "theme_songs":
            pathh = "C:/Users/eiorg/Desktop/FacultateAn4Sem2/IOC/Proiect/music/theme_songs"
        case _:
            pathh = "artist"
    path_dict = {
        'hits': "C:/Users/eiorg/Desktop/FacultateAn4Sem2/IOC/Proiect/music/hits",
        'new_music': "C:/Users/eiorg/Desktop/FacultateAn4Sem2/IOC/Proiect/music/new_music",
        'old_but_gold': "C:/Users/eiorg/Desktop/FacultateAn4Sem2/IOC/Proiect/music/old_but_gold",
        'our_top_picks': "C:/Users/eiorg/Desktop/FacultateAn4Sem2/IOC/Proiect/music/our_top_picks",
        'party': "C:/Users/eiorg/Desktop/FacultateAn4Sem2/IOC/Proiect/music/party",
        'power_music': "C:/Users/eiorg/Desktop/FacultateAn4Sem2/IOC/Proiect/music/power_music",
        'relaxing_music': "C:/Users/eiorg/Desktop/FacultateAn4Sem2/IOC/Proiect/music/relaxing_music",
        'theme_songs': "C:/Users/eiorg/Desktop/FacultateAn4Sem2/IOC/Proiect/music/theme_songs"
    }

    # pathh = path_dict.get(parameter, "artist")
    if pathh == "artist":
        print("am artist " + parameter)
        for info in information:
            print("practic am " + str(info[2]) +" cu " + parameter)
            if info[2].strip() == parameter.strip():
                informatio.append([i,info[1],info[2],info[3],info[4],info[5]])
                i = i + 1
    else:
        for root, dirs, files in os.walk(pathh):
            for filename in fnmatch.filter(files, pattern):
                songs.append(filename)

                full_path = os.path.join(root, filename)

                my_root = "../" + full_path.split("C:/Users/eiorg/Desktop/FacultateAn4Sem2/IOC/Proiect")[1].replace("\\",
                                                                                                                 "/")
                my_path = os.path.join(my_root)
                print("MY PATH " + my_path)

                modified_time = os.path.getmtime(full_path)
                formatted_time = datetime.fromtimestamp(modified_time).strftime('%Y-%m-%d')
                post_date = datetime.strptime(formatted_time, '%Y-%m-%d').date()
                today = datetime.now().date()
                days_ago = (today - post_date).days
                if filename.__contains__("-"):
                    sng = filename.split("-")[1]
                    artist = filename.split("-")[0]
                else:
                    sng = filename
                    artist = "Theme song"
                if sng.__contains__(".mp3"):
                    sng = sng.split(".mp3")[0].strip()
                informatio.append([i, sng, artist, str(days_ago) + " days ago", "not_playing", my_path])
                i = i + 1
    # return render_template('music.html', songs=songs, images=images, type=parameter)
    print("trimit " + str(information))
    return render_template('music.html', songs=songs, information=information, song=song, informatio = informatio)


@app.route('/button_click/<parameter_value>')
def button_click(parameter_value):
    return redirect(url_for('page', parameter=parameter_value))


@app.route('/record', methods=['GET', 'POST'])
def record():
    # CHUNK = 1024  # number of frames per buffer
    # FORMAT = pyaudio.paInt16  # audio format
    # CHANNELS = 1  # mono audio
    # RATE = 44100  # sampling rate
    # RECORD_SECONDS = 5  # length of recording
    # p = pyaudio.PyAudio()
    # stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    # frames = []
    # for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    #     data = stream.read(CHUNK)
    #     frames.append(data)
    # audio = sr.AudioData(b''.join(frames), sample_rate=RATE, sample_width=2)
    # r = sr.Recognizer()
    # try:
    #     text = r.recognize_google(audio)
    #     print("You said: {}".format(text))
    # except sr.UnknownValueError:
    #     print("Could not understand audio")
    # except sr.RequestError as e:
    #     print("Could not request results from Google Speech Recognition service; {0}".format(e))
    # sound_dir = 'music'
    # for filename in os.listdir(sound_dir):
    #     if filename.endswith('.mp3'):
    #         sound_name = os.path.splitext(filename)[0].lower()
    #         if sound_name in text.lower():
    #             os.system("afplay sounds/{}".format(filename))
    #             break
    global text
    global information
    return render_template('record.html', information=information, text=text)

@app.route('/recor', methods=['POST'])
def recor():
    global text
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    RECORD_SECONDS = 5
    WAVE_OUTPUT_FILENAME = "output.wav"

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    frames = []
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    stream.stop_stream()
    stream.close()
    p.terminate()
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    file_path = "output.wav"
    r = sr.Recognizer()

    # create an audio file object from the recorded file
    with sr.AudioFile(file_path) as source:
        print("!!!!!!!!!!!")
        if not source:
            return "No sound detected"
        audio_data = r.record(source)
        if len(audio_data.frame_data) == 0:
            return "No sound detected"

    # use the recognizer to perform speech recognition
    try:
        text = r.recognize_google(audio_data)
        print("Am recunorscut " + text)
        return text
    # except sr.UnknownValueError:
    #     return "Could not understand audio"
    # except sr.RequestError as e:
    #     return f"Could not request results from Google Speech Recognition service; {e}"
    except:
        return "problem"
    # print("am recunoscut " + text)
    # return 'done'
@app.route('/recognize', methods=['POST'])
def recognise():
    file_path = "output.wav"
    r = sr.Recognizer()

    # create an audio file object from the recorded file
    with sr.AudioFile(file_path) as source:
        audio_data = r.record(source)

    # use the recognizer to perform speech recognition
    try:
        text = r.recognize_google(audio_data)
        return text
    except sr.UnknownValueError:
        return "Could not understand audio"
    except sr.RequestError as e:
        return f"Could not request results from Google Speech Recognition service; {e}"


if __name__ == "__main__":
    app.run(debug=True)
