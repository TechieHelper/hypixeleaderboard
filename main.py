from flask import Flask, redirect, url_for, render_template, request, make_response, jsonify, Blueprint
from flask_mail import Mail, Message
import requests, json, os, time, datetime
from os import listdir
from datetime import datetime
import base64, io, nbt

app = Flask(__name__)
#api = Blueprint('blueprint', __name__, template_folder="templates", subdomain="api")

# General Functions

API_KEY = 'ef79537a-945a-4beb-b6b4-40861c13203e'
minecraftColors = {"GOLD": "FFAA00", "BLACK": "000000", "DARK_BLUE": "0000AA", "DARK_GREEN": "00AA00", "DARK_AQUA": "00AAAA", "DARK_RED": "AA0000", "DARK_PURPLE": "AA00AA", "GRAY": "AAAAAA", "DARK_GREY": "555555", "BLUE": "5555FF", "GREEN": "55FF55", "AQUA": "55FFFF", "RED": "FF5555", "LIGHT_PURPLE": "FF55FF", "YELLOW": "FFFF55", "WHITE": "FFFFFF"}


@app.template_filter()
def nameWrapper(name, asApi=False, useGenericReturn=True):
	data = generateData(name)

	def genericName(text, color):
		return "<span style=\"text-shadow: 1px 1px #eee; color:#" + color + "\"> " + text + "</span>"

	def genericReturn(text):
		return "<span style=\"font-family: 'Minecraftia';\">" + text + "</span>"


	html = ""
	try:
		rank = data['newPackageRank']
		if rank == "VIP":
			html = genericName("[VIP] " + name, "3CE63C")
		elif rank == "MVP":
			html = genericName("[MVP] " + name, "3CE636")
		elif rank == "VIP_PLUS":
			html = genericName("[VIP ", "3CE63C") + genericName("+", "FFAA00") + genericName("] " + name, "3CE63C")
		elif rank == "MVP_PLUS":
			if data['monthlyPackageRank'] == 'SUPERSTAR':
				try:
					html = genericName("[MVP ", minecraftColors[data['monthlyRankColor']]) + genericName("++", minecraftColors[data['rankPlusColor']]) + genericName("] " + name, minecraftColors[data['monthlyRankColor']])
				except:
					html = genericName("[MVP ", "3CE6E6") + genericName("++", minecraftColors[data['rankPlusColor']]) + genericName("] " + name, "3CE6E6")
			else:
				html = genericName("[MVP ", "3CE6E6") + genericName("+", minecraftColors[data['rankPlusColor']]) + genericName("] " + name, "3CE6E6")
	except Exception as e:
		html = genericName(name, "AAAAAA")

	if not asApi:
		if not useGenericReturn:
			return html
		else:
			return genericReturn(html)
	else:
		return {"html": genericReturn(html)}


