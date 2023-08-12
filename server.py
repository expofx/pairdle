from flask import Flask, request
import os
import json
from werkzeug.utils import secure_filename
import secrets
import requests
import numpy as np

app = Flask(__name__)

os.makedirs("data", exist_ok=True)
os.makedirs("players", exist_ok=True)
os.makedirs("queue", exist_ok=True)
os.makedirs("usernames", exist_ok=True)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

def get_emb(word):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    data = {
        "input": word,
        "model": "text-embedding-ada-002"
    }
    response = requests.post("https://api.openai.com/v1/embeddings", json=data, headers=headers)
    return np.array(response.json()["data"][0]["embedding"])

def get_distance(word1, word2):
    emb1 = get_emb(word1)
    emb2 = get_emb(word2)
    # cosine similarity
    similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
    return similarity

@app.after_request
def after_request(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

@app.route("/rand")
def rand():
	return secrets.token_urlsafe(16)

@app.route("/api/gamestate", methods=["GET", "POST"])
def gamestate():
	player_raw = secure_filename(request.args["player"])
	player_json = {}
	if os.path.isfile("players/" + player_raw):
		with open("players/" + player_raw) as f:
			player_json = json.load(f)
	else:
		return {"status": "sad"}
	player = player_json["player"]
	gameid = player_json["gameid"]
	cur = {}
	if os.path.isfile("data/" + gameid):
		with open("data/" + gameid) as f:
			cur = json.load(f)
	else:
		return {"status": "sad"}
	if player != 0 and player != 1:
		return {"status": "sad"}
	return {
		"status": "ok",
		"turn": cur["turn"],
		"dist": cur["dist"],
		"word": cur["w" + str(player)],
		"gone": cur["g" + str(player)],
		"history": cur["h" + str(player)],
		"you": cur["p" + str(player)],
		"opp": cur["p" + str(1-player)]
	}

def getdist(w1, w2):
	return get_distance(w1, w2)

@app.route("/api/gameupd", methods=["GET", "POST"])
def gameupd():
	player_raw = secure_filename(request.args["player"])
	player_json = {}
	if os.path.isfile("players/" + player_raw):
		with open("players/" + player_raw) as f:
			player_json = json.load(f)
	else:
		return {"status": "sad"}

	player = player_json["player"]
	gameid = player_json["gameid"]
	word = request.args["word"]

	cur = {}
	if os.path.isfile("data/" + gameid):
		with open("data/" + gameid) as f:
			cur = json.load(f)
	else:
		return {"status": "sad"}
	if player != 0 and player != 1:
		return {"status": "sad"}
	if cur["g" + str(player)]:
		return {"status": "sad"}

	cur["w" + str(player)] = word
	cur["h" + str(player)].append(word)

	cur["g" + str(player)] = True
	if cur["g0"] and cur["g1"]:
		cur["dist"] = getdist(cur["w0"], cur["w1"])
		cur["turn"] += 1
		cur["g0"] = False
		cur["g1"] = False

	with open("data/" + gameid, "w") as f:
		json.dump(cur, f)
	return {"status": "ok"}

@app.route("/initmatch", methods=["GET", "POST"])
def initmatch():
	w = rand()
	with open("usernames/" + w, "w") as f:
		f.write(request.args["username"])
	queues = os.listdir("queue")
	if len(queues) > 0:
		z = queues[0]
		os.remove("queue/" + z)
		gameid = rand()
		with open("players/" + w, "w") as f:
			json.dump({"player": 0, "gameid": gameid}, f)
		with open("players/" + z, "w") as f:
			json.dump({"player": 1, "gameid": gameid}, f)
		opp = ""
		with open("usernames/" + z) as f:
			opp = f.read()
		with open("data/" + gameid, "w") as f:
			json.dump({
				"turn": 0, 
				"dist": 0, 
				"g0": False,
				"g1": False,
				"w0": "",
				"w1": "",
				"h0": [],
				"h1": [],
				"p0": request.args["username"],
				"p1": opp
			}, f)
	else:
		with open("queue/" + w, "w") as f:
			pass
	return w

@app.route("/queuestatus", methods=["GET", "POST"])
def queuestatus():
	player = request.args["player"]
	if player in os.listdir("queue"):
		return {"status": "waiting"}
	else:
		return {"status": "done"}