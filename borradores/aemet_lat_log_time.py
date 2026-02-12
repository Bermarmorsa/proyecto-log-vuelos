import requests
import pandas as pd
from geopy.distance import geodesic
import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("API_KEY_AEMET")


def obtener_estaciones():
    url = f"https://opendata.aemet.es/opendata/api/observacion/convencional/todas/?api_key={token}"
    meta = requests.get(url).json()
    datos_url = meta["datos"]
    estaciones = requests.get(datos_url).json()
    return estaciones


def estacion_mas_cercana(lat, lon, estaciones):
    objetivo = (lat, lon)

    dist_min = float("inf")
    estacion_cercana = None

    for est in estaciones:
        coord = (est["lat"], est["lon"])
        d = geodesic(objetivo, coord).km

        if d < dist_min:
            dist_min = d
            estacion_cercana = est

    return estacion_cercana



def datos_estacion(idema):
    url = f"https://opendata.aemet.es/opendata/api/observacion/convencional/datos/estacion/{idema}/?api_key={token}"
    meta = requests.get(url).json()
    print('meta')
    print(meta)
    datos_url = meta['datos']
    datos = requests.get(datos_url).json()
    return datos

#print('salida de datos_estacion:')
#print(datos_estacion('3209Y'))

from datetime import datetime

def filtrar_por_fecha(datos, fecha, hora):
    print('datos dentro de consultar_meteo')
    print(datos)



    objetivo = f'{fecha[0:4]}-{fecha[4:6]}-{fecha[6:8]}T{hora[0:2]}:{hora[2:4]}:00+0000'


    for dato in datos:
        if dato["fint"] == objetivo:  #este filtro no parece que funcione REVISAR
            return dato

    return None


def consultar_meteo(lat, lon, fecha, hora):
    estaciones = obtener_estaciones()
    est = estacion_mas_cercana(lat, lon, estaciones)

    print(f"Estación más cercana: {est['idema']} - {est['ubi']}")

    datos = datos_estacion(est["idema"])
    resultado = filtrar_por_fecha(datos, fecha, hora)

    return resultado

#taragudo 40.820730, -3.093183

#print(consultar_meteo(40.820730, -3.093183, '20260211', '1200'))



#2026-02-11T20:00:00+0000

fecha = '20260211'
hora = '1200'

print(f'Fecha: {fecha[0:4]}-{fecha[4:6]}-{fecha[6:8]}T{hora[0:2]}:{hora[2:4]}:00+0000')
