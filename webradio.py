from flask import Flask, request, redirect, url_for, jsonify
import json
import subprocess

config = json.load(open("config.json"))
app = Flask(__name__, static_folder='static', static_url_path='')

def mplayer_play(url):
	if (app.mplayer==None):
		app.mplayer = subprocess.Popen(["mplayer", "-slave", "-quiet", url], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
	else:
		try:
			app.mplayer.stdin.write("loadfile %s \n" % (url))
			app.mplayer.stdin.flush()
		except:
			app.mplayer = None
			mplayer_play(url)


@app.route("/stream/play", methods=["GET", "POST"])
def play():
	if request.method == "POST":
		stream = config["streams"][request.json['id']]
		mplayer_play(stream["url"])
		return jsonify(stream)

@app.route("/stream/list", methods=["GET"])
def list():
	return jsonify(config["streams"])

@app.route("/")
def index():
	return redirect(url_for("static", filename="index.html"))

if __name__ == "__main__":
	app.mplayer = None
	#app.debug = True
	app.run(host="0.0.0.0", port=8001)
