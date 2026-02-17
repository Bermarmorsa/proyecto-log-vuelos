# Aqui crearemos los metodos que vana a generar la salida de datos. Un excel que tiene la tabla de datos y una hora añadida que es
# una especie de cuadro de mandos con kpis y algunas gráfica

# cargamos las librerias necesarias
import pandas as pd
from loguru import logger
import tranformacion_calculos
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

ruta_salida = BASE_DIR / "archivos_salida" / 'Log-Vuelos_dashboard.xlsx'


# leemos el df creado en tranformaciones
'''
df = tranformacion_calculos.join_log_meteo()
logger.info('Creamos el df de pandas con todos los datos')


df_dashboard = df[['frecuencia_vuelos', 'coste', 'acumulado_decimales']].max().to_frame().T
print('----------------df para dashboard-------------------')
print(df_dashboard)
'''

def configurar_archivo_excel(ruta_archivo):
    # Definimos el motor xlsxwriter

    writer = pd.ExcelWriter(ruta_archivo, engine='xlsxwriter')
    workbook = writer.book

    # Aquí podemos pre-definir formatos (negritas, colores, bordes)
    formato_cabecera = workbook.add_format({
        'bold': True,
        'bg_color': '#D7E4BC',
        'border': 1
    })

    return writer, formato_cabecera


def ejecutar_reporte_vuelos():
    # 1. Obtener los datos usando tus funciones actuales
    df_final = tranformacion_calculos.join_log_meteo()

    # 2. Calcular KPIs básicos para la segunda hoja
    # Ejemplo: Coste total y tiempo total de vuelo
    df_kpis = df_final[['frecuencia_vuelos', 'coste', 'acumulado_decimales']].max().to_frame().T

    ruta_excel = BASE_DIR / "archivos_salida" / 'Log-Vuelos_dashboard.xlsx'

    # 3. Iniciar el proceso de Excel
    writer, formato = configurar_archivo_excel(ruta_excel)

    try:
        # Enviamos los datos a las hojas
        df_final.to_excel(writer, sheet_name='Datos_Completos', index=False)
        df_kpis.to_excel(writer, sheet_name='KPIs', startrow=1)

        # Guardamos
        writer.close()
        logger.success(f"Reporte generado en {ruta_excel}")
    except Exception as e:
        logger.error(f"Fallo al escribir Excel: {e}")
        writer.close()



def añadir_grafico_tendencia(writer, df):
    workbook = writer.book
    hoja_dash = writer.sheets['Graphics']
    max_row = len(df) # Respuesta 2: Contamos las filas del DataFrame 🧮

    # Creamos un gráfico de líneas
    grafico = workbook.add_chart({'type': 'line'})




ejecutar_reporte_vuelos()


#----------------------------------------------------------------------------------------------

'''def configurar_archivo_excel(ruta_archivo):
    # Definimos el motor xlsxwriter

    writer = pd.ExcelWriter(ruta_archivo, engine='xlsxwriter')
    workbook = writer.book

    # Aquí podemos pre-definir formatos (negritas, colores, bordes)
    formato_cabecera = workbook.add_format({
        'bold': True,
        'bg_color': '#D7E4BC',
        'border': 1
    })

    return writer, formato_cabecera


writer , formato_cabecera = configurar_archivo_excel(ruta_salida)



def diseñar_hojas(writer, df_datos, df_kpis):
    # 1. Escribir los datos brutos
    df.to_excel(writer, sheet_name='Datos', index=False)

    # 2. Escribir los KPIs
    df.to_excel(writer, sheet_name='Dashboard', startrow=1, startcol=1)

    # Obtener los objetos de las hojas para dar formato
    hoja_datos = writer.sheets['Datos']
    hoja_dash = writer.sheets['Dashboard']

    # Ajustar el ancho de las columnas automáticamente (ejemplo)
    hoja_datos.set_column('A:Z', 15)
    hoja_dash.set_column('B:E', 20)

    return hoja_dash

diseñar_hojas(writer , df ,  df_dashboard)'''
