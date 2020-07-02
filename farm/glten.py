import requests
import json

res = requests.get("https://glten.org/api/v0/public/experiment/74")
jres = json.loads(res.text)
print(json.dumps(jres, indent=4, sort_keys=True))
