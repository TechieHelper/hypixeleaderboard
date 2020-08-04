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


@app.route("/")
def bedwarsTemp():
    data = generateData()
    return render_template("bedwars.html", data=data, bedwarsData=data['stats']['Bedwars'])


@app.route("/skywars/")
def skywars():
    data = generateData()
    return render_template("skywars.html", data=data, skywarsData=data['stats']['SkyWars'])


@app.route("/contact-us/")
def contactUs():
    return render_template("contactUs.html")


@app.route("/skywars/", methods=['POST'])
def skywars_post():
    global inputtedName
    inputtedName = request.form['playerName']
    return redirect('/skywars/', code=302)


@app.route("/bedwars/", methods=['POST'])
def bedwars_post():
    global inputtedName
    inputtedName = request.form['playerName']
    return redirect('/bedwars/', code=302)


@app.route("/", methods=['POST'])
def bedwarsTemp_post():
    global inputtedName
    inputtedName = request.form['playerName']
    return redirect('/', code=302)



@app.template_filter()
def format_datetime(value):
    return value


@app.template_filter()
def capitalizeFirstLetter(value):
    valueList = value.split("_")
    return " ".join([i[0].upper() + i[1:].lower() for i in valueList])


def generateData():
    try:
        api_request = requests.get("https://api.hypixel.net/player?uuid=" + getUUIDFromName() + "&key=bf77aa7d-00d7-47f3-8c27-530b359ccb54")
        api = json.loads(api_request.content)
    except:
        with open("exampleData.json") as f:
            api = json.loads(f.read())

    return api['player']


def getUUIDFromName():
    try:
        name = inputtedName
    except:
        name = "TechieHelper"

    if name == "": name = "TechieHelper"
    try:
        api_request = requests.get("https://api.mojang.com/users/profiles/minecraft/" + name)
        api = json.loads(api_request.content)
        return api['id']
    except:
        return "2e26f35fb6a74939937776b1149b4b4d"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

