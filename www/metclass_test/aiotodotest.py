import requests,json

body = json.dumps({"name":"feed the api"})
url = "http://localhost:8080/todos/"

r = requests.post(url=url,data=body)
r.content
