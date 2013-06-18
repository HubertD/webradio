#!/usr/bin/python
from flask import Flask, request, redirect, url_for, jsonify
from threading import Lock
import json
import os
import sys
import subprocess
import time
import urllib

config = json.load(open(os.path.dirname(__file__) + "/config.json"))
app = Flask(__name__, static_folder='static', static_url_path='')
if not "mplayer_lock" in app.__dict__:
	app.mplayer_lock = Lock()
	app.mplayer = None

def mplayer_play(url):
	with app.mplayer_lock:
		try:
			if (app.mplayer!=None):
				print "stream already running, closing..."
				app.mplayer.stdin.write("quit\n")
				app.mplayer.stdin.flush()
				
			print "starting up mplayer..."
			app.mplayer = subprocess.Popen(["mplayer", "-ao","alsa:device=hw=1.1", "-slave", "-quiet", url], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
			print "ok"
		except:
			print "error:", sys.exc_info()
			app.mplayer = None


@app.route("/stream/play", methods=["GET", "POST"])
def play():
	if request.method == "POST":
		stream = config["streams"][request.json['id']]
		mplayer_play(stream["url"])
		return jsonify(stream)

@app.route("/stream/list", methods=["GET"])
def list():
	streams = config["streams"]
	data = json.load(urllib.urlopen("http://detektor.fm/music.json"))
	streams["detector_musik"]["current"] = "%s - %s" % (data["artist"], data["title"])

	data = json.load(urllib.urlopen("http://detektor.fm/word.json"))
	streams["detector_wort"]["current"] = "%s - %s" % (data["artist"], data["title"])

	return jsonify(config["streams"])

@app.route("/")
def index():
	return redirect(url_for("static", filename="index.html"))

if __name__ == "__main__":
	app.debug = False
	app.run(host="0.0.0.0", port=8001)
