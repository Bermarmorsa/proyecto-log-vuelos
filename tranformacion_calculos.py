import pandas as pd
from numpy import dtype
from ingestion_datos import lector_excel
import aemet_lat_log_time
import os



#variables
ruta = 'C:\\Users\\b.martin\\Documents\\Workspace\\proyecto_vuelos\\archivos_entrad\\Log-Vuelos.xlsx'
lat = 40.820730
lon = -3.093183



def transformaciones_log(ruta):

    df_log = lector_excel(ruta)

    #print(df_log.dtypes)


    #extrar del xls las celdas que nos interesan tipo vuelo I y no vacios

    df_log_i = df_log[df_log["tipo vuelo"].fillna("").str.strip() == "I"]


    df_log_lf = df_log_i[['tipo vuelo','Fecha','Hora inicio','Hora Fin','Avion','Aerodromo Origen','Aerodromo Destino']]

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

    return df_log_lf



    #obtener datos de meteo en nuevas columnas los datos de la meteo.

def datos_meteo(df):

    fecha_inicio = (f'{str(df["Fecha"].min())[0:10]}T00:00:00UTC')
    fecha_fin = (f'{str(df["Fecha"].max())[0:10]}T00:00:00UTC')

    nombre_archivo_meteo = f'C:\\Users\\b.martin\\Documents\\Workspace\\proyecto_vuelos\\exp_archivos_salida\\meteo_{str(df["Fecha"].min())[0:10]}_{str(df["Fecha"].max())[0:10]}.csv'
    print('-----------------nombre_archivo_meteo-------------------')
    print(nombre_archivo_meteo)


   #comprobar si hay un csv con primera y ultima fechas como las de inicio y fin
    if os.path.isfile(nombre_archivo_meteo):
        print("El archivo existe.")
        df = pd.read_csv(nombre_archivo_meteo)

    else:
        print("El archivo no existe.")
        # si se ha generado leer el csv y generar el df del csv
        # si no coinciden ejecutar toda la API. generar nuevo df

        print(f'esta es la fecha de inicio: {fecha_inicio} esta la de fin {fecha_fin}')

        df = aemet_lat_log_time.consultar_meteo(lon, lat, fecha_inicio, fecha_fin)

    return df


df_log= transformaciones_log(ruta)
print('-----------------------------log---------------------------')
print(df_log)

df_meteo = datos_meteo(df_log)
print('-----------------------------meteo---------------------------')
print(df_meteo)

df_resultado = pd.merge(df_log, df_meteo, left_on='Fecha', right_on='horatmax', how='left')

print(df_resultado)


    # esta tabla que se genera sera la entrad de datos de la visualización

#cruce pandas

# primero filtrar los datos meteo para trare solo fechas concretas y las horas entre el inicio y el fin del vuelo.



#df_resultado = pd.merge(df1, df2, on='id_cliente', how='inner')



#print(datos_meteo())

