import urllib.request, urllib.error, urllib.parse
URL_EXTENTIONS = ["bedwars", "skywars", "duels", "arena", "mcgo", "battleground", "survival-games", "uhc", "walls", "paintball", "murder-mystery", "super-smash", "speed-uhc", "tntgames", "gingerbread", "build-battle", "arcade", "skyclash", "quakecraft", "true-combat", "walls3", "vampirez"]

with open("./knownUsers.json", "w") as f:
    f.write("{}")

for extention in URL_EXTENTIONS:
    response = urllib.request.urlopen("http://www.hypixeleaderboards.com/leaderboards/" + extention)