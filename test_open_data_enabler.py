import requests
import json

url = "http://localhost:4020/newoffering"

payload = json.dumps({
  "url": "https://ckan.salted-project.eu/dataset/transportation_trafficflowobserved.rdf"
})
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)
print(json.dumps(json.loads(response.text), indent=3))
