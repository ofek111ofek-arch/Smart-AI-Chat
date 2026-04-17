import requests
url = "https://server.iac.ac.il/api/v1/studentapi/generate_key"
payload = {"id": "318969938", "password": "Necr6616"}
print(requests.post(url, json=payload).json())
