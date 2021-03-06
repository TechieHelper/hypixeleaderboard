from flask import Flask, redirect, render_template, request, make_response, jsonify, Response
from flask_babel import gettext, Babel
from os import listdir
from datetime import datetime

import requests
import json
import os
import base64
import io
import nbt
import psycopg2
import atexit
import math

app = Flask(__name__)
babel = Babel(app)
#api = Blueprint('blueprint', __name__, template_folder="templates", subdomain="api")

# General Functions

API_KEY = os.environ['API_KEY']
DATABASE_URL = os.environ['DATABASE_URL']
OCP_API_KEY = os.environ["OCP_API_KEY"]
PSTACK_API_KEY = os.environ["PSTACK_API_KEY"]
minecraftColors = {"GOLD": "FFAA00", "BLACK": "000000", "DARK_BLUE": "0000AA", "DARK_GREEN": "00AA00", "DARK_AQUA": "00AAAA", "DARK_RED": "AA0000", "DARK_PURPLE": "AA00AA", "GRAY": "AAAAAA", "DARK_GREY": "555555", "BLUE": "5555FF", "GREEN": "55FF55", "AQUA": "55FFFF", "RED": "FF5555", "LIGHT_PURPLE": "FF55FF", "YELLOW": "FFFF55", "WHITE": "FFFFFF"}
minecraftChatCodes = {"GOLD": "§6", "BLACK": "§0", "DARK_BLUE": "§1", "DARK_GREEN": "§2", "DARK_AQUA": "§3", "DARK_RED": "§4", "DARK_PURPLE": "§5", "GRAY": "§7", "DARK_GREY": "§8", "BLUE": "§9", "GREEN": "§a", "AQUA": "§b", "RED": "§c", "LIGHT_PURPLE": "§d", "YELLOW": "§e", "WHITE": "§f"}
minecraftCodesToHTML = {"§6": "FFAA00", "§0": "000000", "§1": "0000AA", "§2": "00AA00", "§3": "00AAAA", "§4": "AA0000", "§5": "AA00AA", "§7": "AAAAAA", "§8": "555555", "§9": "5555FF", "§a": "55FF55", "§b": "55FFFF", "§c": "FF5555", "§d": "FF55FF", "§e": "FFFF55", "§f": "FFFFFF"}


@babel.localeselector
def get_locale():
	return request.accept_languages.best_match(["en", "fr"])


@app.template_filter()
def guildTagWrapper(text: str, tagColor: str) -> str:
	"""
	A function to correctly color the guild tag for a given guild.

	:param text: The text that should be coloured
	:param tagColor: The color of the tag
	:return: The formatted text
	"""

	return "<span style=\"color:#" + minecraftColors[tagColor] + ";\"> " + text + "</span>"


@app.template_filter()
def tryFunc(func):
	"""
	A function to try a function, and return nothing on fail.

	:param func: The function to be tried
	:return: The function output or nothing.
	"""
	try:
		return func
	except Exception:
		return ""


@app.template_filter()
def chatCodeParser(text: str, asApi=False):
	"""
	A function to parse a piece of minecraft text with chat codes and format it in HTML.
	Example: '§4George'.

	:param text: The minecraft text to be formatted
	:param asApi: Whether to return the data for the API or not
	:return: The formatted HTML
	"""

	def wrapText(text: str, color: str):
		return "<span style=\"text-shadow: 1px 1px #eee; color:#" + color + "\"> " + text + "</span>"
	currentColor = minecraftColors['BLACK']
	cachedText = ""
	outputText = ""
	isKey = False
	for c in text:
		if isKey:
			try:
				currentColor = minecraftCodesToHTML["§" + c]
			except KeyError:
				return "Invalid String"
			isKey = False
		elif c == "§":
			outputText += wrapText(cachedText, currentColor)
			cachedText = ""
			isKey = True
		else:
			cachedText += c
	if cachedText != "":
		return outputText + wrapText(cachedText, currentColor)
	else:
		return outputText