@app.template_filter()
def bedwarsNameWrapper(name, asApi=False):
	data = generateData(name)

	def starColor(star, color):
		return "<span style=\"text-shadow: 1px 1px #eee; color:#" + color + "\">[" + str(star) + "✫]</span>"

	def primePrestiges(star, color, starColor=""):
		if starColor == "":
			return "<span style=\"text-shadow: 1px 1px #eee; color:#AAAAAA\">[</span>" + \
					"<span style=\"text-shadow: 1px 1px #eee; color:#" + color + "\">[" + str(star) + "</span>" + \
					"<span style=\"text-shadow: 1px 1px #eee; color:#" + color + "\">✪</span>" + \
					"<span style=\"text-shadow: 1px 1px #eee; color:#AAAAAA\">]</span>"
		else:
			return "<span style=\"text-shadow: 1px 1px #eee; color:#AAAAAA\">[</span>" + \
					"<span style=\"text-shadow: 1px 1px #eee; color:#" + color + "\">" + str(star) + "</span>" + \
					"<span style=\"text-shadow: 1px 1px #eee; color:#" + starColor + "\">✪</span>" + \
					"<span style=\"text-shadow: 1px 1px #eee; color:#AAAAAA\">]</span>"

	def genericReturn(text):
		return "<span style=\"font-family: 'Minecraftia';\">" + text + "</span>"


	bedwarsStar = data['achievements']['bedwars_level']
	html = ""
	if bedwarsStar < 100:
		html += starColor(bedwarsStar, "AAAAAA")

	elif 100 < bedwarsStar < 200:
		html += starColor(bedwarsStar, minecraftColors['WHITE'])

	elif 200 < bedwarsStar < 300:
		html += starColor(bedwarsStar, minecraftColors['GOLD'])

	elif 300 < bedwarsStar < 400:
		html += starColor(bedwarsStar, minecraftColors['AQUA'])

	elif 400 < bedwarsStar < 500:
		html += starColor(bedwarsStar, minecraftColors['DARK_GREEN'])

	elif 500 < bedwarsStar < 600:
		html += starColor(bedwarsStar, minecraftColors['DARK_AQUA'])

	elif 600 < bedwarsStar < 700:
		html += starColor(bedwarsStar, minecraftColors['DARK_RED'])

	elif 700 < bedwarsStar < 800:
		html += starColor(bedwarsStar, minecraftColors['LIGHT_PURPLE'])

	elif 800 < bedwarsStar < 900:
		html += starColor(bedwarsStar, minecraftColors['BLUE'])

	elif 900 < bedwarsStar < 1000:
		html += starColor(bedwarsStar, minecraftColors['DARK_PURPLE'])

	elif 1000 < bedwarsStar < 1100:
		html += "<span style=\"text-shadow: 1px 1px #eee; color:#" + minecraftColors['RED'] + "\">[" + \
				"<span style=\"text-shadow: 1px 1px #eee; color:#" + minecraftColors['ORANGE'] + "\">[" + str(bedwarsStar[0]) + \
				"<span style=\"text-shadow: 1px 1px #eee; color:#" + minecraftColors['YELLOW'] + "\">[" + str(bedwarsStar[1]) + \
				"<span style=\"text-shadow: 1px 1px #eee; color:#" + minecraftColors['GREEN'] + "\">[" + str(bedwarsStar[2]) + \
				"<span style=\"text-shadow: 1px 1px #eee; color:#" + minecraftColors['AQUA'] + "\">[" + str(bedwarsStar[3]) + \
				"<span style=\"text-shadow: 1px 1px #eee; color:#" + minecraftColors['LIGHT_PURPLE'] + "\">✫" + \
				"<span style=\"text-shadow: 1px 1px #eee; color:#" + minecraftColors['DARK_PURPLE'] + "\">]"

	elif 1100 < bedwarsStar < 1200:
		html += primePrestiges(bedwarsStar, minecraftColors['WHITE'], "AAAAAA")

	elif 1200 < bedwarsStar < 1300:
		html += primePrestiges(bedwarsStar, minecraftColors['YELLOW'], minecraftColors['GOLD'])

	elif 1300 < bedwarsStar < 1400:
		html += primePrestiges(bedwarsStar, minecraftColors['AQUA'], minecraftColors['DARK_AQUA'])

	elif 1400 < bedwarsStar < 1500:
		html += primePrestiges(bedwarsStar, minecraftColors['GREEN'], minecraftColors['DARK_GREEN'])

	elif 1500 < bedwarsStar < 1600:
		html += primePrestiges(bedwarsStar, minecraftColors['DARK_AQUA'], minecraftColors['LIGHT_BLUE'])

	elif 1600 < bedwarsStar < 1700:
		html += primePrestiges(bedwarsStar, minecraftColors['RED'], minecraftColors['DARK_RED'])

	elif 1700 < bedwarsStar < 1800:
		html += primePrestiges(bedwarsStar, minecraftColors['LIGHT_PURPLE'], minecraftColors['DARK_PURPLE'])

	elif 1800 < bedwarsStar < 1900:
		html += primePrestiges(bedwarsStar, minecraftColors['LIGHT_BLUE'], minecraftColors['DARK_BLUE'])

	elif 1900 < bedwarsStar < 2000:
		html += primePrestiges(bedwarsStar, minecraftColors['DARK_PURPLE'], minecraftColors['DARK_GREY'])


	html += nameWrapper(name, useGenericReturn=False)
	return genericReturn(html)


