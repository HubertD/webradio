#!/usr/bin/python
from flask import Flask, request, redirect, url_for, jsonify
from threading import Lock
import json
import os
import sys
import subprocess
import time
import urllib
import thread
import re

config = json.load(open(os.path.dirname(__file__) + "/config.json"))
app = Flask(__name__, static_folder='static', static_url_path='')

def mplayer_play(url):
	app.mplayer.stdin.write("loadfile \"%s\"\n" % (url))
	app.mplayer.title = "title unknown"

def mplayer_set_volume(volume):
	print "setting volume: %s" % (volume)
	app.mplayer.volume = volume
	app.mplayer.stdin.write("volume %d 1\n" % (volume))

def mplayer_get_volume():
	return app.mplayer.volume

def mplayer_get_title():
	return app.mplayer.title


@app.route("/status")
def status():
	return jsonify({"volume": mplayer_get_volume(), "title": mplayer_get_title()})

@app.route("/volume", methods=["GET", "POST"])
def volume():
	if request.method == "POST":
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

def mplayer_task(app):
	app.mplayer = subprocess.Popen(["mplayer", "-ao","alsa:device=hw=1.1", "-slave", "-idle", "-softvol" , "-volume", "0"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
	app.mplayer.volume = 25
	app.mplayer.title = ""
	while True:
		line = app.mplayer.stdout.readline().strip()
		try:
			line = line.decode("utf8")
		except:
			pass

		if line.startswith("Starting playback"):
			mplayer_set_volume(mplayer_get_volume())

		if line.startswith("ICY Info:"):
			for meta in line[9:].split(";"):
				meta = meta.strip();
				if meta.startswith("StreamTitle='") and meta.endswith("'"):
					title = meta[13:-1]
					for regexp in config["stream_titles"]["blacklist"]:
						if re.search(regexp, title): break
					else:
						for (search,replace) in config["stream_titles"]["replace"]:
							title = re.sub(search, replace, title)
						app.mplayer.title = title
						print "found title: ", app.mplayer.title
		

if __name__ == "__main__":
	app.debug = False
	app.mplayer_thread = thread.start_new_thread(mplayer_task, (app,))
	app.run(host="0.0.0.0", port=8001)
