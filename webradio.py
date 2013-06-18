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

def mplayer_play(url):
	app.mplayer.stdin.write("loadfile \"%s\"\n" % (url))
	mplayer_set_volume(mplayer_get_volume())

def mplayer_set_volume(volume):
	print "setting volume: %s" % (volume)
	app.mplayer.volume = volume
	app.mplayer.stdin.write("volume %d 1\n" % (volume))

def mplayer_get_volume():
	return app.mplayer.volume





@app.route("/volume", methods=["GET", "POST"])
def volume():
	if request.method == "POST":
		print request.json
		mplayer_set_volume(request.json['volume'])
	return jsonify({"volume": mplayer_get_volume()})		
	
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
	app.mplayer = subprocess.Popen(["mplayer", "-ao","alsa:device=hw=1.1", "-quiet", "-slave", "-idle", "-softvol" , "-volume", "0"], stdout=None, stdin=subprocess.PIPE)
	app.mplayer.volume = 0;
	app.run(host="0.0.0.0", port=8001)
