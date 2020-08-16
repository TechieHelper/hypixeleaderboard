from flask import Flask, redirect, url_for, render_template, request, make_response
import requests, json, os, time, datetime
from os import listdir
from os.path import isfile, join
from datetime import datetime

app = Flask(__name__)

# General Functions


def getUUIDFromName(name):
    try:
        api_request = requests.get("https://api.mojang.com/users/profiles/minecraft/" + name)
        api = json.loads(api_request.content)
        return api['id']
    except:
        return "Unknown Name"


def generateData(name="_"):
    if len(name.encode('utf-8')) != 32:
        uuid = getUUIDFromName(name)
    else:
        uuid = name
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


def customReturn(data, dataPoints):
    try:
        newData = data
        for arg in dataPoints:
            newData = newData[arg]
    except (KeyError, TypeError):
        with open("dashedData.json") as f:
            newData = json.loads(f.read())['player']['stats']['Bedwars']
    return newData


def prestigeStrip(value):
    value = value[0].upper() + value[1:]
    return value[:value.find("_")]




# App Commands


@app.template_filter()
def checkIfValid(data, dataPoint):
    try:
        return data[dataPoint]
    except KeyError:
        return "-"


@app.template_filter()
def format_datetime(value):
    return value


@app.template_filter()
def capitalizeFirstLetter(value):
    valueList = value.split("_")
    return " ".join([i[0].upper() + i[1:].lower() for i in valueList])


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


@app.template_filter()
def prestigeRank(mode, duelsData):
    listOfRanks = ['godlike_title_prestige', 'grandmaster_title_prestige', 'legend_title_prestige',
                   'master_title_prestige', 'diamond_title_prestige', 'gold_title_prestige', 'iron_title_prestige',
                   'rookie_title_prestige']

    if mode != 'sw_duels_' and mode != 'bowspleef_duels_' and mode != 'no_debuff_duels_':
        mode = mode[:mode.find("_")] + "_"

    for rank in listOfRanks:
        try:
            level = duelsData[mode + rank]
            if level == 1:
                return prestigeStrip(rank) + " I"
            elif level == 2:
                return prestigeStrip(rank) + " II"
            elif level == 3:
                return prestigeStrip(rank) + " III"
            elif level == 4:
                return prestigeStrip(rank) + " IV"
            elif level == 5:
                return prestigeStrip(rank) + " V"
        except KeyError:
            continue

    return "No Rank!"


@app.template_filter()
def getSkin(_):
    try:
        return "https://crafatar.com/avatars/" + request.cookies['uuid']
    except:
        return "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBxISEhUSEhIVFRUVFRUVFRUVFRcVFRcVFRUXFxUVFRUYHSggGBolHRUVITEhJSkrLi4uFx8zODMtNygtLisBCgoKDQ0NDw0NDisZFRkrKzctLS0tKy0tLTctKy0tKy0tLS0rLTctNy0tNzcrLSstKy0tNystLS03Ny0rLS0rLf/AABEIAOEA4QMBIgACEQEDEQH/xAAWAAEBAQAAAAAAAAAAAAAAAAAAAQL/xAAbEAEBAQACAwAAAAAAAAAAAAAAARECQSGBwf/EABYBAQEBAAAAAAAAAAAAAAAAAAABAv/EABQRAQAAAAAAAAAAAAAAAAAAAAD/2gAMAwEAAhEDEQA/AMkBpCqgChIgALgIBQQDACgBixKsBFAAiKBDQANEBdNAEABNFwBQAAAUEAClAogBoigBADQUAqALqYuoCwCgiighQoIACiII0RNBVIQAMACwAASqCIoABoEAAWIAqABqomg0JS0FEKBANA0VABJAFVIApolACABiAKipAUomABgABAVABRAFKICiALAQAAFMDABbCwEAEAUVCKAhhgAABgQBIKAgpQRSQsBIoYCLYYAYACCggqRRSCkBBUAAoFIACKgAoAyqAohAUAFiKgBAgEUAQFBPAagKugCiKAgUDCiggAFMCArKpQEVAFRQBQEkWxMUCgAkUAChQTAxAbAAEKAKgKioCwADCwgBiYpQSwxUAkXABLFxKoJi4AFMAEWgAUQFQAUSKCCoAasNBFMANRSAAAFIYCKigCKARFgESmLQRQoAAIUoCiYAAAtQoABQUQBYIugAAVFAQCgAaBQAMVABaRAAUEoAINYAkoABQAAAABRACKSgJBUAFQAgAigAkXTRApqioFAAAVFwBDQBSosADUBcIIACgi1FABAUSgBQoFomqAIugCatAVAFEXQT0KAyolBRMAUADUVMBQANVFA0pYAhFARLVANQoABIAEUAEwFEAa0QEQFFEXUBQKBgGgIoAACoAAAJpQwEVAFwAAIAqCggEBQASLABDkALCfQEEAVb00AM0oCAgKLEAU5ACCAixQBIUAVOgBYkAUAEf//Z"


