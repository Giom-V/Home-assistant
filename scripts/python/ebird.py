import requests
import json

url = "https://api.ebird.org/v2/data/obs/geo/recent?lat=46.7777219&lng=-71.3269207&maxResults=10&dist=2&sppLocale=fr"

payload = {}
headers = {
  'X-eBirdApiToken': 'bluvudkg3dkr'
}

response = requests.request("GET", url, headers=headers, data = payload)

print(response.text.encode('utf8'))

json.loads(response.text.encode('utf8'))