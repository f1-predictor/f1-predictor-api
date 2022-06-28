from flask import Flask, request
from flask_cors import CORS
from os import scandir, listdir
from os.path import isfile, join
import json, re

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return 'Hello World!'

@app.route("/last_results", methods=["GET"])
def get_last_race_details():
    folder = [f.path for f in scandir("races") if f.is_dir()][0]
    files = [f for f in listdir(folder) if isfile(join(folder, f))][-2:]

    with open(f"{folder}/{files[-1]}", encoding="utf-8") as f:
        results = json.load(f)
        if "js-practice-3" in results: return results

    with open(f"{folder}/{files[-2]}", encoding="utf-8") as f:
        return json.load(f)    

@app.route("/results", methods=["GET"])
def get_results():
    year = request.args["year"]
    track = request.args["track"]

    with open(f"races/{year}/{track}.json", encoding="utf-8") as f:
        return json.load(f)

@app.route("/get_rounds", methods=["GET"])
def get_rounds():
    rounds = {}

    folders = [f.path for f in scandir("races") if f.is_dir()]
    for folder in folders:
        files = []

        year = folder.split("\\")[1]
        filenames = [f for f in listdir(folder) if isfile(join(folder, f))]

        for filename in filenames:
            with open(f"races/{year}/{filename}", encoding="utf-8") as f:
                data = json.load(f)
                track_name = re.findall(r"\((.+)\)", data["track-name"])[0]

                if year == "2021":
                    print(filename, track_name)

                files.append(track_name)

        rounds[year] = files
        print(files)

    return rounds

app.run(host="0.0.0.0", port=8080)