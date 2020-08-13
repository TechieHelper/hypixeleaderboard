from flask import Flask, redirect, url_for, render_template, request
import requests, json, os, time, datetime
from os import listdir
from os.path import isfile, join
from datetime import datetime

app = Flask(__name__)


def getUUIDFromName(name):
    try:
        api_request = requests.get("https://api.mojang.com/users/profiles/minecraft/" + name)
        api = json.loads(api_request.content)
        return api['id']
    except:
        return "Unknown Name"


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


@app.route("/home/")
def home():
    data = generateData()
    return render_template("home.html", data=data)


@app.route("/")
def home2():
    data = generateData()
    return render_template("home.html", data=data)


@app.route("/suggestions/")
def suggestions():
    data = generateData()
    return render_template("suggestions.html")


@app.route("/leaderboards/<gameType>/")
def leaderboardsAutoGen(gameType):
    data = generateLeaderboardData()
    return render_template("leaderboardAutoGen.html", gameType=gameType, data=data[leaderboardURLFormatting(gameType)])


@app.route("/leaderboards/")
def leaderboards():
    return render_template("leaderboards.html")


@app.route("/robots.txt")
def robotstxt():
    return render_template("robots.txt")


@app.route("/sitemap.xml")
def sitemap():
    files = [f for f in listdir("./templates")]
    filteredFiles = [f for f in files if f[f.find("."):] == ".html" and f != "rootLayout.html" and f != "leaderboardAutoGen.html"]
    for index in range(len(filteredFiles)):
        filteredFiles[index] = [filteredFiles[index]]

        filteredFiles[index].append(datetime.fromtimestamp(os.path.getmtime("./templates/" + filteredFiles[index][0])).strftime("%Y-%m-%d"))

        temp = filteredFiles[index][0]
        temp2 = ""
        for letter in temp:
            if letter.islower() or letter == ".":
                temp2 += letter
            else:
                temp2 += "-" + letter.lower()
        filteredFiles[index][0] = temp2

    return render_template('sitemap.xml', base_url="http://hypixeleaderboards.com", articles=filteredFiles)


@app.route("/bedwars/")
def bedwars():
    data = generateData()
    return render_template("bedwars.html", data=data, bedwarsData=data['stats']['Bedwars'])


@app.route("/player/bedwars/")
def bedwars2():
    data = generateData()
    return render_template("bedwars.html", data=data, bedwarsData=data['stats']['Bedwars'])


@app.route("/duels/")
def duels():
    data = generateData()
    return render_template("duels.html", data=data, duelsData=data['stats']['Duels'])


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


@app.route("/player/skywars/")
def skywars2():
    data = generateData()
    return render_template("skywars.html", data=data, skywarsData=data['stats']['SkyWars'])


@app.route("/contact-us/")
def contactUs():
    return render_template("contactUs.html")


@app.route("/suggestions/", methods=['POST'])
def suggestions_post():
    data = request.form['comment']
    with open("comments.json") as f:
        comments = json.loads(f.read())

    with open("comments.json", "w") as f:
        comments['comments'].append(data)
        comments = "{\"comments\": [" + ", ".join(["\"" + comment + "\"" for comment in comments['comments']]) + "]}"
        f.write(comments)

    return redirect("../bedwars/", code=302)





@app.route("/home/", methods=['POST'])
def home_post():
    data = generateData(request.form['playerName'])
    return render_template("home.html", data=data)


@app.route("/skywars/", methods=['POST'])
def skywars_post():
    data = generateData(request.form['playerName'])
    return render_template("skywars.html", data=data, skywarsData=customReturn(data, ['stats', 'SkyWars']))


@app.route("/player/skywars/", methods=['POST'])
def skywars_post2():
    data = generateData(request.form['playerName'])
    return render_template("skywars.html", data=data, skywarsData=customReturn(data, ['stats', 'SkyWars']))


@app.route("/bedwars/", methods=['POST'])
def bedwars_post():
    data = generateData(request.form['playerName'])
    return render_template("bedwars.html", data=data, bedwarsData=customReturn(data, ['stats', 'Bedwars']))


@app.route("/player/bedwars/", methods=['POST'])
def bedwars_post2():
    data = generateData(request.form['playerName'])
    return render_template("bedwars.html", data=data, bedwarsData=customReturn(data, ['stats', 'Bedwars']))



@app.route("/", methods=['POST'])
def home2_post():
    data = generateData(request.form['playerName'])
    return render_template("home.html", data=data)


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


def generateLeaderboardData():
    try:
        api_request = requests.get("https://api.hypixel.net/leaderboards?key=bf77aa7d-00d7-47f3-8c27-530b359ccb54")
        api = json.loads(api_request.content)
    except:
        with open("dashedLeaderboardData.json") as f:
            api = json.loads(f.read())

    return api['leaderboards']


def leaderboardURLFormatting(value):
    output = ""
    for i in value:
        if i == "-":
            i = "_"
        else:
            i = i.upper()

        output += i

    return output


@app.route("/player/")
def player():
    return render_template("player.html")


@app.template_filter()
def getRankFromUUID(uuid):
    try:
        try:
            with open("knownUsers.json") as f:
                knownUsers = json.loads(f.read())

            return knownUsers[uuid]

        except KeyError:
            api_request = requests.get("https://api.hypixel.net/player?uuid=" + uuid + "&key=bf77aa7d-00d7-47f3-8c27-530b359ccb54")
            api = json.loads(api_request.content)
            with open("knownUsers.json") as f:
                knownUsers = json.loads(f.read())
            with open("knownUsers.json", "w") as r:
                knownUsers[uuid] = api['player']['displayname']
                json.dump(knownUsers, r)
            return api['player']['displayname']

    except KeyError:
        return "Unknown Name"


@app.template_filter()
def tableTry(dict, pos):
    try:
        return dict[pos]
    except:
        return "-"


@app.template_filter()
def customTry(data, dataPoints):
    try:
        newData = data
        for arg in dataPoints:
            newData = newData[arg]

        return newData
    except:
        return "-"


@app.template_filter()
def customEnumerate(value):
    return enumerate(value)


def customReturn(data, dataPoints):
    try:
        newData = data
        for arg in dataPoints:
            newData = newData[arg]
    except (KeyError, TypeError):
        with open("dashedData.json") as f:
            newData = json.loads(f.read())['player']['stats']['Bedwars']
    return newData


if __name__ == "__main__":
    app.run()
