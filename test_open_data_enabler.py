import requests
import json

url = "http://localhost:4020/newoffering"

payload = json.dumps({
  "dcatRDF": "https://ckan.salted-project.eu/dataset/transportation_trafficflowobserved.rdf",
  "accessURL": "https://ckan.salted-project.eu/retriever/realtime/__https%3A%2F%2Fsmartdatamodels.org%2FdataModel.Transportation%2FTrafficFlowObserved__.jsonld"
})

headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)
print(json.dumps(json.loads(response.text), ensure_ascii=False, indent=3))
