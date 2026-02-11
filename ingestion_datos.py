# se ingestaran los datos de el xla
import pandas as pd
import openpyxl
import requests
import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("API_KEY")
ciudad = ''

# exportar libreria para leer xls


ruta = 'C:\\Users\\b.martin\\Documents\\Workspace\\proyecto_vuelos\\archivos_entrad\\Log-Vuelos.xlsx'



def lector_excel(ruta):
    try:
        df = pd.read_excel(ruta , engine='openpyxl')
    except FileNotFoundError as fl:
        print(f'ha habido un error: {fl}')

    return df



# recogida de datos de la API de meteo,

#def leer_api_meteo(lugar, fecha, orig):

def leer_api_meteo(lugar):

    load_dotenv()
    token = os.getenv("API_KEY")
    visibilidad = ''
    windv = ''
    winddir = ''
    pressatm = ''

    url = "https://api.openweathermap.org/data/2.5/weather"
    parametros = {
        "q": lugar,
        "appid": token,  # Usamos la variable cargada
        "units": "metric",
        "lang": "es"
    }

    # ... resto del código con requests.get(url, params=parametros)

    respuesta = requests.get(url, params=parametros)

    try:
        datos = respuesta.json()
        print('-' *50)
        print(datos)
        print(f"Meteologia en {datos['name']}")
        #lugar = datos['name']
        print(f"La visibilidad es {datos['visibility']}m")
        visibilidad = datos['visibility']
        print(f"La temperatura actual es {datos['main']['temp']}°C")
        print(f"La temperatura máxima: {datos['main']['temp_max']}°C")
        print(f"La temperatura mímima: {datos['main']['temp_min']}°C")
        print(f"La humedad actual es {datos['main']['humidity']} %")
        print(f"El viendo con una velocidad de: {round(datos['wind']['speed'] * 3.6, 2)} km/h y desde los {datos['wind']['deg']}º")
        windv = round(datos['wind']['speed'] * 3.6, 2)
        winddir = round(datos['wind']['deg'], 2)
        print(f"La presion atmosferica es: {datos['main']['pressure']}  hPa")
        pressatm = datos['main']['pressure']
        print('-' * 50)

    except requests.exceptions.HTTPError as err:
        print(f'Error de conexión {err}')


   # crear dataframe de los datos con campos fecha lugar



    df_meteo = {
        "lugar": [lugar],
        "visibilidad": [visibilidad],
        "velicidad_viento": [windv],
        "direcion_viento": [winddir]
    }

    print('daframe de con los datos meteo generado' )

    return df_meteo



# SALIDA este objeto de salida se utilizará en las transformaciones


print(leer_api_meteo('Madrid'))