@app.template_filter()
def nameWrapper(name: str, asApi=False, useGenericReturn=True, useChatCodes=False):
	"""
	A function to wrap a name with html to format it, as would be in the game.

	:param name: Name to format
	:param asApi: Whether to return data in API form
	:param useGenericReturn: Whether to include the font tag in the return statement
	:return: Data, in API list or string form
	"""
	data = generateData(name)

	def genericName(text, color):
		return "<span style=\"text-shadow: 1px 1px #eee; color:#" + color + "\"> " + text + "</span>"

	def genericReturn(text):
		return "<span style=\"font-family: 'Minecraftia';\">" + text + "</span>"

	html = ""
	try:
		rank = data['rank']
		if rank == "YOUTUBER":
			if useChatCodes:
				html = "§c[§fYOUTUBE§c] " + name
			else:
				html = "<span style=\"text-shadow: 1px 1px #eee; color:#" + minecraftColors['RED'] + "\">[</span>" + \
						"<span style=\"text-shadow: 1px 1px #aaa; color:#E0E0E0;\">YOUTUBE</span>" + \
						"<span style=\"text-shadow: 1px 1px #eee; color:#" + minecraftColors['RED'] + "\">]" + name + "</span>"
		else:
			raise Exception()
	except Exception:
		try:
			rank = data['newPackageRank']
			if rank == "VIP":
				if useChatCodes:
					html = "§a[VIP]" + name
				else:
					html = genericName("[VIP] " + name, "3CE63C")
			elif rank == "MVP":
				if useChatCodes:
					html = "§a[MVP]" + name
				else:
					html = genericName("[MVP] " + name, "3CE636")
			elif rank == "VIP_PLUS":
				if useChatCodes:
					html = "§a[VIP§6+§a]" + name
				else:
					html = genericName("[VIP ", "3CE63C") + genericName("+", "FFAA00") + genericName("] " + name, "3CE63C")
			elif rank == "MVP_PLUS":
				if data['monthlyPackageRank'] == 'SUPERSTAR':
					try:
						if useChatCodes:
							html = minecraftChatCodes[data['monthlyRankColor']] + "[MVP" + minecraftChatCodes[data['rankPlusColor']] + "++" + minecraftChatCodes[data['monthlyRankData']] + "] " + name
						else:
							html = genericName("[MVP ", minecraftColors[data['monthlyRankColor']]) + genericName("++", minecraftColors[data['rankPlusColor']]) + genericName("] " + name, minecraftColors[data['monthlyRankColor']])
					except Exception:
						if useChatCodes:
							html = "§a[MVP" + minecraftChatCodes[data['rankPlusColor']] + "++§a] " + name
						else:
							html = genericName("[MVP ", "3CE6E6") + genericName("++", minecraftColors[data['rankPlusColor']]) + genericName("] " + name, "3CE6E6")
				else:
					if useChatCodes:
						html = "§a[MVP" + minecraftChatCodes[data['rankPlusColor']] + "+§a] " + name
					else:
						html = genericName("[MVP", "3CE6E6") + genericName("+", minecraftColors[data['rankPlusColor']]) + genericName("] " + name, "3CE6E6")
		except Exception:
			if useChatCodes:
				html = "§7" + name
			else:
				html = genericName(name, "AAAAAA")

	if not asApi:
		if not useGenericReturn:
			return html
		else:
			return genericReturn(html)
	else:
		if useChatCodes:
			return {"html": html}
		else:
			return {"html": genericReturn(html)}


@app.template_filter()
def duelsNameWrapper(name: str, asApi=False):
	"""
	A function to wrap a name with html to format it, as well as its duels title, as would be in the game.

	:param name: Name to format
	:param asApi: Whether to return data in API form
	:return: Data, in API list or string form
	"""
	data = generateData(name)

	html = ""
	try:
		titleKey = data['stats']['Duels']['active_cosmetictitle']
		pos = titleKey.rfind('_')
		titleKeyFinal = titleKey[pos+1:] + "_" + titleKey[:pos] + "_title_prestige"
		title = "✫ The " + capitalizeFirstLetter(titleKey) + " "
		level = data['stats']['Duels'][titleKeyFinal]
		color = titleKey[:pos].upper()
		if level == 1:
			title += "I"
		elif level == 2:
			title += "II"
		elif level == 3:
			title += "III"
		elif level == 4:
			title += "IV"
		elif level == 5:
			title += "V"
		elif level == 6:
			title += "VI"
		elif level == 7:
			title += "VII"
		elif level == 8:
			title += "VIII"
		elif level == 9:
			title += "IX"
		elif level == 10:
			title += "X"
		if color == "ROOKIE":
			html += "<span style=\"text-shadow: 1px 1px #eee; color:#AAAAAA\"> " + title + "</span>"
		elif color == "IRON":
			html += "<span style=\"text-shadow: 1px 1px #eee; color:#" + minecraftColors['WHITE'] + "\"> " + title + "</span>"
		elif color == "GOLD":
			html += "<span style=\"text-shadow: 1px 1px #eee; color:#" + minecraftColors['GOLD'] + "\"> " + title + "</span>"
		elif color == "DIAMOND":
			html += "<span style=\"text-shadow: 1px 1px #eee; color:#" + minecraftColors['AQUA'] + "\"> " + title + "</span>"
		elif color == "MASTER":
			html += "<span style=\"text-shadow: 1px 1px #eee; color:#" + minecraftColors['GREEN'] + "\"> " + title + "</span>"
		elif color == "LEGEND":
			html += "<span style=\"text-shadow: 1px 1px #eee; color:#" + minecraftColors['RED'] + "\"> " + title + "</span>"
		elif color == "GRANDMASTER":
			html += "<span style=\"text-shadow: 1px 1px #eee; color:#" + minecraftColors['YELLOW'] + "\"> " + title + "</span>"
		elif color == "GODLIKE":
			html += "<span style=\"text-shadow: 1px 1px #eee; color:#" + minecraftColors['DARK_PURPLE'] + "\"> " + title + "</span>"

	except Exception:
		pass

	html += nameWrapper(name, useGenericReturn=False)
	if asApi:
		return {"html": html}
	else:
		return html


