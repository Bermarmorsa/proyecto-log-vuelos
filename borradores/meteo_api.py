# cargamos librerias

import requests
import os
from dotenv import load_dotenv
import datetime

# Cargamos las variables del archivo .env
load_dotenv()
token = os.getenv("API_KEY")
ciudad = ''







def clima_ciudad (ciudad):

    url = "https://api.openweathermap.org/data/2.5/weather"
    parametros = {
        "q": ciudad,
        "appid": token,  # Usamos la variable cargada
        "units": "metric",
        "lang": "es"
    }

    # ... resto del código con requests.get(url, params=parametros)


    respuesta = requests.get(url, params=parametros)

    try:
        datos = respuesta.json()
        print(datos)
        print(f"Meteologia en {datos['name']}")
        print(f"La visibilidad es {datos['visibility']}m")
        print(f"La temperatura actual es {datos['main']['temp']}°C")
        print(f"La temperatura máxima: {datos['main']['temp_max']}°C")
        print(f"La temperatura mímima: {datos['main']['temp_min']}°C")
        print(f"La humedad actual es {datos['main']['humidity']} %")
        print(f"El viendo con una velocidad de: {round(datos['wind']['speed'] * 3.6, 2  )} km/h y desde los {datos['wind']['deg']}º")
        print(f"La presion atmosferica es: {datos['main']['pressure']}  hPa")

    except requests.exceptions.HTTPError as err:
        print(f'Error de conexión {err}')

#primero sacaremos las coordenadas por el nombre de la ciudad
def ciudad_to_geo(city_name, state_code, country_code):
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name},{state_code},{country_code}&limit={1}&appid={token}"

    respuesta = requests.get(url)

    try:
        datos = respuesta.json()

    except requests.exceptions.HTTPError as err:
        print(f'Error de conexión {err}')


#coordenadas de taragudo 40.820730, -3.093183
def clima_lugar_fecha():

    lat = 40.820730
    lon = -3.093183
    time = datetime.datetime.now()




    url = f"https://api.openweathermap.org/data/3.0/onecall/timemachine?lat={lat}&lon={lon}&dt={time}&appid={token}"

    # ... resto del código con requests.get(url, params=parametros)

    respuesta = requests.get(url)

    try:
        datos = respuesta.json()
        return datos

    except requests.exceptions.HTTPError as err:
        print(f'Error de conexión {err}')


print(clima_lugar_fecha())


def preguntar_ciudad():

    ciudad = input('De que ciudad quieres saber la meteo: ')
    ciudad = ciudad.lower().capitalize()
    #print(ciudad)

    clima_ciudad(ciudad)
'''
while True:
    if ciudad != 'exit':
        preguntar_ciudad()
    elif ciudad == 'exit':
        break
'''