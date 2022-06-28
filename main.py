from flask import Flask, request
from flask_cors import CORS
import json
from os import scandir, listdir
from os.path import isfile, join

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

app.run(host="0.0.0.0", port=8080)