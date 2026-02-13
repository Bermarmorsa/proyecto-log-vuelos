import requests
import pandas as pd
from geopy.distance import geodesic
import os
from dotenv import load_dotenv
from dateutil.relativedelta import relativedelta
from datetime import datetime
import logging

# 1. Creamos el logger
logger = logging.getLogger("mi_app")
logger.setLevel(logging.DEBUG)

# 2. Definimos el formato que me pediste
formato = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# 3. Handler para la CONSOLA (Pantalla)
consola = logging.StreamHandler()
consola.setFormatter(formato)

# 4. Handler para el ARCHIVO
archivo = logging.FileHandler('registro_programa.log')
archivo.setFormatter(formato)

# 5. Agregamos los manejadores al logger
logger.addHandler(consola)
logger.addHandler(archivo)


load_dotenv()
token = os.getenv("API_KEY_AEMET")



def obtener_estaciones():
    # para conocer que estaciones de meteo hay se extraen las estaciones posibles

    logger.info("Obteniendo lista de estaciones.")

    url = f"https://opendata.aemet.es/opendata/api/observacion/convencional/todas/?api_key={token}"
    meta = requests.get(url).json()
    datos_url = meta["datos"]
    estaciones = requests.get(datos_url).json()
    return estaciones


def estacion_mas_cercana(lat, lon, estaciones):

    # calcula la estación mas cercana a las coordenadas

    logger.info("Buscando estacioon mas cercana")
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


def generate_six_month_periods(start_date_str, end_date_str):
    """
    Generates pairs of dates, each representing a 6-month period,
    within a given start and end date.

    Args:
        start_date_str (str): The initial start date in 'YYYY-MM-DDTHH:MM:SSUTC' format.
        end_date_str (str): The overall end date in 'YYYY-MM-DDTHH:MM:SSUTC' format.

    Returns:
        list: A list of tuples, where each tuple contains (period_start_str, period_end_str).
    """
    date_format = '%Y-%m-%dT%H:%M:%SUTC'
    start_date = datetime.strptime(start_date_str, date_format)
    end_date = datetime.strptime(end_date_str, date_format)

    periods = []
    current_start = start_date

    while current_start < end_date:
        # Calculate 6 months from the current start
        period_end = current_start + relativedelta(months=+6)

        # Ensure the period does not go beyond the overall end_date
        actual_period_end = min(period_end, end_date)

        periods.append((current_start.strftime(date_format), actual_period_end.strftime(date_format)))

        # Set the next start date to the end of the current period
        current_start = actual_period_end

    return periods


def datos_estacion(idema, fechaIniStr, fechaFinStr):
    # Added the api_key to the URL, using the global 'token' variable
    url = f"https://opendata.aemet.es/opendata/api/valores/climatologicos/diarios/datos/fechaini/{fechaIniStr}/fechafin/{fechaFinStr}/estacion/{idema}/?api_key={token}"



    try:
        meta = requests.get(url).json()
        logger.info("Contenido Metadatos" + str(meta))

        datos_url = meta['datos']
        try:
            data = requests.get(datos_url).json()
            df = pd.DataFrame(data)[['fecha', 'horatmax', 'tmed', 'tmin', 'prec']]

            # Convertir 'tmed' y 'tmin' a valores numéricos (float)
            # Primero, reemplazar la coma por un punto para que pandas pueda interpretar el número.
            # Luego, convertir la columna a tipo float.
            df['fecha'] = df['fecha']
            df['tmed'] = df['tmed'].str.replace(',', '.', regex=False).astype(float)
            df['tmin'] = df['tmin'].str.replace(',', '.', regex=False).astype(float)
            df['prec'] = df['prec'].str.replace(',', '.', regex=False).astype(float)
            return df
        except requests.exceptions.HTTPError as err:
            logger.error("Error obteniendo los datos de la estación: " + err)

    except requests.exceptions.HTTPError as err:
        logger.error("Error obteniendo los metadatos: " + meta)

'''
fecha_inicio = '2024-11-01T12:00:00UTC'
fecha_fin = '2025-05-01T12:00:00UTC'
print(datos_estacion('3209Y', fecha_inicio, fecha_fin))
'''





def filtrar_por_fecha_hora(datos, fecha, hora):
    print('datos dentro de consultar_meteo')
    print(datos)

    objetivo = f'{fecha[0:4]}-{fecha[4:6]}-{fecha[6:8]}T{hora[0:2]}:{hora[2:4]}:00+0000'





def consultar_meteo(lat, lon, fecha_inicio, fecha_fin):

    # se ejecutan los metodos para extraer datos de la api de AEMET

    estaciones = obtener_estaciones()
    est = estacion_mas_cercana(lat, lon, estaciones)

    print(f"Estación más cercana: {est['idema']} - {est['ubi']}")

    # antes de extrar los datos habría que generar periodos de seis meses, porque aemet solo deja de 6 en 6 meses USAR generate_six_month_periods

    periodos = generate_six_month_periods(fecha_inicio,fecha_fin)
    print(f"Periodos: {periodos[0]}")

    #ahora hay que generar un bucle que vaya extrayendo de 6 en meses con las fechas generadas anteriormete los dataframes y los añada a uno inicial

    datos = pd.DataFrame()

    for periodo in periodos:

        fecha_inicio = periodo[0]
        fecha_fin = periodo[1]

        datosnew = datos_estacion(est["idema"], fecha_inicio, fecha_fin)

        datos = pd.concat([datos, datosnew], ignore_index=True)

    #hasta aqui tenemos los datos de un periodo extraidos

 # hay que recoger  la hora más cercana filtrar hora y dia

    return datos

#taragudo 40.820730, -3.093183

# formato fecha api '2025-11-01T12:00:00UTC'

#2026-02-11T20:00:00+0000
lat = 40.820730
lon = -3.093183
fecha_inicio = '2024-11-01T12:00:00UTC'
fecha_fin = '2026-02-01T12:00:00UTC'




#df = consultar_meteo(lat, lon, fecha_inicio, fecha_fin)

#df.to_csv('meteo_export.csv', index=False)