@app.template_filter()
def bedwarsNameWrapper(name, asApi=False):
	"""
	A function to wrap a name with html to format it, as well as its bedwars star, as would be in the game.

	:param name: Name to format
	:param asApi: Whether to return data in API form
	:return: Data, in API list or string form
	"""
	data = generateData(name)

	def starColor(star, color):
		return "<span style=\"text-shadow: 1px 1px #eee; color:#" + color + "\">[" + str(star) + "✫]</span>"

	def primePrestiges(star: int, color: str, starColor="") -> str:
		"""
		A function to wrap a prime prestige star with a color.

		:param star: Star to format (1100-1999)
		:param color: Color to format the star text with
		:param starColor: Color to format the actual star with
		:return: A html formatted star with the parameters given
		"""
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

	def specialPresitges(star: int, color1: str, color2: str, color3: str, starColor: str, lastColor: str) -> str:
		"""
		A function to wrap a star above 2000 star with its correct in-game formatting.

		:param star: Star to format (2000+)
		:param color1: The color of the first letter of the star number
		:param color2: The color of the second letter of the star number
		:param color3: The color of the third letter of the star number
		:param starColor: The color of the star and the last number of the star
		:param color3: The color of the last bracket in the star
		:param lastColor: Color to format the actual star with
		:return: A html formatted star with the parameters given
		"""
		return "<span style=\"text-shadow: 1px 1px #eee; color:#" + color1 + "\">[" + str(star)[0] + "</span>" + \
				"<span style=\"text-shadow: 1px 1px #eee; color:#" + color2 + "\">" + str(star)[1] + str(star)[2] + "</span>" + \
				"<span style=\"text-shadow: 1px 1px #eee; color:#" + color3 + "\">" + str(star)[3] + "</span>" + \
				"<span style=\"text-shadow: 1px 1px #eee; color:#" + starColor + "\">⚝</span>" + \
				"<span style=\"text-shadow: 1px 1px #eee; color:#" + lastColor + "\">]</span>"

	def genericReturn(text):
		return "<span style=\"font-family: 'Minecraftia'; background-color: #F5F5F5;\">" + text + "</span>"

	bedwarsStar = data['achievements']['bedwars_level']
	html = ""
	if bedwarsStar < 100:
		html += starColor(bedwarsStar, "AAAAAA")

	elif 100 <= bedwarsStar < 200:
		html += starColor(bedwarsStar, minecraftColors['WHITE'])

	elif 200 <= bedwarsStar < 300:
		html += starColor(bedwarsStar, minecraftColors['GOLD'])

	elif 300 <= bedwarsStar < 400:
		html += starColor(bedwarsStar, minecraftColors['AQUA'])

	elif 400 <= bedwarsStar < 500:
		html += starColor(bedwarsStar, minecraftColors['DARK_GREEN'])

	elif 500 <= bedwarsStar < 600:
		html += starColor(bedwarsStar, minecraftColors['DARK_AQUA'])

	elif 600 <= bedwarsStar < 700:
		html += starColor(bedwarsStar, minecraftColors['DARK_RED'])

	elif 700 <= bedwarsStar < 800:
		html += starColor(bedwarsStar, minecraftColors['LIGHT_PURPLE'])

	elif 800 <= bedwarsStar < 900:
		html += starColor(bedwarsStar, minecraftColors['BLUE'])

	elif 900 <= bedwarsStar < 1000:
		html += starColor(bedwarsStar, minecraftColors['DARK_PURPLE'])

	elif 1000 <= bedwarsStar < 1100:
		html += "<span style=\"text-shadow: 1px 1px #eee; color:#" + minecraftColors['RED'] + "\">[" + \
				"<span style=\"text-shadow: 1px 1px #eee; color:#" + minecraftColors['ORANGE'] + "\">[" + str(bedwarsStar[0]) + \
				"<span style=\"text-shadow: 1px 1px #eee; color:#" + minecraftColors['YELLOW'] + "\">[" + str(bedwarsStar[1]) + \
				"<span style=\"text-shadow: 1px 1px #eee; color:#" + minecraftColors['GREEN'] + "\">[" + str(bedwarsStar[2]) + \
				"<span style=\"text-shadow: 1px 1px #eee; color:#" + minecraftColors['AQUA'] + "\">[" + str(bedwarsStar[3]) + \
				"<span style=\"text-shadow: 1px 1px #eee; color:#" + minecraftColors['LIGHT_PURPLE'] + "\">✫" + \
				"<span style=\"text-shadow: 1px 1px #eee; color:#" + minecraftColors['DARK_PURPLE'] + "\">]"

	elif 1100 <= bedwarsStar < 1200:
		html += primePrestiges(bedwarsStar, minecraftColors['WHITE'], "AAAAAA")

	elif 1200 <= bedwarsStar < 1300:
		html += primePrestiges(bedwarsStar, minecraftColors['YELLOW'], minecraftColors['GOLD'])

	elif 1300 <= bedwarsStar < 1400:
		html += primePrestiges(bedwarsStar, minecraftColors['AQUA'], minecraftColors['DARK_AQUA'])

	elif 1400 <= bedwarsStar < 1500:
		html += primePrestiges(bedwarsStar, minecraftColors['GREEN'], minecraftColors['DARK_GREEN'])

	elif 1500 <= bedwarsStar < 1600:
		html += primePrestiges(bedwarsStar, minecraftColors['DARK_AQUA'], minecraftColors['LIGHT_BLUE'])

	elif 1600 <= bedwarsStar < 1700:
		html += primePrestiges(bedwarsStar, minecraftColors['RED'], minecraftColors['DARK_RED'])

	elif 1700 <= bedwarsStar < 1800:
		html += primePrestiges(bedwarsStar, minecraftColors['LIGHT_PURPLE'], minecraftColors['DARK_PURPLE'])

	elif 1800 <= bedwarsStar < 1900:
		html += primePrestiges(bedwarsStar, minecraftColors['LIGHT_BLUE'], minecraftColors['DARK_BLUE'])

	elif 1900 <= bedwarsStar < 2000:
		html += primePrestiges(bedwarsStar, minecraftColors['DARK_PURPLE'], minecraftColors['DARK_GREY'])

	elif 2000 <= bedwarsStar < 2100:
		html += specialPresitges(bedwarsStar, minecraftColors['LIGHT_GREY'], minecraftColors['WHITE'], minecraftColors['LIGHT_GREY'], minecraftColors['LIGHT_GREY'], minecraftColors['DARK_GREY'])

	elif 2100 <= bedwarsStar < 2200:
		html += specialPresitges(bedwarsStar, minecraftColors['WHITE'], minecraftColors['YELLOW'], minecraftColors['GOLD'], minecraftColors['GOLD'], minecraftColors['GOLD'])

	elif 2200 <= bedwarsStar < 2300:
		html += specialPresitges(bedwarsStar, minecraftColors['GOLD'], minecraftColors['WHITE'], minecraftColors['AQUA'], minecraftColors['DARK_AQUA'], minecraftColors['DARK_AQUA'])

	elif 2300 <= bedwarsStar < 2400:
		html += specialPresitges(bedwarsStar, minecraftColors['DARK_PURPLE'], minecraftColors['LIGHT_PURPLE'], minecraftColors['GOLD'], minecraftColors['YELLOW'], minecraftColors['YELLOW'])

	elif 2400 <= bedwarsStar < 2500:
		html += specialPresitges(bedwarsStar, minecraftColors['AQUA'], minecraftColors['WHITE'], minecraftColors['LIGHT_GREY'], minecraftColors['LIGHT_GREY'], minecraftColors['DARK_GREY'])

	elif 2500 <= bedwarsStar < 2600:
		html += specialPresitges(bedwarsStar, minecraftColors['WHITE'], minecraftColors['GREEN'], minecraftColors['DARK_GREEN'], minecraftColors['DARK_GREEN'], minecraftColors['DARK_GREEN'])

	elif 2600 <= bedwarsStar < 2700:
		html += specialPresitges(bedwarsStar, minecraftColors['DARK_RED'], minecraftColors['RED'], minecraftColors['LIGHT_PURPLE'], minecraftColors['LIGHT_PURPLE'], minecraftColors['DARK_PURPLE'])

	elif 2700 <= bedwarsStar < 2800:
		html += specialPresitges(bedwarsStar, minecraftColors['YELLOW'], minecraftColors['WHITE'], minecraftColors['DARK_GREY'], minecraftColors['DARK_GREY'], minecraftColors['DARK_GREY'])

	elif 2800 <= bedwarsStar < 2900:
		html += specialPresitges(bedwarsStar, minecraftColors['GREEN'], minecraftColors['DARK_GREEN'], minecraftColors['ORANGE'], minecraftColors['ORANGE'], minecraftColors['YELLOW'])

	elif 2900 <= bedwarsStar < 3000:
		html += specialPresitges(bedwarsStar, minecraftColors['AQUA'], minecraftColors['DARK_AQUA'], minecraftColors['BLUE'], minecraftColors['BLUE'], minecraftColors['DARK_BLUE'])

	elif 3000 <= bedwarsStar:
		html += specialPresitges(bedwarsStar, minecraftColors['YELLOW'], minecraftColors['ORANGE'], minecraftColors['RED'], minecraftColors['RED'], minecraftColors['DARK_RED'])

	html += nameWrapper(name, useGenericReturn=False)
	if asApi:
		return {"html": genericReturn(html)}
	else:
		return genericReturn(html)


