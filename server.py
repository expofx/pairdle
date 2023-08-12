from flask import Flask, request
import os
import json
from werkzeug.utils import secure_filename
import secrets
import requests
import numpy as np
import random

app = Flask(__name__)

words = "time way year work government day man world life part house course case system place end group company party information school fact money point example state business night area water thing family head hand order john side home development week power country council use service room market problem court lot a war police interest car law road form face education policy research sort office body person health mother question period name book level child control society minister view door line community south city god father centre effect staff position kind job woman action management act process north age evidence idea west support moment sense report mind church morning death change industry land care century range table back trade history study street committee rate word food language experience result team other sir section programme air authority role reason price town class nature subject department union bank member value need east practice type paper date decision figure right wife president university friend club quality voice lord stage king us situation light tax production march secretary art board may hospital month music cost field award issue bed project chapter girl game amount basis knowledge approach series love top news front future manager account computer security rest labour structure hair bill heart force attention movement success letter agreement capital analysis population environment performance model material theory growth fire chance boy relationship son sea record size property space term director plan behaviour treatment energy st peter income cup scheme design response association choice pressure hall couple technology defence list chairman loss activity contract county wall paul difference army hotel sun product summer set village colour floor season unit park hour investment test garden husband employment style science look deal charge help economy new page risk advice event picture commission fish college oil doctor opportunity film conference operation application press extent addition station window shop access region doubt majority degree television blood statement sound election parliament site mark importance title species increase return concern public competition software glass lady answer earth daughter purpose responsibility leader river eye ability appeal opposition campaign respect task instance sale whole officer method division source piece pattern lack disease equipment surface oxford demand post mouth radio provision attempt sector firm status peace variety teacher show speaker baby arm base miss safety trouble culture direction context character box discussion past weight organisation start brother league condition machine argument sex budget english transport share mum cash principle exchange aid library version rule tea balance afternoon reference protection truth district turn smith review minute duty survey presence influence stone dog benefit collection executive speech function queen marriage stock failure kitchen student effort holiday career attack length horse progress plant visit relation ball memory bar opinion quarter impact scale race image trust justice edge gas railway expression advantage gold wood network text forest sister chair cause foot rise half winter corner insurance step damage credit pain possibility legislation strength speed crime hill debate will supply present confidence mary patient wind solution band museum farm pound henry match assessment message football no animal skin scene article stuff introduction play administration fear dad proportion island contact japan claim kingdom video tv existence telephone move traffic distance relief cabinet unemployment reality target trial rock concept spirit accident organization construction coffee phone distribution train sight difficulty factor exercise weekend battle prison grant aircraft tree bridge strategy contrast communication background shape wine star hope selection detail user path client search master rain offer goal dinner freedom attitude while agency seat manner favour fig pair crisis smile prince danger call capacity output note procedure theatre tour recognition middle absence sentence package track card sign commitment player threat weather element conflict notice victory bottom finance fund violence file profit standard jack route china expenditure second discipline cell pp reaction castle congress individual lead consideration debt option payment exhibition reform emphasis spring audience feature touch estate assembly volume youth contribution curriculum appearance martin tom boat institute membership branch bus waste heat neck object captain driver challenge conversation occasion code crown birth silence literature faith hell entry transfer gentleman bag coal investigation leg belief total major document description murder aim manchester flight conclusion drug tradition pleasure connection owner treaty tony alan desire professor copy ministry acid palace address institution lunch generation partner engine newspaper cross reduction welfare definition key release vote examination judge atmosphere leadership sky breath creation row guide milk cover screen intention criticism jones silver customer journey explanation green measure brain significance phase injury run coast technique valley drink magazine potential drive revolution bishop settlement christ metal motion index adult inflation sport surprise pension factory tape flow iron trip lane pool independence hole un flat content pay noise combination session appointment fashion consumer accommodation temperature mike religion author nation northern sample assistance interpretation aspect display shoulder agent gallery republic cancer proposal sequence simon ship interview vehicle democracy improvement involvement general enterprise van meal breakfast motor channel impression tone sheet pollution bob beauty square vision spot distinction brown crowd fuel desk sum decline revenue fall diet bedroom soil reader shock fruit behalf deputy roof nose steel co artist graham plate song maintenance formation grass spokesman ice talk program link ring expert establishment plastic candidate rail passage joe parish ref emergency liability identity location framework strike countryside map lake household approval border bottle bird constitution autumn cat agriculture concentration guy dress victim mountain editor theme error loan stress recovery electricity recession wealth request comparison lewis white walk focus chief parent sleep mass jane bush foundation bath item lifespan lee publication decade beach sugar height charity writer panel struggle dream outcome efficiency offence resolution reputation specialist taylor pub co-operation port incident representation bread chain initiative clause resistance mistake worker advance empire notion mirror delivery chest licence frank average awareness travel expansion block alternative chancellor meat store self break drama corporation currency extension convention partnership skill furniture round regime inquiry rugby philosophy scope gate minority intelligence restaurant consequence mill golf retirement priority plane gun gap core uncle thatcher fun arrival snow no command abuse limit championship".split(" ")

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
	random.shuffle(cur["words"])
	return {
		"status": "ok",
		"turn": cur["turn"],
		"dist": cur["dist"],
		"word": cur["w" + str(player)],
		"gone": cur["g" + str(player)],
		"history": cur["h" + str(player)],
		"scores": cur["scores"],
		"you": cur["p" + str(player)],
		"opp": cur["p" + str(1-player)],
		"words": cur["words"]
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
		cur["scores"].append(cur["dist"])
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
				"p1": opp,
				"scores": [],
				"words": random.choices(words, k=25)
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
	
@app.route("/quitgame", methods=["GET", "POST"])
def quitgame():
	player = secure_filename(request.args["player"])
	os.remove("players/" + player)
	return {"status": "ok"}