def letterToSpace(s, l):
	ans = ""
	for letter in s:
		if letter == l: ans += " "
		else: ans += letter

	return ans


def getUUIDFromName(name):
	try:
		api_request = requests.get("https://api.mojang.com/users/profiles/minecraft/" + name)
		api = json.loads(api_request.content)
		return api['id']
	except:
		return "Unknown Name"


def getWatchdogstats():
	try:
		api_request = requests.get("https://api.hypixel.net/watchdogstats?key=" + API_KEY)
		api = json.loads(api_request.content)
	except:
		api = json.loads("{'success': true, 'watchdog_lastMinute': 5, 'staff_rollingDaily': 1356, 'watchdog_total': 4924740, 'watchdog_rollingDaily': 7679, 'staff_total': 1608360}")

	return api


def getGameCounts():
	try:
		api_request = requests.get("https://api.hypixel.net/gameCounts?key=" + API_KEY)
		api = json.loads(api_request.content)
	except:
		with open("gameCounts.json") as f:
			api = json.loads(f.read())

	return api


def getBazaarStats():
	try:
		api_request = requests.get("https://api.hypixel.net/skyblock/bazaar?key=" + API_KEY)
		api = json.loads(api_request.content)
	except:
		with open("skyblockdata/bazaar.json") as f:
			api = json.loads(f.read())

	return api


def getSkyblockNews():
	try:
		api_request = requests.get("https://api.hypixel.net/skyblock/news?key=" + API_KEY)
		api = json.loads(api_request.content)
	except:
		with open("skyblockdata/bazaar.json") as f:
			api = json.loads(f.read())

	return api



def getAuctionsStats():
	try:
		api_request = requests.get("https://api.hypixel.net/skyblock/auctions?key=" + API_KEY)
		api = json.loads(api_request.content)
	except:
		with open("skyblockdata/auctions.json") as f:
			api = json.loads(f.read())

	return api


def generateSkyblockPlayerData(playerID):
	try:
		api_request = requests.get(
			"https://api.hypixel.net/skyblock/profile?profile=" + playerID + "&key=" + API_KEY)
		api = json.loads(api_request.content)
	except:
		with open("skyblockdata/profile.json") as f:
			api = json.loads(f.read())

	return api['profile']


def generateData(name="_"):
	if len(name.encode('utf-8')) != 32:
		uuid = getUUIDFromName(name)
		if uuid != "Unknown Name":
			pass  # Write name
	else:
		uuid = name

	if uuid == "Unknown Name":
		with open("dashedData.json") as f:
			api = json.loads(f.read())
	else:
		try:
			api_request = requests.get("https://api.hypixel.net/player?uuid=" + uuid + "&key=" + API_KEY)
			api = json.loads(api_request.content)
		except:
			with open("dashedData.json") as f:
				api = json.loads(f.read())

	return api['player']


def generateLeaderboardData():
	try:
		api_request = requests.get("https://api.hypixel.net/leaderboards?key=" + API_KEY)
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
def getHypixelLevel(data):
	for i in range(1000000):
		try:
			if data['levelingReward_' + str(i)]:
				pass
		except:
			return i - 1


@app.template_filter()
def checkIfValid(data, dataPoint):
	try:
		return data[dataPoint]
	except KeyError:
		return "-"


@app.template_filter()
def format_datetime(ts):
	if type(ts) == int:
		dt = datetime.fromtimestamp(ts / 1000).strftime("%d/%m/%Y %H:%M:%S")
		return dt
	else:
		return "-"


@app.template_filter()
def capitalizeFirstLetter(value):
	valueList = value.split("_")
	return " ".join([i[0].upper() + i[1:].lower() for i in valueList])


