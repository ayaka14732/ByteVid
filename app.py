from typing import Optional
from flask import Flask, request, jsonify
from flask_cors import CORS
from concurrent.futures import ThreadPoolExecutor
import youtube_dl
import re
import os
import sqlite3
import traceback
from uuid import uuid4
from glob import glob

from lib.video_preprocessing import speedup_1_6x
from lib.transcription import transcribe
from lib.transcript_postprocessing import transcript_to_article
from lib.translation import translate
from lib.keyphrase_extraction import extract_keyphrase
from lib.summarisation import summarise
from lib.keyframe_determination import determine_keyframes
from lib.slides_detection import extract_slides

VIDEO_FOLDER = 'workdir'
ALLOWED_EXTENSIONS = {'mp4', 'mp3', 'mkv'}

app = Flask(__name__, static_url_path='/static', static_folder='workdir')
CORS(app)
app.config['work_dir'] = VIDEO_FOLDER

if not os.path.exists(app.config["work_dir"]):
    os.mkdir(app.config["work_dir"])

executor = ThreadPoolExecutor(4)

# initialise database
conn = sqlite3.connect('database.db')
conn.executescript("""
            CREATE TABLE IF NOT EXISTS results (
                uuid TEXT PRIMARY KEY,
                transcript TEXT,
                translated TEXT,
                error_message TEXT,
                status INTEGER
            );

            CREATE TABLE IF NOT EXISTS keywords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid TEXT NOT NULL,
                keyword TEXT NOT NULL,
                FOREIGN KEY (uuid) REFERENCES results
            );

            CREATE TABLE IF NOT EXISTS summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid TEXT NOT NULL,
                text TEXT NOT NULL,
                image TEXT,
                FOREIGN KEY (uuid) REFERENCES results
            );
            """)
conn.close()


@app.route("/result/<uuid>", methods=["GET"])
def result(uuid):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    result = {}

    # get transcript, translated, and status
    res = cur.execute("SELECT * from results WHERE uuid = ?",
                      (uuid, )).fetchone()

    if not res:
        return jsonify({"status": -1})

    _, transcript, translated, error_message, status = res

    result["transcript"] = transcript
    result["translated"] = translated
    result["status"] = status
    result["error_message"] = error_message

    # get summaries
    res = cur.execute("SELECT * from summaries WHERE uuid = ?",
                      (uuid, )).fetchall()

    if len(res) != 0:
        result["summaries"] = []
        for row in res:
            result["summaries"].append({})
            result["summaries"][-1]["text"] = row[2]
            result["summaries"][-1]["image"] = row[3]

    # get keywords
    res = cur.execute("SELECT * from keywords WHERE uuid = ?",
                      (uuid, )).fetchall()

    if len(res) != 0:
        result["keywords"] = []
        for row in res:
            result["keywords"].append(row[2])

    return jsonify(result), 200


@app.route("/video", methods=["POST"])
def video():
    if request.method == "POST":
        video_type = request.form.get("type")
        video_file = request.files.get("file")
        url = request.form.get("url")
        video_language = request.form.get("videoLanguage")
        translate_language = request.form.get("translateLanguage")

        print(video_type, video_language, translate_language)

        if not video_type or not video_language or not translate_language:
            return "Incomplete form!", 400

        curr_uuid = str(uuid4())

        if video_type == "upload":
            if not video_file:
                return 'No file part', 400
            elif video_file.filename == '':
                return 'No selected file', 400
            elif not allowed_file(video_file.filename):
                return 'file extension not allowed!', 400

            save_dir = os.path.join(app.config['work_dir'], curr_uuid)
            save_path = os.path.join(
                save_dir, "video." + get_extension(video_file.filename))
            if not os.path.exists(save_dir):
                os.mkdir(save_dir)
            video_file.save(save_path)

            executor.submit(begin, curr_uuid, video_type, None, video_language,
                            translate_language)
        elif video_type == "youtube":
            if (not validate_youtube_url(url)):
                return "YouTube url invalid", 400
            executor.submit(begin, curr_uuid, video_type, url, video_language,
                            translate_language)

        return curr_uuid, 202
    else:
        return "Only POST request accepted!", 405


def allowed_file(filename: str) -> bool:
    return '.' in filename and get_extension(filename) in ALLOWED_EXTENSIONS


def get_extension(filename: str) -> str:
    return filename.rsplit('.', 1)[1].lower()


def validate_youtube_url(url: str) -> bool:
    match = re.match(
        "^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$",
        url)
    if not match or not match[4]: return False
    return True


def download_youtube_video(url: str, uuid: str) -> None:
    ydl_opts = {
        'outtmpl': os.path.join(app.config['work_dir'], uuid, 'video.%(ext)s')
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def begin(uuid: str, video_type: str, url: Optional[str], language_src: str,
          language_dst: str) -> None:
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute("INSERT INTO results (uuid, status) VALUES (?, ?)", (uuid, 0))
    conn.commit()

    try:
        # download video
        if video_type == 'youtube':
            download_youtube_video(url, uuid)

        work_dir = os.path.join(app.config['work_dir'], uuid)
        if not os.path.exists(work_dir):
            print(f"Folder {uuid} not found!")
            raise OSError(f"Folder {uuid} not found!")

        filename_preprocessed = speedup_1_6x(work_dir)

        cur.execute("UPDATE results set status = ? WHERE uuid = ?", (1, uuid))
        conn.commit()
        print("Video loaded")

        # transcribe video
        transcribe(work_dir, filename_preprocessed, language=language_src)
        article = transcript_to_article(work_dir)

        with open(glob(os.path.join(work_dir, '*.srt'))[0],
                  "r",
                  encoding="utf-8") as f:
            transcript = f.read()

        cur.execute(
            "UPDATE results set status = ?, transcript = ? WHERE uuid = ?",
            (2, transcript, uuid))
        conn.commit()
        print("Transcription done")

        # extract key phrases
        article = transcript_to_article(work_dir)
        keyphrases = extract_keyphrase(article)

        for keyphrase in keyphrases:
            cur.execute("INSERT INTO keywords (uuid, keyword) VALUES (?, ?)",
                        (uuid, keyphrase))
        cur.execute("UPDATE results set status = ? WHERE uuid = ?", (3, uuid))
        conn.commit()
        print("Keyphrases extracted")

        # extract summary
        summaries = summarise(article)

        cur.execute("UPDATE results set status = ? WHERE uuid = ?", (4, uuid))
        conn.commit()
        print("Summarised")

        # extract slides image
        keyframe_paths = determine_keyframes(work_dir, summaries)
        extracted_paths = extract_slides(work_dir, keyframe_paths)

        for index, path in enumerate(extracted_paths):
            cur.execute(
                "INSERT INTO summaries (uuid, text, image) VALUES (?, ?, ?)",
                (uuid, summaries[index], path))

        cur.execute("UPDATE results set status = ? WHERE uuid = ?", (5, uuid))
        conn.commit()
        print("Key slides extracted")

        article_translated = translate(article,
                                       src=language_src,
                                       dst=language_dst)

        cur.execute(
            "UPDATE results set status = ?, translated = ? WHERE uuid = ?",
            (200, article_translated, uuid))
        conn.commit()
        print("Translation complete")
    except Exception as e:
        print(traceback.format_exc())
        cur.execute("UPDATE results set status = ?, error_message = ? WHERE uuid = ?", (500, repr(e), uuid))
        conn.commit()

    print("All processing done")
