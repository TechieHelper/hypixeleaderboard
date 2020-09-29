import json
with open("dashedData.json") as f:
    api = json.loads(f.read())
api = api["player"]["stats"]["SkyWars"]
for i in api:
    print("\"" + i + "\": \"-\",")