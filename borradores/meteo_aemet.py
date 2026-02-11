import http.client
import os
from dotenv import load_dotenv

# Cargamos las variables del archivo .env
load_dotenv()
token = os.getenv("API_KEY_AEMET")

conn = http.client.HTTPSConnection("opendata.aemet.es")

headers = {
    'cache-control': "no-cache"
    }

conn.request("GET", f"/opendata/api/valores/climatologicos/inventarioestaciones/todasestaciones/?api_key={token}", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))


import requests

url = "https://opendata.aemet.es/opendata/api/valores/climatologicos/inventarioestaciones/todasestaciones/"

querystring = {"api_key":token}

headers = {
    'cache-control': "no-cache"
    }
params = {

}

response = requests.request("GET", url, headers=headers, params=querystring)



print(response.json())