@app.template_filter()
def getCookiesName(_):
    try:
        api_request = requests.get("https://api.hypixel.net/player?uuid=" + request.cookies['uuid'] + "&key=bf77aa7d-00d7-47f3-8c27-530b359ccb54")
        return json.loads(api_request.content)['player']['displayname']
    except:
        return "-"



# Pages


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
    filteredFiles = [f for f in files if f[f.find("."):] == ".html" and f != "rootLayout.html" and
                     f != "leaderboardAutoGen.html" and f != "401.html" and f != "403.html" and f != "404.html"
                     and f != "500.html"]
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

        if temp2 == "bedwars.html" or temp2 == "skywars.html" or temp2 == "duels.html":
            temp2 = "player/" + temp2
        filteredFiles[index][0] = temp2

    return render_template('sitemap.xml', base_url="http://hypixeleaderboards.com", articles=filteredFiles)


@app.route("/bedwars/")
def bedwars():
    data = generateData()
    return render_template("bedwars.html", data=data, bedwarsData=data['stats']['Bedwars'])


@app.route("/sign-in/")
def signIn():
    data = generateData()
    resp = make_response(render_template("signIn.html", data=data))
    return resp


@app.route("/player/bedwars/")
def bedwars2():
    try:
        uuid = request.cookies['uuid']
        data = generateData(uuid)
    except KeyError:
        data = generateData()
    return render_template("bedwars.html", data=data, bedwarsData=data['stats']['Bedwars'])


@app.route("/player/duels/")
def duels():
    try:
        uuid = request.cookies['uuid']
        data = generateData(uuid)
    except KeyError:
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
    try:
        uuid = request.cookies['uuid']
        data = generateData(uuid)
    except KeyError:
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


# Post / Get Requests

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


@app.route("/player/duels/", methods=['POST'])
def duels_post():
    data = generateData(request.form['playerName'])
    return render_template("duels.html", data=data, duelsData=customReturn(data, ['stats', 'Duels']))


@app.route("/", methods=['POST'])
def home2_post():
    data = generateData(request.form['playerName'])
    return render_template("home.html", data=data)


@app.route("/sign-in/", methods=['POST'])
def signIn_post():
    data = generateData(request.form['playerName'])
    resp = make_response(render_template("signIn.html", data=data))
    resp.set_cookie("uuid", max_age=0)
    resp.set_cookie("uuid", data['uuid'])
    return resp


# Error Pages

@app.errorhandler(403)
def error_403(e):
    return render_template("403.html"), 403


@app.errorhandler(404)
def error_404(e):
    return render_template("404.html"), 404


@app.errorhandler(405)
def error_405(e):
    return render_template("405.html"), 405


@app.errorhandler(500)
def error_500(e):
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run()