@app.template_filter()
def getRankFromUUID(uuid):
	try:
		try:
			with open("knownUsers.json") as f:
				knownUsers = json.loads(f.read())

			return knownUsers[uuid]

		except KeyError:
			api_request = requests.get("https://api.hypixel.net/player?uuid=" + uuid + "&key=" + API_KEY)
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
def customTry2(dict, pos):
	try:
		_ = dict[pos]
		return True
	except:
		return False


@app.template_filter()
def skyblockProfileCapitalise(word):
	words = word.split('_')
	for i in range(len(words)):
		words[i] = words[i][0:1].upper() + words[i][1:].lower()
	return " ".join(words)


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
def secondsToTimeParkour(seconds):
	mins = seconds // 3600
	return str(mins) + "m " + str(seconds % 60) + "s"


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
		api_request = requests.get("https://api.hypixel.net/player?uuid=" + request.cookies['uuid'] + "&key=" + API_KEY)
		return json.loads(api_request.content)['player']['displayname']
	except:
		return "-"


@app.template_filter()
def doesModesExist(data, modeList):
	try:
		for mode in modeList:
			data = data[mode]

		if data == "":
			return False
	except:
		return False
	return True


@app.template_filter()
def currentName(uuid):
	try:
		api_request = requests.get("https://api.mojang.com/user/profiles/" + uuid + "/names")
		api = json.loads(api_request.content)
		return api[len(api)-1]['name']
	except:
		return "Your name cannot be found"


@app.template_filter()
def unHash(hash):
	data = nbt.nbt.NBTFile(fileobj=io.BytesIO(base64.b64decode(hash)))
	return data


@app.template_filter()
def profileGeneratorTry(generator, pos):
	try:
		_ = generator[pos]
		return "text-success"
	except:
		return "text-warning"


@app.template_filter()
def stripNumbers(generator):
	try:
		_ = int(generator[len(generator)-2])
		return generator[:-3]
	except:
		return generator[:-2]

# API stuff


@app.route('/api/nameWrapper/<name>')
def apiTest(name):
	return nameWrapper(name, True)


# Pages

@app.route('/api/documentation/')
def apiDocumentation():
	return redirect('https://github.com/TechieHelper/HypixelToolsAPI')

@app.route('/skyblock/profile/')
def profile():
	try:
		uuid = request.cookies['uuid']
		data = generateData(uuid)
	except KeyError:
		data = generateData()
	return render_template("profile.html", data=data, profileAsk=True)


@app.route('/skyblock/')
def skyblock():
	data = ""
	return render_template("skyblock.html", data=data)


@app.route('/skyblock/auctions/')
def auctions():
	data = getAuctionsStats()
	return render_template("auctions.html", data=data)



@app.route('/skyblock/bazaar/')
def bazaar():
	data = getBazaarStats()
	return render_template("bazaar.html", data=data)


@app.route('/skyblock/news/')
def news():
	data = getSkyblockNews()
	return render_template("news.html", data=data)



@app.route('/skyblockBazaarPost')
def skyblockBazaarPost():
	try:
		chosenItem = request.args.get('chosenItem', 0, type=str)
		data = getBazaarStats()
		fittingProducts = []
		if data['success']:
			for product in data['products']:
				if letterToSpace(chosenItem.lower(), "+") in letterToSpace(product.lower(), "_"):
					dataToAppend = '<button type="button" class="btn btn-info dropdown-toggle mr-1 mb-1" data-toggle="dropdown">' + capitalizeFirstLetter(product) + '</button>'
					dataToAppend += '<div class="dropdown-menu">'
					dataToAppend += '<a class="dropdown-item" href="#">Sell Summary</a>'
					for i in data['products'][product]['sell_summary']:
						dataToAppend += '<a class="dropdown-item" href="#">Amount: ' + str(i['amount']) + ' Price Per Unit: ' + str(i['pricePerUnit']) + ' Orders: ' + str(i['orders']) + '</a>'
					#dataToAppend += '<div class="dropdown-divider></div>'
					dataToAppend += '<a class="dropdown-item" href="#">Buy Summary</a>'
					for i in data['products'][product]['buy_summary']:
						dataToAppend += '<a class="dropdown-item" href="#">Amount: ' + str(i['amount']) + ' Price Per Unit: ' + str(i['pricePerUnit']) + ' Orders: ' + str(i['orders']) + '</a>'
					dataToAppend += '</div>'
					fittingProducts.append(dataToAppend)
		return jsonify(result=fittingProducts)
	except Exception as e:
		return jsonify(result=str(e))


