import pandas as pd
from src.log_vuelos.ingestion_datos import lector_excel
from src.log_vuelos import open_meteo
import os
from loguru import logger
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

#variables
ruta = BASE_DIR / "archivos_entrad" / 'Log-Vuelos.xlsx'
print(ruta)
lat = 40.820730
lon = -3.093183



def transformaciones_log(ruta):

    df_log = lector_excel(ruta)

    #print(df_log.dtypes)


    #extrar del xls las celdas que nos interesan tipo vuelo I y no vacios

    df_log_i = df_log[df_log["tipo vuelo"].fillna("").str.strip() == "I"]


    df_log_lf = df_log_i[['tipo vuelo','Fecha','Hora inicio','Hora Fin','Avion','Aerodromo Origen','Aerodromo Destino','Observaciones']]

    #pasar los datos de horas de inicio y fin a fecha

    if pd.api.types.is_object_dtype(df_log_lf['Hora inicio']):
        df_log_lf['Hora inicio'] = pd.to_datetime(df_log_lf['Fecha'].dt.strftime('%Y-%m-%d') + ' ' + df_log_lf['Hora inicio'].astype(str))

    # Check if 'Hora Fin' is still an object type before converting
    if pd.api.types.is_object_dtype(df_log_lf['Hora Fin']):
        df_log_lf['Hora Fin'] = pd.to_datetime(df_log_lf['Fecha'].dt.strftime('%Y-%m-%d') + ' ' + df_log_lf['Hora Fin'].astype(str))




    #calcular las horas acumuladas por cada linea en un nuevo campo


    df_log_lf['Tiempo vuelo'] = df_log_lf['Hora Fin'] - df_log_lf['Hora inicio']

    df_log_lf['tiempo acumulado'] = df_log_lf['Tiempo vuelo'].cumsum()

    df_log_lf["acumulado_decimales"] = df_log_lf["tiempo acumulado"].dt.total_seconds() / 3600





    #crear nuevo campo con el calculo de coste horas_acumuladas * precio

    df_log_lf["precio"] = 150 # se puede cambiar por un precio añadido a la tabla por los cambios


    df_log_lf["coste"] = df_log_lf["precio"] * df_log_lf["acumulado_decimales"]


    #crear nuevo campo que sea el calculo de frecuencia de vuelo para cada linea, horas de vuelo / dias trascurridos de instrucción

    min_fecha = df_log_lf["Fecha"].min()

    #print(min_fecha)

    #df_log_lf['frecuencia_vuelos'] = df_log_lf["acumulado_decimales"] / (df_log_lf["Fecha"] - min_fecha )

    df_log_lf['frecuencia_vuelos'] = round((df_log_lf["Fecha"] - min_fecha ).dt.days / df_log_lf["acumulado_decimales"],2)




    logger.info('dataframe de log')
    print(df_log_lf)

    return df_log_lf



    #obtener datos de meteo en nuevas columnas los datos de la meteo.

def datos_meteo(df):

    print('-----------------contenido df log para buscar fechas min y max-------------------')
    print(df)

    fecha_inicio_to_met = f'{str(df["Fecha"].min())[0:10]}'
    print('Fecha inicio: ',fecha_inicio_to_met)
    fecha_fin_to_met = f'{str(df["Fecha"].max())[0:10]}'
    nombre_archivo = f'meteo_open_{fecha_inicio_to_met[0:10]}_{fecha_fin_to_met[0:10]}.parquet'

    nombre_archivo_meteo = BASE_DIR / "archivos_salida" / nombre_archivo

    logger.info('-----------------nombre_archivo_meteo-------------------')
    logger.info(nombre_archivo)


   #comprobar si hay un csv con primera y ultima fechas como las de inicio y fin
    if os.path.isfile(nombre_archivo_meteo):
        logger.info("El archivo existe.")
        df = pd.read_parquet(nombre_archivo_meteo)

    else:
        logger.info("El archivo csv de meteo no existe. Recargamos los datos desde la API.")
        logger.info(nombre_archivo_meteo)
        # si se ha generado leer el csv y generar el df del csv
        # si no coinciden ejecutar toda la API. generar nuevo df

        logger.info(f'esta es la fecha de inicio: {fecha_inicio_to_met} esta la de fin {fecha_fin_to_met}')

        df = open_meteo.df_meteo_open(fecha_inicio_to_met, fecha_fin_to_met, lon, lat)
        #print('-----------------------OBTENER DATOS METEO OPEN')
        #print(df)

    return df

def join_log_meteo():

    # cracion de dataframe de log de vuelos
    df_log= transformaciones_log(ruta)
    logger.info('Creando el dataframe de log')

    df_log = df_log.sort_values("Hora Fin")
    logger.info('ordenamos el dataframe de log previo a join')
    print(df_log)


    #cargamos la meteo creación de la meteo de la API
    df_meteo = datos_meteo(df_log)

    logger.info('Carga de la Meteo')

    # Para crear la fecha como la que hay en el log

    # Mantener solo las filas donde horatmax != "Varias"
    #df_meteo = df_meteo[df_meteo["horatmax"] != "Varias"]
    try:
        df_meteo['fecha_hora'] = df_meteo["date"]
        print(f'--------------------------------formato de fecha en meteo {df_meteo["fecha_hora"]}')
        df_meteo["fecha_hora"] = pd.to_datetime(df_meteo['fecha_hora'], format="%Y-%m-%d %H:%M:%S", errors="raise")

        # fitramos los nulos
        df_meteo = df_meteo[df_meteo["fecha_hora"].notna()]
        # antes del cruce hay que ordenar los dartaframes
        df_meteo = df_meteo.sort_values("fecha_hora")
        logger.info('Filtrados de meteo y orden previo a join')
    except Exception as e:
        logger.info(e)

    #print(df_meteo)
    #print(df_meteo.dtypes)




    print('------------tipo log----------------------')
    print(df_log.dtypes)
    print('------------tipo meteo----------------------')
    print(df_meteo.dtypes)

    # cambiar tipo de campo de cruce en el log
    df_log["Hora Fin"] = df_log["Hora Fin"].dt.tz_localize(None)

    #cambiar fecha de cruce en meteo

    #df_meteo["fecha_hora"] = df_meteo["fecha_hora"].astype("datetime64[us]")

    df_meteo["fecha_hora"] = (
        df_meteo["fecha_hora"]
        .dt.tz_localize(None)
        .astype("datetime64[s]")  # quita sub-segundos
        .astype("datetime64[us]")  # misma info pero en resolución us
    )

    df_meteo["date"] = (
        df_meteo["date"]
        .dt.tz_localize(None)
        .astype("datetime64[s]")  # quita sub-segundos
        .astype("datetime64[us]")  # misma info pero en resolución us
    )

    print('------------tipo log despues de cambio fecha----------------------')
    print(df_log.dtypes)
    print('------------tipo log despues de cambio fecha----------------------')
    print(df_meteo.dtypes)
    print('------------tipo log despues de cambio fecha fin----------------------')



    # union de los dataframes de por la fecha y hora mas cercanas para añadir los datos de estación mas proximos a la hora y dia del vuelo.
    df_resultado = pd.merge_asof(
        df_log, df_meteo,
        left_on="Hora Fin",
        right_on='fecha_hora', # o left_on/right_on si se llaman distinto
        direction="nearest"     # o 'backward'/'forward'
    )

    logger.info('Creacion de join de log y meteo')

    return df_resultado


print(join_log_meteo())