# Aqui crearemos los metodos que vana a generar la salida de datos. Un excel que tiene la tabla de datos y una hora añadida que es
# una especie de cuadro de mandos con kpis y algunas gráfica
import datetime

# cargamos las librerias necesarias
import pandas as pd
from loguru import logger
from pandas.core.interchange.from_dataframe import primitive_column_to_ndarray

import tranformacion_calculos
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

ruta_salida = BASE_DIR / "archivos_salida" / 'Log-Vuelos_dashboard.xlsx'


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



def añadir_grafico_lineas(writer, df, campo_x, campo_y, graf_name, posicion_hoja , width, height, hoja_nombre="Graphics" ):
    workbook = writer.book

    # Asegurarnos de que la hoja tenga los datos escritos antes de graficar
    # Si no escribes el DF en esta hoja, el gráfico no tiene de dónde leer.
    if hoja_nombre not in writer.sheets:
        df.to_excel(writer, sheet_name=hoja_nombre, index=False)

    worksheet = writer.sheets[hoja_nombre]

    # Localizar índices de columnas
    try:
        col_fecha = df.columns.get_loc(campo_x)
        col_acumulado = df.columns.get_loc(campo_y)
    except KeyError as e:
        print(f"Error: No se encontró la columna {e}")
        return

    # Crear el objeto gráfico
    grafico = workbook.add_chart({'type': 'line'})

    # Definir el número de filas (datos + cabecera)
    max_row = len(df)

    # Configurar la serie
    # Formato: [hoja, fila_inicio, col_inicio, fila_fin, col_fin]
    grafico.add_series({
        'name': graf_name,
        'categories': [hoja_nombre, 1, col_fecha, max_row, col_fecha],
        'values': [hoja_nombre, 1, col_acumulado, max_row, col_acumulado],
        'line': {'color': 'blue'},
    })

    grafico.set_title({'name': graf_name})
    grafico.set_x_axis({'name': campo_x,
                        'date_axis': True,
                        'num_format': 'YYYY-MM-DD' } )
    grafico.set_y_axis({'name': campo_y,
                        'num_format': '#.##0,00'} )
    grafico.set_size({'width': width, 'height': height})

    # Insertar el gráfico
    worksheet.insert_chart(posicion_hoja, grafico)  # Movido a la derecha para no tapar datos

def ejecutar_reporte_vuelos():
    # 1. Obtener los datos usando tus funciones actuales
    df_final = tranformacion_calculos.join_log_meteo()
    df_final["Fecha"] = pd.to_datetime(df_final["Fecha"])

    print(df_final.dtypes)



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
        # para generar las graficas
        añadir_grafico_lineas(writer, df_final, "Fecha" , "frecuencia_vuelos", 'Evol Frecuencia', 'V5', 800, 400)
        añadir_grafico_lineas(writer, df_final, "Fecha", "acumulado_decimales" , 'Acumulado horas', 'V30', 800, 400)
        añadir_grafico_lineas(writer, df_final, "Fecha", "coste", 'Acumulado coste', 'V51', 800, 400)

        # Guardamos
        writer.close()
        logger.success(f"Reporte generado en {ruta_excel}")
    except Exception as e:
        logger.error(f"Fallo al escribir Excel: {e}")
        writer.close()



ejecutar_reporte_vuelos()