def getGuildStats(name):
	"""
	A function to get guild data for a given guild name from the hypixel API.

	:param name: Guild name
	:return: API data, or example data for test purposes
	"""
	try:
		api_request = requests.get("https://api.hypixel.net/guild?key=" + API_KEY + "&name=" + name)
		api = json.loads(api_request.content)
	except Exception:
		with open('guildExampleData.json') as f:
			api = json.load(f)
	return api['guild']


def letterToSpace(s: str, l: chr) -> str:
	"""
	A simple function to take a string, find all times a certain character is used and replace them with a space.

	:param s: String to modify
	:param l: Character to find in string
	:return: Formatted string
	"""
	ans = ""
	for letter in s:
		if letter == l: ans += " "
		else: ans += letter

	return ans


def getUUIDFromName(name: str, conn=None, cur=None) -> str:
	"""
	A function to contact the minecraft mojang API with a username and convert it to a UUID, returning 'Unknown Name'
	if it cannot be found.

	:param name: Player name to be converted
	:return: Player UUID or 'Unknown Name'
	"""
	if conn is None:
		conn = psycopg2.connect(DATABASE_URL)
		cur = conn.cursor()
		endConn = True
	else:
		endConn = False

	try:
		cur.execute(
			f"""
			SELECT uuid
			FROM uuids
			WHERE username = '{name}';
			"""
		)
		try:
			username = cur.fetchall()
			return username[0][0]
		except Exception:
			api_request = requests.get("https://api.mojang.com/users/profiles/minecraft/" + name)
			api = json.loads(api_request.content)
			username = api['id']

			cur.execute(
				f"""
				INSERT INTO uuids (uuid, username)
				SELECT '{username}', '{name}'
				ON CONFLICT DO NOTHING;
				"""
			)
			print(username, name)

			if endConn:
				conn.commit()
				cur.close()
			return username
	except KeyError:
		print(api)
	except Exception as e:
		print(e)
		if endConn:
			conn.commit()
			cur.close()
		return "Unknown Name"