@app.route("/game-counts/")
def gameCounts():
	data = getGameCounts()
	return render_template("gameCounts.html", data=data)


@app.route("/player/")
def player():
	return render_template("player.html")


@app.route("/watchdogstats/")
def watchdogstats():
	data = getWatchdogstats()
	return render_template("watchdogstats.html", data=data)


@app.route("/")
def home2():
	try:
		uuid = request.cookies['uuid']
		data = generateData(uuid)
	except KeyError:
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
					 and f != "405.html" and f != "500.html"]
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

		if temp2 == "bazaar.html" or temp2 == "auctions.html" or temp2 == "profile.html" or temp2 == "news.html":
			temp2 = "skyblock/" + temp2

		if temp2 == "home.html":
			temp2 = "/"

		if temp2[-5:] == ".html":
			temp2 = temp2[:-5] + "/"

		filteredFiles[index][0] = temp2

	with open("static/knownUsers.json") as f:
		users = json.loads(f.read())

	return render_template('sitemap.xml', base_url="http://hypixeleaderboards.com", articles=filteredFiles, knownUsers=users)


@app.route("/bedwars/")
def bedwars():
	data = generateData()
	return render_template("bedwars.html", data=data, bedwarsData=data['stats']['Bedwars'])

@app.route("/player/other/")
def other():
	data = generateData()
	return render_template("other.html", data=data)

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


@app.route("/player/bedwars/<username>")
def bedwars3(username):
	data = generateData(username)
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


@app.route("/player/skywars/")
def skywars():
	try:
		uuid = request.cookies['uuid']
		data = generateData(uuid)
	except KeyError:
		data = generateData()
	return render_template("skywars.html", data=data, skywarsData=data['stats']['SkyWars'])


@app.route("/player/skywars/<username>")
def skywars2(username):
	data = generateData(username)
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


@app.route('/skyblock/profile/', methods=['POST'])
def profile_post():
	try:
		profileData = generateSkyblockPlayerData(request.form['profile_id'])
		return render_template("profile.html", skyblockData=profileData, profileAsk=False)
	except:
		data = generateData(request.form['playerName'])
		return render_template("profile.html", data=data, profileAsk=True)


@app.route("/player/skywars/", methods=['POST'])
def skywars_post():
	return redirect("/player/skywars/" + request.form['playerName'])


@app.route("/player/skywars/<username>", methods=['POST'])
def skywars_post2(username):
	return redirect("/player/skywars/" + request.form['playerName'])


@app.route("/bedwars/", methods=['POST'])
def bedwars_post():
	data = generateData(request.form['playerName'])
	return render_template("bedwars.html", data=data, bedwarsData=customReturn(data, ['stats', 'Bedwars']))


@app.route("/player/bedwars/", methods=['POST'])
def bedwars_post2():
	return redirect("/player/bedwars/" + request.form['playerName'])


@app.route("/player/bedwars/<username>", methods=['POST'])
def bedwars_post3(username):
	return redirect("/player/bedwars/" + request.form['playerName'])



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
	# with open('static/config.json') as f:
	# 	data = json.load(f)
	# 	API_KEY = data['api_key']

	# s = sched.scheduler(time.time, time.sleep)
	#
	#
	# def refresh_key():
	# 	with open('static/config.json') as f:
	# 		data = json.load(f)
	# 		API_KEY = data['api_key']
	#
	# refresh_key()
	#s.enter(60, 1, refresh_key)
	# app.config['SERVER_NAME'] = 'hypixeleaderboard.herokuapp.com:5000'
	#app.register_blueprint(api)
	app.run()
