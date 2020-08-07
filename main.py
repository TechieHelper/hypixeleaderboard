from flask import Flask, redirect, url_for, render_template, request
import requests, json, os, time, datetime

app = Flask(__name__)


@app.route("/home/")
def home():
    data = generateData()
    return render_template("index.html", data=data)


@app.route("/bedwars/")
def bedwars():
    data = generateData()
    return render_template("bedwars.html", data=data, bedwarsData=data['stats']['Bedwars'])


@app.route("/duels/")
def duels():
    data = generateData()
    return render_template("duels.html", data=data, duelsData=data['stats']['Duels'])


@app.route("/")
def bedwarsTemp():
    data = generateData()
    return render_template("bedwars.html", data=data, bedwarsData=data['stats']['Bedwars'])


@app.route("/privacy-policy/")
def privacyPolicy():
    return render_template("privacyPolicy.html")


@app.route("/terms-of-service/")
def termsOfService():
    return render_template("termsOfService.html")


@app.route("/skywars/")
def skywars():
    data = generateData()
    return render_template("skywars.html", data=data, skywarsData=data['stats']['SkyWars'])


@app.route("/contact-us/")
def contactUs():
    return render_template("contactUs.html")


@app.route("/home/", methods=['POST'])
def home_post():
    data = generateData(request.form['playerName'])
    return render_template("index.html", data=data)


@app.route("/skywars/", methods=['POST'])
def skywars_post():
    data = generateData(request.form['playerName'])
    return render_template("skywars.html", data=data, skywarsData=data['stats']['SkyWars'])


@app.route("/bedwars/", methods=['POST'])
def bedwars_post():
    data = generateData(request.form['playerName'])
    return render_template("bedwars.html", data=data, bedwarsData=data['stats']['Bedwars'])


@app.route("/", methods=['POST'])
def bedwarsTemp_post():
    data = generateData(request.form['playerName'])
    return render_template("bedwars.html", data=data, bedwarsData=data['stats']['Bedwars'])


@app.template_filter()
def checkIfValid(data, dataPoint):
    try:
        return data[dataPoint]
    except:
        return "-"



@app.template_filter()
def format_datetime(value):
    return value


@app.template_filter()
def capitalizeFirstLetter(value):
    valueList = value.split("_")
    return " ".join([i[0].upper() + i[1:].lower() for i in valueList])


def generateData(name="_"):
    uuid = getUUIDFromName(name)
    if uuid == "Unknown Name":
        with open("dashedData.json") as f:
            api = json.loads(f.read())
    else:
        try:
            api_request = requests.get("https://api.hypixel.net/player?uuid=" + uuid + "&key=bf77aa7d-00d7-47f3-8c27-530b359ccb54")
            api = json.loads(api_request.content)
        except:
            with open("dashedData.json") as f:
                api = json.loads(f.read())

    return api['player']


def getUUIDFromName(name):
    try:
        api_request = requests.get("https://api.mojang.com/users/profiles/minecraft/" + name)
        api = json.loads(api_request.content)
        return api['id']
    except:
        return "Unknown Name"


if __name__ == "__main__":
    app.run()