def getWatchdogstats():
	"""
	A function to get the hypixel watchdog statistics from the hypixel API, and load a JSON string if the API is
	unreachable or for testing purposes.

	:return: API data
	"""
	try:
		api_request = requests.get("https://api.hypixel.net/watchdogstats?key=" + API_KEY)
		api = json.loads(api_request.content)
	except Exception:
		api = json.loads("{'success': true, 'watchdog_lastMinute': 5, 'staff_rollingDaily': 1356, 'watchdog_total': 4924740, 'watchdog_rollingDaily': 7679, 'staff_total': 1608360}")

	return api


def getGameCounts():
	"""
	A function to get the hypixel player game counts from the hypixel API, and load a JSON file if the API is
	unreachable or for debug purposes.

	:return: The API data
	"""
	try:
		api_request = requests.get("https://api.hypixel.net/gameCounts?key=" + API_KEY)
		api = json.loads(api_request.content)
	except Exception:
		with open("gameCounts.json") as f:
			api = json.loads(f.read())

	return api


def getBazaarStats():
	"""
	A function to get the hypixel bazaar data from the hypixel API, and load a JSON file if the API is unreachable or
	for debug purposes.

	:return: The API data
	"""
	try:
		api_request = requests.get("https://api.hypixel.net/skyblock/bazaar?key=" + API_KEY)
		api = json.loads(api_request.content)
	except Exception:
		with open("skyblockdata/bazaar.json") as f:
			api = json.loads(f.read())

	return api


def getSkyblockNews():
	"""
	A function to get the hypixel skyblock news data from the hypixel API, and load a JSON file if the API is
	unreachable or for debug purposes.

	:return: The API data
	"""
	try:
		api_request = requests.get("https://api.hypixel.net/skyblock/news?key=" + API_KEY)
		api = json.loads(api_request.content)
	except Exception:
		with open("skyblockdata/bazaar.json") as f:
			api = json.loads(f.read())

	return api


def getAuctionsStats():
	"""
	A function to get the hypixel skyblock auctions data from the hypixel API, and load a JSON file if the API is
	unreachable or for debug purposes.

	:return: The API data
	"""
	try:
		api_request = requests.get("https://api.hypixel.net/skyblock/auctions?key=" + API_KEY)
		api = json.loads(api_request.content)
	except Exception:
		with open("skyblockdata/auctions.json") as f:
			api = json.loads(f.read())

	return api


def generateSkyblockPlayerData(playerID):
	"""
	A function to get the hypixel skyblock player profile data from the hypixel API, and load a JSON file if the API is
	unreachable or for debug purposes.

	:param playerID: The player UUID
	:return: The API data
	"""

	try:
		api_request = requests.get(
			"https://api.hypixel.net/skyblock/profile?profile=" + playerID + "&key=" + API_KEY)
		api = json.loads(api_request.content)
	except Exception:
		with open("skyblockdata/profile.json") as f:
			api = json.loads(f.read())

	return api['profile']


def getPlayerStatus(name="_"):
	if len(name.encode('utf-8')) != 32:
		uuid = getUUIDFromName(name)
		if uuid != "Unknown Name":
			pass
	else:
		uuid = name

	if uuid == "Unknown Name":
		with open("dashedSessionData.json") as f:
			api = json.loads(f.read())
	else:
		try:
			api_request = requests.get("https://api.hypixel.net/status?uuid=" + uuid + "&key=" + API_KEY)
			api = json.loads(api_request.content)
		except Exception:
			with open("dashedSessionData.json") as f:
				api = json.loads(f.read())

	return api


def generateData(name="_"):
	"""
	The main player data grabber from the hypixel API. This function does a few things. First, it checks if the name
	given is a UUID, and if it is not then it turns it into a UUID using the function. If the UUID is an unknown name,
	the function opens another file that contains an empty data set for the data. If the UUID is known, it tries to get
	the corresponding data from the hypixel API for that player. On fail, it reads this data from a file. It then
	returns this data.

	:param name: The player name or player UUID
	:return: The player data for the given name or UUID
	"""
	if len(name.encode('utf-8')) != 32:
		uuid = getUUIDFromName(name)
		if uuid != "Unknown Name":
			pass
	else:
		uuid = name

	if uuid == "Unknown Name":
		with open("dashedData.json") as f:
			api = json.loads(f.read())
	else:
		try:
			api_request = requests.get("https://api.hypixel.net/player?uuid=" + uuid + "&key=" + API_KEY)
			api = json.loads(api_request.content)
		except Exception:
			with open("dashedData.json") as f:
				api = json.loads(f.read())

	return api['player']


def generateLeaderboardData():
	"""
	A function to get the hypixel leaderboards data from the hypixel API, and load a JSON file if the API is unreachable
	or for debug purposes.

	:return: The API data
	"""
	try:
		api_request = requests.get("https://api.hypixel.net/leaderboards?key=" + API_KEY)
		api = json.loads(api_request.content)
	except Exception:
		with open("dashedLeaderboardData.json") as f:
			api = json.loads(f.read())

	return api['leaderboards']


def leaderboardURLFormatting(value: str) -> str:
	"""
	A function that takes a value, finds all occurrences of the character '-', changing all of these occurrences to '-'.
	It also capitalises the output

	:param value: The input string
	:return: The output after parsing the string
	"""
	output = ""
	for i in value:
		if i == "-":
			i = "_"
		else:
			i = i.upper()

		output += i

	return output


def customReturn(data, dataPoints: list):
	"""
	A function to get a datapoint of a dictionary, and add it to another dictionary. If one cannot be found, it catches
	the subsequent error and opens some filler data instead.

	:param data: The dictionary
	:param dataPoints: The datapoints
	:return: The dictionary after processing
	"""
	try:
		newData = data
		for arg in dataPoints:
			newData = newData[arg]
	except (KeyError, TypeError):
		with open("dashedData.json") as f:
			newData = json.loads(f.read())['player']['stats']['Bedwars']
	return newData


def prestigeStrip(value: str) -> str:
	"""
	A function to capitalise the first letter of a string, and return all of the data to the right of the first (and
	only) underscore ('_').

	:param value: The string to parse
	:return: The parsed string
	"""
	value = value[0].upper() + value[1:]
	return value[:value.find("_")]




# App Commands


@app.template_filter()
def getHypixelLevel(data) -> int:
	"""
	A function to loop through all of the possible hypixel levels, and extract them from the data given, and find the
	maximal level that the user has - this is because the API often produces mangled results, with levels above 100
	often not existing.

	:param data: The API data previously grabbed
	:return: The hypxiel level
	"""
	highest = 0
	for i in range(10000):
		try:
			if data['levelingReward_' + str(i)]:
				highest = i-1 if highest < i-1 else highest
		except Exception:
			pass
	return highest if highest != 1000000 else 0


@app.template_filter()
def checkIfValid(data, dataPoint: str):
	"""
	A function to check if a dataPoint is present in a dictionary of data, and to return the datapoint if it is, else
	to return '-'. This is because try, catch statements don't exist in jinja2.

	:param data: The full dictionary
	:param dataPoint: The datapoint that should be found in the dictionary
	:return: The datapoint if it is valid, else '-'
	"""
	try:
		return data[dataPoint]
	except KeyError:
		return "-"


@app.template_filter()
def format_datetime(ts) -> str:
	"""
	A function to take a UNIX timestamp, and turn it into a formatted datetime. If it is not a UNIX timestamp, the
	function returns '-'.

	:param ts: The UNIX timestamp
	:return: The formatted datetime if ts is a UNIX timestamp, else '-'
	"""
	if isinstance(ts, int):
		dt = datetime.fromtimestamp(ts / 1000).strftime("%d/%m/%Y %H:%M:%S")
		return dt
	else:
		return "-"


@app.template_filter()
def capitalizeFirstLetter(value: str) -> str:
	"""
	A function to split a string by its underscores ('_') and to replace these with spaces, as well as capitalising the
	first letter of each new word.

	:param value: The string to be formatted
	:return: The formatted string
	"""
	return " ".join([i[0].upper() + i[1:].lower() for i in value.split('_')])


@app.template_filter()
def getRankFromUUID(uuid: str) -> str:
	"""
	A function to get a players name display name from their UUID, and also to cache this in a file if it was not
	already there. To get the display name, first the cache file is checked for the name, and if it is not present
	there, the hypixel API is contacted for the name. Then the data is cached and the name returned. If neither of
	these places contain the UUID corresponding to a name, then 'Unknown Name' is returned.

	:param uuid: The player's UUID
	:return: The players display name, or 'Unknown Name'
	"""
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
def customTry2(dictionary: dict, pos: str) -> bool:
	"""
	A function to get a dictionary position, and if it is found, to return True. Else, it returns False.

	:param dictionary: The dictionary to find the datapoint in
	:param pos: The datapoint
	:return: True if datapoint is valid, else false
	"""
	try:
		_ = dictionary[pos]
		return True
	except KeyError:
		return False



@app.template_filter()
def customTry(data: dict, dataPoints: list):
	"""
	A function to cycle through a path of datapoints in a dictionary (e.g. data['test']['test2']), and check if they
	are valid. If they are, it will return what is found at then end of that path, else it will return '-'.

	:param data: The dictionary
	:param dataPoints: The datapoints
	:return: What is at the end of the datapoints, or '-'
	"""
	try:
		newData = data
		for arg in dataPoints:
			newData = newData[arg]

		return newData
	except Exception:
		return "-"


@app.template_filter()
def customEnumerate(value):
	"""
	A function to simply return the enumerated value of a list, as this is not in-built into jinja2.

	:param value: The list
	:return: The enumerated list
	"""
	return enumerate(value)


@app.template_filter()
def secondsToTimeParkour(seconds):
	mins = seconds // 3600
	return str(mins) + "m " + str(seconds % 60) + "s"


@app.template_filter()
def prestigeRank(mode, duelsData):
	"""
	A function to get the rank of a player in duels, as the hypixel API returns the data in a complex way.

	:param mode: The duels mode
	:param duelsData: The data to find the rank of the given mode in
	:return: The rank of the player, or 'No Rank!'
	"""
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
	"""
	A program to get the skin of the player.

	:param _: Temp variable, as jinja2 doesn't like filters with no parameters.
	:return: A link to the skin, or a link to a grey box as a filler
	"""
	try:
		return "https://crafatar.com/avatars/" + request.cookies['uuid']
	except Exception:
		return "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBxISEhUSEhIVFRUVFRUVFRUVFRcVFRcVFRUXFxUVFRUYHSggGBolHRUVITEhJSkrLi4uFx8zODMtNygtLisBCgoKDQ0NDw0NDisZFRkrKzctLS0tKy0tLTctKy0tKy0tLS0rLTctNy0tNzcrLSstKy0tNystLS03Ny0rLS0rLf/AABEIAOEA4QMBIgACEQEDEQH/xAAWAAEBAQAAAAAAAAAAAAAAAAAAAQL/xAAbEAEBAQACAwAAAAAAAAAAAAAAARECQSGBwf/EABYBAQEBAAAAAAAAAAAAAAAAAAABAv/EABQRAQAAAAAAAAAAAAAAAAAAAAD/2gAMAwEAAhEDEQA/AMkBpCqgChIgALgIBQQDACgBixKsBFAAiKBDQANEBdNAEABNFwBQAAAUEAClAogBoigBADQUAqALqYuoCwCgiighQoIACiII0RNBVIQAMACwAASqCIoABoEAAWIAqABqomg0JS0FEKBANA0VABJAFVIApolACABiAKipAUomABgABAVABRAFKICiALAQAAFMDABbCwEAEAUVCKAhhgAABgQBIKAgpQRSQsBIoYCLYYAYACCggqRRSCkBBUAAoFIACKgAoAyqAohAUAFiKgBAgEUAQFBPAagKugCiKAgUDCiggAFMCArKpQEVAFRQBQEkWxMUCgAkUAChQTAxAbAAEKAKgKioCwADCwgBiYpQSwxUAkXABLFxKoJi4AFMAEWgAUQFQAUSKCCoAasNBFMANRSAAAFIYCKigCKARFgESmLQRQoAAIUoCiYAAAtQoABQUQBYIugAAVFAQCgAaBQAMVABaRAAUEoAINYAkoABQAAAABRACKSgJBUAFQAgAigAkXTRApqioFAAAVFwBDQBSosADUBcIIACgi1FABAUSgBQoFomqAIugCatAVAFEXQT0KAyolBRMAUADUVMBQANVFA0pYAhFARLVANQoABIAEUAEwFEAa0QEQFFEXUBQKBgGgIoAACoAAAJpQwEVAFwAAIAqCggEBQASLABDkALCfQEEAVb00AM0oCAgKLEAU5ACCAixQBIUAVOgBYkAUAEf//Z"


@app.template_filter()
def getCookiesName(_):
	try:
		api_request = requests.get("https://api.hypixel.net/player?uuid=" + request.cookies['uuid'] + "&key=" + API_KEY)
		return json.loads(api_request.content)['player']['displayname']
	except Exception:
		return "-"


@app.template_filter()
def doesModesExist(data, modeList):
	try:
		for mode in modeList:
			data = data[mode]

		if data == "":
			return False
	except Exception:
		return False
	return True


@app.template_filter()
def currentName(uuid, conn=None, cur=None):
	if conn is None:
		conn = psycopg2.connect(DATABASE_URL)
		cur = conn.cursor()
		endConn = True
	else:
		endConn = False

	try:
		cur.execute(
			f"""
			SELECT username
			FROM uuids
			WHERE uuid = '{uuid}';
			"""
		)
		try:
			username = cur.fetchall()
			return username[0][0]
		except Exception:
			api_request = requests.get("https://sessionserver.mojang.com/session/minecraft/profile/" + uuid)
			api = json.loads(api_request.content)
			username = api['name']

			cur.execute(
				f"""
				INSERT INTO uuids (uuid, username)
				SELECT '{uuid}', '{username}'
				ON CONFLICT DO NOTHING;
				"""
			)

			if endConn:
				conn.commit()
				cur.close()
			return username
	except KeyError:
		print(api)
	except Exception as e:
		print(e)
		if endConn:
			conn.commit()
			cur.close()
		return "Your name cannot be found"


@app.template_filter()
def unHash(hash):
	data = nbt.nbt.NBTFile(fileobj=io.BytesIO(base64.b64decode(hash)))
	return data


@app.template_filter()
def profileGeneratorTry(generator, pos) -> str:
	"""
	A function to try to get a position of a dictionary, on success returning 'text-success', else returning
	'text-warning'.

	:param generator: The dictionary
	:param pos: The dataPoint
	:return: 'text-success' or 'text-warning'
	"""
	try:
		_ = generator[pos]
		return "text-success"
	except Exception:
		return "text-warning"


@app.template_filter()
def doSocialsExist(data) -> bool:
	try:
		_ = data['socialMedia']['links']
		return True
	except KeyError:
		return False


@app.template_filter()
def guildExpToLevel(exp: int) -> int:
	"""
	A function to change the guild xp of a guild into the level of that guild

	:param exp: The xp of the guild
	:return: The level of the guild
	"""
	if exp < 100000:
		return 0
	elif exp < 250000:
		return 1
	elif exp < 500000:
		return 2
	elif exp < 1000000:
		return 3
	elif exp < 1750000:
		return 4
	elif exp < 2750000:
		return 5
	elif exp < 4000000:
		return 6
	elif exp < 5500000:
		return 7
	elif exp < 7500000:
		return 8
	elif exp >= 7500000:
		if exp < 15000000:
			return math.floor((exp - 7500000) // 2500000) + 9
		else:
			return math.floor((exp - 15000000) // 3000000) + 12


@app.template_filter()
def getSocials(data):
	"""
	A function to get the links to the socials of people on hypixel.

	:param data: The data of the person
	:return: HTML data relating to the persons links
	"""
	html = ""
	for key, value in data['socialMedia']['links'].items():
		if key == "YOUTUBE":
			html += "<a href=\"" + value + "\"><img src=\"../static/images/youtubeLogo.png\", height=\"80\", width=\"80\"</img></a>"
		elif key == "TWITTER":
			html += "<a href=\"" + value + "\"><img src=\"../static/images/twitterLogo.png\", height=\"80\", width=\"80\"</img></a>"
	return html


@app.template_filter()
def stripNumbers(generator):
	try:
		_ = int(generator[len(generator)-2])
		return generator[:-3]
	except Exception:
		return generator[:-2]

# API stuff


@app.route('/api/bedwarsNameWrapper', methods=['GET'])
def apiBedwarsNameWrapper():
	name = request.args.get('name', 0, type=str)
	if name == 0:
		return {"status": 0, "reason": "Invalid Name"}
	return bedwarsNameWrapper(name, True)


@app.route('/api/duelsNameWrapper', methods=['GET'])
def apiDuelsNameWrapper():
	name = request.args.get('name', 0, type=str)
	if name == 0:
		return {"status": 0, "reason": "Invalid Name"}
	return duelsNameWrapper(name, True)


@app.route('/api/nameWrapper', methods=['GET'])
def apiNameWrapper():
	name = request.args.get('name', 0, type=str)
	useChatCodes = request.args.get('useChatCodes', False, type=str)
	if name == 0:
		return {"status": 0, "reason": "Invalid Name"}
	if useChatCodes.lower() == "true":
		return nameWrapper(name, True, useChatCodes=True)
	else:
		return nameWrapper(name, True)


@app.route("/private-proxy/", methods=['GET'])
def privateProxy_get():
	response = Response()
	response.headers["Access-Control-Allow-Origin"] = "*"
	response.headers["content-type"] = "application/json"

	url = request.args.get('url', 0, type=str)
	header = request.args.get("header", 0, type=str)
	if header == "ocp":
		response.set_data(requests.get(url, headers={"Ocp-Apim-Subscription-Key": OCP_API_KEY}).text)
		return response
	elif header == "pstack":
		query = request.args.get("query", 0, type=str)
		response.set_data(requests.get(url + "?access_key=" + PSTACK_API_KEY + "&query=" + query).text)
		return response

	return {"status": 0, "reason": "no"}


# Pages


@app.route('/guild/<name>')
def guild(name):
	data = getGuildStats(name)
	if data is None:
		return render_template('guild.html', data=0)
	else:
		conn = psycopg2.connect(DATABASE_URL)
		cur = conn.cursor()
		for i in range(len(data['members'])):
			data['members'][i]['name'] = currentName(data['members'][i]['uuid'], cur=cur, conn=conn)
		conn.commit()
		cur.close()
		return render_template('guild.html', data=data)


@app.route('/guild/')
def guildN():
	return render_template('guild.html', data=0)


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
	try:
		uuid = request.cookies['uuid']
		data = generateData(uuid)
	except KeyError:
		data = generateData()
	return render_template("player.html", data=data)


@app.route("/player/<username>")
def playerUsername(username):
	data = generateData(username)
	return render_template("player.html", data=data)


@app.route("/player/bedwars/<username>")
def player2(username):
	data = generateData(username)
	return render_template("bedwars.html", data=data, bedwarsData=data['stats']['Bedwars'])


@app.route("/watchdogstats/")
def watchdogstats():
	data = getWatchdogstats()
	return render_template("watchdogstats.html", data=data)


@app.route("/")
def home2():
	try:
		uuid = request.cookies['uuid']
		data = generateData(uuid)
		playerData = getPlayerStatus(uuid)
	except KeyError:
		data = generateData()
		playerData = getPlayerStatus()
	return render_template("home.html", data=data, status=playerData['session'])


@app.route("/suggestions/")
def suggestions():
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
	for index, item in enumerate(filteredFiles):
		filteredFiles[index] = [item]

		filteredFiles[index].append(datetime.fromtimestamp(os.path.getmtime("./templates/" + item[0])).strftime("%Y-%m-%d"))

		temp = item[0]
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

	return render_template('sitemap.xml', base_url="https://hypixeleaderboards.com", articles=filteredFiles, knownUsers=users)


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


@app.route('/guild/', methods=['POST'])
def guildPost():
	return redirect('../guild/' + request.form['playerName'])


@app.route('/guild/<username>', methods=['POST'])
def guildPost2(username):
	return redirect('/guild/' + request.form['playerName'])


@app.route('/skyblock/profile/', methods=['POST'])
def profile_post():
	try:
		profileData = generateSkyblockPlayerData(request.form['profile_id'])
		return render_template("profile.html", skyblockData=profileData, profileAsk=False)
	except Exception:
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


@app.route("/player/", methods=['POST'])
def player_post1():
	return redirect("/player/" + request.form['playerName'])


@app.route("/player/<username>", methods=['POST'])
def player_post2(username):
	return redirect("/player/" + request.form['playerName'])


@app.route("/player/duels/", methods=['POST'])
def duels_post():
	data = generateData(request.form['playerName'])
	return render_template("duels.html", data=data, duelsData=customReturn(data, ['stats', 'Duels']))


@app.route("/", methods=['POST'])
def home2_post():
	data = generateData(request.form['playerName'])
	status = getPlayerStatus(request.form['playerName'])
	return render_template("home.html", data=data, status=status['session'])


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


def exit_handler():
	pass


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
	# _2147483648

	atexit.register(exit_handler)
	commands = [
		"""
		CREATE TABLE IF NOT EXISTS uuids (
			uuid text,
			username text
		);
		"""
	]

	conn = psycopg2.connect(DATABASE_URL)
	cur = conn.cursor()
	for command in commands:
		cur.execute(command)

	cur.execute("""SELECT * from uuids;""")
	print(cur.fetchall())

	conn.commit()
	cur.close()

	app.run()
